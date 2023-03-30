"""Generic model for an Electronic Control Unit (ECU)."""

from pubsub import pub

from digital_twin_model import fault_injection


class ECU:

  def __init__(self):
    self.input_dict = {}
    self.intermediate_dict = {}
    self.output_dict = {}

    self.fault_injector = fault_injection.FaultInjector()
    self.dtcs_dict = self.fault_injector.dtcs_dict
    self.fault_tree_dict = self.fault_injector.fault_tree_dict
    self.active_dtcs = []

  def listener(self, arg1, arg2, arg3=None):
    """Listens to inputs for the ECU.

    Args:
      arg1: variable (has to be named as such) representing ECU input.
      arg2: variable (has to be named as such) representing ECU output.
    """
    self.input_dict = arg1
    self.output_dict = arg2

  def subscribe(self, topic):
    """Subscribes listener to a topic.

    Args:
      topic: string representing a comms channel.
    """
    pub.subscribe(self.listener, topic)

  def send(self, topic):
    """Sends outputs to a topic.

    Args:
      topic: string representing a comms channel.
    """
    pub.sendMessage(
        topic, arg1=self.input_dict, arg2=self.output_dict, arg3=None)

  def get_input(self, input_key):
    """Returns an input signal value given its name/key."""
    return self.input_dict.get(input_key)

  def set_dtcs(self, active_dtcs):
    """Sets the value of active DTCs."""
    self.active_dtcs = active_dtcs

  def get_dtcs(self):
    """Gets the value of active DTCs."""
    return self.active_dtcs

  def get_output(self, output_key):
    """Returns an output signal value given its name/key."""
    return self.output_dict.get(output_key)

  def populate_inputs(self, *args, **kwargs):
    raise NotImplementedError

  def populate_outputs(self, *args, **kwargs):
    raise NotImplementedError

  def inject_fault(self, *args, **kwargs):
    raise NotImplementedError
