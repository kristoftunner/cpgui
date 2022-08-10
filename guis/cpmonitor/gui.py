from csv import QUOTE_MINIMAL
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QApplication, QWidget, \
                            QLabel, QMainWindow, QTabWidget, QFrame, QGridLayout,\
                            QGroupBox, QScrollArea, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib import pyplot as plt
import numpy as np

import tesla, fronius 

class TeslaMeasurementData():
  """ placeholder class for tesla measurements """
  def __init__(self) -> None:
    self.temperatures = np.zeros((1,50), dtype=np.float32) 
    self.voltages = np.zeros((1,80), dtype=np.float32)

  def update_measurements(self, temperatures : np.array, voltages : np.array):
    self.temperatures = np.concatenate((self.temperatures, temperatures), axis=0)
    self.voltages = np.concatenate((self.voltages, voltages), axis=0)

class FroniusMeasurementData():
  def __init__(self) -> None:
    self.voltages = np.zeros((1,3), dtype=np.float32)
    self.currents = np.zeros((1,3), dtype=np.float32)
    self.power = np.array([0])
    self.frequency = np.array([0])

  def update_measurements(self, voltages: np.array, currents: np.array, power: float, frequency: float):
    self.voltages = np.concatenate((self.voltages, voltages), axis=0)
    self.currents = np.concatenate((self.currents, currents), axis=0)
    self.power = np.append(self.power, values=power)
    self.frequency = np.append(self.frequency, values=frequency)

class AppWindow(QMainWindow):
  def __init__(self, upper_tesla : tesla.TeslaManager, lower_tesla : tesla.TeslaManager, fronius : fronius.FroniusManager) -> None:
    super().__init__()
    self.teslas = {"upper" : upper_tesla, "lower" : lower_tesla}
    self.tesla_measurements = {"upper" : TeslaMeasurementData(), "lower" : TeslaMeasurementData()}
    self.fronius = fronius
    self.fronius_measurements = FroniusMeasurementData()
    loadUi("guis/cpmonitor/cpmonitor.ui", self)
    self.battery_plot_layout = self.findChild(QHBoxLayout, "battery_plot_layout")
    self.inverter_plot_layout = self.findChild(QHBoxLayout, "inverter_plot_layout")
    self.tab = self.findChild(QTabWidget, "tabWidget")
    self.tab.setTabText(0, "controls")
    self.tab.setTabText(1, "battery measuerements")
    self.tab.setTabText(2, "inverter measuerements")

    # update the battery plots
    self.init_battery_plots()
    self.init_inverter_plots()
    self.battery_timer = QTimer()
    self.battery_timer.timeout.connect(self.update_plots)
    self.battery_timer.start(2000)

  def update_plots(self):
    self.update_measurements()
    if self.tab.currentIndex() == 1:
      self.draw_battery_plots()
    elif self.tab.currentIndex() == 2:
      self.draw_inverter_plots()

  def update_measurements(self):
    # update the tesla measurements
    for tesla, measurement in zip(self.teslas, self.tesla_measurements):
      self.teslas[tesla].update_measurements()
      self.tesla_measurements[measurement].update_measurements(self.teslas[tesla].get_temperatures(), self.teslas[tesla].get_voltages())
    
    self.fronius.update_measurements()
    if self.fronius.is_measurement_valid():
      self.fronius_measurements.update_measurements(self.fronius.get_voltages(), self.fronius.get_currents(), 
                                                    self.fronius.get_power(), self.fronius.get_frequency())

  def init_battery_plots(self):
    self.battery_canvas = FigureCanvasQTAgg(plt.figure())
    graph_container = QWidget()
    single_tesla_layout = QVBoxLayout(graph_container)
    for index, measurement in enumerate(self.tesla_measurements):
      plt.subplot(2,2,index*2 + 1)
      plt.title("battery voltages of {} tesla".format(measurement))
      plt.subplot(2,2,index*2 + 2)
      plt.title("battery temperatures of {} tesla".format(measurement))
      self.battery_canvas.draw()
      single_tesla_layout.addWidget(self.battery_canvas)
    self.battery_plot_layout.addWidget(graph_container)

  def draw_battery_plots(self):

    # draw the battery plots
    for index, measurement in enumerate(self.tesla_measurements):
      voltage_ax = self.battery_canvas.figure.axes[index*2] # we have one axe per 
      voltage_ax.plot(self.tesla_measurements[measurement].voltages, 'o')
      temperature_ax = self.battery_canvas.figure.axes[index*2+1]
      temperature_ax.plot(self.tesla_measurements[measurement].temperatures, 'o')
      self.battery_canvas.draw()

  def init_inverter_plots(self):
    graph_container = QWidget()
    single_inverter_layout = QVBoxLayout(graph_container)
    self.inverter_canvas = FigureCanvasQTAgg(plt.figure())
    plt.subplot(2,2,1)
    plt.title("Fronius currents")
    plt.subplot(2,2,2)
    plt.title("Fronius voltages")
    plt.subplot(2,2,3)
    plt.title("Fronius power")
    self.inverter_canvas.draw()
    single_inverter_layout.addWidget(self.inverter_canvas)
    self.inverter_plot_layout.addWidget(graph_container)

  def draw_inverter_plots(self):
    current_ax = self.inverter_canvas.figure.axes[0]
    voltage_ax = self.inverter_canvas.figure.axes[1]
    power_ax = self.inverter_canvas.figure.axes[2]
    current_ax.plot(self.fronius_measurements.currents, 'o')
    voltage_ax.plot(self.fronius_measurements.voltages, 'o')
    power_ax.plot(self.fronius_measurements.power, 'o')
    self.inverter_canvas.draw()
     
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
      ax.plot(data, 'o')
      canvas.draw()
      fig2 = plt.figure()
      canvas2 = FigureCanvasQTAgg(fig2)
      ax2 = fig2.add_subplot()
      ax2.plot(data, 'o')
      canvas2.draw()
      vertical_layout.addWidget(canvas)
      vertical_layout.addWidget(canvas2)

      self.battery_plot_layout.addWidget(graph_container)
