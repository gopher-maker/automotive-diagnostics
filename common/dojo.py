"""Tool for running multiple instances of a vehicle simulation.

The purpose of `dojo.py` is to parallelize  online training of the digital twin
model by wrapping each vehicle instance in its own process.
"""

import argparse
import time

from multiprocessing.pool import Pool

from vehicle_model import vehicle


# Constants.
RUN_TIME = 2  # [Sec], simulation runtime.


def spawn_vehicles(num_vehicles):
  """Creates multiple vehicle instances to run in parallel."""
  vehicle_instances = [
      vehicle.Vehicle(vehicle_id=i+1, fault_injection_mode=True) for i in range(num_vehicles)]
  for vehicle_instance in vehicle_instances:
    print(f"Created vehicle: {vehicle_instance.get_vehicle_id()}.")

  return vehicle_instances

def run_vehicle(vehicle_instance):
  """Runs a standalone vehicle simulation i.e. without plotting."""
  start_time = time.time()

  while (time.time() - start_time) <= RUN_TIME:
    vehicle_instance.run_time_step(start_time)
    msg = vehicle_instance.get_sim_outputs()
    print(msg)

  return vehicle_instance.get_vehicle_id()


if __name__ == "__main__":
  # Parse user input arguments.
  parser = argparse.ArgumentParser()

  parser.add_argument(
      "--num_vehicles", type=int, required=True,
      help="Number of vehicle instances to spawn for the simulation.")
  parser.add_argument(
      "--sim_run_time", type=float, required=True,
      help="Number of seconds to run each vehicle simulation.")

  args = parser.parse_args()

  # Run vehicle simulation(s).
  with Pool() as pool:
    vehicle_instances = spawn_vehicles(args.num_vehicles)

    for result in pool.map(run_vehicle, vehicle_instances):
      print(f"End of simulation for Vehicle ID: {result}.", flush=True)
