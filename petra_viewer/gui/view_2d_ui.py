# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/view_2d.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_View2D(object):
    def setupUi(self, View2D):
        View2D.setObjectName("View2D")
        View2D.resize(631, 697)
        self.v_layout = QtWidgets.QVBoxLayout(View2D)
        self.v_layout.setObjectName("v_layout")

        self.retranslateUi(View2D)
        QtCore.QMetaObject.connectSlotsByName(View2D)

    def retranslateUi(self, View2D):
        _translate = QtCore.QCoreApplication.translate
        View2D.setWindowTitle(_translate("View2D", "Form"))
