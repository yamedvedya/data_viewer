# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/base_2d_setup.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Base2DDetectorSetup(object):
    def setupUi(self, Base2DDetectorSetup):
        Base2DDetectorSetup.setObjectName("Base2DDetectorSetup")
        Base2DDetectorSetup.resize(822, 832)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Base2DDetectorSetup)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.v_layout = QtWidgets.QVBoxLayout()
        self.v_layout.setObjectName("v_layout")
        self.line_2 = QtWidgets.QFrame(Base2DDetectorSetup)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.v_layout.addWidget(self.line_2)
        self.w_setup = QtWidgets.QWidget(Base2DDetectorSetup)
        self.w_setup.setObjectName("w_setup")
        self.v_layout.addWidget(self.w_setup)
        self.label = QtWidgets.QLabel(Base2DDetectorSetup)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.v_layout.addWidget(self.label)
        self.rb_mask_off = QtWidgets.QRadioButton(Base2DDetectorSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rb_mask_off.setFont(font)
        self.rb_mask_off.setChecked(True)
        self.rb_mask_off.setObjectName("rb_mask_off")
        self.bg_mask_option = QtWidgets.QButtonGroup(Base2DDetectorSetup)
        self.bg_mask_option.setObjectName("bg_mask_option")
        self.bg_mask_option.addButton(self.rb_mask_off)
        self.v_layout.addWidget(self.rb_mask_off)
        self.rb_mask_on = QtWidgets.QRadioButton(Base2DDetectorSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rb_mask_on.setFont(font)
        self.rb_mask_on.setObjectName("rb_mask_on")
        self.bg_mask_option.addButton(self.rb_mask_on)
        self.v_layout.addWidget(self.rb_mask_on)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lb_mask_file = QtWidgets.QLabel(Base2DDetectorSetup)
        self.lb_mask_file.setMinimumSize(QtCore.QSize(200, 0))
        self.lb_mask_file.setText("")
        self.lb_mask_file.setObjectName("lb_mask_file")
        self.horizontalLayout_2.addWidget(self.lb_mask_file)
        self.but_load_mask = QtWidgets.QPushButton(Base2DDetectorSetup)
        self.but_load_mask.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_load_mask.setFont(font)
        self.but_load_mask.setObjectName("but_load_mask")
        self.horizontalLayout_2.addWidget(self.but_load_mask)
        self.v_layout.addLayout(self.horizontalLayout_2)
        self.line = QtWidgets.QFrame(Base2DDetectorSetup)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.v_layout.addWidget(self.line)
        self.label_9 = QtWidgets.QLabel(Base2DDetectorSetup)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.v_layout.addWidget(self.label_9)
        self.rb_fill_off = QtWidgets.QRadioButton(Base2DDetectorSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rb_fill_off.setFont(font)
        self.rb_fill_off.setChecked(True)
        self.rb_fill_off.setObjectName("rb_fill_off")
        self.bg_fill_option = QtWidgets.QButtonGroup(Base2DDetectorSetup)
        self.bg_fill_option.setObjectName("bg_fill_option")
        self.bg_fill_option.addButton(self.rb_fill_off)
        self.v_layout.addWidget(self.rb_fill_off)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.rb_fill_on = QtWidgets.QRadioButton(Base2DDetectorSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rb_fill_on.setFont(font)
        self.rb_fill_on.setObjectName("rb_fill_on")
        self.bg_fill_option.addButton(self.rb_fill_on)
        self.horizontalLayout_9.addWidget(self.rb_fill_on)
        self.label_10 = QtWidgets.QLabel(Base2DDetectorSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_9.addWidget(self.label_10)
        self.sb_fill = QtWidgets.QSpinBox(Base2DDetectorSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.sb_fill.setFont(font)
        self.sb_fill.setObjectName("sb_fill")
        self.horizontalLayout_9.addWidget(self.sb_fill)
        self.label_11 = QtWidgets.QLabel(Base2DDetectorSetup)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout_9.addWidget(self.label_11)
        self.v_layout.addLayout(self.horizontalLayout_9)
        self.line_5 = QtWidgets.QFrame(Base2DDetectorSetup)
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.v_layout.addWidget(self.line_5)
        self.label_2 = QtWidgets.QLabel(Base2DDetectorSetup)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.v_layout.addWidget(self.label_2)
        self.rb_ff_off = QtWidgets.QRadioButton(Base2DDetectorSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rb_ff_off.setFont(font)
        self.rb_ff_off.setChecked(True)
        self.rb_ff_off.setObjectName("rb_ff_off")
        self.bg_ff_option = QtWidgets.QButtonGroup(Base2DDetectorSetup)
        self.bg_ff_option.setObjectName("bg_ff_option")
        self.bg_ff_option.addButton(self.rb_ff_off)
        self.v_layout.addWidget(self.rb_ff_off)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.rb_ff_on = QtWidgets.QRadioButton(Base2DDetectorSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rb_ff_on.setFont(font)
        self.rb_ff_on.setObjectName("rb_ff_on")
        self.bg_ff_option.addButton(self.rb_ff_on)
        self.horizontalLayout_7.addWidget(self.rb_ff_on)
        self.label_3 = QtWidgets.QLabel(Base2DDetectorSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_7.addWidget(self.label_3)
        self.dsb_ff_from = QtWidgets.QDoubleSpinBox(Base2DDetectorSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.dsb_ff_from.setFont(font)
        self.dsb_ff_from.setObjectName("dsb_ff_from")
        self.horizontalLayout_7.addWidget(self.dsb_ff_from)
        self.label_6 = QtWidgets.QLabel(Base2DDetectorSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_7.addWidget(self.label_6)
        self.dsb_ff_to = QtWidgets.QDoubleSpinBox(Base2DDetectorSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.dsb_ff_to.setFont(font)
        self.dsb_ff_to.setObjectName("dsb_ff_to")
        self.horizontalLayout_7.addWidget(self.dsb_ff_to)
        self.v_layout.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.lb_ff_file = QtWidgets.QLabel(Base2DDetectorSetup)
        self.lb_ff_file.setMinimumSize(QtCore.QSize(200, 0))
        self.lb_ff_file.setText("")
        self.lb_ff_file.setObjectName("lb_ff_file")
        self.horizontalLayout_3.addWidget(self.lb_ff_file)
        self.but_load_ff = QtWidgets.QPushButton(Base2DDetectorSetup)
        self.but_load_ff.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_load_ff.setFont(font)
        self.but_load_ff.setObjectName("but_load_ff")
        self.horizontalLayout_3.addWidget(self.but_load_ff)
        self.v_layout.addLayout(self.horizontalLayout_3)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.v_layout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.v_layout)
        self.gv_main = GraphicsView(Base2DDetectorSetup)
        self.gv_main.setAutoFillBackground(False)
        self.gv_main.setStyleSheet("")
        self.gv_main.setObjectName("gv_main")
        self.horizontalLayout.addWidget(self.gv_main)

        self.retranslateUi(Base2DDetectorSetup)
        QtCore.QMetaObject.connectSlotsByName(Base2DDetectorSetup)

    def retranslateUi(self, Base2DDetectorSetup):
        _translate = QtCore.QCoreApplication.translate
        Base2DDetectorSetup.setWindowTitle(_translate("Base2DDetectorSetup", "Form"))
        self.label.setText(_translate("Base2DDetectorSetup", "Mask correction:"))
        self.rb_mask_off.setText(_translate("Base2DDetectorSetup", "OFF"))
        self.rb_mask_on.setText(_translate("Base2DDetectorSetup", "ON"))
        self.but_load_mask.setText(_translate("Base2DDetectorSetup", "Load new"))
        self.label_9.setText(_translate("Base2DDetectorSetup", "Mask gaps fill:"))
        self.rb_fill_off.setText(_translate("Base2DDetectorSetup", "OFF"))
        self.rb_fill_on.setText(_translate("Base2DDetectorSetup", "ON"))
        self.label_10.setText(_translate("Base2DDetectorSetup", "radius:"))
        self.label_11.setText(_translate("Base2DDetectorSetup", "px."))
        self.label_2.setText(_translate("Base2DDetectorSetup", "Flat field correction:"))
        self.rb_ff_off.setText(_translate("Base2DDetectorSetup", "OFF"))
        self.rb_ff_on.setText(_translate("Base2DDetectorSetup", "ON"))
        self.label_3.setText(_translate("Base2DDetectorSetup", "from"))
        self.label_6.setText(_translate("Base2DDetectorSetup", "to"))
        self.but_load_ff.setText(_translate("Base2DDetectorSetup", "Load new"))
from pyqtgraph import GraphicsView
