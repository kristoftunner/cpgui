from distutils.core import setup
import time
from PyQt5.QtWidgets import QApplication 
import queue, sys, threading, logging

# own scripts
import gui, tesla

def generate_random_tesla_input(source : str) -> tesla.SerialBuffer:
  pass

def generate_tesla_input(source : str) -> tesla.SerialBuffer:
  sbuffer = tesla.SerialBuffer
  sbuffer.source = source
  with open("guis/cpmonitor/battery_screen.txt") as f:
    sbuffer.buffer = f.read()

  return sbuffer

def tesla_serial_thread(tesla_serial : tesla.TeslaSerialReader):
  time.sleep(1)
  sbuffer = generate_tesla_input("battery")
  tesla_serial.sbuffers.append(sbuffer)
  tesla_serial.update()  

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

  t_lower_tesla = threading.Thread(target=tesla_serial_thread, args=(lower_tesla_serial,))
  t_upper_tesla = threading.Thread(target=tesla_serial_thread, args=(upper_tesla_serial,))
  t_lower_tesla.start()
  t_upper_tesla.start()
  window = gui.AppWindow(upper_tesla, lower_tesla)
  window.show()
  sys.exit(app.exec_())