"""Model of a vehicle Powertrain."""

import math
import time

from common import model_math
from vehicle_model import inverter, motor


# Constants.
RUN_TIME = 30  # [Sec], simulation runtime.

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


def run_vehicle():
  inverter_1 = inverter.Inverter(r_ds_on, f_switching)
  motor_1 = motor.Motor(Ld, Lq, Ke, Rs, n_pp, flux_linkage)

  # TODO(jmbagara): Make these "dynamic" as they should be.
  # "Static" state variables.
  v_bus = 400  # [V].
  i_bus = 200  # [A].
  omega_mech = 100.0  # [rad/s].

  start_time = last_time_stamp = time.time()

  while (time.time() - start_time) < RUN_TIME:
    # Compute elpased time.
    elapsed_time = time.time() - start_time

    # Compute dt.
    delta_time = time.time() - last_time_stamp

    # Run inverter model.
    theta_elec = math.sin(omega_mech * n_pp * elapsed_time)
    inverter_1.update_inputs(v_bus, i_bus, theta_elec)
    iq_cmd = inverter_1.update_outputs()

    # Run motor model.
    motor_1.update_inputs(iq_cmd, v_bus, i_bus, omega_mech)
    torque_mech = motor_1.update_outputs()

    # Update last timestamp.
    last_time_stamp = time.time()

    # Print outputs.
    if elapsed_time:
      print(
        f"t: {elapsed_time},\tdt: {delta_time},\tiq_cmd: {round(iq_cmd, 1)},\t"
        f"theta_elec: {theta_elec},\ttorque_mech: {torque_mech}"
      )


if __name__ == "__main__":
  run_vehicle()
