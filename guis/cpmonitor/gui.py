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
class AppWindow(QMainWindow):
  def __init__(self, upper_tesla : tesla.TeslaManager, lower_tesla : tesla.TeslaManager, fronius : fronius.FroniusManager) -> None:
    super().__init__()
    self.teslas = {"upper" : upper_tesla, "lower" : lower_tesla}
    self.tesla_measurements = {"upper" : TeslaMeasurementData(), "lower" : TeslaMeasurementData()}
    self.fronius = fronius
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
    self.battery_timer.timeout.connect(self.draw_battery_plots)
    self.battery_timer.start(1000)

  def update_plots(self):
    self.draw_battery_plots()
    #self.draw_inverter_plots()

  def init_battery_plots(self):
    self.battery_canvases = []
    for index, measurement in enumerate(self.tesla_measurements):
      graph_container = QWidget()
      single_tesla_layout = QVBoxLayout(graph_container)
      voltage_canvas = FigureCanvasQTAgg(plt.figure())
      self.battery_canvases.append(voltage_canvas)
      voltage_ax = plt.axes()
      voltage_ax.set_title("battery voltages of {} tesla".format(measurement))
      voltage_canvas.draw()
      single_tesla_layout.addWidget(voltage_canvas)
      
      temperature_canvas = FigureCanvasQTAgg(plt.figure())
      self.battery_canvases.append(temperature_canvas)
      temperature_ax = plt.axes()
      temperature_ax.set_title("battery temperatures of {} tesla".format(measurement))
      temperature_canvas.draw()
      single_tesla_layout.addWidget(temperature_canvas)
      self.battery_plot_layout.addWidget(graph_container)

  def draw_battery_plots(self):
    # update the tesla measurements
    for tesla, measurement in zip(self.teslas, self.tesla_measurements):
      self.teslas[tesla].update_measurements()
      self.tesla_measurements[measurement].update_measurements(self.teslas[tesla].get_temperatures(), self.teslas[tesla].get_voltages())

    # draw the battery plots
    for index, measurement in enumerate(self.tesla_measurements):
      voltage_canvas = self.battery_canvases[index*2] 
      voltage_ax = voltage_canvas.figure.axes[0] # we have one axe per 
      voltage_ax.plot(self.tesla_measurements[measurement].voltages, 'o')
      voltage_canvas.draw()
      
      temperature_canvas = self.battery_canvases[index*2 + 1] 
      temperature_ax = temperature_canvas.figure.axes[0]
      temperature_ax.plot(self.tesla_measurements[measurement].temperatures, 'o')
      temperature_canvas.draw()

  def init_inverter_plots(self):
    self.inverter_canvases = []
    graph_container = QWidget()
    single_inverter_layout = QVBoxLayout(graph_container)
    inverter_canvas = FigureCanvasQTAgg(plt.figure())
    self.inverter_canvases.append(inverter_canvas)
    plt.subplot(2,2,1)
    plt.title("Fronius currents")
    plt.subplot(2,2,2)
    plt.title("Fronius voltages")
    plt.subplot(2,2,3)
    plt.title("Fronius power")
    inverter_canvas.draw()
    single_inverter_layout.addWidget(inverter_canvas)
      
    self.inverter_plot_layout.addWidget(graph_container)

  def draw_inverter_plots(self):
    self.fronius.update_measurements()
     
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
