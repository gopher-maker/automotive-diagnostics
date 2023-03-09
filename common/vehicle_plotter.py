"""Tool for plotting vehicle simulation parameters."""

import importlib
import numpy
import sys

from PySide6 import QtCore
from PySide6 import QtWidgets


# Must be included after PySide in order to force pyqtgraph to use it.
pyqtgraph = importlib.import_module('pyqtgraph')
dockarea = importlib.import_module('pyqtgraph.dockarea')


class MainWindow(QtWidgets.QMainWindow):

  _REALTIME_DATA_LEN = 3000

  def __init__(self):
    super(MainWindow, self).__init__()
    self._InitUI()

  def _InitUI(self):
    """Creates and arranges all GUI elements."""
    central_widget = QtWidgets.QWidget()

    load_btn = QtWidgets.QPushButton('Load')

    plot_dockarea = dockarea.DockArea()

    status_message = QtWidgets.QLabel('')

    hbox = QtWidgets.QHBoxLayout()
    hbox.addWidget(load_btn)

    vbox = QtWidgets.QVBoxLayout()
    vbox.addLayout(hbox)
    vbox.addWidget(plot_dockarea, stretch=1)

    central_widget.setLayout(vbox)

    self.setCentralWidget(central_widget)
    self.setGeometry(300, 150, 1200, 1000)
    self.setWindowTitle('Vehicle Plotter')
    self.statusBar().addWidget(status_message)
    self.show()

    self._status_message = status_message
    self._plot_dockarea = plot_dockarea


def main():
  app = QtWidgets.QApplication(sys.argv)
  unused_win = MainWindow()
  sys.exit(app.exec())


if __name__ == '__main__':
  main()
