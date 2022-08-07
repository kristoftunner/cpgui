from nis import match
import os
import re
input = str()
with open("guis/cpmonitor/battery_screen.txt") as f:
  input = f.read()
  print(input)

matched_lines = re.findall("\#[0-1A-B].*\n", input)

#iterate trough half of the list
for single_match in matched_lines[0:len(matched_lines)//2]:
  voltages = [float(match) for match in re.findall("[0-9]*\.[0-9]*",single_match)[0]]
  temperatures = [float(match) for match in re.findall(" [0-9]+[ \n]", single_match)]
