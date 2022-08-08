from pyModbusTCP.utils import encode_ieee, decode_ieee, \
                              long_list_to_word, word_list_to_long
import queue
import minimalmodbus

class FroniusMessage():
  def __init__(self) -> None:
    self.message_valid = False
    self.measurements = {"L1Voltage" : None, "L2Voltage" : None, "L3Voltage" : None, 
                        "L1Current" : None, "L2Current" : None, "L3Current" : None, "Power" : None, "Frequency" : None}

class FroniusModbusIf():
  def __init__(self, port : str, baudrate : int, address, serial_input : queue.Queue, serial_output: queue.Queue) -> None:
    self.port = port
    self.baudrate = baudrate 
    self.address = address
    self.instrument = minimalmodbus.Instrument(port=port, slaveaddress=address, debug=True)
    self.input_queue = serial_input
    self.output_queue = serial_output
    self.message = FroniusMessage()

  def set_power(self):
    pass

  def update(self):
    if self.message.measurements["MessageValid"]:
      self.output_queue.put(self.message)

  def read_measurements(self):
    pass
