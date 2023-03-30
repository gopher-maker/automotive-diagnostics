"""Model of a vehicle Powertrain."""

import math
# TODO(jmbagara): Remove this import.
import random
import time

from common import model_math
from vehicle_model.plant import cooling_system, battery, inverter, motor


# Constants.
RUN_TIME = 20  # [Sec], simulation runtime.
DATA_RATE = 0.01  # [Sec], interval at which to yield simulation data.

# TODO(jmbagara): Move these parameters to a YAML file.

# Battery parameters.
# See: https://www.secondlife-evbatteries.com/products/tesla-5-3-kwh-electric-vehicle-battery.
v_nominal = 400.0  # [V], nominal battery voltage at 100% state of charge.
q_nominal = 3712  # [A.h], battery capacity i.e. 16x modules, @ 232 A.h/5.3 kWh.
r_internal = 0.02  # [Ohm], assumes 6S12P configuration of cells in each module.

# Inverter parameters.
r_ds_on = 0.004  # [Ohm].
f_switching = 15000  # [Hz].
t_rise = 4e-9  # [s]
t_fall = 6e-9  # [s]

# Motor parameters.
Ld = 165e-6  # [H], motor direct inductance.
Lq = 165e-6  # [H], motor quadrature inductance.
Ke = 0.067  # [Vphpk/(rad/s)], motor EMF constant.
Rs = 0.04  # [Ohm], motor winding resistance.
n_pp = 32  # [], number of motor pole pairs.
flux_linkage = 0.15  # [N-m/A = V-s/rad = Wb], motor flux linkage.

# Cooling system parameters.
T_ambient = 25  # [degC], ambient temperature.
Rth_batt_junc = 5e-3  # [degC/W], thermal resistance of Al-fluid interface.
Rth_inverter_junc = 5e-3  # [degC/W], thermal resistance of Al-fluid interface.
Rth_motor_junc = 5e-3  # [degC/W], thermal resistance of Al-fluid interface.
# See: https://lairdthermal.com/thermal-technical-library/application-notes/common-coolant-types-and-their-uses-liquid-cooling-systems
# 50-50 Water-Ethylene glycol.
fluid_density = 1082  # [kg/m^3], density of cooling fluid.
pipe_area = 2e-4  # [m^2], assumes 5/8 inch diameter cooling pipes.
fluid_heat_capacity = 3283  # [J/kg.K], specific heat capacity of cooling fluid.


