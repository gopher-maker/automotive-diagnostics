"""Model of a vehicle Powertrain."""

import math
# TODO(jmbagara): Remove this import.
import random
import time

from common import model_math
from vehicle_model import battery, inverter, motor


# Constants.
RUN_TIME = 20  # [Sec], simulation runtime.
DATA_RATE = 0.01  # [Sec], interval at which to yield simulation data.

# TODO(jmbagara): Move these parameters to a YAML file.

# Battery parameters.
v_nominal = 400.0  # [V], nominal battery voltage at 100% state of charge.
q_nominal = 3712  # [A.h], battery capacity i.e. 16x modules, @ 232 A.h/5.3 kWh.

# Inverter parameters.
r_ds_on = 0.004  # [Ohm].
f_switching = 30000  # [Hz].

# Motor parameters.
Ld = 165e-6  # [H], motor direct inductance.
Lq = 165e-6  # [H], motor quadrature inductance.
Ke = 0.067  # [Vphpk/(rad/s)], motor EMF constant.
Rs = 0.04  # [Ohm], motor winding resistance.
n_pp = 32  # [], number of motor pole pairs.
flux_linkage = 0.15  # [N-m/A = V-s/rad = Wb], motor flux linkage.


class Vehicle:
  """Representation of a vehicle powertrain."""

  def __init__(self):
    self._battery = battery.Battery(v_nominal, q_nominal)
    self._inverter = inverter.Inverter(r_ds_on, f_switching)
    self._motor = motor.Motor(Ld, Lq, Ke, Rs, n_pp, flux_linkage)
    
    # Time parameters.
    self._loop_start_timestamp = None
    self._loop_end_timestamp = None
    self._loop_dt = None
    self._elapsed_time = None

    # TODO(jmbagara): Make these "dynamic" as they should be.
    # Simulator input variables.
    self._i_bus_cmd = 200  # [A]

    # TODO(jmbagara): Make these "dynamic" as they should be.
    # Simulator output variables.
    self._v_bus = 400  # [V].
    self._i_bus = 0  # [A].
    self._v_a = 0
    self._v_b = 0
    self._v_c = 0
    self._iq_cmd = 0
    self._batt_soc = 100.0  # [%].
    self._torque_mech = 0
    self._omega_mech = 100.0  # [rad/s].
    self._iq_cmd = 0
    self._theta_elec = 0

    self._sim_out = {
      # Time.
      "elapsed_time": self._elapsed_time,
      # Battery.
      "v_bus": self._v_bus,
      "i_bus": self._i_bus,
      "batt_soc": self._batt_soc,
      # Inverter.
      "vq_a": self._v_a,
      "vq_b": self._v_b,
      "vq_c": self._v_c,
      "iq_cmd": self._iq_cmd,
      # Motor.
      "torque_mech": self._torque_mech,
      "omega_mech": self._omega_mech,
    }

  def run_time_step(self, start_time):
    """Runs a time step of the vehicle simulation."""
    self._loop_start_timestamp = time.time()
    self._elapsed_time = self._loop_start_timestamp - start_time

    if self._loop_end_timestamp:  # Guard against first call.
      # Calculate loop dt.
      self._loop_dt = self._loop_start_timestamp - self._loop_end_timestamp

      # Update battery model.
      self._battery.update_inputs(self._i_bus_cmd)
      self._v_bus, self._i_bus, self._batt_soc = self._battery.update_outputs(
        self._loop_dt)

      # Update inverter model.
      self._theta_elec = (
          (self._omega_mech * n_pp * self._elapsed_time) % (2 * math.pi))
      self._inverter.update_inputs(self._v_bus, self._i_bus, self._theta_elec)
      self._v_a, self._v_b, self._v_c, self._iq_cmd = (
          self._inverter.update_outputs())

      # Update motor model.
      self._motor.update_inputs(
          self._iq_cmd, self._v_bus, self._i_bus, self._omega_mech)
      self._torque_mech = self._motor.update_outputs()

      # TODO(jmbagara): Make generic function for injecting noise and inject in the plant models.
      # Update sim outputs.
      self._sim_out["elapsed_time"] = self._elapsed_time
      self._sim_out["v_bus"] = self._v_bus + random.uniform(-0.01 * self._v_bus, 0.01 * self._v_bus)
      self._sim_out["i_bus"] = self._i_bus + random.uniform(-0.01 * self._i_bus, 0.01 * self._i_bus)
      self._sim_out["batt_soc"] = self._batt_soc
      self._sim_out["v_a"] = self._v_a
      self._sim_out["v_b"] = self._v_b
      self._sim_out["v_c"] = self._v_c
      self._sim_out["iq_cmd"] = self._iq_cmd
      self._sim_out["torque_mech"] = self._torque_mech + random.uniform(-0.02 * self._v_bus, 0.02 * self._v_bus)
      self._sim_out["omega_mech"] = self._omega_mech + random.uniform(-0.02 * self._v_bus, 0.02 * self._v_bus)

    # Capture time at completion of calculation loop.
    self._loop_end_timestamp = time.time()

  def run_vehicle(self):
    """Runs a simulation of the currently configured vehicle."""
    start_time = time.time()

    while (time.time() - start_time) <= RUN_TIME:
      self.run_time_step(start_time)

      # TODO(jmbagara): Remove this print statement.
      print(self._sim_out)

  def get_sim_outputs(self):
    """Gets the sim outputs at the current time."""
    time.sleep(DATA_RATE)  # Limit period of data retrieval.
    return self._sim_out


if __name__ == "__main__":
  """Runs a standalone vehicle simulation i.e. without plotting or printing."""
  vehicle_1 = Vehicle()
  vehicle_1.run_vehicle()
