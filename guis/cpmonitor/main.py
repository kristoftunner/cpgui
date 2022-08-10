import time, os
from PyQt5.QtWidgets import QApplication 
import queue, sys, threading, logging

# own scripts
import gui, tesla, fronius

def setup_logging():
  logger = logging.getLogger("cplog")
  c_handler = logging.StreamHandler()
  f_handler = logging.FileHandler('file.log')
  c_handler.setLevel(logging.WARNING)
  f_handler.setLevel(logging.ERROR)

  # Create formatters and add it to handlers
  c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  c_handler.setFormatter(c_format)
  f_handler.setFormatter(f_format)

  # Add handlers to the logger
  logger.addHandler(c_handler)
  logger.addHandler(f_handler)


def generate_random_tesla_input(source : str) -> tesla.SerialBuffer:
  pass

def generate_tesla_input(source : str) -> tesla.SerialBuffer:
  sbuffer = tesla.SerialBuffer
  sbuffer.source = source
  with open("guis/cpmonitor/battery_screen.txt") as f:
    sbuffer.buffer = f.read()
  return sbuffer

def generate_fronius_input() -> fronius.FroniusMessage:
  message = fronius.FroniusMessage()
  message.measurements = {"L1Voltage" : 231.0, "L2Voltage" : 230.0, "L3Voltage" : 229.0, 
                        "L1Current" : 10.2, "L2Current" : 10.15, "L3Current" : 10.3, "Power" : 4979.4, "Frequency" : 49.99}
  message.message_valid = True
  return message

def tesla_serial_thread(tesla_serial : tesla.TeslaSerialReader):
  sbuffer = generate_tesla_input("battery")
  tesla_serial.sbuffers["battery"] = sbuffer
  tesla_serial.update()  

def fronius_modbus_thread(fronius_modbus : fronius.FroniusModbusIf):
  fronius_modbus.message = generate_fronius_input()
  fronius_modbus.update()

if __name__ == '__main__':
  setup_logging()
  app = QApplication(sys.argv)

  lower_serial_iqueue = queue.Queue()
  lower_serial_oqueue = queue.Queue()
  lower_tesla_serial = tesla.TeslaSerialReader("/dev/ttyUSB0", "lower", lower_serial_iqueue, lower_serial_oqueue)
  lower_tesla = tesla.TeslaManager("lower", lower_serial_iqueue, lower_serial_oqueue)
  
  upper_serial_iqueue = queue.Queue()
  upper_serial_oqueue = queue.Queue()
  upper_tesla = tesla.TeslaManager("upper", upper_serial_iqueue, upper_serial_oqueue)
  upper_tesla_serial = tesla.TeslaSerialReader("/dev/ttyUSB0", "lower", upper_serial_iqueue, upper_serial_oqueue)

  fronius_modbus_iqueue = queue.Queue()
  fronius_modbus_oqueue = queue.Queue()
  fronius_modbus = fronius.FroniusModbusIf("/dev/ttyUSB0", 19200, 2, fronius_modbus_iqueue, fronius_modbus_oqueue)
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