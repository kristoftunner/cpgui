import tesla, os, sys, queue
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QApplication, QWidget, \
                            QLabel, QMainWindow, QTabWidget, QFrame, QGridLayout,\
                            QGroupBox, QScrollArea, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib import pyplot as plt
import numpy as np

class MeasurementData():
  def __init__(self) -> None:
    self.temperatures = np.zeros((1,50), dtype=np.float32) 
    self.voltages = np.zeros((1,80), dtype=np.float32)

  def update_measurements(self, temperatures : np.array, voltages : np.array):
    self.temperatures = np.concatenate((self.temperatures, temperatures), axis=1)
    self.voltages = np.concatenate((self.voltages, voltages), axis=1)

class AppWindow(QMainWindow):
  def __init__(self, upper_tesla : tesla.TeslaManager, lower_tesla : tesla.TeslaManager) -> None:
    super().__init__()
    self.teslas = {"upper" : upper_tesla, "lower" : lower_tesla}
    self.tesla_measurements = {"upper" : MeasurementData(), "lower" : MeasurementData()}

    loadUi("guis/cpmonitor/cpmonitor.ui", self)
    self.plot_layout = self.findChild(QHBoxLayout, "plot_layout")

    self.draw_example_plots()

  def draw_battery_plots(self):
    # update the tesla measurements
    for tesla, measurement in zip(self.teslas, self.tesla_measurements):
      self.teslas[tesla].update_measurements()
      self.tesla_measurements[measurement].update_measurements(self.teslas[tesla].get_temperatures(), self.teslas[tesla].get_voltages())

    # draw the battery plots
    for index, measurement in enumerate(self.tesla_measurements):
      graph_container = QWidget()
      single_tesla_layout = QVBoxLayout(graph_container)
      voltage_fig = plt.figure()
      voltage_canvas = FigureCanvasQTAgg(voltage_fig)
      voltage_ax = voltage_fig.add_subplot()
      voltage_ax.set_title("battery voltages of {} tesla".format(measurement))
      voltage_ax.plot(self.tesla_measurements[measurement].voltages, '-')
      voltage_canvas.draw()
      single_tesla_layout.addWidget(voltage_canvas)
      
      temperature_fig = plt.figure()
      temperature_canvas = FigureCanvasQTAgg(temperature_fig)
      temperature_ax = temperature_fig.add_subplot()
      temperature_ax.set_title("battery temperatures of {} tesla".format(measurement))
      temperature_ax.plot(self.tesla_measurements[measurement].temperatures, '-')
      temperature_canvas.draw()
      single_tesla_layout.addWidget(temperature_canvas)

      self.plot_layout.addWidget(single_tesla_layout)

  def draw_example_plots(self):
    index = 0
    for row in range(3):
      graph_container = QWidget()
      vertical_layout = QVBoxLayout(graph_container)
      data1 = np.linspace(0,10,10)
      data2 = np.linspace(2,12,10)
      data = np.zeros((10,2))
      data[:,0] = data1
      data[:,1] = data2
      index += 1

      fig = plt.figure()
      canvas = FigureCanvasQTAgg(fig)
      ax = fig.add_subplot()
      ax.set_title("asd")
      ax.plot(data, '-')
      canvas.draw()
      fig2 = plt.figure()
      canvas2 = FigureCanvasQTAgg(fig2)
      ax2 = fig2.add_subplot()
      ax2.plot(data, '-')
      canvas2.draw()
      vertical_layout.addWidget(canvas)
      vertical_layout.addWidget(canvas2)

      self.plot_layout.addWidget(graph_container)
