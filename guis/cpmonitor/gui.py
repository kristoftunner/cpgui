from csv import QUOTE_MINIMAL
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QApplication, QWidget, \
                            QLabel, QMainWindow, QTabWidget, QFrame, QGridLayout,\
                            QGroupBox, QScrollArea, QHBoxLayout, QPushButton, QLineEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib import pyplot as plt
import numpy as np
import logging
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
    self.initial = True
    self.voltages = np.zeros((1,3), dtype=np.float32)
    self.currents = np.zeros((1,3), dtype=np.float32)
    self.power = np.array([0])
    self.frequency = np.array([0])

  def update_measurements(self, voltages: np.array, currents: np.array, power: float, frequency: float):
    if self.initial:
      self.voltages = voltages.reshape((1,3))
      self.currents = currents.reshape((1,3))
      self.power = np.array([power])
      self.frequency = np.array([frequency])
      self.initial = False
    else:
      self.voltages = np.concatenate((self.voltages, voltages), axis=0)
      self.currents = np.concatenate((self.currents, currents), axis=0)
      self.power = np.append(self.power, values=power)
      self.frequency = np.append(self.frequency, values=frequency)

class AppWindow(QMainWindow):
  def __init__(self, upper_tesla : tesla.TeslaManager, lower_tesla : tesla.TeslaManager, fronius : fronius.FroniusManager) -> None:
    super().__init__()
    self.logger = logging.getLogger("cplog")
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
    self.start_button = self.findChild(QPushButton, "startButton")
    self.start_button.setCheckable(True)
    self.start_button.pressed.connect(self.update_power)
    self.power_text = self.findChild(QLineEdit, "powerText")

    # update the battery plots
    self.init_battery_plots()
    self.init_inverter_plots()
    self.battery_timer = QTimer()
    self.battery_timer.timeout.connect(self.update_plots)
    self.battery_timer.start(2000)

    self.max_charge = 5000
    self.max_discharge = 12000
    self.do_draw_battery_plots = False 
    self.do_draw_inverter_plots = False

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
      if self.teslas[tesla].measurement_recvd():
        self.do_draw_battery_plots = True
        temperatures, voltages = self.teslas[tesla].get_measurements()
        self.tesla_measurements[measurement].update_measurements(temperatures, voltages)
    
    self.fronius.update_measurements()
    if self.fronius.is_measurement_valid():
      self.do_draw_inverter_plots = True
      self.fronius_measurements.update_measurements(self.fronius.get_voltages(), self.fronius.get_currents(), 
                                                    self.fronius.get_power(), self.fronius.get_frequency())

  def init_battery_plots(self):
    self.battery_canvas = FigureCanvasQTAgg(plt.figure())
    graph_container = QWidget()
    single_tesla_layout = QVBoxLayout(graph_container)
    for index, measurement in enumerate(self.tesla_measurements):
      plt.subplot(2,2,index*2 + 1)
      plt.title("battery voltages of {} tesla".format(measurement))
      plt.ylim(3.5,3.9)
      plt.subplot(2,2,index*2 + 2)
      plt.title("battery temperatures of {} tesla".format(measurement))
      plt.ylim(20,40)
      self.battery_canvas.draw()
      single_tesla_layout.addWidget(self.battery_canvas)
    self.battery_plot_layout.addWidget(graph_container)

  def draw_battery_plots(self):

    # draw the battery plots
    if self.do_draw_battery_plots:
      for index, measurement in enumerate(self.tesla_measurements):
        if self.tesla_measurements[measurement].voltages.shape[0] > 1:
          voltage_ax = self.battery_canvas.figure.axes[index*2] # we have one axe per 
          voltage_shape = (self.tesla_measurements[measurement].voltages.shape[0]-1,self.tesla_measurements[measurement].voltages.shape[1])
          voltage_ax.plot(self.tesla_measurements[measurement].voltages[1:,:].reshape(voltage_shape), 'o')
          temperature_ax = self.battery_canvas.figure.axes[index*2+1]
          temperature_shape = (self.tesla_measurements[measurement].temperatures.shape[0]-1,self.tesla_measurements[measurement].temperatures.shape[1])
          temperature_ax.plot(self.tesla_measurements[measurement].temperatures[1:,:].reshape(temperature_shape), 'o')
          self.battery_canvas.draw()
      self.do_draw_battery_plots = False

  def init_inverter_plots(self):
    graph_container = QWidget()
    single_inverter_layout = QVBoxLayout(graph_container)
    self.inverter_canvas = FigureCanvasQTAgg(plt.figure())
    plt.subplot(2,3,1)
    plt.title("Fronius L1 Voltage")
    plt.ylabel("Voltage [A]")
    plt.subplot(2,3,2)
    plt.title("Fronius L2 Voltage")
    plt.ylabel("Voltage [A]")
    plt.subplot(2,3,3)
    plt.title("Fronius L3 Voltage")
    plt.ylabel("Voltage [A]")
    plt.subplot(2,3,4)
    plt.title("Fronius L2 current")
    plt.ylabel("Current [A]")
    plt.subplot(2,3,5)
    plt.title("Fronius L3 current")
    plt.ylabel("Current [A]")
    plt.subplot(2,3,6)
    plt.title("Fronius L1 current")
    plt.ylabel("Current [A]")
    self.inverter_canvas.draw()
    single_inverter_layout.addWidget(self.inverter_canvas)
    self.inverter_plot_layout.addWidget(graph_container)

  def draw_inverter_plots(self):
    if self.do_draw_inverter_plots:
      if self.fronius_measurements.currents.shape[0] > 1:
        l1_voltage_ax = self.inverter_canvas.figure.axes[0]
        l2_voltage_ax = self.inverter_canvas.figure.axes[1]
        l3_voltage_ax = self.inverter_canvas.figure.axes[2]
        l1_current_ax = self.inverter_canvas.figure.axes[3]
        l2_current_ax = self.inverter_canvas.figure.axes[4]
        l3_current_ax = self.inverter_canvas.figure.axes[5]
        self.logger.debug("currents shape: {}".format(self.fronius_measurements.currents.shape))
        self.logger.debug("voltages shape: {}".format(self.fronius_measurements.voltages.shape))
        self.logger.debug("power shape: {}".format(self.fronius_measurements.power.shape))
        l1_voltage_ax.plot(self.fronius_measurements.voltages[:,0], "-o", color="b")
        l2_voltage_ax.plot(self.fronius_measurements.voltages[:,1], "-o", color="b")
        l3_voltage_ax.plot(self.fronius_measurements.voltages[:,2], "-o", color="b")
        l1_current_ax.plot(self.fronius_measurements.currents[:,0], "-o", color="r")
        l2_current_ax.plot(self.fronius_measurements.currents[:,1], "-o", color="r")
        l3_current_ax.plot(self.fronius_measurements.currents[:,2], "-o", color="r")
        self.inverter_canvas.draw()
        self.do_draw_inverter_plots = False
     
  def update_power(self):
    if self.start_button.isChecked() == False: # transition from unchecked to checked
      self.start_button.setStyleSheet("background-color: green")
      self.start_button.setText("Started")
      power = float(self.power_text.text())
      if power > self.max_discharge or power < self.max_charge:
        if power > 0:
          # charge
          channel_power = power / 4
          self.teslas["upper"].start(channel_power, "ch1")
          self.teslas["upper"].start(channel_power, "ch2")
          self.teslas["lower"].start(channel_power, "ch2")
          self.teslas["lower"].start(channel_power, "ch2")
        else:
          # discharge
          self.fronius.set_power(power)
    else:
      self.start_button.setStyleSheet("background-color: red")
      self.start_button.setText("Stopped")
      self.fronius.set_power(0.0)
      self.teslas["upper"].stop()
      self.teslas["lower"].stop() 