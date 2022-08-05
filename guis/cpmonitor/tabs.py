import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QLabel
from PyQt5.QtGui import QPixmap

class Screen(QDialog):
  def __init__(self):
    super(Screen, self).__init__()
    loadUi("tabsd.ui", self)
    label = self.findChild(QLabel, "label") 
    label.setText("label has been changed")

app = QApplication(sys.argv)
screen = Screen()
screen.show()
sys.exit(app.exec_())
