"""Model of a vehicle Powertrain."""

import math
import time

from common import model_math
from vehicle_model import inverter, motor


# Constants.
RUN_TIME = 20  # [Sec], simulation runtime.
DATA_RATE = 0.01  # [Sec], interval at which to yield simulation data.

# TODO(jmbagara): Move these parameters to a YAML file.

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
    self._inverter = inverter.Inverter(r_ds_on, f_switching)
    self._motor = motor.Motor(Ld, Lq, Ke, Rs, n_pp, flux_linkage)
    self._elapsed_time = 0
    # TODO(jmbagara): Make these "dynamic" as they should be.
    # Simulator inputs variables.
    self._v_bus = 400  # [V].
    self._i_bus = 200  # [A].
    self._omega_mech = 100.0  # [rad/s]

    # Simulator output variables.
    self._torque_mech = 0
    self._iq_cmd = 0
    self._theta_elec = 0
    self._sim_out = {
      "elapsed_time": 0,
      "torque_mech": 0,
      "iq_cmd": 0,
    }

  def run_time_step(self, start_time):
    """Runs a time step of the vehicle simulation."""
    self._elapsed_time = time.time() - start_time

    # Update inverter model.
    self._theta_elec = math.sin(self._omega_mech * n_pp * self._elapsed_time)
    self._inverter.update_inputs(self._v_bus, self._i_bus, self._theta_elec)
    self._iq_cmd = self._inverter.update_outputs()

    # Update motor model.
    self._motor.update_inputs(
        self._iq_cmd, self._v_bus, self._i_bus, self._omega_mech)
    self._torque_mech = self._motor.update_outputs()

    # Update sim outputs.
    self._sim_out["elapsed_time"] = self._elapsed_time
    self._sim_out["torque_mech"] = self._torque_mech
    self._sim_out["iq_cmd"] = self._iq_cmd

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
