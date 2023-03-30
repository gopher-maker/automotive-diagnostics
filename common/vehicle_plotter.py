"""Tool for plotting vehicle simulation parameters.

Credits: Referenced Makani motor plotter at:
https://github.com/google/makani/blob/master/avionics/motor/motor_plotter.py.
"""

import collections
import importlib
import math
import numpy
import queue
import sys
import time

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from vehicle_model import vehicle

# Must be included after PySide in order to force pyqtgraph to use it.
pyqtgraph = importlib.import_module("pyqtgraph")
dockarea = importlib.import_module("pyqtgraph.dockarea")


class MainWindow(QtWidgets.QMainWindow):
  """GUI window for plotting realtime vehicle simulator data."""

  _REALTIME_DATA_LEN = 3000

  def __init__(self):
    super(MainWindow, self).__init__()
    self._threads = []
    self._InitUI()
    self._is_paused = False

  def _InitUI(self):
    """Creates and arranges all GUI elements."""
    central_widget = QtWidgets.QWidget()

    downsample_ledit = QtWidgets.QLineEdit(self)
    downsample_ledit.setValidator(QtGui.QIntValidator(1, 10000))

    fault_injection_cbox = QtWidgets.QCheckBox("Fault Injection Mode", self)

    run_btn = QtWidgets.QPushButton("Run")
    run_btn.clicked.connect(self._HandlePlotRequest)

    pause_btn = QtWidgets.QPushButton("Pause", self)
    pause_btn.clicked.connect(self._HandlePauseRequest)

    plot_dockarea = dockarea.DockArea()

    status_message = QtWidgets.QLabel("")

    hbox = QtWidgets.QHBoxLayout()
    hbox.addWidget(QtWidgets.QLabel("Downsample:", self))
    hbox.addWidget(downsample_ledit)
    hbox.addWidget(fault_injection_cbox)
    hbox.addWidget(run_btn)
    hbox.addWidget(pause_btn)

    vbox = QtWidgets.QVBoxLayout()
    vbox.addLayout(hbox)
    vbox.addWidget(plot_dockarea, stretch=1)

    central_widget.setLayout(vbox)

    self.setCentralWidget(central_widget)
    self.setGeometry(300, 150, 1200, 1000)
    self.setWindowTitle("Vehicle Plotter")
    self.statusBar().addWidget(status_message)
    self.show()

    self._downsample_ledit = downsample_ledit
    self._fault_injection_cbox = fault_injection_cbox
    self._status_message = status_message
    self._plot_dockarea = plot_dockarea

  def _CleanDockArea(self):
    """Removes all containers and docks from self._plot_dockarea."""
    (_, docks) = self._plot_dockarea.findAll()
    for d in docks.values():
      d.hide()
      d.setParent(None)
      d.label.setParent(None)

  def _SetupMotorPlot(self):
    """Sets up GUI items for plotting motor data."""
    self._plots = {}
    self._plot_items = []

    self._CleanDockArea()

    # Battery Parameters.
    dock1 = dockarea.Dock("HV Battery")
    self._plot_dockarea.addDock(dock1, "top")
    glw = pyqtgraph.GraphicsLayoutWidget()
    dock1.addWidget(glw)

    plot1 = glw.addPlot(title="Voltages")
    plot1.addLegend()
    self._plots["v_bus"] = plot1.plot(name="Bus Voltage", pen="g")
    plot1.setLabel("bottom", "Time", "s")
    plot1.setLabel("left", "Voltage", "V")
    plot1.showGrid(True, True)
    self._plot_items.append(plot1)

    glw.nextRow()

    plot2 = glw.addPlot(title="Currents")
    plot2.addLegend()
    self._plots["i_bus"] = plot2.plot(name="Bus Current", pen="r")
    plot2.setLabel("bottom", "Time", "s")
    plot2.setLabel("left", "Current", "A")
    plot2.showGrid(True, True)
    plot2.setXLink(plot1)
    self._plot_items.append(plot2)

    glw.nextRow()

    plot3 = glw.addPlot(title="State of Charge (SOC)")
    plot3.addLegend()
    self._plots["batt_soc"] = plot3.plot(name="SOC", pen="r")
    plot3.setLabel("bottom", "Time", "s")
    plot3.setLabel("left", "SOC", "%")
    plot3.showGrid(True, True)
    plot3.setXLink(plot1)
    self._plot_items.append(plot3)

    # Inverter Parameters.
    dock2 = dockarea.Dock("Inverter")
    self._plot_dockarea.addDock(dock2, "below", dock1)
    glw = pyqtgraph.GraphicsLayoutWidget()
    dock2.addWidget(glw)

    plot4 = glw.addPlot(title="Voltages")
    plot4.addLegend()
    self._plots["v_d"] = plot4.plot(name="Vd", pen="r")
    self._plots["v_q"] = plot4.plot(name="Vq", pen="g")
    plot4.setLabel("bottom", "Time", "s")
    plot4.setLabel("left", "Voltage", "V")
    plot4.showGrid(True, True)
    self._plot_items.append(plot4)

    glw.nextRow()

    plot5 = glw.addPlot(title="Currents")
    plot5.addLegend()
    self._plots["i_d"] = plot5.plot(name="Id cmd", pen="r")
    self._plots["iq_cmd"] = plot5.plot(name="Iq cmd", pen="g")
    plot5.setLabel("bottom", "Time", "s")
    plot5.setLabel("left", "Current", "A")
    plot5.showGrid(True, True)
    plot5.setXLink(plot1)
    self._plot_items.append(plot5)

    # Motor Parameters.
    dock3 = dockarea.Dock("Motor")
    self._plot_dockarea.addDock(dock3, "below", dock2)
    glw = pyqtgraph.GraphicsLayoutWidget()
    dock3.addWidget(glw)

    plot6 = glw.addPlot(title="Torque")
    plot6.addLegend()
    self._plots["torque_mech"] = plot6.plot(name="Mechanical Torque", pen="g")
    plot6.setLabel("bottom", "Time", "s")
    plot6.setLabel("left", "Torque", "N-m")
    plot6.showGrid(True, True)
    self._plot_items.append(plot6)

    glw.nextRow()

    plot7 = glw.addPlot(title="Omega")
    plot7.addLegend()
    self._plots["omega_mech"] = plot7.plot(name="Omega", pen="r")
    plot7.setLabel("bottom", "Time", "s")
    plot7.setLabel("left", "Omega", "rad/s")
    plot7.showGrid(True, True)
    plot7.setXLink(plot1)
    self._plot_items.append(plot7)

    # Cooling System Parameters.
    dock4 = dockarea.Dock("Cooling System")
    self._plot_dockarea.addDock(dock4, "below", dock3)
    glw = pyqtgraph.GraphicsLayoutWidget()
    dock4.addWidget(glw)

    plot8 = glw.addPlot(title="Torque")
    plot8.addLegend()
    self._plots["T_junc_batt"] = plot8.plot(name="Battery Junc. Temp.", pen="r")
    self._plots["T_junc_inverter"] = plot8.plot(
        name="Inverter Junc. Temp.", pen="g")
    self._plots["T_junc_motor"] = plot8.plot(name="Motor Junc. Temp", pen="b")
    self._plots["T_fluid"] = plot8.plot(name="Fluid Temp", pen="y")
    plot8.setLabel("bottom", "Time", "s")
    plot8.setLabel("left", "Temperature", "deg. C")
    plot8.showGrid(True, True)
    self._plot_items.append(plot8)

    # Raise Dock 1 to foreground.
    stack = dock1.container().stack
    current = stack.currentWidget()
    current.label.setDim(True)
    stack.setCurrentWidget(dock1)
    dock1.label.setDim(False)

  def _SetupRealtimeData(self, downsample):
    """Sets up data structure for real-time data plotting."""
    self._realtime_x = 0.01 * downsample * numpy.arange(
        -self._REALTIME_DATA_LEN + 1, 1)
    self._realtime_data = collections.defaultdict(
        lambda: numpy.zeros(self._REALTIME_DATA_LEN))

  def _HandlePlotRequest(self):
    """Handles user request to plot realtime data."""
    downsample = self._downsample_ledit.text()

    # Close old threads and create new data queue.
    self._TryCloseThreads()

    self._listener_data_queue = queue.Queue(maxsize=1000)
    self._runner_data_queue = queue.Queue(maxsize=1000)

    if not downsample or int(downsample) == 0:
      self._PrintError("No downsample given.")
      return

    downsample = int(downsample)
    buffer_size = math.ceil(5.0/downsample)

    self._PrintMessage("Starting realtime plotter.")

    self._SetupRealtimeData(downsample)
    self._SetupMotorPlot()

    for plot in self._plot_items:
      plot.setXRange(-0.01 * self._REALTIME_DATA_LEN * downsample, 0)

    vehicle_runner = VehicleRunner(
        buffer_size, self._runner_data_queue,
        fault_injection_mode=self._fault_injection_cbox.isChecked())
    self._threads.append(vehicle_runner)
    vehicle_runner.has_data.connect(self._GetVehicleData)
    vehicle_runner.has_error.connect(self._PrintError)
    vehicle_runner.start()

    vehicle_listener = VehicleListener(
        downsample, buffer_size, self._listener_data_queue,
        vehicle_runner.get_vehicle_sim())
    self._threads.append(vehicle_listener)

    vehicle_listener.has_data.connect(self._PlotRealtimeData)
    vehicle_listener.has_error.connect(self._PrintError)
    vehicle_listener.start()

  def _GetVehicleData(self):
    """Gets real-time status data from VehicleRunner instance."""
    buffer_count = 0

    while True:
      try:
        msg = self._runner_data_queue.get_nowait()
      except queue.Empty:
        break

      if buffer_count < self._REALTIME_DATA_LEN - 1:
        buffer_count += 1

  def _PlotRealtimeData(self):
    """Plots real-time status data from VehicleListener instance."""
    buffer_count = 0

    while True:
      try:
        msg = self._listener_data_queue.get_nowait()
      except queue.Empty:
        break

      # Battery.
      self._realtime_data["v_bus"][buffer_count] = msg["v_bus"]
      self._realtime_data["i_bus"][buffer_count] = msg["i_bus"]
      self._realtime_data["batt_soc"][buffer_count] = msg["batt_soc"]
      # Inverter.
      self._realtime_data["v_d"][buffer_count] = msg["v_d"]
      self._realtime_data["v_q"][buffer_count] = msg["v_q"]
      self._realtime_data["i_d"][buffer_count] = msg["i_d"]
      self._realtime_data["iq_cmd"][buffer_count] = msg["iq_cmd"]
      # Motor.
      self._realtime_data["torque_mech"][buffer_count] = msg["torque_mech"]
      self._realtime_data["omega_mech"][buffer_count] = msg["omega_mech"]
      # Cooling System.
      self._realtime_data["T_junc_batt"][buffer_count] = msg["T_junc_batt"]
      self._realtime_data["T_junc_inverter"][buffer_count] = (
          msg["T_junc_inverter"])
      self._realtime_data["T_junc_motor"][buffer_count] = msg["T_junc_motor"]
      self._realtime_data["T_fluid"][buffer_count] = msg["T_fluid"]

      if buffer_count < self._REALTIME_DATA_LEN - 1:
        buffer_count += 1

    for key, plot in self._plots.items():
      self._realtime_data[key] = numpy.roll(
          self._realtime_data[key], -buffer_count)
      if not self._is_paused:
        plot.setData(x=self._realtime_x, y=self._realtime_data[key])

  def _HandlePauseRequest(self):
    """Handles user request to pause data."""
    self._is_paused = not self._is_paused

  def _PrintMessage(self, msg):
    """Prints message in status bar and stdout."""
    self._status_message.setText(msg)

  def _PrintError(self, error):
    """Print error message."""
    self._PrintMessage("ERROR: " + error)

  def _TryCloseThreads(self):
    """Try to close running threads."""
    for thread in self._threads:
      if thread.isRunning():
        thread.should_exit = True
        thread.wait(2000)
        if thread.isRunning():
          self._PrintError("Could not terminate {:s}".format(thread))
          self.close()
    self._threads = []

  def closeEvent(self, event):
    """Overrides close event to add thread closing call.
    Args:
      event: A GUI event.
    """
    self._TryCloseThreads()
    event.accept()


