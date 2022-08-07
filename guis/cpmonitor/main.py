import tesla, re, os, sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QApplication, QWidget, \
                            QLabel, QMainWindow, QTabWidget, QFrame, QGridLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib import pyplot as plt
import numpy as np

class AppWindow(QMainWindow):
  def __init__(self) -> None:
    super().__init__()
    loadUi("guis/cpmonitor/cpmonitor.ui", self)
    self.plot_grid = self.findChild(QGridLayout, "plot_layout")

  def draw_plots(self):
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

        self.plot_grid.addLayout(frameContainer, row, col)

if __name__ == '__main__':
  app = QApplication(sys.argv)
  window = AppWindow()
  window.show()
  sys.exit(app.exec_())