"""Model Battery Management Module (PMM). Extends ECU."""

import random
import datetime

from vehicle_model.ecu import ecu

class PMM(ecu.ECU):

  def __init__(self):
    super().__init__()

  def populate_inputs(self, v_bus, i_bus, theta_elec):
    """Populates PMM input variables."""
    self.input_dict["v_bus"] = v_bus
    self.input_dict["i_bus"] = i_bus
    self.input_dict["theta_elec"] = theta_elec

  def populate_outputs(self, v_d, v_q, i_d, i_q, inverter_losses):
    """Populates PMM output variables."""
    self.output_dict["v_d"] = v_d
    self.output_dict["v_q"] = v_q
    self.output_dict["i_d"] = i_d
    self.output_dict["i_q"] = i_q
    self.output_dict["inverter_losses"] = inverter_losses

  def inject_fault(self):
    # Inject short circuit.
    if random.uniform(0, 1) < 0.5:
      self.output_dict["v_q"] = 0.0
      self.output_dict["i_q"] = 0.0
      # self.set_dtcs()

    # # Inject open circuit.
    # if random.uniform(0, 1) < 0.5:
    #   self.output_dict["v_q"] = float("Nan")
    #   self.output_dict["i_q"] = float("Nan")
    #   self.output_dict["v_d"] = float("Nan")
    #   self.output_dict["i_d"] = float("Nan")

  def set_dtcs(self):
    if self.output_dict["v_q"] < 300.0 or self.output_dict["v_q"] > 405.0:
      now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      print(f"{now} PMM DTC: A005 - Motor Voltage Rationality Fault.")

    if self.output_dict["i_q"] < 0.0 or self.output_dict["i_q"] > 225.0:
      now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      print(f"{now} PMM DTC: A007 - Motor Current Rationality Fault.")