class Vehicle:
  """Representation of a vehicle powertrain."""

  def __init__(self, vehicle_id=1, fault_injection_mode=False):
    self._vehicle_id = vehicle_id
    self._battery = battery.Battery(
        v_nominal, q_nominal, r_internal, fault_injection_mode)
    self._inverter = inverter.Inverter(
        r_ds_on, f_switching, t_rise, t_fall, fault_injection_mode)
    self._motor = motor.Motor(
        Ld, Lq, Ke, Rs, n_pp, flux_linkage, fault_injection_mode)
    self._cooling_sys = cooling_system.CoolingSystem(
        T_ambient, Rth_batt_junc, Rth_inverter_junc, Rth_motor_junc,
        fluid_density, pipe_area, fluid_heat_capacity, fault_injection_mode)

    # Time parameters.
    self._loop_start_timestamp = None
    self._loop_end_timestamp = None
    self._loop_dt = None
    self._elapsed_time = None

    # TODO(jmbagara): Make these "dynamic" as they should be.
    # Simulator input variables.
    self._i_bus_cmd = 200  # [A].
    self._fluid_velocity = 2  # [m/s], typical 6-8 ft/s (1.8-2.4 m/s) flow rate.

    # TODO(jmbagara): Make these "dynamic" as they should be.
    # Simulator output variables.
    ## Battery.
    self._v_bus = 400  # [V].
    self._i_bus = 0  # [A].
    self._batt_soc = 100.0  # [%].
    ## Inverter.
    self._v_d = 0
    self._v_q = 0
    self._i_d = 0
    self._iq_cmd = 0
    ## Motor.
    self._torque_mech = 0
    self._omega_mech = 100.0  # [rad/s].
    self._theta_elec = 0  # TODO(jmbagara): Clean up usage of this variable.
    ## Cooling System.
    self._T_junc_batt = 0.0
    self._T_junc_inverter = 0.0
    self._T_junc_motor = 0.0
    self._T_fluid = 0.0

    # Power loss variables.
    self._batt_losses = 0.0
    self._inverter_losses = 0.0
    self._motor_losses = 0.0

    self._sim_out = {
      # Vehicle ID.
      "vehicle_id": self.get_vehicle_id(),
      # Time.
      "elapsed_time": self._elapsed_time,
      # Battery.
      "v_bus": self._v_bus,
      "i_bus": self._i_bus,
      "batt_soc": self._batt_soc,
      # Inverter.
      "v_d": self._v_d,
      "v_q": self._v_q,
      "i_d": self._i_d,
      "iq_cmd": self._iq_cmd,
      # Motor.
      "torque_mech": self._torque_mech,
      "omega_mech": self._omega_mech,
      # Cooling System.
      "T_junc_batt": self._T_junc_batt,
      "T_junc_inverter": self._T_junc_inverter,
      "T_junc_motor": self._T_junc_motor,
      "T_fluid": self._T_fluid,
    }

  def get_vehicle_id(self):
    """Returns vehicle ID."""
    return self._vehicle_id

  def run_time_step(self, start_time):
    """Runs a time step of the vehicle simulation."""
    self._loop_start_timestamp = time.time()
    self._elapsed_time = self._loop_start_timestamp - start_time

    if self._loop_end_timestamp:  # Guard against first call.
      # Calculate loop dt.
      self._loop_dt = self._loop_start_timestamp - self._loop_end_timestamp

      # Update battery model.
      self._battery.update_inputs(self._i_bus_cmd)
      self._v_bus, self._i_bus, self._batt_soc, self._batt_losses = (
          self._battery.update_outputs(self._loop_dt))

      # Update inverter model.
      self._theta_elec = (
          (self._omega_mech * n_pp * self._elapsed_time) % (2 * math.pi))
      self._inverter.update_inputs(self._v_bus, self._i_bus, self._theta_elec)
      self._v_d, self._v_q, self._i_d, self._iq_cmd, self._inverter_losses = (
          self._inverter.update_outputs())

      # Update motor model.
      self._motor.update_inputs(
          self._iq_cmd, self._v_bus, self._i_bus, self._omega_mech)
      self._torque_mech, self._motor_losses = self._motor.update_outputs()

      # Update cooling system model.
      self._cooling_sys.update_inputs(
        self._batt_losses, self._inverter_losses, self._motor_losses,
        self._fluid_velocity)
      (self._T_junc_batt, self._T_junc_inverter,
       self._T_junc_motor, self._T_fluid) = self._cooling_sys.update_outputs()

      # TODO(jmbagara): Make generic function for injecting noise and inject in the plant models.
      # Update sim outputs.
      ## Time.
      self._sim_out["elapsed_time"] = self._elapsed_time
      ## Battery.
      self._sim_out["v_bus"] = model_math.add_white_noise(self._v_bus, 0.01)
      self._sim_out["i_bus"] = model_math.add_white_noise(self._i_bus, 0.01)
      self._sim_out["batt_soc"] = self._batt_soc
      ## Inverter.
      self._sim_out["v_d"] = self._v_d
      self._sim_out["v_q"] = self._v_q
      self._sim_out["i_d"] = self._i_d
      self._sim_out["iq_cmd"] = self._iq_cmd
      ## Motor.
      self._sim_out["torque_mech"] = model_math.add_white_noise(
          self._torque_mech, 0.02)
      self._sim_out["omega_mech"] = model_math.add_white_noise(
          self._omega_mech, 0.02)
      ## Cooling System.
      self._sim_out["T_junc_batt"] = model_math.add_white_noise(
          self._T_junc_batt, 0.01)
      self._sim_out["T_junc_inverter"] = model_math.add_white_noise(
          self._T_junc_inverter, 0.01)
      self._sim_out["T_junc_motor"] = model_math.add_white_noise(
          self._T_junc_motor, 0.01)
      self._sim_out["T_fluid"] = model_math.add_white_noise(
          self._T_fluid, 0.01)

    # Capture time at completion of calculation loop.
    self._loop_end_timestamp = time.time()

  def get_sim_outputs(self):
    """Gets the sim outputs at the current time."""
    time.sleep(DATA_RATE)  # Limit period of data retrieval.
    return self._sim_out

def run_vehicle():
  """Runs a standalone vehicle simulation i.e. without plotting."""
  vehicle_1 = Vehicle(vehicle_id=1)
  start_time = time.time()

  while (time.time() - start_time) <= RUN_TIME:
    vehicle_1.run_time_step(start_time)
    msg = vehicle_1.get_sim_outputs()
    print(msg)


if __name__ == "__main__":
  run_vehicle()
