import serial, time, queue
import tesla, fronius
import minimalmodbus
#with serial.Serial("COM10", 115200, timeout=1) as ser:
#  #ser.write("\x1B[OS")
#  buffer = ""
#  ser.write("^[[11~".encode())
#  time.sleep(1)
#  ser.write("\r".encode())
#  time.sleep(1)
#  for i in range(50):
#    line = str(i) + "  " + str(ser.readline()) + "\n"
#    #print(line)
#    buffer += line
#    #print("--------{}---------".format(i))
#
#f = open("charger.txt", "w+")
#f.write(buffer)
#print(buffer)
#buffer = ""
#with open("log.txt") as f:
#  buffer = f.read()
#matched_lines = re.findall("\#[0-9A-B].*\n", buffer)
#for line in matched_lines:
#  print(line)
#
#temperatures = []
#voltages = []
#for line in matched_lines:
#lower_serial_iqueue = queue.Queue()
#lower_serial_oqueue = queue.Queue()
#lower_tesla_serial = tesla.TeslaSerialReader("COM10", "lower", lower_serial_iqueue, lower_serial_oqueue)
#
#while True:
#  lower_tesla_serial.readout_tesla()
#  lower_tesla_serial.update()
#  time.sleep(1)
AC_CURRENT_REG_BASE = 40071
AC_VOLTAGE_REG_BASE = 40079
AC_POWER_BASE = 40083
STATUS_REG_BASE = 40107
POWER_SETPOINT_REG_BASE = 40232
THROTTLE_EN_REG_BASE = 40236
instrument = minimalmodbus.Instrument(port="COM8", slaveaddress=1, debug=True)
instrument.serial.baudrate = 9600
instrument.write_register(40232, 0,functioncode=6)
instrument.write_register(40236, 1, functioncode=6)
time.sleep(1)
instrument.write_register(40236, 1, functioncode=6)

fronius_modbus_iqueue = queue.Queue()
fronius_modbus_oqueue = queue.Queue()
fronius_modbus = fronius.FroniusModbusIf("COM8", 19200, 1, fronius_modbus_iqueue, fronius_modbus_oqueue)
fronius_modbus.read_measurements()
print("hello")