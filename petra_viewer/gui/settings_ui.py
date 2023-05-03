# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/settings.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName("Settings")
        Settings.resize(796, 812)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(Settings)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.tabWidget = QtWidgets.QTabWidget(Settings)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_12 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.chk_beamline = QtWidgets.QCheckBox(self.groupBox_2)
        self.chk_beamline.setChecked(False)
        self.chk_beamline.setObjectName("chk_beamline")
        self.gridLayout_12.addWidget(self.chk_beamline, 5, 0, 1, 1)
        self.label_21 = QtWidgets.QLabel(self.groupBox_2)
        self.label_21.setObjectName("label_21")
        self.gridLayout_12.addWidget(self.label_21, 0, 0, 1, 1)
        self.chk_p11scan = QtWidgets.QCheckBox(self.groupBox_2)
        self.chk_p11scan.setChecked(False)
        self.chk_p11scan.setObjectName("chk_p11scan")
        self.gridLayout_12.addWidget(self.chk_p11scan, 2, 0, 1, 1)
        self.chk_p23scan = QtWidgets.QCheckBox(self.groupBox_2)
        self.chk_p23scan.setChecked(False)
        self.chk_p23scan.setObjectName("chk_p23scan")
        self.gridLayout_12.addWidget(self.chk_p23scan, 4, 0, 1, 1)
        self.label_22 = QtWidgets.QLabel(self.groupBox_2)
        self.label_22.setObjectName("label_22")
        self.gridLayout_12.addWidget(self.label_22, 0, 1, 1, 1)
        self.chk_roi = QtWidgets.QCheckBox(self.groupBox_2)
        self.chk_roi.setChecked(True)
        self.chk_roi.setObjectName("chk_roi")
        self.gridLayout_12.addWidget(self.chk_roi, 1, 1, 1, 1)
        self.chk_asapo = QtWidgets.QCheckBox(self.groupBox_2)
        self.chk_asapo.setChecked(False)
        self.chk_asapo.setObjectName("chk_asapo")
        self.gridLayout_12.addWidget(self.chk_asapo, 1, 0, 1, 1)
        self.chk_tests = QtWidgets.QCheckBox(self.groupBox_2)
        self.chk_tests.setChecked(False)
        self.chk_tests.setObjectName("chk_tests")
        self.gridLayout_12.addWidget(self.chk_tests, 6, 0, 1, 1)
        self.chk_cube = QtWidgets.QCheckBox(self.groupBox_2)
        self.chk_cube.setChecked(True)
        self.chk_cube.setObjectName("chk_cube")
        self.gridLayout_12.addWidget(self.chk_cube, 2, 1, 1, 1)
        self.chk_metadata = QtWidgets.QCheckBox(self.groupBox_2)
        self.chk_metadata.setChecked(True)
        self.chk_metadata.setObjectName("chk_metadata")
        self.gridLayout_12.addWidget(self.chk_metadata, 4, 1, 1, 1)
        self.chk_p1mscan = QtWidgets.QCheckBox(self.groupBox_2)
        self.chk_p1mscan.setChecked(False)
        self.chk_p1mscan.setObjectName("chk_p1mscan")
        self.gridLayout_12.addWidget(self.chk_p1mscan, 3, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.gb_max_files_4 = QtWidgets.QGroupBox(self.tab)
        self.gb_max_files_4.setObjectName("gb_max_files_4")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.gb_max_files_4)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_14 = QtWidgets.QLabel(self.gb_max_files_4)
        self.label_14.setObjectName("label_14")
        self.gridLayout_5.addWidget(self.label_14, 0, 0, 1, 1)
        self.cmb_memory_mode = QtWidgets.QComboBox(self.gb_max_files_4)
        self.cmb_memory_mode.setObjectName("cmb_memory_mode")
        self.cmb_memory_mode.addItem("")
        self.cmb_memory_mode.addItem("")
        self.gridLayout_5.addWidget(self.cmb_memory_mode, 0, 1, 1, 1)
        self.fr_drive_setting = QtWidgets.QFrame(self.gb_max_files_4)
        self.fr_drive_setting.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.fr_drive_setting.setFrameShadow(QtWidgets.QFrame.Raised)
        self.fr_drive_setting.setObjectName("fr_drive_setting")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.fr_drive_setting)
        self.gridLayout_7.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.chk_frame_buffer = QtWidgets.QCheckBox(self.fr_drive_setting)
        self.chk_frame_buffer.setObjectName("chk_frame_buffer")
        self.gridLayout_7.addWidget(self.chk_frame_buffer, 0, 0, 1, 1)
        self.sp_frame_buffer = QtWidgets.QSpinBox(self.fr_drive_setting)
        self.sp_frame_buffer.setEnabled(False)
        self.sp_frame_buffer.setMinimum(1)
        self.sp_frame_buffer.setMaximum(100000)
        self.sp_frame_buffer.setObjectName("sp_frame_buffer")
        self.gridLayout_7.addWidget(self.sp_frame_buffer, 0, 1, 1, 1)
        self.chk_frame_bunch = QtWidgets.QCheckBox(self.fr_drive_setting)
        self.chk_frame_bunch.setObjectName("chk_frame_bunch")
        self.gridLayout_7.addWidget(self.chk_frame_bunch, 1, 0, 1, 1)
        self.sp_frame_bunch = QtWidgets.QSpinBox(self.fr_drive_setting)
        self.sp_frame_bunch.setEnabled(False)
        self.sp_frame_bunch.setMinimum(1)
        self.sp_frame_bunch.setMaximum(100000)
        self.sp_frame_bunch.setObjectName("sp_frame_bunch")
        self.gridLayout_7.addWidget(self.sp_frame_bunch, 1, 1, 1, 1)
        self.gridLayout_5.addWidget(self.fr_drive_setting, 1, 0, 1, 2)
        self.verticalLayout.addWidget(self.gb_max_files_4)
        self.gb_max_files = QtWidgets.QGroupBox(self.tab)
        self.gb_max_files.setObjectName("gb_max_files")
        self.gridLayout = QtWidgets.QGridLayout(self.gb_max_files)
        self.gridLayout.setObjectName("gridLayout")
        self.sb_lim_mem = QtWidgets.QSpinBox(self.gb_max_files)
        self.sb_lim_mem.setEnabled(True)
        self.sb_lim_mem.setMaximum(100000)
        self.sb_lim_mem.setObjectName("sb_lim_mem")
        self.gridLayout.addWidget(self.sb_lim_mem, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.gb_max_files)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.gb_max_files)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.gb_max_files)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.sp_lim_num = QtWidgets.QSpinBox(self.gb_max_files)
        self.sp_lim_num.setEnabled(True)
        self.sp_lim_num.setMaximum(1000)
        self.sp_lim_num.setObjectName("sp_lim_num")
        self.gridLayout.addWidget(self.sp_lim_num, 0, 1, 1, 1)
        self.verticalLayout.addWidget(self.gb_max_files)
        self.gb_max_files_3 = QtWidgets.QGroupBox(self.tab)
        self.gb_max_files_3.setObjectName("gb_max_files_3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.gb_max_files_3)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_10 = QtWidgets.QLabel(self.gb_max_files_3)
        self.label_10.setObjectName("label_10")
        self.gridLayout_4.addWidget(self.label_10, 0, 0, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.gb_max_files_3)
        self.label_11.setObjectName("label_11")
        self.gridLayout_4.addWidget(self.label_11, 1, 0, 1, 1)
        self.le_separator = QtWidgets.QLineEdit(self.gb_max_files_3)
        self.le_separator.setObjectName("le_separator")
        self.gridLayout_4.addWidget(self.le_separator, 0, 1, 1, 1)
        self.le_format = QtWidgets.QLineEdit(self.gb_max_files_3)
        self.le_format.setObjectName("le_format")
        self.gridLayout_4.addWidget(self.le_format, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.gb_max_files_3)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.frame = QtWidgets.QFrame(self.tab)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.cmd_reset_settings = QtWidgets.QPushButton(self.frame)
        self.cmd_reset_settings.setObjectName("cmd_reset_settings")
        self.horizontalLayout.addWidget(self.cmd_reset_settings)
        spacerItem1 = QtWidgets.QSpacerItem(556, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.cmd_load_profile = QtWidgets.QPushButton(self.frame)
        self.cmd_load_profile.setObjectName("cmd_load_profile")
        self.horizontalLayout.addWidget(self.cmd_load_profile)
        self.cmd_sav_profile = QtWidgets.QPushButton(self.frame)
        self.cmd_sav_profile.setObjectName("cmd_sav_profile")
        self.horizontalLayout.addWidget(self.cmd_sav_profile)
        self.verticalLayout.addWidget(self.frame)
        self.tabWidget.addTab(self.tab, "")
        self.tab_6 = QtWidgets.QWidget()
        self.tab_6.setObjectName("tab_6")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tab_6)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.tb_sources = QtWidgets.QTabWidget(self.tab_6)
        self.tb_sources.setObjectName("tb_sources")
        self.verticalLayout_4.addWidget(self.tb_sources)
        self.tabWidget.addTab(self.tab_6, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_5 = QtWidgets.QLabel(self.tab_2)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 0, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem2, 1, 1, 1, 1)
        self.le_macro_server = QtWidgets.QLineEdit(self.tab_2)
        self.le_macro_server.setObjectName("le_macro_server")
        self.gridLayout_2.addWidget(self.le_macro_server, 0, 1, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem3, 0, 2, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab_4)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.chk_cross = QtWidgets.QCheckBox(self.tab_4)
        self.chk_cross.setObjectName("chk_cross")
        self.gridLayout_3.addWidget(self.chk_cross, 3, 0, 1, 2)
        self.chk_grid = QtWidgets.QCheckBox(self.tab_4)
        self.chk_grid.setObjectName("chk_grid")
        self.gridLayout_3.addWidget(self.chk_grid, 2, 0, 1, 2)
        self.chk_aspect = QtWidgets.QCheckBox(self.tab_4)
        self.chk_aspect.setObjectName("chk_aspect")
        self.gridLayout_3.addWidget(self.chk_aspect, 4, 0, 1, 2)
        self.label_4 = QtWidgets.QLabel(self.tab_4)
        self.label_4.setObjectName("label_4")
        self.gridLayout_3.addWidget(self.label_4, 6, 0, 1, 1)
        self.cmb_backend = QtWidgets.QComboBox(self.tab_4)
        self.cmb_backend.setObjectName("cmb_backend")
        self.cmb_backend.addItem("")
        self.cmb_backend.addItem("")
        self.gridLayout_3.addWidget(self.cmb_backend, 6, 1, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem4, 7, 0, 1, 1)
        self.chk_axes_titles = QtWidgets.QCheckBox(self.tab_4)
        self.chk_axes_titles.setObjectName("chk_axes_titles")
        self.gridLayout_3.addWidget(self.chk_axes_titles, 1, 0, 1, 2)
        self.chk_axes = QtWidgets.QCheckBox(self.tab_4)
        self.chk_axes.setObjectName("chk_axes")
        self.gridLayout_3.addWidget(self.chk_axes, 0, 0, 1, 2)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem5, 6, 2, 1, 1)
        self.label_20 = QtWidgets.QLabel(self.tab_4)
        self.label_20.setObjectName("label_20")
        self.gridLayout_3.addWidget(self.label_20, 5, 0, 1, 1)
        self.cmd_default_hist = QtWidgets.QComboBox(self.tab_4)
        self.cmd_default_hist.setObjectName("cmd_default_hist")
        self.cmd_default_hist.addItem("")
        self.cmd_default_hist.addItem("")
        self.gridLayout_3.addWidget(self.cmd_default_hist, 5, 1, 1, 1)
        self.tabWidget.addTab(self.tab_4, "")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.tab_5)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_16 = QtWidgets.QLabel(self.tab_5)
        self.label_16.setObjectName("label_16")
        self.gridLayout_6.addWidget(self.label_16, 0, 0, 1, 1)
        self.sp_slices = QtWidgets.QSpinBox(self.tab_5)
        self.sp_slices.setObjectName("sp_slices")
        self.gridLayout_6.addWidget(self.sp_slices, 0, 1, 1, 1)
        self.chk_smooth = QtWidgets.QCheckBox(self.tab_5)
        self.chk_smooth.setObjectName("chk_smooth")
        self.gridLayout_6.addWidget(self.chk_smooth, 1, 0, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.tab_5)
        self.label_17.setObjectName("label_17")
        self.gridLayout_6.addWidget(self.label_17, 2, 0, 1, 1)
        self.sp_borders = QtWidgets.QSpinBox(self.tab_5)
        self.sp_borders.setObjectName("sp_borders")
        self.gridLayout_6.addWidget(self.sp_borders, 2, 1, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(564, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem6, 2, 3, 1, 1)
        self.chk_white_background = QtWidgets.QCheckBox(self.tab_5)
        self.chk_white_background.setObjectName("chk_white_background")
        self.gridLayout_6.addWidget(self.chk_white_background, 3, 0, 1, 1)
        spacerItem7 = QtWidgets.QSpacerItem(20, 521, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_6.addItem(spacerItem7, 4, 2, 1, 1)
        self.tabWidget.addTab(self.tab_5, "")
        self.verticalLayout_3.addWidget(self.tabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(Settings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_3.addWidget(self.buttonBox)

        self.retranslateUi(Settings)
        self.tabWidget.setCurrentIndex(0)
        self.tb_sources.setCurrentIndex(-1)
        self.buttonBox.accepted.connect(Settings.accept)
        self.buttonBox.rejected.connect(Settings.reject)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        _translate = QtCore.QCoreApplication.translate
        Settings.setWindowTitle(_translate("Settings", "Settings"))
        self.groupBox_2.setTitle(_translate("Settings", "Widget configuration"))
        self.chk_beamline.setText(_translate("Settings", "Beamline (P23)"))
        self.label_21.setText(_translate("Settings", "File types"))
        self.chk_p11scan.setText(_translate("Settings", "P11 scans"))
        self.chk_p23scan.setText(_translate("Settings", "P23 scans"))
        self.label_22.setText(_translate("Settings", "Visualization widgets"))
        self.chk_roi.setText(_translate("Settings", "ROI"))
        self.chk_asapo.setText(_translate("Settings", "ASAPO streams (P02; P23)"))
        self.chk_tests.setText(_translate("Settings", "Tests"))
        self.chk_cube.setText(_translate("Settings", "Cube view"))
        self.chk_metadata.setText(_translate("Settings", "Meta data view"))
        self.chk_p1mscan.setText(_translate("Settings", "P1m scans"))
        self.gb_max_files_4.setTitle(_translate("Settings", "General:"))
        self.label_14.setText(_translate("Settings", "Memory mode"))
        self.cmb_memory_mode.setItemText(0, _translate("Settings", "RAM"))
        self.cmb_memory_mode.setItemText(1, _translate("Settings", "DRIVE/ASAPO"))
        self.chk_frame_buffer.setText(_translate("Settings", "Frame buffer"))
        self.chk_frame_bunch.setText(_translate("Settings", "Bunch frames reading"))
        self.gb_max_files.setTitle(_translate("Settings", "Max open files:"))
        self.label_3.setText(_translate("Settings", "* 0 means no limit"))
        self.label.setText(_translate("Settings", "Max images number:"))
        self.label_2.setText(_translate("Settings", "Max memory usage"))
        self.gb_max_files_3.setTitle(_translate("Settings", "File export settings:"))
        self.label_10.setText(_translate("Settings", "Separator:"))
        self.label_11.setText(_translate("Settings", "Format:"))
        self.le_separator.setText(_translate("Settings", "semicolumn"))
        self.le_format.setText(_translate("Settings", ".6e"))
        self.cmd_reset_settings.setText(_translate("Settings", "Reset settings to default"))
        self.cmd_load_profile.setText(_translate("Settings", "Load profile"))
        self.cmd_sav_profile.setText(_translate("Settings", "Save profile"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Settings", "General"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), _translate("Settings", "Data sources"))
        self.label_5.setText(_translate("Settings", "Macro server"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Settings", "ROI"))
        self.chk_cross.setText(_translate("Settings", "Display cross"))
        self.chk_grid.setText(_translate("Settings", "Display grid"))
        self.chk_aspect.setText(_translate("Settings", "Keep aspect ratio"))
        self.label_4.setText(_translate("Settings", "Backend"))
        self.cmb_backend.setItemText(0, _translate("Settings", "pyqt"))
        self.cmb_backend.setItemText(1, _translate("Settings", "silx"))
        self.chk_axes_titles.setText(_translate("Settings", "Display axes titles"))
        self.chk_axes.setText(_translate("Settings", "Display axes"))
        self.label_20.setText(_translate("Settings", "Default histogram"))
        self.cmd_default_hist.setItemText(0, _translate("Settings", "selection"))
        self.cmd_default_hist.setItemText(1, _translate("Settings", "all frames"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("Settings", "2D View"))
        self.label_16.setText(_translate("Settings", "Slices"))
        self.chk_smooth.setText(_translate("Settings", "Smooth"))
        self.label_17.setText(_translate("Settings", "Borders"))
        self.chk_white_background.setText(_translate("Settings", "White backround"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), _translate("Settings", "3D view"))
