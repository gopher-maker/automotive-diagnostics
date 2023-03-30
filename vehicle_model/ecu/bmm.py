"""Model Battery Management Module (BMM). Extends ECU."""

import random
import datetime

from vehicle_model.ecu import ecu
from vehicle_model.diagnostics import dtc_util


class BMM(ecu.ECU):

  def __init__(self):
    super().__init__()

  def populate_inputs(self, i_bus_cmd):
    """Populates BMM input variables."""
    self.input_dict["i_bus_cmd"] = i_bus_cmd

  def populate_outputs(self, **kwargs):
    """Populates BMM output variables."""
    self.output_dict["v_bus"] = kwargs["v_bus"]
    self.output_dict["i_bus"] = kwargs["i_bus"]
    self.output_dict["batt_soc"] = kwargs["batt_soc"]
    self.output_dict["batt_losses"] = kwargs["batt_losses"]

  def inject_fault(self):
    # Inject short circuit fault.
    if random.uniform(0, 1) < 0.5:
      self.fault_injector.inject_fault("short")
      self.set_dtcs()
      self.output_dict["v_bus"] = self.fault_injector.vehicle_output["v_bus"]
      self.output_dict["i_bus"] = self.fault_injector.vehicle_output["i_bus"]
      self.output_dict["v_d"] = self.fault_injector.vehicle_output["v_d"]
      self.output_dict["v_q"] = self.fault_injector.vehicle_output["v_q"]
      self.output_dict["i_d"] = self.fault_injector.vehicle_output["i_d"]
      self.output_dict["iq_cmd"] = self.fault_injector.vehicle_output["iq_cmd"]
    else:
      self.clear_dtcs()

    # # TODO(jmabagara): Clean this out after debugging.
    # # Inject short circuit.
    # if random.uniform(0, 1) < 0.5:
    #   self.output_dict["v_bus"] = 0.0
    #   self.output_dict["i_bus"] = 0.0
    #   # self.set_dtcs()

    # # TODO(jmabagara): Clean this out after debugging.
    # # Inject open circuit.
    # if random.uniform(0, 1) < 0.5:
    #   self.output_dict["v_bus"] = float("NaN")
    #   self.output_dict["i_bus"] = float("NaN")
    #   self.set_dtcs()

  def set_dtcs(self):
    """Sets the active DTCs."""
    self.active_dtcs = self.fault_injector.active_dtcs

    # # TODO(jmabagara): Clean this out after debugging.
    # # Set short circuit DTCs.
    # self.active_dtcs = ["A001", "A002", "C001", "C002"]

    # # Set open circuit DTCs.
    # self.active_dtcs = ["A001", "A002", "D001", "D002"]

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for dtc in self.active_dtcs:
      dtc_metadata_bmm = dtc_util.get_dtc_metadata("bmm", dtc, self.dtcs_dict)
      print(f"{now} {dtc} {dtc_metadata}")

    symptoms_map = dtc_util.parse_fault_tree_dict(
        self.fault_tree_dict, self.active_dtcs)
    cause_probabilities = dtc_util.calculate_cause_probabilities(
        symptoms_map)

    print(f"{now} Symptoms map: {symptoms_map}")
    print(f"{now} Cause probabilities: {cause_probabilities}")

  def clear_dtcs(self):
    """Clears active DTCs."""
    self.active_dtcs = []
