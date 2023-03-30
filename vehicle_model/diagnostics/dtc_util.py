"""Utility for reading DTC information from YAML file definitions."""

import yaml

from rules_python.python.runfiles import runfiles


# Constants.
r = runfiles.Create()

DTCS_YAML_PATH = r.Rlocation(
    "automotive-diagnostics/vehicle_model/diagnostics/dtcs.yaml")
_ECUS = ["bmm", "pmm", "tmm"]


class DTCReaderError(Exception):
  pass


def load_yaml():
  """Loads a yaml file into a dictionary."""
  yaml_dict = {}

  with open(DTCS_YAML_PATH, "r") as f:  
    try:
      yaml_dict = yaml.safe_load(f)
    except yaml.YAMLError as e:
      print(e)

  return yaml_dict


def parse_dtcs_dict(dtcs_dict):
  """Returns a DTC and its metadata.

  Args:
    dtcs_dict: Dictionary containing DTC's and their metadata.
  """
  for ecu, dtcs in dtcs_dict.items():
    for dtc, metadata in dtcs.items():
      dtc_description = metadata["description"]
      print(f"ECU: {ecu.upper()}, DTC: {dtc}, Description: {dtc_description}")


def get_dtc_metadata(ecu, dtc, dtcs_dict):
  """Returns DTC metadata given a DTC value."""
  if ecu not in _ECUS:
    raise DTCReaderError(f"{ecu} should be one of: `{_ECUS}`.")

  if dtc not in dtcs_dict[ecu].keys():
    raise DTCReaderError(f"{dtc} is not defined in: `{DTCS_YAML_PATH}`.")

  dtc_metadata = dtcs_dict[ecu][dtc]
  dtc_type = dtc_metadata["type"]

  if dtc_type == "rationality":
    return (
      dtc_type,
      dtc_metadata["description"],
      dtc_metadata["lower_limit"],
      dtc_metadata["upper_limit"],
    )
  else:
    return (
      dtc_type,
      dtc_metadata["description"],
    )


if __name__ == "__main__":
  """Quick functionality tests for this library."""
  dtcs_dict = load_yaml()

  print(dtcs_dict)
  print()
  parse_dtcs_dict(dtcs_dict)

  print(get_dtc_metadata("bmm", "A001", dtcs_dict))
  print(get_dtc_metadata("bmm", "B001", dtcs_dict))
  print(get_dtc_metadata("bmm", "C001", dtcs_dict))
  print(get_dtc_metadata("bmm", "D001", dtcs_dict))
  print(get_dtc_metadata("pmm", "A004", dtcs_dict))
  print(get_dtc_metadata("pmm", "B004", dtcs_dict))
