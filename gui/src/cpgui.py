from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)
import matplotlib
matplotlib.use('Qt5Agg')
import random
import os
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

def voltageTodB(signal,ref):
    return 20*np.log10(np.abs(signal/ref))

class MainWindow(QDialog):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.originalPalette = QApplication.palette()

        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())

        QApplication.setStyle('Fusion')

        self.createLeftGroupBox()
        self.createRightGroupBox()

        topLayout = QHBoxLayout()
        topLayout.addStretch(1)

        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.leftGroupBox, 1, 0)
        mainLayout.addWidget(self.rightGroupBox, 1, 1)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("Pmu Plotter")

    def createLeftGroupBox(self):
        self.leftGroupBox = QGroupBox("Controls")

        lineLabel = QLabel()
        lineLabel.setText("Enter the filename:")

        self.lineEdit = QLineEdit('')
        
        #Pushbutton for filename read
        drawPlotPushButton = QPushButton("Draw the plot")
        drawPlotPushButton.setDefault(True)
        drawPlotPushButton.clicked.connect(self.drawPlot)

        #FFT spectrum of the signal
        self.frequencySpectrumCanvas = MplCanvas(self, width=6, height=4, dpi=100)
        self.frequencySpectrumCanvas.axes.set_title("Frequency domain signal")
        self.frequencySpectrumCanvas.axes.set_ylabel("Amplitude [dBFs]")
        self.frequencySpectrumCanvas.axes.set_xlabel("Frequency[Hz]")
        toolbar = NavigationToolbar(self.frequencySpectrumCanvas, self)
        
        layout = QGridLayout()
        layout.addWidget(lineLabel,0,0,1,1)
        layout.addWidget(self.lineEdit,0,1,1,1)
        layout.addWidget(drawPlotPushButton,1,0,1,2)
        layout.addWidget(toolbar,2,0,1,2)
        layout.addWidget(self.frequencySpectrumCanvas,3,0,1,2)
        self.leftGroupBox.setLayout(layout)

    def createRightGroupBox(self):
        self.rightGroupBox = QGroupBox("Time domain signal")

        self.timeDomainCanvas = MplCanvas(self, width=6, height=4, dpi=100)
        self.timeDomainCanvas.axes.set_title("Time Domain Signal")
        self.timeDomainCanvas.axes.set_ylabel("Vpp[V]")
        self.timeDomainCanvas.axes.set_xlabel("Sample Num") 
        toolbar = NavigationToolbar(self.timeDomainCanvas, self)

        layout = QGridLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.timeDomainCanvas)
        self.rightGroupBox.setLayout(layout)


    def updatePlot(self):
        self.ydata = self.ydata[1:] + [random.randint(0,10)]
        self.timeDomainCanvas.axes.cla()
        self.timeDomainCanvas.axes.plot(self.xdata, self.ydata, 'r')
        self.timeDomainCanvas.draw()

    def drawPlot(self):
        nData = 50
        fileName = "../data/" + str(self.lineEdit.text())
        print(fileName)
        dspContainer = calculateAlgos(fileName,4096,8000)
        self.xdata = dspContainer.buffer.data
        self.timeDomainCanvas.axes.plot(self.xdata, 'r')
        self.timeDomainCanvas.draw()
        self.frequencySpectrumCanvas.axes.plot(dspContainer.dF, dspContainer.nfftIndb)
        self.frequencySpectrumCanvas.draw()


class dataBuffer():
    def __init__(self,fName,N):
        self.data_filename = fName
        self.num_of_samples = N
        self.data = np.zeros(N)
        self.readData()

    def twosCompl(self,val):
        temp = np.uint32(val | 0xff000000)
        if(temp & (1<<23)):
            outval = -(~temp + 1)
            return outval
        else:
            return val

    def readData(self):
        size = os.path.getsize(self.data_filename)
        data = np.fromfile(self.data_filename,dtype=np.int32).reshape((size//28,7))
        data_converted = np.zeros(data.shape,dtype=np.float)
    
        for row in range(data_converted.shape[0]):
            for col in range(data_converted.shape[1]):
                data_converted[row][col] = self.twosCompl(data[row][col])*1.2/(2**23)
        self.data = data_converted[0:self.num_of_samples,3]

class calculateAlgos():
    def __init__(self,fName,N,fs):
        self.fs = fs
        self.buffer = dataBuffer(fName,N)
        self.calculateFFt()
        self.calculatePhase()

    def convertTodB(self,val1,val2):
        return 20*np.log10(np.abs(val1))

    def calculateFFt(self):
        self.nfft = np.abs(np.fft.fftshift(np.fft.fft(self.buffer.data))/len(self.buffer.data))
        self.nfftIndb = np.zeros(len(self.nfft))
        max = np.max(self.nfft)
        for i in range(len(self.nfft)):
            self.nfftIndb[i] = voltageTodB(self.nfft[i], max)
        self.dF = np.fft.fftshift(np.fft.fftfreq(n=len(self.nfft),d=1/self.fs))
    
    def calculatePhase(self):
        threshold = np.max(self.nfft)/2
        tempNfft = self.nfft
        tempNfft[abs(tempNfft) < threshold] = 0
        self.phase = np.angle(tempNfft)
        

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height),dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas,self).__init__(fig)



if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    gallery = MainWindow()
    gallery.show()
    sys.exit(app.exec_()) 