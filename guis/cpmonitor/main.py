import time, os
from PyQt5.QtWidgets import QApplication 
import queue, sys, threading, logging
import numpy as np

# own scripts
import gui, tesla, fronius

def setup_logging():
  logger = logging.getLogger("cplog")
  # Create handlers
  c_handler = logging.StreamHandler()
  f_handler = logging.FileHandler('file.log')
  c_handler.setLevel(logging.DEBUG)
  f_handler.setLevel(logging.DEBUG)

  # Create formatters and add it to handlers
  c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
  f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  c_handler.setFormatter(c_format)
  f_handler.setFormatter(f_format)

  # Add handlers to the logger
  logger.addHandler(c_handler)
  logger.addHandler(f_handler)
  logger.setLevel(logging.DEBUG)
  

  return logger

def generate_random_tesla_input(source : str) -> tesla.SerialBuffer:
  """ generate  random"""
  message = tesla.TeslaSerialMessage()
  rng = np.random.default_rng()
  message.measurements_valid = True
  message.measurements["voltages"] = rng.random((1,80), dtype=np.float32) * 0.8 + 3.2
  message.measurements["temperatures"] = rng.random((1,50), dtype=np.float32) * 3 + 28.0
  return message 

def generate_tesla_input(source : str) -> tesla.SerialBuffer:
  sbuffer = tesla.SerialBuffer
  sbuffer.source = source
  with open("guis/cpmonitor/battery_screen.txt") as f:
    sbuffer.sbuffer = f.read()
  return sbuffer

def generate_fronius_input() -> fronius.FroniusMessage:
  message = fronius.FroniusMessage()
  message.measurements = {"L1Voltage" : 231.0, "L2Voltage" : 230.0, "L3Voltage" : 229.0, 
                        "L1Current" : 10.2, "L2Current" : 10.15, "L3Current" : 10.3, "Power" : 4979.4, "Frequency" : 49.99}
  message.message_valid = True
  return message

def tesla_serial_thread(tesla_serial : tesla.TeslaSerialReader):
  while True:
    message = generate_tesla_input("battery")
    tesla_serial.sbuffers["battery"] = message
    tesla_serial.update() 
    time.sleep(2)
  #while True:
  #  tesla_serial.readout_tesla()
  #  tesla_serial.update() 
  #  time.sleep(2) 

def fronius_modbus_thread(fronius_modbus : fronius.FroniusModbusIf):
  while True:
    message = generate_fronius_input()
    fronius_modbus.message = message
    fronius_modbus.update()
    time.sleep(2) 
  #while True:
  #  fronius_modbus.read_measurements()
  #  fronius_modbus.update()
  #  time.sleep(2)

if __name__ == '__main__':
  setup_logging()
  logger = logging.getLogger("cplog")
  logger.debug("hello from main")
  app = QApplication(sys.argv)

  lower_serial_iqueue = queue.Queue()
  lower_serial_oqueue = queue.Queue()
  lower_tesla_serial = tesla.TeslaSerialReader("COM4", "lower", lower_serial_iqueue, lower_serial_oqueue)
  lower_tesla = tesla.TeslaManager("lower", lower_serial_iqueue, lower_serial_oqueue)
  
  upper_serial_iqueue = queue.Queue()
  upper_serial_oqueue = queue.Queue()
  upper_tesla_serial = tesla.TeslaSerialReader("COM6", "upper", upper_serial_iqueue, upper_serial_oqueue)
  upper_tesla = tesla.TeslaManager("upper", upper_serial_iqueue, upper_serial_oqueue)

  fronius_modbus_iqueue = queue.Queue()
  fronius_modbus_oqueue = queue.Queue()
  fronius_modbus = fronius.FroniusModbusIf("COM7", 9600, 1, fronius_modbus_iqueue, fronius_modbus_oqueue)
  fronius_manager = fronius.FroniusManager(fronius_modbus_iqueue, fronius_modbus_oqueue)

  t_lower_tesla = threading.Thread(target=tesla_serial_thread, args=(lower_tesla_serial,))
  t_upper_tesla = threading.Thread(target=tesla_serial_thread, args=(upper_tesla_serial,))
  t_fronius = threading.Thread(target=fronius_modbus_thread, args=(fronius_modbus,))
  t_lower_tesla.start()
  t_upper_tesla.start()
  t_fronius.start()
  window = gui.AppWindow(upper_tesla, lower_tesla, fronius_manager)
  window.show()
  sys.exit(app.exec_())