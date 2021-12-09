# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/datasource_setup_asapo.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ASAPOImageSetup(object):
    def setupUi(self, ASAPOImageSetup):
        ASAPOImageSetup.setObjectName("ASAPOImageSetup")
        ASAPOImageSetup.resize(822, 832)
        self.horizontalLayout = QtWidgets.QHBoxLayout(ASAPOImageSetup)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(ASAPOImageSetup)
        self.frame.setObjectName("frame")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.label_5 = QtWidgets.QLabel(self.frame)
        self.label_5.setObjectName("label_5")
        self.gridLayout_7.addWidget(self.label_5, 1, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.frame)
        self.label_14.setObjectName("label_14")
        self.gridLayout_7.addWidget(self.label_14, 7, 1, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.frame)
        self.label_15.setObjectName("label_15")
        self.gridLayout_7.addWidget(self.label_15, 8, 0, 1, 1)
        self.sp_max_messages = QtWidgets.QSpinBox(self.frame)
        self.sp_max_messages.setMaximum(100000)
        self.sp_max_messages.setProperty("value", 1000)
        self.sp_max_messages.setObjectName("sp_max_messages")
        self.gridLayout_7.addWidget(self.sp_max_messages, 9, 1, 1, 1)
        self.le_host = QtWidgets.QLineEdit(self.frame)
        self.le_host.setObjectName("le_host")
        self.gridLayout_7.addWidget(self.le_host, 1, 1, 1, 1)
        self.label_16 = QtWidgets.QLabel(self.frame)
        self.label_16.setObjectName("label_16")
        self.gridLayout_7.addWidget(self.label_16, 9, 0, 1, 1)
        self.le_token = QtWidgets.QLineEdit(self.frame)
        self.le_token.setObjectName("le_token")
        self.gridLayout_7.addWidget(self.le_token, 5, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.frame)
        self.label_8.setObjectName("label_8")
        self.gridLayout_7.addWidget(self.label_8, 5, 0, 1, 1)
        self.le_detectors = QtWidgets.QLineEdit(self.frame)
        self.le_detectors.setObjectName("le_detectors")
        self.gridLayout_7.addWidget(self.le_detectors, 6, 1, 1, 1)
        self.le_beamtime = QtWidgets.QLineEdit(self.frame)
        self.le_beamtime.setObjectName("le_beamtime")
        self.gridLayout_7.addWidget(self.le_beamtime, 4, 1, 1, 1)
        self.sp_max_streams = QtWidgets.QSpinBox(self.frame)
        self.sp_max_streams.setMaximum(100000)
        self.sp_max_streams.setProperty("value", 100)
        self.sp_max_streams.setObjectName("sp_max_streams")
        self.gridLayout_7.addWidget(self.sp_max_streams, 8, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.frame)
        self.label_12.setObjectName("label_12")
        self.gridLayout_7.addWidget(self.label_12, 6, 0, 1, 1)
        self.chk_filesystem = QtWidgets.QCheckBox(self.frame)
        self.chk_filesystem.setObjectName("chk_filesystem")
        self.gridLayout_7.addWidget(self.chk_filesystem, 3, 0, 1, 1)
        self.le_path = QtWidgets.QLineEdit(self.frame)
        self.le_path.setObjectName("le_path")
        self.gridLayout_7.addWidget(self.le_path, 2, 1, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.frame)
        self.label_13.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_13.setObjectName("label_13")
        self.gridLayout_7.addWidget(self.label_13, 2, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.frame)
        self.label_7.setObjectName("label_7")
        self.gridLayout_7.addWidget(self.label_7, 4, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout_7.addWidget(self.label_4, 0, 0, 1, 2)
        self.verticalLayout.addWidget(self.frame)
        self.line_2 = QtWidgets.QFrame(ASAPOImageSetup)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.label = QtWidgets.QLabel(ASAPOImageSetup)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.rb_mask_off = QtWidgets.QRadioButton(ASAPOImageSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rb_mask_off.setFont(font)
        self.rb_mask_off.setChecked(True)
        self.rb_mask_off.setObjectName("rb_mask_off")
        self.bg_mask_option = QtWidgets.QButtonGroup(ASAPOImageSetup)
        self.bg_mask_option.setObjectName("bg_mask_option")
        self.bg_mask_option.addButton(self.rb_mask_off)
        self.verticalLayout.addWidget(self.rb_mask_off)
        self.rb_mask_on = QtWidgets.QRadioButton(ASAPOImageSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rb_mask_on.setFont(font)
        self.rb_mask_on.setObjectName("rb_mask_on")
        self.bg_mask_option.addButton(self.rb_mask_on)
        self.verticalLayout.addWidget(self.rb_mask_on)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lb_mask_file = QtWidgets.QLabel(ASAPOImageSetup)
        self.lb_mask_file.setMinimumSize(QtCore.QSize(200, 0))
        self.lb_mask_file.setText("")
        self.lb_mask_file.setObjectName("lb_mask_file")
        self.horizontalLayout_2.addWidget(self.lb_mask_file)
        self.but_load_mask = QtWidgets.QPushButton(ASAPOImageSetup)
        self.but_load_mask.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_load_mask.setFont(font)
        self.but_load_mask.setObjectName("but_load_mask")
        self.horizontalLayout_2.addWidget(self.but_load_mask)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.line = QtWidgets.QFrame(ASAPOImageSetup)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.label_9 = QtWidgets.QLabel(ASAPOImageSetup)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.verticalLayout.addWidget(self.label_9)
        self.rb_fill_off = QtWidgets.QRadioButton(ASAPOImageSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rb_fill_off.setFont(font)
        self.rb_fill_off.setChecked(True)
        self.rb_fill_off.setObjectName("rb_fill_off")
        self.bg_fill_option = QtWidgets.QButtonGroup(ASAPOImageSetup)
        self.bg_fill_option.setObjectName("bg_fill_option")
        self.bg_fill_option.addButton(self.rb_fill_off)
        self.verticalLayout.addWidget(self.rb_fill_off)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.rb_fill_on = QtWidgets.QRadioButton(ASAPOImageSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rb_fill_on.setFont(font)
        self.rb_fill_on.setObjectName("rb_fill_on")
        self.bg_fill_option.addButton(self.rb_fill_on)
        self.horizontalLayout_9.addWidget(self.rb_fill_on)
        self.label_10 = QtWidgets.QLabel(ASAPOImageSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_9.addWidget(self.label_10)
        self.sb_fill = QtWidgets.QSpinBox(ASAPOImageSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.sb_fill.setFont(font)
        self.sb_fill.setObjectName("sb_fill")
        self.horizontalLayout_9.addWidget(self.sb_fill)
        self.label_11 = QtWidgets.QLabel(ASAPOImageSetup)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout_9.addWidget(self.label_11)
        self.verticalLayout.addLayout(self.horizontalLayout_9)
        self.line_5 = QtWidgets.QFrame(ASAPOImageSetup)
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.verticalLayout.addWidget(self.line_5)
        self.label_2 = QtWidgets.QLabel(ASAPOImageSetup)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.rb_ff_off = QtWidgets.QRadioButton(ASAPOImageSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rb_ff_off.setFont(font)
        self.rb_ff_off.setChecked(True)
        self.rb_ff_off.setObjectName("rb_ff_off")
        self.bg_ff_option = QtWidgets.QButtonGroup(ASAPOImageSetup)
        self.bg_ff_option.setObjectName("bg_ff_option")
        self.bg_ff_option.addButton(self.rb_ff_off)
        self.verticalLayout.addWidget(self.rb_ff_off)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.rb_ff_on = QtWidgets.QRadioButton(ASAPOImageSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rb_ff_on.setFont(font)
        self.rb_ff_on.setObjectName("rb_ff_on")
        self.bg_ff_option.addButton(self.rb_ff_on)
        self.horizontalLayout_7.addWidget(self.rb_ff_on)
        self.label_3 = QtWidgets.QLabel(ASAPOImageSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_7.addWidget(self.label_3)
        self.dsb_ff_from = QtWidgets.QDoubleSpinBox(ASAPOImageSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.dsb_ff_from.setFont(font)
        self.dsb_ff_from.setObjectName("dsb_ff_from")
        self.horizontalLayout_7.addWidget(self.dsb_ff_from)
        self.label_6 = QtWidgets.QLabel(ASAPOImageSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_7.addWidget(self.label_6)
        self.dsb_ff_to = QtWidgets.QDoubleSpinBox(ASAPOImageSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.dsb_ff_to.setFont(font)
        self.dsb_ff_to.setObjectName("dsb_ff_to")
        self.horizontalLayout_7.addWidget(self.dsb_ff_to)
        self.verticalLayout.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.lb_ff_file = QtWidgets.QLabel(ASAPOImageSetup)
        self.lb_ff_file.setMinimumSize(QtCore.QSize(200, 0))
        self.lb_ff_file.setText("")
        self.lb_ff_file.setObjectName("lb_ff_file")
        self.horizontalLayout_3.addWidget(self.lb_ff_file)
        self.but_load_ff = QtWidgets.QPushButton(ASAPOImageSetup)
        self.but_load_ff.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_load_ff.setFont(font)
        self.but_load_ff.setObjectName("but_load_ff")
        self.horizontalLayout_3.addWidget(self.but_load_ff)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.gv_main = GraphicsView(ASAPOImageSetup)
        self.gv_main.setAutoFillBackground(False)
        self.gv_main.setStyleSheet("")
        self.gv_main.setObjectName("gv_main")
        self.horizontalLayout.addWidget(self.gv_main)

        self.retranslateUi(ASAPOImageSetup)
        QtCore.QMetaObject.connectSlotsByName(ASAPOImageSetup)

    def retranslateUi(self, ASAPOImageSetup):
        _translate = QtCore.QCoreApplication.translate
        ASAPOImageSetup.setWindowTitle(_translate("ASAPOImageSetup", "Form"))
        self.label_5.setText(_translate("ASAPOImageSetup", "Host:"))
        self.label_14.setText(_translate("ASAPOImageSetup", "* separate with semicolomn"))
        self.label_15.setText(_translate("ASAPOImageSetup", "Max displayed streams:"))
        self.label_16.setText(_translate("ASAPOImageSetup", "Max messages"))
        self.label_8.setText(_translate("ASAPOImageSetup", "Token:"))
        self.label_12.setText(_translate("ASAPOImageSetup", "Detectors:"))
        self.chk_filesystem.setText(_translate("ASAPOImageSetup", "Has filesystem"))
        self.label_13.setText(_translate("ASAPOImageSetup", "Path:"))
        self.label_7.setText(_translate("ASAPOImageSetup", "Beamtime:"))
        self.label_4.setText(_translate("ASAPOImageSetup", "ASAPO consumer settings:"))
        self.label.setText(_translate("ASAPOImageSetup", "Mask correction:"))
        self.rb_mask_off.setText(_translate("ASAPOImageSetup", "OFF"))
        self.rb_mask_on.setText(_translate("ASAPOImageSetup", "ON"))
        self.but_load_mask.setText(_translate("ASAPOImageSetup", "Load new"))
        self.label_9.setText(_translate("ASAPOImageSetup", "Mask gaps fill:"))
        self.rb_fill_off.setText(_translate("ASAPOImageSetup", "OFF"))
        self.rb_fill_on.setText(_translate("ASAPOImageSetup", "ON"))
        self.label_10.setText(_translate("ASAPOImageSetup", "radius:"))
        self.label_11.setText(_translate("ASAPOImageSetup", "px."))
        self.label_2.setText(_translate("ASAPOImageSetup", "Flat field correction:"))
        self.rb_ff_off.setText(_translate("ASAPOImageSetup", "OFF"))
        self.rb_ff_on.setText(_translate("ASAPOImageSetup", "ON"))
        self.label_3.setText(_translate("ASAPOImageSetup", "from"))
        self.label_6.setText(_translate("ASAPOImageSetup", "to"))
        self.but_load_ff.setText(_translate("ASAPOImageSetup", "Load new"))

from pyqtgraph import GraphicsView
