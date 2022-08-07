#!/usr/bin/python3
import sys
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QVBoxLayout, QScrollArea, QGridLayout, QFrame, QDialog, QGroupBox, QWidget, QApplication
from PyQt5.QtGui import QDrag

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib import pyplot as plt
import numpy as np

class MyApp(QWidget):
  def __init__(self) :
    super().__init__()
    self.setWindowTitle("graphs")
    self.setMinimumSize(600, 400)
    self.setAcceptDrops(True)

    self.scrollArea = QScrollArea()
    self.scrollArea.setWidgetResizable(True)

    self.layout = QVBoxLayout()
    self.setLayout(self.layout)

    # graph window container
    self.graphContainer = QWidget()
    self.gridLayout = QGridLayout(self.graphContainer)

    self.scrollArea.setWidget(self.graphContainer)
    self.layout.addWidget(self.scrollArea)

    self.create_graphs()

  def event_filer(self, obj, event):
    if event.type() == QEvent.MouseButtonPress:
      pass
    elif event.type() == QEvent.MouseMove:
      pass
    return super().eventFiler(obj, event)

  def mouse_press_event(self, event):
    if event.button() == Qt.LeftButton:
      coord = event.WindowPos().toPoint() # QPoint object
      self.target_index = self.get_window_index(coord)
    else:
      self.target_index = None

  def get_window_index(self, pos) -> int:
    for i in range(self.gridLayout.count()):
      if self.gridLayout.itemAt(i).geometry().contains(pos):
        return i

  def create_graphs(self):
    index = 0

    for col in range(3):
      for row in range(3):
        frame = QFrame()
        frame.setStyleSheet('background-color: white;')
        frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        frameContainer = QVBoxLayout()

        data = np.linspace(0,10,10)
        index += 1

        fig = plt.figure()
        canvas = FigureCanvasQTAgg(fig)
        ax = fig.add_subplot()
        ax.plot(data, '-')
        canvas.draw()

        canvas.installEventFilter(self)

        box = QVBoxLayout()
        box.addWidget(frame)

        frameContainer.addWidget(canvas)

        self.gridLayout.addLayout(frameContainer, row, col)
if __name__ == '__main__':
  app = QApplication(sys.argv)
  myApp = MyApp()
  myApp.show()

  try:
    sys.exit(app.exec_())
  except SystemExit:
    print("exited")
