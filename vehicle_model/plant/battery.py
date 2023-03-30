"""Model of the HV battery."""

from vehicle_model.ecu import bmm

import numpy as np


class Battery:

  def __init__(
    self, v_nominal, q_nominal, r_internal, fault_injection_mode=False):
    # Instance of Battery Management Module (BMM).
    self.bmm = bmm.BMM()

    # Battery parameters.
    self._v_nominal = v_nominal
    self._q_nominal = q_nominal
    self._r_internal = r_internal
    self._fault_injection_mode = fault_injection_mode

    # Discharge curve.
    self.batt_socs = [
        0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85,
        90, 95, 100
    ]
    self.batt_voltages = [
      285.7, 291.4, 297.1, 302.9, 308.6, 314.3, 320.0, 325.7, 331.4, 337.1,
      342.9, 348.6, 354.3, 360.0, 365.7, 371.4, 377.2, 382.9, 388.6, 394.3,
      400.0
    ]

    # Battery inputs.
    self.i_bus_cmd = 0.0

    self.bmm.input_dict = {
      "i_bus_cmd": self.i_bus_cmd,
    }

    # Battery outputs.
    self.v_bus = 400.0
    self.i_bus = 0.0
    self.batt_soc = 100.0
    self.batt_losses = 0.0  # Assume only resistive loss.

    self.bmm.output_dict = {
      "v_bus": self.v_bus,
      "i_bus": self.i_bus,
      "batt_soc": self.batt_soc,
      "batt_losses": self.batt_losses,
    }

    # BMM subscribe to `battery` topic.
    self.bmm.subscribe('battery')

  def update_inputs(self, i_bus_cmd):
    """Updates Battery inputs for each time step."""
    self.i_bus_cmd = i_bus_cmd
    self.bmm.populate_inputs(self.i_bus_cmd)

  def  _calculate_soc(self, dt):
    """Computes battery state of charge (SOC) given params and inputs."""
    # Assume perfect tracking of bus current command.
    self.i_bus = self.i_bus_cmd

    # Multipy `self._q_nominal` by `3600` to convert to [A.s] a.k.a [Coulomb].
    # Multiply the whole result by `100.0` to convert to percent [%].
    self.batt_soc -= self.i_bus / (self._q_nominal * 3600) * dt * 100.0

    # Calculate resultant bus voltage for the time step.
    self.v_bus = np.interp(self.batt_soc, self.batt_socs, self.batt_voltages)

  def _update_losses(self):
    """Updates battery electrical losses for each time step."""
    self.batt_losses = self.i_bus**2 * self._r_internal

  def update_outputs(self, dt):
    """Updates battery outputs for each time step."""
    self._calculate_soc(dt)
    self._update_losses()

    self.bmm.populate_outputs(
        v_bus=self.v_bus,
        i_bus=self.i_bus,
        batt_soc=self.batt_soc,
        batt_losses=self.batt_losses
    )

    if self._fault_injection_mode:
      self.bmm.inject_fault()
  
    self.bmm.send('battery-inverter')

    return (
      self.bmm.get_output("v_bus"),
      self.bmm.get_output("i_bus"),
      self.bmm.get_output("batt_soc"),
      self.bmm.get_output("batt_losses"),
    )
