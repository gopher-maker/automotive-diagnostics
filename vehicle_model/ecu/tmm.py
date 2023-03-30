"""Model Thermal Management Module (TMM). Extends ECU."""

import random
import datetime

from vehicle_model.ecu import ecu


class TMM(ecu.ECU):

  def __init__(self):
    super().__init__()

  def populate_inputs(
    self, batt_losses, inverter_losses, motor_losses, fluid_velocity):
    """Populates TMM input variables."""
    self.input_dict["batt_losses"] = batt_losses
    self.input_dict["inverter_losses"] = inverter_losses
    self.input_dict["motor_losses"] = motor_losses
    self.input_dict["fluid_velocity"] = fluid_velocity

  def populate_outputs(
    self, T_junc_batt, T_junc_inverter, T_junc_motor, T_fluid):
    """Populates TMM output variables."""
    self.output_dict["T_junc_batt"] = T_junc_batt
    self.output_dict["T_junc_inverter"] = T_junc_inverter
    self.output_dict["T_junc_motor"] = T_junc_motor
    self.output_dict["T_fluid"] = T_fluid

  def inject_fault(self):
    if random.uniform(0, 1) < 0.5:
      self.output_dict["T_junc_batt"] = 0.0
      self.output_dict["T_junc_batt"] = 0.0
      # self.set_dtcs()

  def set_dtcs(self):
    if self.output_dict["v_q"] < 300.0 or self.output_dict["v_q"] > 405.0:
      now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      print(f"{now} TMM DTC: A005 - Motor Voltage Rationality Fault.")

    if self.output_dict["i_q"] < 0.0 or self.output_dict["i_q"] > 225.0:
      now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      print(f"{now} TMM DTC: A007 - Motor Current Rationality Fault.")

