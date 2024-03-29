# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/datasource_setup_p23scan.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_P23ScanSetup(object):
    def setupUi(self, P23ScanSetup):
        P23ScanSetup.setObjectName("P23ScanSetup")
        P23ScanSetup.resize(376, 272)
        self.gridLayout = QtWidgets.QGridLayout(P23ScanSetup)
        self.gridLayout.setObjectName("gridLayout")
        self.gb_door = QtWidgets.QFrame(P23ScanSetup)
        self.gb_door.setObjectName("gb_door")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gb_door)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.lb_door_address = QtWidgets.QLabel(self.gb_door)
        self.lb_door_address.setObjectName("lb_door_address")
        self.gridLayout_2.addWidget(self.lb_door_address, 0, 0, 1, 1)
        self.le_door_address = QtWidgets.QLineEdit(self.gb_door)
        self.le_door_address.setObjectName("le_door_address")
        self.gridLayout_2.addWidget(self.le_door_address, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.gb_door, 1, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.rb_inten_on = QtWidgets.QRadioButton(P23ScanSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rb_inten_on.setFont(font)
        self.rb_inten_on.setObjectName("rb_inten_on")
        self.bg_intensity = QtWidgets.QButtonGroup(P23ScanSetup)
        self.bg_intensity.setObjectName("bg_intensity")
        self.bg_intensity.addButton(self.rb_inten_on)
        self.horizontalLayout_3.addWidget(self.rb_inten_on)
        self.cmb_intensity = QtWidgets.QComboBox(P23ScanSetup)
        self.cmb_intensity.setEnabled(False)
        self.cmb_intensity.setObjectName("cmb_intensity")
        self.horizontalLayout_3.addWidget(self.cmb_intensity)
        self.gridLayout.addLayout(self.horizontalLayout_3, 4, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(P23ScanSetup)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 5, 0, 1, 1)
        self.rb_atten_off = QtWidgets.QRadioButton(P23ScanSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rb_atten_off.setFont(font)
        self.rb_atten_off.setChecked(True)
        self.rb_atten_off.setObjectName("rb_atten_off")
        self.bg_attenuator = QtWidgets.QButtonGroup(P23ScanSetup)
        self.bg_attenuator.setObjectName("bg_attenuator")
        self.bg_attenuator.addButton(self.rb_atten_off)
        self.gridLayout.addWidget(self.rb_atten_off, 7, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(P23ScanSetup)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.rb_atten_on = QtWidgets.QRadioButton(P23ScanSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rb_atten_on.setFont(font)
        self.rb_atten_on.setObjectName("rb_atten_on")
        self.bg_attenuator.addButton(self.rb_atten_on)
        self.horizontalLayout_6.addWidget(self.rb_atten_on)
        self.cmb_attenuator = QtWidgets.QComboBox(P23ScanSetup)
        self.cmb_attenuator.setEnabled(False)
        self.cmb_attenuator.setObjectName("cmb_attenuator")
        self.horizontalLayout_6.addWidget(self.cmb_attenuator)
        self.gridLayout.addLayout(self.horizontalLayout_6, 8, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(P23ScanSetup)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 6, 0, 1, 1)
        self.rb_inten_off = QtWidgets.QRadioButton(P23ScanSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rb_inten_off.setFont(font)
        self.rb_inten_off.setChecked(True)
        self.rb_inten_off.setObjectName("rb_inten_off")
        self.bg_intensity.addButton(self.rb_inten_off)
        self.gridLayout.addWidget(self.rb_inten_off, 3, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(P23ScanSetup)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)

        self.retranslateUi(P23ScanSetup)
        QtCore.QMetaObject.connectSlotsByName(P23ScanSetup)

    def retranslateUi(self, P23ScanSetup):
        _translate = QtCore.QCoreApplication.translate
        P23ScanSetup.setWindowTitle(_translate("P23ScanSetup", "Form"))
        self.lb_door_address.setText(_translate("P23ScanSetup", "Address:"))
        self.rb_inten_on.setText(_translate("P23ScanSetup", "ON"))
        self.rb_atten_off.setText(_translate("P23ScanSetup", "OFF"))
        self.label_2.setText(_translate("P23ScanSetup", "Intensity correction:"))
        self.rb_atten_on.setText(_translate("P23ScanSetup", "ON"))
        self.label_4.setText(_translate("P23ScanSetup", "Attenuator correction:"))
        self.rb_inten_off.setText(_translate("P23ScanSetup", "OFF"))
        self.label_3.setText(_translate("P23ScanSetup", "Door monitor"))
