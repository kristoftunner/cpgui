from PyQt5.QtWidgets import QApplication 
import queue, sys, threading, logging

# own scripts
import gui, tesla

def generate_tesla_input():
  pass

def lower_tesla_thread():
  pass

def upper_tesla_thread():
  pass

if __name__ == '__main__':
  app = QApplication(sys.argv)
  
  lower_serial_iqueue = queue.Queue()
  lower_serial_oqueue = queue.Queue()
  lower_tesla_serial = tesla.TeslaSerialReader("/dev/ttyUSB0", "lower", lower_serial_iqueue, lower_serial_oqueue)
  lower_tesla = tesla.TeslaManager("lower", lower_serial_iqueue, lower_serial_oqueue)
  
  upper_serial_iqueue = queue.Queue()
  upper_serial_oqueue = queue.Queue()
  upper_tesla = tesla.TeslaManager("upper", upper_serial_iqueue, upper_serial_oqueue)
  upper_tesla_serial = tesla.TeslaSerialReader("/dev/ttyUSB0", "lower", upper_serial_iqueue, upper_serial_oqueue)

  window = gui.AppWindow(upper_tesla, lower_tesla)
  window.show()
  sys.exit(app.exec_())