# Created by matveyev at 18.02.2021

MEMORY_MODE = 'ram' #'disk' or 'ram'

WIDGET_NAME = 'ASAPOScanSetup'

import pyqtgraph as pg
import numpy as np
import asapo_consumer
import configparser

from PyQt5 import QtWidgets, QtCore
from pyqtgraph.graphicsItems.GradientEditorItem import Gradients

from src.gui.asapo_image_setup_ui import Ui_ASAPOImageSetup
from src.utils.utils import read_mask_file
from src.main_window import APP_NAME
from src.data_sources.abstract_data_file import AbstractDataFile

from AsapoWorker.asapo_receiver import SerialDatasetAsapoReceiver
from AsapoWorker.data_handler import get_image

SETTINGS = {'mask_mode': 'off',
            'loaded_mask': None,
            'loaded_mask_info': {'file': ''},
            'displayed_param': 'frame_ID',
            }


class ASAPOScan(AbstractDataFile):

    # ----------------------------------------------------------------------
    def __init__(self, detector_name, stream_name, data_pool):
        super(ASAPOScan, self).__init__(data_pool)

        self.my_name = stream_name
        self._detector_name = detector_name
        self._spaces = ['real']
        self._axes_names = {'real': ['frame_ID', 'detector X', 'detector Y']}
        self._cube_axes_map = {'real': {0: 2,
                                        1: 1,
                                        2: 0}}

        settings = configparser.ConfigParser()
        settings.read('./settings.ini')

        host = settings['ASAPO']['host']
        beamtime = settings['ASAPO']['beamtime']
        token = settings['ASAPO']['token']

        self.receiver = SerialDatasetAsapoReceiver(asapo_consumer.create_consumer(host, "", False,
                                                                                  beamtime, detector_name,
                                                                                  token, 1000))

        self.receiver.stream = stream_name
        self.receiver.data_source = detector_name

        self._data['scanned_values'] = ['frame_ID']

        if MEMORY_MODE == 'ram':
            self._3d_cube = self._reload_stream()
            self._data['cube_shape'] = self._3d_cube.shape
        else:
            cube = self._reload_stream()
            self._data['cube_shape'] = cube.shape

        self._data['frame_ID'] = np.arange(self._data['cube_shape'][0])

    # -------------------------------------------------------------------
    def _reload_stream(self):

        self.receiver.set_start_id(1)
        data, meta_data = self.receiver.get_next(False)
        cube = get_image(data[0], meta_data[0])[np.newaxis, :]
        for _ in range(1, self.receiver.get_current_size()):
            data, meta_data = self.receiver.get_next(False)
            cube = np.vstack((cube, get_image(data[0], meta_data[0])[np.newaxis, :]))

        return np.array(cube, dtype=np.float32)

    # ----------------------------------------------------------------------
    def apply_settings(self):

        if SETTINGS['mask_mode'] == 'file' and SETTINGS['loaded_mask'] is not None:
            self._pixel_mask = SETTINGS['loaded_mask'] > 0
        else:
            self._pixel_mask = None

        if MEMORY_MODE == 'ram':
            self._3d_cube = self._reload_stream()
            try:
                if self._pixel_mask is not None:
                    for frame in self._3d_cube:
                        frame[self._pixel_mask] = 0

            except Exception as err:
                self._data_pool.main_window.report_error("{}: cannot apply mask: {}".format(self.my_name, err))

    # ----------------------------------------------------------------------
    def get_2d_cut(self, space, axis, value, x_axis, y_axis):
        if space in self._spaces:
            cut_axis = self._cube_axes_map[space][axis]

            if MEMORY_MODE == 'ram':
                if cut_axis == 0:
                    data = np.copy(self._3d_cube[value, :, :])
                elif cut_axis == 1:
                    data = np.copy(self._3d_cube[:, value, :])
                else:
                    data = np.copy(self._3d_cube[:, :, value])

            else:
                if cut_axis == 0:
                    self.receiver.set_start_id(value)
                    data, meta_data = self.receiver.get_next(False)
                    data = get_image(data[0], meta_data[0])
                    if self._pixel_mask is not None:
                        data[self._pixel_mask] = 0
                elif cut_axis == 1:
                    data = self._reload_stream()[:, value, :]
                    if self._pixel_mask is not None:
                        cut_mask = self._pixel_mask[value, :]
                        for line in data:
                            line[cut_mask] = 0
                else:
                    data = self._reload_stream()[:, :, value]
                    if self._pixel_mask is not None:
                        cut_mask = self._pixel_mask[:, value]
                        for line in data:
                            line[cut_mask] = 0

            if self._cube_axes_map[space][x_axis] > self._cube_axes_map[space][y_axis]:
                return np.transpose(data)
            else:
                return data

        else:
            return []

    # ----------------------------------------------------------------------
    def get_roi_plot(self, space, sect):
        if space in self._spaces:
            plot_axis = self._cube_axes_map[space][sect['axis']]
            cut_axis_1 = self._cube_axes_map[space][sect['roi_1_axis']]

            if MEMORY_MODE == 'ram':
                cube = self._3d_cube
            else:
                cube = self._reload_stream()

            if plot_axis == 0:
                if SETTINGS['displayed_param'] not in self._data['scanned_values']:
                    return None, None

                if cut_axis_1 == 1:
                    cube_cut = cube[:,
                                    sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                    sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']]

                    if MEMORY_MODE != 'ram' and self._pixel_mask is not None:
                        mask_cut = self._pixel_mask[sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                   sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']]

                else:
                    cube_cut = cube[:,
                                    sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                    sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']]

                    if MEMORY_MODE != 'ram' and self._pixel_mask is not None:
                        mask_cut = self._pixel_mask[sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                   sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']]

                if MEMORY_MODE != 'ram':
                    for frame in cube_cut:
                        frame[mask_cut] = 0

                cube_cut = np.sum(cube_cut, axis=1)
                cube_cut = np.sum(cube_cut, axis=1)

            elif plot_axis == 1:
                if cut_axis_1 == 0:
                    cube_cut = self._3d_cube[sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                             :,
                                             sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']]

                    if MEMORY_MODE != 'ram' and self._pixel_mask is not None:
                        for z in range(sect['roi_2_pos'], sect['roi_2_pos'] + sect['roi_2_width']):
                            mask_cut = self._pixel_mask[:, z]
                            for frame in cube_cut:
                                frame[mask_cut, z] = 0
                else:
                    cube_cut = self._3d_cube[sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                             :,
                                             sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']]

                    if MEMORY_MODE != 'ram' and self._pixel_mask is not None:
                        for z in range(sect['roi_1_pos'], sect['roi_1_pos'] + sect['roi_1_width']):
                            mask_cut = self._pixel_mask[:, z]
                            for frame in cube_cut:
                                frame[mask_cut, z] = 0

                cube_cut = np.sum(cube_cut, axis=2)
                cube_cut = np.sum(cube_cut, axis=0)

            else:
                if cut_axis_1 == 0:
                    cube_cut = self._3d_cube[sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                             sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                             :]
                    if MEMORY_MODE != 'ram' and self._pixel_mask is not None:
                        for y in range(sect['roi_2_pos'], sect['roi_2_pos'] + sect['roi_2_width']):
                            mask_cut = self._pixel_mask[y, :]
                            for frame in cube_cut:
                                frame[y, mask_cut] = 0

                else:
                    cube_cut = self._3d_cube[sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                             sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                             :]
                    if MEMORY_MODE != 'ram' and self._pixel_mask is not None:
                        for y in range(sect['roi_1_pos'], sect['roi_1_pos'] + sect['roi_1_width']):
                            mask_cut = self._pixel_mask[y, :]
                            for frame in cube_cut:
                                frame[y, mask_cut] = 0

                cube_cut = np.sum(cube_cut, axis=0)
                cube_cut = np.sum(cube_cut, axis=0)

            return self._get_roi_axis(plot_axis), cube_cut

        return None, None

# ----------------------------------------------------------------------
class ASAPOScanSetup(QtWidgets.QWidget):
    """
    SETTINGS = {'mask_mode': 'off',
                'loaded_mask': None,
                'loaded_mask_info': {'file': ''},
                'displayed_param': 'point_nb',
                }
    """

    # ----------------------------------------------------------------------
    def __init__(self, main_window, data_pool):
        """
        """
        super(ASAPOScanSetup, self).__init__()
        self._ui = Ui_ASAPOImageSetup()
        self._ui.setupUi(self)

        self._main_window = main_window
        self._data_pool = data_pool

        self._main_plot = pg.PlotItem()
        self._main_plot.showAxis('left', False)
        self._main_plot.showAxis('bottom', False)
        self._main_plot.setMenuEnabled(False)

        self._ui.gv_main.setStyleSheet("")
        self._ui.gv_main.setBackground('w')
        self._ui.gv_main.setObjectName("gvMain")

        self._ui.gv_main.setCentralItem(self._main_plot)
        self._ui.gv_main.setRenderHints(self._ui.gv_main.renderHints())

        self._main_plot.getViewBox().setAspectLocked()

        self._old_settings = dict(SETTINGS)

        if SETTINGS['mask_mode'] == 'off':
            self._ui.rb_no_mask.setChecked(True)
            _mask = None
        else:
            self._ui.rb_file.setChecked(True)
            self._ui.but_load_mask.setEnabled(True)
            self._ui.lb_mask_file.setText(SETTINGS['loaded_mask_info']['file'])
            _mask = SETTINGS['loaded_mask']

        self._plot_2d = pg.ImageItem()
        if _mask is not None:
            self._plot_2d.setImage(np.copy(_mask), autoLevels=True)
        self._plot_2d.setLookupTable(pg.ColorMap(*zip(*Gradients['grey']["ticks"])).getLookupTable())
        self._main_plot.addItem(self._plot_2d)

        self._ui.bg_mask_option.buttonClicked.connect(self.change_mode)
        self._ui.but_load_mask.clicked.connect(self.load_mask_from_file)

        self._main_plot.scene().sigMouseClicked.connect(self._mouse_clicked)

        try:
            self.restoreGeometry(QtCore.QSettings(APP_NAME).value("{}/geometry".format(WIDGET_NAME)))
        except Exception as err:
            self._main_window.log.error("{} : cannot restore geometry: {}".format(WIDGET_NAME, err))

    # ----------------------------------------------------------------------
    def get_name(self):
        return 'ASAPO Scan Setup'

    # ----------------------------------------------------------------------
    def change_mode(self, button):
        self._ui.but_load_mask.setEnabled(False)

        if button == self._ui.rb_no_mask:
            SETTINGS['mask_mode'] = 'off'
            self._plot_2d.clear()
            return

        elif button == self._ui.rb_file:
            SETTINGS['mask_mode'] = 'file'
            if SETTINGS['loaded_mask'] is None:
                self.load_mask_from_file()

            self._ui.but_load_mask.setEnabled(True)
            self._ui.lb_mask_file.setText(SETTINGS['loaded_mask_info']['file'])

            try:
                self._plot_2d.setImage(np.copy(SETTINGS['loaded_mask']), autoLevels=True)
            except Exception as err:
                self._main_window.log.error("{} : cannot display mask geometry: {}".format(WIDGET_NAME, err))
                self._plot_2d.clear()

    # ----------------------------------------------------------------------
    def load_mask_from_file(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file with mask',
                                                             self._main_window.get_current_folder())

        if file_name:
            mask, mask_info = read_mask_file(file_name)
            if mask is not None:
                SETTINGS['loaded_mask'] = mask
                SETTINGS['loaded_mask_info'] = mask_info
                self._plot_2d.setImage(np.copy(mask), autoLevels=True)
                self._ui.lb_mask_file.setText(mask_info['file'])

    # ----------------------------------------------------------------------
    def accept(self):

        QtCore.QSettings(APP_NAME).setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())

    # ----------------------------------------------------------------------
    def reject(self):

        for key in SETTINGS.keys():
            SETTINGS[key] = self._old_settings[key]

        QtCore.QSettings(APP_NAME).setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())

    # ----------------------------------------------------------------------
    def _mouse_clicked(self, event):
        """
        """
        if event.double():
            try:
                self._main_plot.autoRange()
            except:
                pass
