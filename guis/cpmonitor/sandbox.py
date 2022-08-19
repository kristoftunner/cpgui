import serial, re, os
#with serial.Serial("/dev/ttyS11", 115200, timeout=1) as ser:
#  #ser.write("\x1B[OS")
#  buffer = ""
#  ser.write("^[[11~".encode())
#  for i in range(100):
#    line = str(i) + "  " + str(ser.readline()) + "\n"
#    #print(line)
#    buffer += line
#    #print("--------{}---------".format(i))
import logging

# Create a custom logger
logger = logging.getLogger("cplog")

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('file.log')
c_handler.setLevel(logging.WARNING)
f_handler.setLevel(logging.ERROR)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

logger.warning('This is a warning')
logger.error('This is an error')