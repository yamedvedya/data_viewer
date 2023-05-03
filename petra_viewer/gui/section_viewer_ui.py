# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/section_viewer.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SectionView(object):
    def setupUi(self, SectionView):
        SectionView.setObjectName("SectionView")
        SectionView.resize(1206, 492)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(SectionView)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtWidgets.QSplitter(SectionView)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.v_layout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.v_layout.setContentsMargins(0, 6, 0, 0)
        self.v_layout.setSpacing(0)
        self.v_layout.setObjectName("v_layout")
        self.widget = QtWidgets.QWidget(self.layoutWidget)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout.setSpacing(3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cmd_delete_me = QtWidgets.QPushButton(self.widget)
        self.cmd_delete_me.setObjectName("cmd_delete_me")
        self.horizontalLayout.addWidget(self.cmd_delete_me)
        self.v_layout.addWidget(self.widget)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_7.addWidget(self.label)
        self.cb_section_axis = QtWidgets.QComboBox(self.layoutWidget)
        self.cb_section_axis.setObjectName("cb_section_axis")
        self.horizontalLayout_7.addWidget(self.cb_section_axis)
        self.v_layout.addLayout(self.horizontalLayout_7)
        self.range_selectors = QtWidgets.QWidget(self.layoutWidget)
        self.range_selectors.setMinimumSize(QtCore.QSize(330, 0))
        self.range_selectors.setObjectName("range_selectors")
        self.v_layout.addWidget(self.range_selectors)
        self.v_layout.setStretch(2, 1)
        self.layoutWidget1 = QtWidgets.QWidget(self.splitter)
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.v_layout_2 = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.v_layout_2.setContentsMargins(0, 0, 0, 0)
        self.v_layout_2.setObjectName("v_layout_2")
        self.gv_main = GraphicsView(self.layoutWidget1)
        self.gv_main.setAutoFillBackground(False)
        self.gv_main.setStyleSheet("")
        self.gv_main.setObjectName("gv_main")
        self.v_layout_2.addWidget(self.gv_main)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_10 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_8.addWidget(self.label_10)
        self.rb_range_all = QtWidgets.QRadioButton(self.layoutWidget1)
        self.rb_range_all.setChecked(True)
        self.rb_range_all.setObjectName("rb_range_all")
        self.bg_cut_range = QtWidgets.QButtonGroup(SectionView)
        self.bg_cut_range.setObjectName("bg_cut_range")
        self.bg_cut_range.addButton(self.rb_range_all)
        self.horizontalLayout_8.addWidget(self.rb_range_all)
        self.rb_range_cut = QtWidgets.QRadioButton(self.layoutWidget1)
        self.rb_range_cut.setObjectName("rb_range_cut")
        self.bg_cut_range.addButton(self.rb_range_cut)
        self.horizontalLayout_8.addWidget(self.rb_range_cut)
        self.label_8 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_8.addWidget(self.label_8)
        self.dsp_cut_from = QtWidgets.QDoubleSpinBox(self.layoutWidget1)
        self.dsp_cut_from.setEnabled(False)
        self.dsp_cut_from.setDecimals(5)
        self.dsp_cut_from.setMinimum(-10000.0)
        self.dsp_cut_from.setMaximum(10000.0)
        self.dsp_cut_from.setSingleStep(0.01)
        self.dsp_cut_from.setObjectName("dsp_cut_from")
        self.horizontalLayout_8.addWidget(self.dsp_cut_from)
        self.label_9 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_8.addWidget(self.label_9)
        self.dsp_cut_to = QtWidgets.QDoubleSpinBox(self.layoutWidget1)
        self.dsp_cut_to.setEnabled(False)
        self.dsp_cut_to.setDecimals(5)
        self.dsp_cut_to.setMinimum(-10000.0)
        self.dsp_cut_to.setMaximum(10000.0)
        self.dsp_cut_to.setSingleStep(0.01)
        self.dsp_cut_to.setObjectName("dsp_cut_to")
        self.horizontalLayout_8.addWidget(self.dsp_cut_to)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem1)
        self.lb_status = QtWidgets.QLabel(self.layoutWidget1)
        self.lb_status.setMinimumSize(QtCore.QSize(200, 0))
        font = QtGui.QFont()
        font.setFamily("rsfs10")
        font.setPointSize(8)
        self.lb_status.setFont(font)
        self.lb_status.setStyleSheet("color: rgb(0, 0, 119);")
        self.lb_status.setText("")
        self.lb_status.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lb_status.setObjectName("lb_status")
        self.horizontalLayout_8.addWidget(self.lb_status)
        self.v_layout_2.addLayout(self.horizontalLayout_8)
        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(SectionView)
        QtCore.QMetaObject.connectSlotsByName(SectionView)

    def retranslateUi(self, SectionView):
        _translate = QtCore.QCoreApplication.translate
        SectionView.setWindowTitle(_translate("SectionView", "Form"))
        self.cmd_delete_me.setText(_translate("SectionView", "Delete"))
        self.label.setText(_translate("SectionView", "Section axis:"))
        self.label_10.setText(_translate("SectionView", "Fit range:"))
        self.rb_range_all.setText(_translate("SectionView", "Full spectra"))
        self.rb_range_cut.setText(_translate("SectionView", "Cut range"))
        self.label_8.setText(_translate("SectionView", "from:"))
        self.label_9.setText(_translate("SectionView", "to:"))
from pyqtgraph import GraphicsView
import petra_viewer.gui.icons_rc
