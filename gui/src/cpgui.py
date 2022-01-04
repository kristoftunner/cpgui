from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QPlainTextEdit)

import random 
import os
import sys
import logparser
import time
import serial

log_messages = ["[INF] main teslactrl 2021-05-02_05:23 Logging started",
                "[WRN] main gsm 2021-05-06_07:23 Logging started",
                "[ERR] gsm_controlProcess gsm 2022-06-04_05:23 Logging started",
                "[INF] main gsm 2023-10-04_09:13 Logging started",
                "[ERR] main teslactrl 2021-05-04_05:23 Logging started"]

class MainWindow(QDialog):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.initUi()

    def initUi(self):    
        self.lp = logparser.LogParser()
        self.messageIndex = 0
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
        self.setWindowTitle("CatchPenny Debug Tool")

        # timer for updating the parser
        self.ioTimer = QTimer()
        self.ioTimer.timeout.connect(self.updateParser)
        self.ioTimer.start(1000)

        self.ser = serial.Serial()

    def createLeftGroupBox(self):
        self.leftGroupBox = QGroupBox("Log parsing")

        self.textEdit = QPlainTextEdit()
        self.textEdit.setReadOnly(True)

        self.parsedFunctions = ["all"]
        self.parsedModules = ["all"]
        self.printedMessageTypes = ["INF","WRN","DBG","ERR"]
        self.printedFunctionMessages = []
        self.printedModuleMessages = []

        radioButton1 = QRadioButton("Debug")
        radioButton2 = QRadioButton("Info")
        radioButton3 = QRadioButton("Warning")
        radioButton4 = QRadioButton("Error")
        radioButton1.setChecked(True)
        radioButton2.setChecked(True)
        radioButton3.setChecked(True)
        radioButton4.setChecked(True)
        
        
        moduleSelector = QComboBox()
        moduleSelector.addItems(self.parsedModules)
        moduleSelectorLabel = QLabel("Modules:") 
        moduleSelectorLabel.setBuddy(moduleSelector)
        functionSelector = QComboBox()
        functionSelector.addItems(self.parsedFunctions)
        functionSelectorLabel = QLabel("Functions:") 
        functionSelectorLabel.setBuddy(moduleSelector)
        

        layout = QGridLayout()
        layout.addWidget(radioButton1,0,0,1,1)
        layout.addWidget(radioButton2,1,0,1,1)
        layout.addWidget(radioButton3,2,0,1,1)
        layout.addWidget(radioButton4,3,0,1,1)
        layout.addWidget(moduleSelector,0,2,1,1)
        layout.addWidget(moduleSelectorLabel,0,1,1,1)
        layout.addWidget(functionSelector,1,2,1,1)
        layout.addWidget(functionSelectorLabel,1,1,1,1)
        layout.addWidget(self.textEdit,4,0,1,3)

        self.leftGroupBox.setLayout(layout)

    def createRightGroupBox(self):
        self.rightGroupBox = QGroupBox("Time domain signal")

    def updateParser(self): 
        """At this state the IO access is implemented here.
           In the future it has to be multithreaded: 1 thread for the GUI
           1 thread for the IO
        """
        if self.messageIndex < len(log_messages):
            self.lp.update(log_messages[self.messageIndex])
            self.messageIndex += 1

            functions = self.lp.functions
            for f in functions:
                if f not in self.parsedFunctions:
                    self.parsedFunctions.append(f)
        
            for m in self.lp.modules:
                if m not in self.parsedModules:
                    self.parsedModules.append(m)

            for m in self.lp.messages:
                text = ' '.join(m)
                self.textEdit.appendPlainText(text)
    
    def checkMessageTypeButtons(self):

        pass


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    gallery = MainWindow()
    gallery.show()
    sys.exit(app.exec_()) 