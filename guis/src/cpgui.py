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
        self.lph = logparser.LogParserHandler()
        self.inputType = "file"
        self.lph.update_input_source(self.inputType,"gui\src\example_msg")
        self.lph.update_write_filename("asd")
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
        self.ioTimer.start(100)

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
        self.parserInputSelection = ["file","uart"]

        self.typeButtonDebug = QRadioButton("Debug")
        self.typeButtonInfo = QRadioButton("Info")
        self.typeButtonWarning = QRadioButton("Warning")
        self.typeButtonError = QRadioButton("Error")
        self.typeButtonDebug.setChecked(True)
        self.typeButtonInfo.setChecked(True)
        self.typeButtonWarning.setChecked(True)
        self.typeButtonError.setChecked(True)
        
        
        self.moduleSelector = QComboBox()
        self.moduleSelector.addItems(self.parsedModules)
        self.moduleSelectorLabel = QLabel("Modules:") 
        self.moduleSelectorLabel.setBuddy(self.moduleSelector)
        self.functionSelector = QComboBox()
        self.functionSelector.addItems(self.parsedFunctions)
        self.functionSelectorLabel = QLabel("Functions:") 
        self.functionSelectorLabel.setBuddy(self.functionSelector)
        
        self.parserInputSelector = QComboBox()
        self.parserInputSelector.addItems(self.parserInputSelection)  
        self.parserInputSelectorLabel = QLabel("Input")
        self.parserInputSelectorLabel.setBuddy(self.parserInputSelector)  
        
        self.saveMessagesToFileButton = QPushButton("Save to file")
        self.saveMessagesToFileButton.clicked.connect(self.saveParsedMessages)

        layout = QGridLayout()
        layout.addWidget(self.typeButtonDebug,0,0,1,1)
        layout.addWidget(self.typeButtonInfo,1,0,1,1)
        layout.addWidget(self.typeButtonWarning,2,0,1,1)
        layout.addWidget(self.typeButtonError,3,0,1,1)
        layout.addWidget(self.parserInputSelector,0,2,1,1)
        layout.addWidget(self.parserInputSelectorLabel,0,1,1,1)
        layout.addWidget(self.moduleSelector,1,2,1,1)
        layout.addWidget(self.moduleSelectorLabel,1,1,1,1)
        layout.addWidget(self.functionSelector,2,2,1,1)
        layout.addWidget(self.functionSelectorLabel,2,1,1,1)
        layout.addWidget(self.saveMessagesToFileButton,3,1,1,1)
        layout.addWidget(self.textEdit,4,0,1,3)

        self.leftGroupBox.setLayout(layout)

    def createRightGroupBox(self):
        self.rightGroupBox = QGroupBox("Time domain signal")

    def updateParser(self): 
        """At this state the IO access is implemented here.
           In the future it has to be multithreaded: 1 thread for the GUI
           1 thread for the IO
        """
        
        if self.inputType != self.parserInputSelector.currentText():
            self.inputType = self.parserInputSelector.currentText()
            self.lph.update_input_source(self.inputType,"gui\src\example_msg")
        self.lph.update()

        functions = self.lph.get_functions()
        for f in functions:
            if f not in self.parsedFunctions:
                self.parsedFunctions.append(f)
    
        for m in self.lph.get_modules():
            if m not in self.parsedModules:
                self.parsedModules.append(m)

        self.checkMessageTypeButtons()
        self.checkPrintMessageSelectors()
        self.printParsedMessages()

    def saveParsedMessages(self):
        self.lph.save_to_file()
        
    def checkMessageTypeButtons(self):
        if self.typeButtonError.isChecked():
            if "ERR" not in self.printedMessageTypes:
                self.printedMessageTypes.append("ERR")
        else:
            if "ERR" in self.printedMessageTypes:
                self.printedMessageTypes.remove("ERR")
        if self.typeButtonWarning.isChecked():
            if "WRN" not in self.printedMessageTypes:
                self.printedMessageTypes.append("WRN")
        else:
            if "WRN" in self.printedMessageTypes:
                self.printedMessageTypes.remove("WRN")
        if self.typeButtonInfo.isChecked():
            if "INF" not in self.printedMessageTypes:
                self.printedMessageTypes.append("INF")
        else:
            if "INF" in self.printedMessageTypes:
                self.printedMessageTypes.remove("INF")
        if self.typeButtonDebug.isChecked():
            if "DBG" not in self.printedMessageTypes:
                self.printedMessageTypes.append("DBG")
        else:
            if "DBG" in self.printedMessageTypes:
                self.printedMessageTypes.remove("DBG")
        
    def checkPrintMessageSelectors(self):
        # fill printed message selection then update selectable items
        self.printedFunctionMessages = self.functionSelector.currentText()
        self.printedModuleMessages = self.moduleSelector.currentText()
        for m in self.parsedModules:
            if self.moduleSelector.findText(m) == -1:
                self.moduleSelector.addItem(m)
        for f in self.parsedFunctions:
            if self.functionSelector.findText(f) == -1:
                self.functionSelector.addItem(f)
      
    def printParsedMessages(self):
        """print the selected parsed messages
        """
        # msg format ['INF', 'main', 'teslactrl', '2021-05-02_05:23', 'Logging started']
        # check selectors ->
        self.textEdit.clear() 
        for msg in self.lph.get_messages():
            if (msg[0] in self.printedMessageTypes) \
                and ((self.printedFunctionMessages == "all") or (msg[1] in self.printedFunctionMessages)) \
                and ((self.printedModuleMessages == "all") or (msg[2] in self.printedModuleMessages)):
                text = " ".join(msg)
                self.textEdit.appendPlainText(text)

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    gallery = MainWindow()
    gallery.show()
    sys.exit(app.exec_()) 