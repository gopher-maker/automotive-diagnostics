"""Model of the cooling system."""

class CoolingSystem:

  def __init__(
    self, T_ambient, Rth_batt_junc, Rth_inverter_junc, Rth_motor_junc,
    fluid_density, pipe_area, fluid_heat_capacity):
    # Cooling system parameters.
    self.T_ambient = T_ambient
    self.Rth_batt_junc = Rth_batt_junc
    self.Rth_inverter_junc = Rth_inverter_junc
    self.Rth_motor_junc = Rth_motor_junc
    self.fluid_density = fluid_density
    self.pipe_area = pipe_area
    self.fluid_heat_capacity = fluid_heat_capacity

    # Cooling system inputs.
    self.batt_losses = 0.0
    self.inverter_losses = 0.0
    self.motor_losses = 0.0
    self.fluid_velocity = 0.0

    # Cooling system outputs. NOTE: All temperatures in degC.
    self.T_junc_batt = 0.0
    self.T_junc_inverter = 0.0
    self.T_junc_motor = 0.0
    self.T_fluid = 0.0

  def update_inputs(
    self, batt_losses, inverter_losses, motor_losses, fluid_velocity):
    """Updates cooling system inputs for each time step.

    Args:
      batt_losses: Battery losses [W].
      inverter_losses: Inverter losses [W].
      motor_losses: Motor losses [W].
    """
    self.batt_losses = batt_losses
    self.inverter_losses = inverter_losses
    self.motor_losses = motor_losses
    self.fluid_velocity = fluid_velocity

  def _update_temps(self):
    """Updates battery, inverter and motor junction temps for each time step."""
    # Update junction temps.
    self.T_junc_batt = self.T_ambient + (self.Rth_batt_junc * self.batt_losses)
    self.T_junc_inverter = self.T_ambient + (
        self.Rth_inverter_junc * self.inverter_losses)
    self.T_junc_motor = self.T_ambient + (
        self.Rth_motor_junc * self.motor_losses)

    # Update the cooling fluid temp.
    total_loss = self.batt_losses + self.inverter_losses + self.motor_losses
    m_dot_c = self.fluid_density * self.fluid_velocity * self.pipe_area * \
              self.fluid_heat_capacity
    if m_dot_c != 0:
      self.T_fluid = self.T_ambient + (total_loss / m_dot_c)


  def _calculate_step(self):
    """Calculates cooling system output quantities for each time step."""
    self._update_temps()

  def update_outputs(self):
    """Updates cooling system outputs for each time step."""
    self._calculate_step()
    return (
        self.T_junc_batt, self.T_junc_inverter, self.T_junc_motor, self.T_fluid)