class VehicleListener(QtCore.QThread):
  """A thread that listens for status data.
  Attributes:
    has_error: A signal used to communicate to other threads that the
      VehicleListener thread has encountered an error.  An error string
      is passed with the signal.
    has_data: A signal used to communicate to other threads that the
      VehicleListener thread has new data in the queue provided during
      instantiation.
    should_exit: A boolean indicating if the thread should stop executing.
  """
  # These are class members that via some magic create
  # instance members of the same name.  Magic here:
  # http://qt-project.org/wiki/Signals_and_Slots_in_PySide
  has_error = QtCore.Signal(str)
  has_data = QtCore.Signal()

  def __init__(
      self, downsample, buffer_size, data_queue, vehicle_sim, parent=None):
    """Initializes a VehicleListener.
    Args:
      downsample: An integer specifying the subsample ratio of the data that is
        passed back via the queue.
      buffer_size: An integer specifying how many data points are added to the
        queue before the thread emits its has_data signal.
      data_queue: A Queue.Queue used to pass data back to the instantiating
        thread in a thread-safe manner.
      parent: An optional parent argument for QtCore.QThread.
    """
    QtCore.QThread.__init__(self, parent)

    self.should_exit = False
    self._downsample = downsample
    self._buffer_size = buffer_size
    self._data_queue = data_queue
    self._vehicle_sim = vehicle_sim

  def run(self):
    """Runs in a separate thread."""
    downsample_counter = 0
    buffer_counter = 0

    while not self.should_exit:
      try:
        if downsample_counter < self._downsample - 1:
          downsample_counter += 1
        else:
          downsample_counter = 0
          msg = self._vehicle_sim.get_sim_outputs()
          # Print sim outputs to console.
          # print(msg)
          self._data_queue.put(msg)

        if buffer_counter < self._buffer_size - 1:
          buffer_counter += 1
        else:
          buffer_counter = 0
          self.has_data.emit()
      except Exception as e:
        print(e)
        pass

