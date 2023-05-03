# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/datasource_setup_asapo.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ASAPOSetup(object):
    def setupUi(self, ASAPOSetup):
        ASAPOSetup.setObjectName("ASAPOSetup")
        ASAPOSetup.resize(414, 317)
        self.gridLayout = QtWidgets.QGridLayout(ASAPOSetup)
        self.gridLayout.setObjectName("gridLayout")
        self.label_14 = QtWidgets.QLabel(ASAPOSetup)
        self.label_14.setObjectName("label_14")
        self.gridLayout.addWidget(self.label_14, 7, 1, 1, 1)
        self.le_token = QtWidgets.QLineEdit(ASAPOSetup)
        self.le_token.setObjectName("le_token")
        self.gridLayout.addWidget(self.le_token, 5, 1, 1, 1)
        self.le_path = QtWidgets.QLineEdit(ASAPOSetup)
        self.le_path.setObjectName("le_path")
        self.gridLayout.addWidget(self.le_path, 2, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(ASAPOSetup)
        self.label_12.setObjectName("label_12")
        self.gridLayout.addWidget(self.label_12, 6, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(ASAPOSetup)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 4, 0, 1, 1)
        self.chk_filesystem = QtWidgets.QCheckBox(ASAPOSetup)
        self.chk_filesystem.setObjectName("chk_filesystem")
        self.gridLayout.addWidget(self.chk_filesystem, 3, 0, 1, 1)
        self.le_detectors = QtWidgets.QLineEdit(ASAPOSetup)
        self.le_detectors.setObjectName("le_detectors")
        self.gridLayout.addWidget(self.le_detectors, 6, 1, 1, 1)
        self.label_15 = QtWidgets.QLabel(ASAPOSetup)
        self.label_15.setObjectName("label_15")
        self.gridLayout.addWidget(self.label_15, 8, 0, 1, 1)
        self.le_beamtime = QtWidgets.QLineEdit(ASAPOSetup)
        self.le_beamtime.setObjectName("le_beamtime")
        self.gridLayout.addWidget(self.le_beamtime, 4, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(ASAPOSetup)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 5, 0, 1, 1)
        self.sp_max_streams = QtWidgets.QSpinBox(ASAPOSetup)
        self.sp_max_streams.setMaximum(100000)
        self.sp_max_streams.setProperty("value", 100)
        self.sp_max_streams.setObjectName("sp_max_streams")
        self.gridLayout.addWidget(self.sp_max_streams, 8, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(ASAPOSetup)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 2)
        self.label_16 = QtWidgets.QLabel(ASAPOSetup)
        self.label_16.setObjectName("label_16")
        self.gridLayout.addWidget(self.label_16, 9, 0, 1, 1)
        self.le_host = QtWidgets.QLineEdit(ASAPOSetup)
        self.le_host.setObjectName("le_host")
        self.gridLayout.addWidget(self.le_host, 1, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(ASAPOSetup)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 1)
        self.label_13 = QtWidgets.QLabel(ASAPOSetup)
        self.label_13.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_13.setObjectName("label_13")
        self.gridLayout.addWidget(self.label_13, 2, 0, 1, 1)
        self.sp_max_messages = QtWidgets.QSpinBox(ASAPOSetup)
        self.sp_max_messages.setMaximum(100000)
        self.sp_max_messages.setProperty("value", 1000)
        self.sp_max_messages.setObjectName("sp_max_messages")
        self.gridLayout.addWidget(self.sp_max_messages, 9, 1, 1, 1)

        self.retranslateUi(ASAPOSetup)
        QtCore.QMetaObject.connectSlotsByName(ASAPOSetup)

    def retranslateUi(self, ASAPOSetup):
        _translate = QtCore.QCoreApplication.translate
        ASAPOSetup.setWindowTitle(_translate("ASAPOSetup", "Form"))
        self.label_14.setText(_translate("ASAPOSetup", "* separate with semicolomn"))
        self.label_12.setText(_translate("ASAPOSetup", "Detectors:"))
        self.label_7.setText(_translate("ASAPOSetup", "Beamtime:"))
        self.chk_filesystem.setText(_translate("ASAPOSetup", "Has filesystem"))
        self.label_15.setText(_translate("ASAPOSetup", "Max displayed streams:"))
        self.label_8.setText(_translate("ASAPOSetup", "Token:"))
        self.label_4.setText(_translate("ASAPOSetup", "ASAPO consumer settings:"))
        self.label_16.setText(_translate("ASAPOSetup", "Max messages"))
        self.label_5.setText(_translate("ASAPOSetup", "Host:"))
        self.label_13.setText(_translate("ASAPOSetup", "Path:"))
