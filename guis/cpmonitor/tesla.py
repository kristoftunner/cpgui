import serial
import queue
from typing import Dict
import re, logging
import numpy as np

SCREENS = {"ch1" : 25, "ch2" : 25, "ch3" : 25, "battery" : 24}

class TeslaSerialMessage():
  def __init__(self) -> None:
    self.measurements_valid = False
    self.power_setpoints_valid = False
    self.measurements = {"voltages" : np.zeros((1,80), dtype=np.float32), "temperatures" : np.zeros((1,50), dtype=np.float32)}
    self.tesla_setpoints = {"ch1" : {"power" : 0}, "ch2" : {"power" : 0}, "ch3" : {"power" : 0}}

class SerialBuffer():
  def __init__(self, buffer : str, source : str) -> None:
    self.sbuffer = buffer
    self.source = source

class TeslaSerialReader():
  def __init__(self, port : str, tesla_id : str, serial_input : queue.Queue, serial_output: queue.Queue) -> None:
    self.logger = logging.getLogger("cplog")
    self.serial_input = serial_input
    self.serial_output = serial_output
    self.message = TeslaSerialMessage()
    self.id = tesla_id
    self.sbuffers = {}
    self.baudrate = 115200
    self.port = port

  def parse_message(self, sbuffer : SerialBuffer):
    if sbuffer.source == "battery":
      matched_lines = re.findall("\#[0-9A-B] 3\..*\n", sbuffer.sbuffer)
      #iterate trough half of the list and extract temperatures and voltages
      voltages = list()
      temperatures = list()
      for single_match in matched_lines[0:len(matched_lines)//2]:
        [voltages.append(float(voltage)) for voltage in re.findall("[0-9]*\.[0-9]*",single_match)]
        [temperatures.append(float(temperature)) for temperature in re.findall(" [0-9]+[ \n]", single_match)]
      if len(voltages) == 80 and len(temperatures) == 50:
        voltages = np.array(voltages, dtype=np.float32).reshape((1,80))
        temperatures = np.array(temperatures, dtype=np.float32).reshape((1,50))
        self.message.measurements["voltages"] = voltages
        self.message.measurements["temperatures"] = temperatures
        self.message.measurements_valid = True
    elif sbuffer.source == "ch1":
      pass
    elif sbuffer.source == "ch2":
      pass
    elif sbuffer.source == "ch3":
      pass
  
  def readout_tesla(self):
    with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
      for (key,value) in SCREENS.items():
        if key == "ch1":
          ser.write("^[[11~".encode())
          ser.write("\r".encode())
        elif key == "ch2":
          ser.write("^[[12~".encode())
          ser.write("\r".encode())
        elif key == "ch3":
          ser.write("^[[13~".encode())
          ser.write("\r".encode())
        elif key == "battery":
          ser.write("^[[14~".encode())
          ser.write("\r".encode())
        else:
          raise ValueError("wrong screen was selected!")
        sbuffer = SerialBuffer("","")
        for i in range(value*2):
          line = ser.readline()
          sbuffer.sbuffer += line.decode()
        sbuffer.source = key
        self.sbuffers[key] = sbuffer
        self.logger.debug("received at tesla {}: from channel:{} - {}".format(self.id, sbuffer.source, sbuffer.sbuffer))
  
  def update(self):
    self.message.measurements_valid = False
    self.message.power_setpoints_valid = False
    for buffer in self.sbuffers:
      self.parse_message(self.sbuffers[buffer])
      self.serial_output.put(self.message)
    self.serial_output.put(self.message)

    if not self.serial_input.empty():
      pass # do the update here

class TeslaManager():
  def __init__(self, tesla_id : str, serial_input : queue.Queue, serial_output : queue.Queue) -> None:
    self.logger = logging.getLogger("cplog")
    self.id = tesla_id
    self.input_queue = serial_output
    self.output_queue = serial_input
    self.tesla_status = TeslaSerialMessage()
  
  def start(self, power_setpoint : float, channel : str):
    self.logger.debug("started {} tesla".format(self.id))
    output_message = TeslaSerialMessage()
    output_message.tesla_setpoints[channel] = {"power" : power_setpoint}
    self.output_queue.put(output_message)

  def stop(self):
    self.logger.debug("stopped {} tesla".format(self.id))
    output_message = TeslaSerialMessage()
    self.output_queue.put(output_message) 

  def update_measurements(self):
    """ flush the input queue and get the latest message"""
    while not self.input_queue.empty():
      self.tesla_status = self.input_queue.get()
  
  def get_temperatures(self):
    data = np.zeros((1,50), dtype=np.float32)
    data[0,:] = self.tesla_status.measurements["temperatures"]
    return data 

  def get_voltages(self):
    data = np.zeros((1,80), dtype=np.float32)
    data[0,:] = self.tesla_status.measurements["voltages"]
    return data 