class VehicleRunner(QtCore.QThread):
  """A thread that listens for vehicle sim data.
  Attributes:
    has_error: A signal used to communicate to other threads that the
      VehicleRunner thread has encountered an error.  An error string
      is passed with the signal.
    has_data: A signal used to communicate to other threads that the
      VehicleRunner thread has new data in the queue provided during
      instantiation.
    should_exit: A boolean indicating if the thread should stop executing.
  """
  # These are class members that via some magic create
  # instance members of the same name.  Magic here:
  # http://qt-project.org/wiki/Signals_and_Slots_in_PySide
  has_error = QtCore.Signal(str)
  has_data = QtCore.Signal()

  def __init__(
    self, buffer_size, data_queue, fault_injection_mode=False, parent=None):
    """Initializes a VehicleRunner."""
    QtCore.QThread.__init__(self, parent)

    self.should_exit = False
    self._vehicle_sim = vehicle.Vehicle(
        vehicle_id=1, fault_injection_mode=fault_injection_mode)
    self._buffer_size = buffer_size
    self._data_queue = data_queue
    self._start_time = time.time()

  def get_vehicle_sim(self):
    """Gets the current vehicle_sim instance."""
    return self._vehicle_sim

  def run(self):
    """Runs vehicle simulation in a separate thread."""
    buffer_counter = 0

    while not self.should_exit:
      try:
        self._vehicle_sim.run_time_step(self._start_time)
        msg = self._vehicle_sim.get_sim_outputs()
        self._data_queue.put(msg)

        if buffer_counter < self._buffer_size - 1:
            buffer_counter += 1
        else:
          buffer_counter = 0
          self.has_data.emit()

        time.sleep(0.01)
      except Exception as e:
        print(e)
        pass


def main():
  app = QtWidgets.QApplication(sys.argv)
  unused_win = MainWindow()
  sys.exit(app.exec())


if __name__ == "__main__":
  main()
