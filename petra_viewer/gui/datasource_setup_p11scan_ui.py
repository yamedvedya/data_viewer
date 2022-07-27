# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/datasource_setup_p11scan.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_P11ScanSetup(object):
    def setupUi(self, P11ScanSetup):
        P11ScanSetup.setObjectName("P11ScanSetup")
        P11ScanSetup.resize(379, 79)
        self.gridLayout = QtWidgets.QGridLayout(P11ScanSetup)
        self.gridLayout.setObjectName("gridLayout")
        self.gb_door = QtWidgets.QFrame(P11ScanSetup)
        self.gb_door.setObjectName("gb_door")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gb_door)
        self.gridLayout_2.setContentsMargins(-1, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.lb_door_address = QtWidgets.QLabel(self.gb_door)
        self.lb_door_address.setObjectName("lb_door_address")
        self.gridLayout_2.addWidget(self.lb_door_address, 0, 0, 1, 1)
        self.sp_max_frames_in_dataset = QtWidgets.QSpinBox(self.gb_door)
        self.sp_max_frames_in_dataset.setMinimum(1)
        self.sp_max_frames_in_dataset.setMaximum(100000)
        self.sp_max_frames_in_dataset.setProperty("value", 1000)
        self.sp_max_frames_in_dataset.setObjectName("sp_max_frames_in_dataset")
        self.gridLayout_2.addWidget(self.sp_max_frames_in_dataset, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.gb_door, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(P11ScanSetup)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)

        self.retranslateUi(P11ScanSetup)
        QtCore.QMetaObject.connectSlotsByName(P11ScanSetup)

    def retranslateUi(self, P11ScanSetup):
        _translate = QtCore.QCoreApplication.translate
        P11ScanSetup.setWindowTitle(_translate("P11ScanSetup", "Form"))
        self.lb_door_address.setText(_translate("P11ScanSetup", "Max frames in dataset"))
        self.label_3.setText(_translate("P11ScanSetup", "Max frames in dataset"))

