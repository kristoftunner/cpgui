import serial, re, os
with serial.Serial("/dev/ttyS11", 115200, timeout=1) as ser:
  #ser.write("\x1B[OS")
  buffer = ""
  ser.write("^[[11~".encode())
  for i in range(100):
    line = str(i) + "  " + str(ser.readline()) + "\n"
    #print(line)
    buffer += line
    #print("--------{}---------".format(i))

f = open("charger.txt", "w+")
f.write(buffer)
print(buffer)
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
