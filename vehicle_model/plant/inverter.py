"""Model of the motor controller / inverter."""

import math

from common import model_math
from vehicle_model.ecu import pmm


class Inverter:

  def __init__(
    self, r_ds_on, f_switching, t_rise, t_fall, fault_injection_mode=False):
    # Instance of Powertrain Management Module (PMM).
    self.pmm = pmm.PMM()

    # Inverter parameters.
    self._r_ds_on = r_ds_on
    self._f_switching = f_switching
    self._t_rise = t_rise
    self._t_fall = t_fall
    self._fault_injection_mode = fault_injection_mode

    # Inverter inputs.
    self.v_bus = 0.0
    self.i_bus = 0.0
    self.theta_elec = 0.0

    self.pmm.input_dict = {
      "v_bus": self.v_bus,
      "i_bus": self.i_bus,
      "theta_elec": self.theta_elec,
    }

    # Inverter intermediate variables.
    self.v_a, self.v_b, self.v_c = (0.0, 0.0, 0.0)
    self.i_a, self.i_b, self.i_c = (0.0, 0.0, 0.0)

    # Inverter outputs.
    self.v_d, self.v_q = (0.0, 0.0)
    self.i_d, self.i_q = (0.0, 0.0)
    self.inverter_losses = 0.0

    self.pmm.output_dict = {
      "v_d": self.v_d,
      "v_q": self.v_q,
      "i_d": self.i_d,
      "i_q": self.i_q,
      "inverter_losses": self.inverter_losses,
    }

    # PMM subscribe to `battery-inverter` topic.
    self.pmm.subscribe('battery-inverter')

  def update_inputs(self, v_bus, i_bus, theta_elec):
    """Updates Inverter inputs for each time step."""
    self.v_bus = v_bus
    self.i_bus = i_bus
    self.theta_elec = theta_elec
    # self.pmm.populate_inputs(v_bus, i_bus, theta_elec)
    self.pmm.populate_inputs(0.0, 0.0, 0.0)

  def  _calculate_3_phase(self):
    """Computes 3 phase voltage and current waveforms."""
    # self.v_a, self.v_b, self.v_c = (
    #   self.pmm.get_output("v_bus") * math.sin(self.theta_elec),
    #   self.pmm.get_output("v_bus") * math.sin(self.theta_elec - (2 * math.pi / 3)),
    #   self.pmm.get_output("v_bus") * math.sin(self.theta_elec + (2 * math.pi / 3)),
    # )

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

  def _update_losses(self):
    """Updates inverter electrical losses for each time step."""
    conduction_loss = 1.5 * self.i_q**2 * self._r_ds_on
    # switching_loss = (
    #    0.5 * self.pmm.get_output("v_bus") * self.i_bus * (
    #       self._t_rise + self._t_fall) * self._f_switching)
    switching_loss = (
       0.5 * self.v_bus * self.i_bus * (
          self._t_rise + self._t_fall) * self._f_switching)
    self.inverter_losses = conduction_loss + switching_loss

  def update_outputs(self):
    """Updates motor outputs for each time step."""
    self._calculate_3_phase()

    self.v_d, self.v_q = model_math.park_transform(
      self.v_a, self.v_b, self.v_c, self.theta_elec)
    self.i_d, self.i_q = model_math.park_transform(
      self.i_a, self.i_b, self.i_c, self.theta_elec)

    self._update_losses()

    self.pmm.populate_outputs(
        self.v_d, self.v_q, self.i_d, self.i_q, self.inverter_losses)

    if self._fault_injection_mode:
      self.pmm.inject_fault()
  
    self.pmm.send('inverter-motor')

    # return self.v_d, self.v_q, self.i_d, self.i_q, self.inverter_losses
    return (
      self.pmm.get_output("v_d"),
      self.pmm.get_output("v_q"),
      self.pmm.get_output("i_d"),
      self.pmm.get_output("i_q"),
      self.pmm.get_output("inverter_losses"),
    )
