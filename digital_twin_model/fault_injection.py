"""Module for injecting faults in ECUs."""

import random

from digital_twin_model import fault_tree_util
from vehicle_model.diagnostics import dtc_util


FAULT_TYPES = ["short", "open", "comms_missing"]


class FaultInjectionError(Exception):
  pass


class FaultInjector:

  def __init__(self, vehicle_id=None):
    self.dtcs_dict = dtc_util.load_yaml()
    self.fault_tree_dict = fault_tree_util.load_yaml()
    self.active_dtcs = []
    self.vehicle_id = vehicle_id

    self.vehicle_output = {
      # Vehicle ID.
      "vehicle_id": self.get_vehicle_id,
      # Battery.
      "v_bus": None,
      "i_bus": None,
      "batt_soc": None,
      # Inverter.
      "v_d": None,
      "v_q": None,
      "i_d": None,
      "iq_cmd": None,
      # Motor.
      "torque_mech": None,
      "omega_mech": None,
      # Cooling System.
      "T_junc_batt": None,
      "T_junc_inverter": None,
      "T_junc_motor": None,
      "T_fluid": None,
    }

  def inject_fault(self, fault_type=None):
    """Injects a fault of a specified type.
    Args:
      fault_type: string that specifies a fault type. One of `FAULT_TYPES`.
    """
    if not fault_type or fault_type not in FAULT_TYPES:
      raise FaultInjectionError(f"{fault_type} not one of {FAULT_TYPES}.")

    # CASE 1: Sets short circuit on BMM and PMM.
    if fault_type == "short":
      self.active_dtcs = [
        "A001", "A002", "A004", "A005", "A006", "A007",
        "D001", "D002", "D003", "D004", "D005", "D006"
      ]

      self.vehicle_output["v_bus"] = 0.0
      self.vehicle_output["i_bus"] = 0.0
      self.vehicle_output["v_d"] = 0.0
      self.vehicle_output["v_q"] = 0.0
      self.vehicle_output["i_d"] = 0.0
      self.vehicle_output["iq_cmd"] = 0.0

    # CASE 2: Sets open circuit on BMM and PMM.
    if fault_type == "open":
      self.active_dtcs = [
        "A001", "A002", "A004", "A005", "A006", "A007",
        "C001", "C002", "C003", "C004"
      ]

      self.vehicle_output["v_bus"] = float("inf")
      self.vehicle_output["i_bus"] = float("inf")
      self.vehicle_output["v_d"] = float("inf")
      self.vehicle_output["v_q"] = float("inf")
      self.vehicle_output["i_d"] = float("inf")
      self.vehicle_output["iq_cmd"] = float("inf")

    # CASE 3: Sets comms missing on BMM, PMM and TMM.
    if fault_type == "comms_missing":
      self.active_dtcs = [
        "B001", "B002", "B004", "B005", "B006", "B007", "B011", "B013"
      ]

      self.vehicle_output["v_bus"] = float("Nan")
      self.vehicle_output["i_bus"] = float("Nan")
      self.vehicle_output["v_d"] = float("Nan")
      self.vehicle_output["v_q"] = float("Nan")
      self.vehicle_output["i_d"] = float("Nan")
      self.vehicle_output["iq_cmd"] = float("Nan")
      self.vehicle_output["T_junc_inverter"] = float("Nan")
      self.vehicle_output["T_fluid"] = float("Nan")

  def clear_fault(self, fault_type=None):
    """Clears a fault of a specified type.
    Args:
      fault_type: string that specifies a fault type. One of `FAULT_TYPES`.
    """
    if not fault_type or fault_type not in FAULT_TYPES:
      raise FaultInjectionError(f"{fault_type} not one of {FAULT_TYPES}.")

    # CASE 1: Clears short circuit on BMM and PMM.
    if fault_type == "short":
      self.active_dtcs = []
      self.vehicle_output["v_bus"] = None
      self.vehicle_output["i_bus"] = None
      self.vehicle_output["v_d"] = None
      self.vehicle_output["v_q"] = None
      self.vehicle_output["i_d"] = None
      self.vehicle_output["iq_cmd"] = None

    # CASE 2: Clears open circuit on BMM and PMM.
    if fault_type == "open":
      self.active_dtcs = []
      self.vehicle_output["v_bus"] = None
      self.vehicle_output["i_bus"] = None
      self.vehicle_output["v_d"] = None
      self.vehicle_output["v_q"] = None
      self.vehicle_output["i_d"] = None
      self.vehicle_output["iq_cmd"] = None

    # CASE 3: Clears comms missing on BMM and PMM.
    if fault_type == "comms_missing":
      self.active_dtcs = []
      self.vehicle_output["v_bus"] = None
      self.vehicle_output["i_bus"] = None
      self.vehicle_output["batt_soc"] = None
      self.vehicle_output["v_d"] = None
      self.vehicle_output["v_q"] = None
      self.vehicle_output["i_d"] = None
      self.vehicle_output["iq_cmd"] = None

  def get_active_dtcs(self):
    """Retrieves active DTCs."""
    return self.active_dtcs

  def get_vehicle_id(self):
    """Retrieves vehicle ID as needed."""
    return self.vehicle_id

  def get_vehicle_output(self):
    """Retrieves vehicle output signals."""
    return self.vehicle_output

