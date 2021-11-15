# Created by matveyev at 19.02.2021

WIDGET_NAME = 'CubeView'

import pyqtgraph.opengl as gl
import numpy as np

from distutils.util import strtobool

from PyQt5 import QtWidgets, QtCore

from data_viewer.utils.axes_3d import Custom3DAxis
from data_viewer.utils.fake_image_item import FakeImageItem
from data_viewer.utils.utils import refresh_combo_box
from data_viewer.widgets.abstract_widget import AbstractWidget
from data_viewer.gui.cube_view_ui import Ui_CubeView


# ----------------------------------------------------------------------
class CubeView(AbstractWidget):
    """
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent, data_pool):
        """
        """
        super(CubeView, self).__init__(parent)
        self._ui = Ui_CubeView()
        self._ui.setupUi(self)

        self._data_pool = data_pool

        self._make_actions()
        self._ui.v_layout.setStretch(1, 1)

        self._fake_image_item = FakeImageItem(data_pool)
        self._ui.hist.item.setImageItem(self._fake_image_item)
        self._ui.hist.setBackground('w')

        self.view_widget = gl.GLViewWidget()
        # self.view_widget.orbit(256, 256)
        # self.view_widget.setCameraPosition(0, 0, 0)
        # self.view_widget.opts['distance'] = 200

        self.axes = Custom3DAxis(self.view_widget, color=(0.2,0.2,0.2,.6))
        self.view_widget.addItem(self.axes)

        self.volume_item = None        

        self._ui.h_layout.insertWidget(0, self.view_widget, 1)

        self._ui.hist.item.sigLevelChangeFinished.connect(lambda: self._auto_levels(False))
        self._ui.hist.item.sigLookupTableChanged.connect(self.display_file)

        self._ui.hist.scene().sigMouseClicked.connect(self._hist_mouse_clicked)

        self._ui.chk_auto_levels.clicked.connect(self._auto_levels)

        self._ui.bg_lev_mode.buttonClicked.connect(self._change_level_mode)

        self._status_timer = QtCore.QTimer(self)
        self._status_timer.timeout.connect(self._refresh_camera_position)
        self._status_timer.start(100)

    # ----------------------------------------------------------------------
    def _auto_levels(self, state):
        if state:
            self._block_hist_signals(True)

            self._fake_image_item.setAutoLevels()
            l_min, l_max = self._fake_image_item.levels
            self._ui.hist.item.setLevels(l_min, l_max)

            self._block_hist_signals(False)
        else:
            self._change_chk_auto_levels_state(False)

        self.display_file()

    # ----------------------------------------------------------------------
    def _hist_mouse_clicked(self, event):

        if event.double():
            self._auto_levels(True)
            self._change_chk_auto_levels_state(True)

    # ----------------------------------------------------------------------
    def _change_level_mode(self, button):

        self._block_hist_signals(True)

        if button == self._ui.rb_lin_levels:
            self._fake_image_item.setMode('lin')
        elif button == self._ui.rb_sqrt_levels:
            self._fake_image_item.setMode('sqrt')
        else:
            self._fake_image_item.setMode('log')

        self._block_hist_signals(False)

        self._auto_levels(True)
        self._change_chk_auto_levels_state(True)

    # ----------------------------------------------------------------------
    def _change_chk_auto_levels_state(self, state):
        self._ui.chk_auto_levels.blockSignals(True)
        self._ui.chk_auto_levels.setChecked(state)
        self._ui.chk_auto_levels.blockSignals(False)

    # ----------------------------------------------------------------------
    def _refresh_camera_position(self):
        for param in ['distance', 'elevation', 'azimuth']:
            if not getattr(self, f'sp_cam_{param}').hasFocus():
                getattr(self, f'sp_cam_{param}').blockSignals(True)
                getattr(self, f'sp_cam_{param}').setValue(int(self.view_widget.opts[param]))
                getattr(self, f'sp_cam_{param}').blockSignals(False)

    # ----------------------------------------------------------------------
    def set_settings(self, settings):

        self._block_signals(True)

        if 'slices' in settings:
            self.sp_slices.setValue(int(settings['slices']))

        if 'smooth' in settings:
            self.chk_smooth.setChecked(strtobool(settings['smooth']))

        if 'borders' in settings:
            self.sp_borders.setValue(int(settings['borders']))

        if 'white_background' in settings:
            self.chk_white_bck.setChecked(strtobool(settings['white_background']))

        self.display_file()

        self._block_signals(False)

    # ----------------------------------------------------------------------
    def fill_roi(self):
        current_selection = self.cmb_area.currentText()
        self.cmb_area.blockSignals(True)
        self.cmb_area.clear()
        self.cmb_area.addItem('Whole data')
        for ind in range(self._data_pool.roi_counts()):
            self.cmb_area.addItem(f'ROI_{ind}')

        if not refresh_combo_box(self.cmb_area, current_selection):
            self.display_file()

        self.cmb_area.blockSignals(False)

    # ----------------------------------------------------------------------
    def _block_hist_signals(self, state):
        if state:
            self._ui.hist.item.sigLevelChangeFinished.disconnect()
            self._ui.hist.item.sigLookupTableChanged.disconnect()
        else:
            self._ui.hist.item.sigLevelChangeFinished.connect(lambda: self._auto_levels(False))
            self._ui.hist.item.sigLookupTableChanged.connect(self.display_file)

    # ----------------------------------------------------------------------
    def roi_changed(self, roi_ind):
        if roi_ind == self.cmb_area.currentIndex() - 1:
            self.display_file()

    # ----------------------------------------------------------------------
    def new_file(self):

        self._block_hist_signals(True)
        self._fake_image_item.setNewFile(self._parent.get_current_file())
        self._block_hist_signals(False)

        self.display_file()

    # ----------------------------------------------------------------------
    def data_updated(self):
        self._auto_levels(True)
        self._change_chk_auto_levels_state(True)
        self._fake_image_item.sigImageChanged.emit()

    # ----------------------------------------------------------------------
    def display_file(self):

        file_name = self._parent.get_current_file()
        if file_name is None:
            return

        data = self._data_pool.get_3d_cube(file_name, self.cmb_area.currentIndex() - 1)

        if data is None:
            return

        levels = self._ui.hist.item.getLevels()

        if self._ui.rb_log_levels.isChecked():
            data = np.log(data + 1)
        elif self._ui.rb_sqrt_levels.isChecked():
            data = np.sqrt(data + 1)

        data = np.maximum(np.minimum((data - levels[0]) / float(levels[1] - levels[0]) * 255, 255), 0)

        data_to_display = np.zeros(data.shape + (4,), dtype=np.ubyte)
        data_to_display[..., 0] = 0 if self.chk_white_bck.isChecked() else 255
        data_to_display[..., 1] = 0 if self.chk_white_bck.isChecked() else 255
        data_to_display[..., 2] = 0 if self.chk_white_bck.isChecked() else 255
        data_to_display[..., 3] = data

        borders = int(self.sp_borders.value())
        if borders > 0:
            data_to_display[:, :borders, :borders] = [255, 0, 0, 255]
            data_to_display[:borders, :, :borders] = [255, 0, 0, 255]
            data_to_display[:borders, :borders, :] = [255, 0, 0, 255]

            data_to_display[:, :borders, -borders:] = [255, 0, 0, 255]
            data_to_display[:borders, :, -borders:] = [255, 0, 0, 255]
            data_to_display[:borders, -borders:, :] = [255, 0, 0, 255]

            data_to_display[:, -borders:, :borders] = [255, 0, 0, 255]
            data_to_display[-borders:, :, :borders] = [255, 0, 0, 255]
            data_to_display[-borders:, :borders, :] = [255, 0, 0, 255]

            data_to_display[:, -borders:, -borders:] = [255, 0, 0, 255]
            data_to_display[-borders:, :, -borders:] = [255, 0, 0, 255]
            data_to_display[-borders:, -borders:, :] = [255, 0, 0, 255]

        if self.volume_item is not None:
            self.view_widget.removeItem(self.volume_item)
        self.volume_item = gl.GLVolumeItem(data_to_display,  sliceDensity=int(self.sp_slices.value()),
                                           smooth=self.chk_smooth.isChecked(), glOptions='translucent')

        self.view_widget.addItem(self.volume_item)
        self.volume_item.translate(-data_to_display.shape[0] / 2,
                                   -data_to_display.shape[1] / 2,
                                   -data_to_display.shape[2] / 2)

        self.view_widget.setCameraPosition(distance=max(data_to_display.shape)*5)

        self.axes.setSize(data_to_display.shape[0], data_to_display.shape[1], data_to_display.shape[2])
        axes = self._data_pool.get_file_axes(file_name)

        self.axes.set_labels(axes[0], axes[1], axes[2])

    # ----------------------------------------------------------------------
    def _set_background(self, status):

        self.view_widget.setBackgroundColor('w' if status else 'b')
        self.display_file()

    # ----------------------------------------------------------------------
    def _reset_view(self):
        self.chk_white_bck.blockSignals(True)
        self.chk_white_bck.setChecked(False)
        self.view_widget.reset()
        self.chk_white_bck.blockSignals(False)
        self.display_file()

    # ----------------------------------------------------------------------
    def _move_camera(self):

        self.view_widget.setCameraPosition(distance=self.sp_cam_distance.value(),
                                           elevation=self.sp_cam_elevation.value(),
                                           azimuth=self.sp_cam_azimuth.value())

    # ----------------------------------------------------------------------
    def _make_actions(self):

        toolbar = QtWidgets.QToolBar("Main toolbar", self)

        label = QtWidgets.QLabel("Area to render: ", self)
        toolbar.addWidget(label)

        self.cmb_area = QtWidgets.QComboBox(self)
        self.cmb_area.addItem('Whole data')
        self.cmb_area.currentTextChanged.connect(self.display_file)
        toolbar.addWidget(self.cmb_area)

        toolbar.addSeparator()

        label = QtWidgets.QLabel("View options: ", self)
        toolbar.addWidget(label)

        label = QtWidgets.QLabel("Slices: ", self)
        toolbar.addWidget(label)

        self.sp_slices = QtWidgets.QSpinBox(self)
        self.sp_slices.valueChanged.connect(self.display_file)
        toolbar.addWidget(self.sp_slices)

        self.chk_smooth = QtWidgets.QCheckBox('Smooth', self)
        self.chk_smooth.clicked.connect(self.display_file)
        toolbar.addWidget(self.chk_smooth)

        label = QtWidgets.QLabel("Borders: ", self)
        toolbar.addWidget(label)

        self.sp_borders = QtWidgets.QSpinBox(self)
        self.sp_borders.valueChanged.connect(self.display_file)
        toolbar.addWidget(self.sp_borders)

        self.chk_white_bck = QtWidgets.QCheckBox('White background', self)
        self.chk_white_bck.stateChanged.connect(self._set_background)
        toolbar.addWidget(self.chk_white_bck)

        toolbar.addSeparator()

        label = QtWidgets.QLabel("Camera position: ", self)
        toolbar.addWidget(label)

        label = QtWidgets.QLabel("Distance: ", self)
        toolbar.addWidget(label)

        self.sp_cam_distance = QtWidgets.QSpinBox(self)
        self.sp_cam_distance.setMaximum(100000)
        self.sp_cam_distance.setMinimum(0)
        self.sp_cam_distance.valueChanged.connect(self._move_camera)
        toolbar.addWidget(self.sp_cam_distance)

        label = QtWidgets.QLabel("Elevation: ", self)
        toolbar.addWidget(label)

        self.sp_cam_elevation = QtWidgets.QSpinBox(self)
        self.sp_cam_elevation.setMaximum(180)
        self.sp_cam_elevation.setMinimum(-180)
        self.sp_cam_elevation.valueChanged.connect(self._move_camera)
        toolbar.addWidget(self.sp_cam_elevation)

        label = QtWidgets.QLabel("Azimuth: ", self)
        toolbar.addWidget(label)

        self.sp_cam_azimuth = QtWidgets.QSpinBox(self)
        self.sp_cam_azimuth.setMaximum(360)
        self.sp_cam_azimuth.setMinimum(-360)
        self.sp_cam_azimuth.valueChanged.connect(self._move_camera)
        toolbar.addWidget(self.sp_cam_azimuth)

        cmd_reset = QtWidgets.QPushButton('Reset view')
        cmd_reset.clicked.connect(self._reset_view)
        toolbar.addWidget(cmd_reset)

        self._ui.v_layout.insertWidget(0, toolbar, 0)

    # ----------------------------------------------------------------------
    def _block_signals(self, flag):

        self.sp_slices.blockSignals(flag)
        self.chk_smooth.blockSignals(flag)
