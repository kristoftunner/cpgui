import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QCheckBox, QDialog, QApplication, QWidget, QLabel, QMainWindow, QTabWidget
from PyQt5.QtGui import QPixmap

class Screen(QDialog):
  def __init__(self):
    super(Screen, self).__init__()
    loadUi("cpmonitor/tabsd.ui", self)
    label = self.findChild(QLabel, "label") 
    label.setText("label has been changed")

class Screen2(QWidget):
  def __init__(self):
    super().__init__()
    layout = QVBoxLayout()
    self.setLayout(layout)
    tabs = QTabWidget()
    tabs.addTab(self.generalTabUi(), "general")
    tabs.addTab(self.networkTabUi(), "network")
    layout.addWidget(tabs)

  def generalTabUi(self):
    generalTab = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(QCheckBox("option1"))
    layout.addWidget(QCheckBox("option 2"))
    generalTab.setLayout(layout)
    return generalTab

  def networkTabUi(self):
    networkTab = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(QCheckBox("network option1"))
    layout.addWidget(QCheckBox("network option 2"))
    networkTab.setLayout(layout)
    return networkTab

app = QApplication(sys.argv)
screen = Screen2()
#screen = Screen()
screen.show()
sys.exit(app.exec_())
