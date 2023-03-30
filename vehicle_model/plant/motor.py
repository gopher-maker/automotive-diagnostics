"""Model of the electric motor."""

class Motor:

  def __init__(
    self, Ld, Lq, Ke, Rs, n_pp, flux_linkage, fault_injection_mode=False):
    # Motor parameters.
    self._Ld = Ld  # [H].
    self._Lq = Lq  # [H].
    self.Ke = Ke  # [Vphpk/(rad/s)].
    self._Rs = Rs  # [Ohm].
    self._n_pp = n_pp  # [].
    self._flux_linkage = flux_linkage  # [Wb], a.k.a. "Lambda".

    # Motor inputs.
    self.iq_cmd = 0.0
    self.v_bus = 0.0
    self.i_bus = 0.0
    self.omega_mech = 0.0
    self.omega_elec = 0.0

    # Motor outputs.
    self.i_q = 0.0
    self.torque_mech = 0.0
    self.motor_losses = 0.0  # Assume only resistive loss.

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
    self.omega_elec = self.omega_mech * self._n_pp

  def _update_losses(self):
    """Updates motor electrical losses for each time step."""
    self.motor_losses = 1.5 * self.i_q**2 * self._Rs

  def _calculate_step(self):
    """Calculates motor output quantities for each time step."""
    elec_power = self.v_bus * self.i_bus
    self._update_losses()

    # TODO(jmbagara): Make generic function for injecting noise.
    self.torque_mech = (elec_power - self.motor_losses) / self.omega_mech

  def update_outputs(self):
    """Updates motor outputs for each time step."""
    self._calculate_step()
    return self.torque_mech, self.motor_losses
