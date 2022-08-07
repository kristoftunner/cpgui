import numpy as np
import os
import re
input = str()
with open("guis/cpmonitor/battery_screen.txt") as f:
  input = f.read()
  print(input)

matched_lines = re.findall("\#[0-9A-B].*\n", input)

#iterate trough half of the list
voltages = list()
temperatures = list()
for single_match in matched_lines[0:len(matched_lines)//2 + 1]:
  [voltages.append(float(match)) for match in re.findall("[0-9]*\.[0-9]*",single_match)]
  [temperatures.append(float(match)) for match in re.findall(" [0-9]+[ \n]", single_match)]

temperature_array = np.array(temperatures, dtype=np.float32).reshape((1,50))
voltage_array = np.array(voltages, dtype=np.float32).reshape((1,80))
print(str(voltages))
print(str(temperatures))