# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/axis_selector.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AxisSelector(object):
    def setupUi(self, AxisSelector):
        AxisSelector.setObjectName("AxisSelector")
        AxisSelector.resize(162, 38)
        self.horizontalLayout = QtWidgets.QHBoxLayout(AxisSelector)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lb_name = QtWidgets.QLabel(AxisSelector)
        self.lb_name.setObjectName("lb_name")
        self.horizontalLayout.addWidget(self.lb_name)
        self.cmb_selector = QtWidgets.QComboBox(AxisSelector)
        self.cmb_selector.setObjectName("cmb_selector")
        self.horizontalLayout.addWidget(self.cmb_selector)

        self.retranslateUi(AxisSelector)
        QtCore.QMetaObject.connectSlotsByName(AxisSelector)

    def retranslateUi(self, AxisSelector):
        _translate = QtCore.QCoreApplication.translate
        AxisSelector.setWindowTitle(_translate("AxisSelector", "Form"))
        self.lb_name.setText(_translate("AxisSelector", "TextLabel"))
