# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cpmonitor.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(772, 544)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.control_tab = QtWidgets.QWidget()
        self.control_tab.setObjectName("control_tab")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.control_tab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.control_groupbox = QtWidgets.QGroupBox(self.control_tab)
        self.control_groupbox.setObjectName("control_groupbox")
        self.horizontalLayout.addWidget(self.control_groupbox)
        self.tabWidget.addTab(self.control_tab, "")
        self.plot_tab = QtWidgets.QWidget()
        self.plot_tab.setObjectName("plot_tab")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.plot_tab)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.plot_layout = QtWidgets.QHBoxLayout()
        self.plot_layout.setObjectName("plot_layout")
        self.horizontalLayout_2.addLayout(self.plot_layout)
        self.tabWidget.addTab(self.plot_tab, "")
        self.verticalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 772, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.control_groupbox.setTitle(_translate("MainWindow", "Controls"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.control_tab), _translate("MainWindow", "Tab 1"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.plot_tab), _translate("MainWindow", "Tab 2"))
