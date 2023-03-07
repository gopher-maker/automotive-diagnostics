"""Model of the motor controller / inverter."""

import math

from common import model_math

class Inverter:

  def __init__(self, r_ds_on, f_switching):
    # Inverter parameters.
    self.r_ds_on = 0
    self.f_switching = f_switching

    # Inverter inputs.
    self.v_bus = 0.0
    self.i_bus = 0.0
    self.theta_elec = 0.0

    # Inverter intermediate variables.
    self.v_a, self.v_b, self.v_c = (0.0, 0.0, 0.0)
    self.i_a, self.i_b, self.i_c = (0.0, 0.0, 0.0)

    # Inverter outputs.
    self._vd, self.v_q = (0.0, 0.0)
    self._id, self.i_q = (0.0, 0.0)

  def update_inputs(self, v_bus, i_bus, theta_elec):
    """Updates Inverter inputs for each time step."""
    self.v_bus = v_bus
    self.i_bus = i_bus
    self.theta_elec = theta_elec

  def  _calculate_3_phase(self):
    """Computes 3 phase voltage and current waveforms."""
    self.v_a, self.v_b, self.v_c = (
      self.v_bus * math.sin(self.theta_elec),
      self.v_bus * math.sin(self.theta_elec - (2 * math.pi / 3)),
      self.v_bus * math.sin(self.theta_elec + (2 * math.pi / 3)),
    )

    self.i_a, self.i_b, self.i_c = (
      self.i_bus * math.sin(self.theta_elec),
      self.i_bus * math.sin(self.theta_elec - (2 * math.pi / 3)),
      self.i_bus * math.sin(self.theta_elec + (2 * math.pi / 3)),
    )

  def update_outputs(self):
    """Updates motor outputs for each time step."""
    self._calculate_3_phase()

    self.v_d, self.v_q = model_math.park_transform(
      self.v_a, self.v_b, self.v_c, self.theta_elec)
    self.i_d, self.i_q = model_math.park_transform(
      self.i_a, self.i_b, self.i_c, self.theta_elec)

    return self.i_q
