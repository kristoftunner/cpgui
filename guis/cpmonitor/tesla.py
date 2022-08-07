import serial
import queue
from typing import Dict
import re, logging

SCREENS = [{"ch1" : 25}, {"ch2" : 25}, {"ch3" : 25}, {"battery" : 24}]

class TeslaSerialMessage():
  def __init__(self) -> None:
    self.measurements = {"voltages" : [], "temperatures" : []}
    self.tesla_setpoints = {"ch1" : {"voltage" : None, "current" : None}, "ch2" : {"voltage" : None, "current" : None}, "ch3" : {"voltage" : None, "current" : None}}

class SerialBuffer():
  def __init__(self, buffer : str, source : str) -> None:
    self.sbuffer = buffer
    self.source = source

class TeslaSerialReader():
  def __init__(self, port : str, tesla_id, serial_output : queue.Queue, serial_input: queue.Queue) -> None:
    self.logger = logging.getLogger("cplog")
    self.serial_input = serial_input
    self.serial_output = serial_output
    self.message = TeslaSerialMessage()
    self.id = tesla_id
    self.sbuffers = [] 
    self.baudrate = 115200
    self.port = port

  def parse_message(self, sbuffer : SerialBuffer):
    if sbuffer.source == "battery":
      matched_lines = re.findall("\#[0-1A-B].*\n", self.sbuffer.buffer)

      #iterate trough half of the list and extract temperatures and voltages
      for single_match in matched_lines[0:len(matched_lines)//2]:
        [self.message.measurements["voltages"].append(float(voltage)) for voltage in re.findall("[0-9]*\.[0-9]*",single_match)[0]]
        [self.message.measurements["temperatures"].append(float(temperature)) for temperature in re.findall(" [0-9]+[ \n]", single_match)]
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
          ser.write("\x1B[OP")
        elif key == "ch2":
          ser.write("\x1B[OQ")
        elif key == "ch3":
          ser.write("\x1B[OR")
        elif key == "battery":
          ser.write("\x1B[OS")
        else:
          raise ValueError("wrong screen was selected!")
        sbuffer = SerialBuffer()
        for i in range(value):
          sbuffer.buffer += ser.readline()
        sbuffer.source = key
        self.sbuffers.append(sbuffer)
        self.logger.debug("received at tesla {}: from channel:{} - {}".format(self.id, sbuffer.source, sbuffer.buffer))
  
  def update(self):
    for buffer in self.sbuffers:
      self.parse_message(buffer)
      self.serial_output.put(self.message)
    self.serial_output.put(self.message)

  def change_screen(self, screen : SCREENS):
    self.current_screen = screen

class TeslaManager():
  def __init__(self, serial_input : queue.Queue, serial_output : queue.Queue) -> None:
    self.logger = logging.getLogger("cplog")
    self.input_queue = serial_output
    self.output_queue = serial_input
    self.tesla_status = TeslaSerialMessage()
  
  def start(self, power_setpoint : float, channel : str):
    output_message = TeslaSerialMessage()
    voltage = 240.0
    current = power_setpoint / voltage
    output_message.tesla_setpoints[channel] = {"voltage" : voltage, "current" : current}

  def stop(self):
    pass

  def update_measurements(self):
    """ flush the input queue and get the latest message"""
    while not self.input_queue.empty():
      tesla_status = queue.get()
  
  def get_temperatures(self):
    return self.measurements["temperatures"]

  def get_voltages(self):
    return self.measurements["voltages"]
    
