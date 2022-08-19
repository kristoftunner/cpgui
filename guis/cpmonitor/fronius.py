from pyModbusTCP.utils import encode_ieee, decode_ieee, \
                              long_list_to_word, word_list_to_long
import queue, logging, math
import numpy as np
import minimalmodbus

AC_CURRENT_REG_BASE = 40071
AC_VOLTAGE_REG_BASE = 40079
AC_POWER_BASE = 40083
STATUS_REG_BASE = 40107
POWER_SETPOINT_REG_BASE = 40232
THROTTLE_EN_REG_BASE = 40236

class FroniusMessage():
  def __init__(self) -> None:
    self.message_valid = False
    self.measurements = {"L1Voltage" : None, "L2Voltage" : None, "L3Voltage" : None, 
                        "L1Current" : None, "L2Current" : None, "L3Current" : None, "Power" : None, "Frequency" : None}

class FroniusManager():
  def __init__(self, modbus_input : queue.Queue, modbus_output: queue.Queue) -> None:
    self.input_queue = modbus_output
    self.output_queue = modbus_input
    self.fronius_status = FroniusMessage()

  def update_measurements(self):
    """ flush the input queue and get the latest message""" 
    while not self.input_queue.empty():
      self.fronius_status = self.input_queue.get()

  def set_power(self, power : float):
    self.output_queue.put(power)

  def get_voltages(self):
    if self.fronius_status.message_valid:
      return np.array([self.fronius_status.measurements["L1Voltage"], self.fronius_status.measurements["L2Voltage"], self.fronius_status.measurements["L3Voltage"]], dtype=np.float32).reshape((1,3))

  def get_currents(self):
    if self.fronius_status.message_valid:
      return np.array([self.fronius_status.measurements["L1Current"], self.fronius_status.measurements["L2Current"], self.fronius_status.measurements["L3Current"]], dtype=np.float32).reshape((1,3))

  def get_frequency(self):
     if self.fronius_status.message_valid:
      return self.fronius_status.measurements["Frequency"]

  def get_power(self):
    if self.fronius_status.message_valid:
      return self.fronius_status.measurements["Power"]

  def is_measurement_valid(self):
    return self.fronius_status.message_valid
      
class FroniusModbusIf():
  def __init__(self, port : str, baudrate : int, address, modbus_input : queue.Queue, modbus_output: queue.Queue) -> None:
    self.logger = logging.getLogger("cplog")
    self.max_power = 5000 # TODO: update this number
    self.port = port
    self.power_setpoint = 0
    self.baudrate = baudrate 
    self.address = address
    self.instrument = None
    self.instrument = minimalmodbus.Instrument(port=port, slaveaddress=address, debug=True)
    self.instrument.serial.baudrate = 9600
    self.input_queue = modbus_input
    self.output_queue = modbus_output
    self.message = FroniusMessage()

  def set_power(self, power : float):
    if power > self.max_power:
      self.logger.warning("Requested power from Fronius is higher than the nameplate value")
    else:
      percentage : int = int(((power / self.max_power) * 100))
      self.power_setpoint = power
      self.logger.debug("precentage set for the fronius throttle is: {}%".format(percentage))
      self.instrument.write_register(POWER_SETPOINT_REG_BASE, percentage,functioncode=6)
      self.instrument.write_register(THROTTLE_EN_REG_BASE, 1, functioncode=6)

  def update(self):
    """ get single power value from the input queue """
    if self.message.message_valid:
      self.output_queue.put(self.message)
    if not self.input_queue.empty():
      self.set_power(self.input_queue.get())

  def read_measurements(self):
    """ this function should be read in a loop in a specific thread handling IOs"""
    # read the voltages, power and frequency
    is_valid = True
    measurements = self.instrument.read_registers(AC_VOLTAGE_REG_BASE, 14, functioncode=3)
    if len(measurements) == 14:
      self.message.measurements["L1Voltage"] = measurements[0] * math.pow(10,measurements[3])
      self.message.measurements["L2Voltage"] = measurements[1] * math.pow(10,measurements[3])
      self.message.measurements["L3Voltage"] = measurements[2] * math.pow(10,measurements[3])
      self.message.measurements["Power"] = measurements[4] * math.pow(10, measurements[5])
      self.message.measurements["Frequency"] = measurements[6] * math.pow(10, measurements[7])
    else:
      self.logger.warning("read failed from fronius at reg: {}".format(AC_VOLTAGE_REG_BASE))
      is_valid = False 
    # read the currents
    measurements = self.instrument.read_registers(AC_CURRENT_REG_BASE, 5)
    if len(measurements) == 5:
      self.message.measurements["L1Current"] = measurements[1] * math.pow(10, measurements[4])
      self.message.measurements["L2Current"] = measurements[2] * math.pow(10, measurements[4])
      self.message.measurements["L3Current"] = measurements[3] * math.pow(10, measurements[4])
    else:
      self.logger.warning("read failed from fronius at reg: {}".format(AC_CURRENT_REG_BASE))
      is_valid = False 
    self.message.message_valid = is_valid

