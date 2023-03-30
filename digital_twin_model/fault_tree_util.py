"""Utility for reading DTC information from YAML file definitions."""

import yaml

from rules_python.python.runfiles import runfiles

from vehicle_model.diagnostics import dtc_util

# Constants.
r = runfiles.Create()

FAULT_TREE_YAML_PATH = r.Rlocation(
    "automotive-diagnostics/digital_twin_model/fault_tree.yaml")
_DTC_TYPES = ["comms_missing", "rationality", "open_circuit", "short_circuit"]
_ECUS = ["bmm", "pmm", "tmm"]


class DTCReaderError(Exception):
  pass


def load_yaml():
  """Loads a yaml file into a dictionary."""
  yaml_dict = {}

  with open(FAULT_TREE_YAML_PATH, "r") as f:  
    try:
      yaml_dict = yaml.safe_load(f)
    except yaml.YAMLError as e:
      print(e)

  return yaml_dict


def parse_fault_tree_dict(fault_tree_dict, dtcs_vector):
  """Returns conditions as they map to their corresponding faults.

  Args:
    fault_tree_dict: Dictionary containing faults mapped to DTC conditions.
  """
  symptoms_map = {}

  for symptom, metadata in fault_tree_dict["symptoms"].items():
    if all(item in dtcs_vector for item in metadata["conditions"]):
      symptoms_map[symptom] = metadata["probable_cause_weights"]

  return symptoms_map


def calculate_cause_probabilities(symptoms_map):
  """Returns list of causes and assigned probabilities.

  Args:
    symptoms_map: list of dicts mapping symptoms with cause weights.
  """
  causes_map = {}

  for symptom in symptoms_map.keys():
    causes = symptoms_map[symptom]
    for cause in causes.keys():
      if causes_map.get(cause):
        causes_map[cause] *= causes[cause]
      else:
        causes_map[cause] = causes[cause]

  return causes_map


if __name__ == "__main__":
  """Quick functionality tests for this library."""
  dtcs_dict = dtc_util.load_yaml()

  fault_tree_dict = load_yaml()
  print(fault_tree_dict)

  dtcs_vector_1 = ["A001", "A002", "C001"]
  dtcs_vector_2 = ["A001", "A002", "C001", "C002"]
  dtcs_vector_3 = ["A001", "A002", "D001", "D002"]

  smap_1 = parse_fault_tree_dict(fault_tree_dict, dtcs_vector_1)
  smap_2 = parse_fault_tree_dict(fault_tree_dict, dtcs_vector_2)
  smap_3 = parse_fault_tree_dict(fault_tree_dict, dtcs_vector_3)

  print(dtcs_vector_1)
  print(smap_1)
  print(calculate_cause_probabilities(smap_1))
  print()
  print(dtcs_vector_2)
  print(smap_2)
  print(calculate_cause_probabilities(smap_2))
  print()
  print(dtcs_vector_3)
  print(smap_3)
  print(calculate_cause_probabilities(smap_3))
