# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/cube_view.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CubeView(object):
    def setupUi(self, CubeView):
        CubeView.setObjectName("CubeView")
        CubeView.resize(864, 603)
        self.v_layout = QtWidgets.QVBoxLayout(CubeView)
        self.v_layout.setObjectName("v_layout")
        self.h_layout = QtWidgets.QHBoxLayout()
        self.h_layout.setObjectName("h_layout")
        self.groupBox = QtWidgets.QGroupBox(CubeView)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.sp_borders = QtWidgets.QSpinBox(self.groupBox)
        self.sp_borders.setObjectName("sp_borders")
        self.gridLayout.addWidget(self.sp_borders, 4, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.chk_smooth = QtWidgets.QCheckBox(self.groupBox)
        self.chk_smooth.setObjectName("chk_smooth")
        self.gridLayout.addWidget(self.chk_smooth, 6, 0, 1, 1)
        self.chk_white_bck = QtWidgets.QCheckBox(self.groupBox)
        self.chk_white_bck.setObjectName("chk_white_bck")
        self.gridLayout.addWidget(self.chk_white_bck, 5, 0, 1, 1)
        self.line_3 = QtWidgets.QFrame(self.groupBox)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 1, 0, 1, 2)
        self.cmb_area = QtWidgets.QComboBox(self.groupBox)
        self.cmb_area.setObjectName("cmb_area")
        self.cmb_area.addItem("")
        self.gridLayout.addWidget(self.cmb_area, 0, 1, 1, 1)
        self.sp_slices = QtWidgets.QSpinBox(self.groupBox)
        self.sp_slices.setObjectName("sp_slices")
        self.gridLayout.addWidget(self.sp_slices, 3, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 2)
        self.label_7 = QtWidgets.QLabel(self.groupBox)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 9, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.groupBox)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 10, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.groupBox)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 11, 0, 1, 1)
        self.sp_cam_distance = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.sp_cam_distance.setMaximum(100000.0)
        self.sp_cam_distance.setObjectName("sp_cam_distance")
        self.gridLayout.addWidget(self.sp_cam_distance, 9, 1, 1, 1)
        self.line_4 = QtWidgets.QFrame(self.groupBox)
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.gridLayout.addWidget(self.line_4, 7, 0, 1, 2)
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 8, 0, 1, 1)
        self.cmd_reset_scale = QtWidgets.QPushButton(self.groupBox)
        self.cmd_reset_scale.setObjectName("cmd_reset_scale")
        self.gridLayout.addWidget(self.cmd_reset_scale, 18, 0, 1, 2)
        self.cmd_reset_camera = QtWidgets.QPushButton(self.groupBox)
        self.cmd_reset_camera.setObjectName("cmd_reset_camera")
        self.gridLayout.addWidget(self.cmd_reset_camera, 12, 0, 1, 2)
        self.sp_cam_elevation = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.sp_cam_elevation.setMinimum(-180.0)
        self.sp_cam_elevation.setMaximum(180.0)
        self.sp_cam_elevation.setObjectName("sp_cam_elevation")
        self.gridLayout.addWidget(self.sp_cam_elevation, 10, 1, 1, 1)
        self.sp_cam_azimuth = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.sp_cam_azimuth.setMinimum(-360.0)
        self.sp_cam_azimuth.setMaximum(360.0)
        self.sp_cam_azimuth.setObjectName("sp_cam_azimuth")
        self.gridLayout.addWidget(self.sp_cam_azimuth, 11, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.groupBox)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 14, 0, 1, 1)
        self.line_6 = QtWidgets.QFrame(self.groupBox)
        self.line_6.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_6.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_6.setObjectName("line_6")
        self.gridLayout.addWidget(self.line_6, 13, 0, 1, 2)
        self.sp_x_scale = QtWidgets.QSpinBox(self.groupBox)
        self.sp_x_scale.setMaximum(20)
        self.sp_x_scale.setObjectName("sp_x_scale")
        self.gridLayout.addWidget(self.sp_x_scale, 15, 1, 1, 1)
        self.sp_z_scale = QtWidgets.QSpinBox(self.groupBox)
        self.sp_z_scale.setMaximum(20)
        self.sp_z_scale.setObjectName("sp_z_scale")
        self.gridLayout.addWidget(self.sp_z_scale, 17, 1, 1, 1)
        self.z_label = QtWidgets.QLabel(self.groupBox)
        self.z_label.setObjectName("z_label")
        self.gridLayout.addWidget(self.z_label, 17, 0, 1, 1)
        self.y_label = QtWidgets.QLabel(self.groupBox)
        self.y_label.setObjectName("y_label")
        self.gridLayout.addWidget(self.y_label, 16, 0, 1, 1)
        self.x_label = QtWidgets.QLabel(self.groupBox)
        self.x_label.setObjectName("x_label")
        self.gridLayout.addWidget(self.x_label, 15, 0, 1, 1)
        self.sp_y_scale = QtWidgets.QSpinBox(self.groupBox)
        self.sp_y_scale.setMaximum(20)
        self.sp_y_scale.setObjectName("sp_y_scale")
        self.gridLayout.addWidget(self.sp_y_scale, 16, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 19, 0, 1, 1)
        self.h_layout.addWidget(self.groupBox)
        self.fr_hist = QtWidgets.QFrame(CubeView)
        self.fr_hist.setMinimumSize(QtCore.QSize(150, 0))
        self.fr_hist.setMaximumSize(QtCore.QSize(200, 16777215))
        self.fr_hist.setObjectName("fr_hist")
        self.hist_layout = QtWidgets.QVBoxLayout(self.fr_hist)
        self.hist_layout.setObjectName("hist_layout")
        self.label = QtWidgets.QLabel(self.fr_hist)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.hist_layout.addWidget(self.label)
        self.line_2 = QtWidgets.QFrame(self.fr_hist)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.hist_layout.addWidget(self.line_2)
        self.rb_lin_levels = QtWidgets.QRadioButton(self.fr_hist)
        self.rb_lin_levels.setChecked(True)
        self.rb_lin_levels.setObjectName("rb_lin_levels")
        self.bg_lev_mode = QtWidgets.QButtonGroup(CubeView)
        self.bg_lev_mode.setObjectName("bg_lev_mode")
        self.bg_lev_mode.addButton(self.rb_lin_levels)
        self.hist_layout.addWidget(self.rb_lin_levels)
        self.rb_log_levels = QtWidgets.QRadioButton(self.fr_hist)
        self.rb_log_levels.setObjectName("rb_log_levels")
        self.bg_lev_mode.addButton(self.rb_log_levels)
        self.hist_layout.addWidget(self.rb_log_levels)
        self.rb_sqrt_levels = QtWidgets.QRadioButton(self.fr_hist)
        self.rb_sqrt_levels.setObjectName("rb_sqrt_levels")
        self.bg_lev_mode.addButton(self.rb_sqrt_levels)
        self.hist_layout.addWidget(self.rb_sqrt_levels)
        self.line = QtWidgets.QFrame(self.fr_hist)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.hist_layout.addWidget(self.line)
        self.chk_auto_levels = QtWidgets.QCheckBox(self.fr_hist)
        self.chk_auto_levels.setChecked(True)
        self.chk_auto_levels.setObjectName("chk_auto_levels")
        self.hist_layout.addWidget(self.chk_auto_levels)
        self.hist = HistogramLUTWidget(self.fr_hist)
        self.hist.setObjectName("hist")
        self.hist_layout.addWidget(self.hist)
        self.hist_layout.setStretch(7, 1)
        self.h_layout.addWidget(self.fr_hist)
        self.v_layout.addLayout(self.h_layout)

        self.retranslateUi(CubeView)
        QtCore.QMetaObject.connectSlotsByName(CubeView)

    def retranslateUi(self, CubeView):
        _translate = QtCore.QCoreApplication.translate
        CubeView.setWindowTitle(_translate("CubeView", "3D Cube View"))
        self.groupBox.setTitle(_translate("CubeView", "Settings"))
        self.label_5.setText(_translate("CubeView", "Border"))
        self.chk_smooth.setText(_translate("CubeView", "Smooth"))
        self.chk_white_bck.setText(_translate("CubeView", "White background"))
        self.cmb_area.setItemText(0, _translate("CubeView", "Whole cube"))
        self.label_2.setText(_translate("CubeView", "Area to render"))
        self.label_4.setText(_translate("CubeView", "Slices"))
        self.label_3.setText(_translate("CubeView", "View options"))
        self.label_7.setText(_translate("CubeView", "Distance:"))
        self.label_8.setText(_translate("CubeView", "Elevation:"))
        self.label_9.setText(_translate("CubeView", "Azimuth:"))
        self.label_6.setText(_translate("CubeView", "Camera position:"))
        self.cmd_reset_scale.setText(_translate("CubeView", "Reset scale"))
        self.cmd_reset_camera.setText(_translate("CubeView", "Reset camera"))
        self.label_10.setText(_translate("CubeView", "Cube scale:"))
        self.z_label.setText(_translate("CubeView", "Z"))
        self.y_label.setText(_translate("CubeView", "Y"))
        self.x_label.setText(_translate("CubeView", "X"))
        self.label.setText(_translate("CubeView", "Levels"))
        self.rb_lin_levels.setText(_translate("CubeView", "Lin"))
        self.rb_log_levels.setText(_translate("CubeView", "Log"))
        self.rb_sqrt_levels.setText(_translate("CubeView", "Sqrt"))
        self.chk_auto_levels.setText(_translate("CubeView", "Auto"))
from pyqtgraph import HistogramLUTWidget
