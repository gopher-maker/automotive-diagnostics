"""Model of the electric motor."""

from common import model_math
from vehicle_model import inverter


class Motor:

  def __init__(self, Ld, Lq, Ke, Rs, n_pp, flux_linkage):
    # Motor parameters.
    self.Ld = Ld  # [H].
    self.Lq = Lq  # [H].
    self.Ke = Ke  # [Vphpk/(rad/s)].
    self.Rs = Rs  # [Ohm].
    self.n_pp = n_pp  # [].
    self.flux_linkage = flux_linkage  # [Wb], a.k.a. "Lambda".

    # Motor inputs.
    self.iq_cmd = 0.0
    self.v_bus = 0.0
    self.i_bus = 0.0
    self.omega_mech = 0.0
    self.omega_elec = 0.0

    # Motor outputs.
    self.iq = 0.0
    self.torque_mech = 0.0

    # Motor losses.
    self.resistive_loss = 0.0
    self.hysterisis_loss = 0.0
    self.motor_loss = 0.0

  def update_inputs(self, iq_cmd, v_bus, i_bus, omega_mech):
    """Updates motor inputs for each time step.

    Args:
      iq_cmd: float representing quiescent current command [A].
      v_bus: float representing DC bus voltage from HV battery [V].
      i_bus: float representing DC bus current from HV battery [A].
      omega_mech: float representing mechanical rotational speed of motor [].
    """
    self.iq_cmd = iq_cmd
    self.v_bus = v_bus
    self.i_bus = i_bus
    self.omega_mech = omega_mech
    self.omega_elec = self.omega_mech * self.n_pp

  def _calculate_losses(self):
    """Calculates electrical losses for each time step."""
    self.resistive_loss = 0.0
    self.hysterisis_loss = 0.0
    self.motor_loss = self.resistive_loss + self.hysterisis_loss

  def _calculate_step(self):
    """Calculates motor output quantities for each time step."""
    elec_power = self.v_bus * self.i_bus
    self._calculate_losses()

    # self.torque_mech = (elec_power - self.motor_loss) / self.omega_mech

    # TODO(jmbagara): Make generic function for injecting noise.
    self.torque_mech = (elec_power - self.motor_loss) / self.omega_mech

  def update_outputs(self):
    """Updates motor outputs for each time step."""
    self._calculate_step()
    return self.torque_mech
