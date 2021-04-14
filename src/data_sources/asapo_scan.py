# Created by matveyev at 18.02.2021

MEMORY_MODE = 'ram' #'disk' or 'ram'

WIDGET_NAME = 'LambdaScanSetup'

import h5py
import os

import pyqtgraph as pg
import numpy as np

from PyQt5 import QtWidgets, QtCore
from pyqtgraph.graphicsItems.GradientEditorItem import Gradients

from src.gui.lambda_setup_ui import Ui_LambdaSetup
from src.utils.utils import read_mask_file, refresh_combo_box
from src.main_window import APP_NAME
from src.data_sources.abstract_data_file import AbstractDataFile

SETTINGS = {'mask_mode': 'off',
            'loaded_mask': None,
            'loaded_mask_info': {'file': ''},
            'atten_correction': 'on',
            'atten_param': 'atten',
            'inten_correction': 'on',
            'inten_param': 'eh_c01',
            'displayed_param': 'point_nb',
            'all_params': []
            }


class ASAPOScan(AbstractDataFile):

    # ----------------------------------------------------------------------
    def __init__(self, file_name, data_pool, opened_file):
        super(ASAPOScan, self).__init__(file_name, data_pool, opened_file)

        self._original_file = file_name
        self._spaces = ['real']
        self._axes_names = {'real': ['detector X', 'detector Y', 'scan point']}
        self._cube_axes_map = {'real': {0: 2,
                                        1: 1,
                                        2: 0}}

        self._data['scanned_values'] = []

        self._correction = None

        scan_data = opened_file['scan']['data']
        for key in scan_data.keys():
            if key == 'lmbd':
                self._detector = 'lmbd'
                self._detector_folder = os.path.join(os.path.dirname(opened_file.filename),
                                                     os.path.splitext(os.path.basename(opened_file.filename))[0], 'lmbd')

                self._last_loaded_file = ''
                self._reload_detector_data()

            elif len(scan_data[key].shape) > 1:
                self._detector = key
                self._data['cube_key'] = key
                self._data['cube_shape'] = scan_data[key].shape
                if MEMORY_MODE == 'ram':
                    self._3d_cube = np.array(scan_data[key][...], dtype=np.float32)

        for key in scan_data.keys():
            if key != 'lmbd' and len(scan_data[key].shape) == 1:
                if len(scan_data[key][...]) == self._data['cube_shape'][0]:
                    self._data['scanned_values'].append(key)
                    self._data[key] = np.array(scan_data[key][...])

        if 'point_nb' not in self._data['scanned_values']:
            self._data['scanned_values'].append('point_nb')
            self._data['point_nb'] = np.arange(self._data['cube_shape'][0])

        pass

    # ----------------------------------------------------------------------
    def _reload_detector_data(self, reload=True):

        file_lists = [f for f in os.listdir(self._detector_folder) if f.endswith('.nxs')]

        self._data['cube_shape'] = (0, 0, 0)
        if len(file_lists) > 0:
            if reload or MEMORY_MODE == 'disk':
                self._3d_cube = None
                source_file = h5py.File(os.path.join(self._detector_folder, file_lists[0]), 'r')
                data = np.array(source_file['entry']['instrument']['detector']['data'], dtype=np.float32)
                try:
                    self._attached_mask = \
                        np.array(source_file['entry']['instrument']['detector']['pixel_mask'])[0, :, :]
                except:
                    print('Cannot load mask!')
                    self._attached_mask = None
                name = file_lists[0]

                for name in file_lists[1:]:
                    source_file = h5py.File(os.path.join(self._detector_folder, name), 'r')
                    data = np.vstack((data, np.array(source_file['entry']['instrument']['detector']['data'],
                                                     dtype=np.float32)))

                self._data['cube_shape'] = data.shape
                if MEMORY_MODE == 'ram':
                    self._3d_cube = data
            else:
                name = self._last_loaded_file
                start_ind = file_lists.index(self._last_loaded_file)
                for name in file_lists[start_ind:]:
                    source_file = h5py.File(os.path.join(self._detector_folder, name), 'r')
                    self._3d_cube = np.vstack((self._3d_cube,
                                               np.array(source_file['entry']['instrument']['detector']['data'],
                                                        dtype=np.float32)))

                self._data['cube_shape'] = self._3d_cube.shape

            self._last_loaded_file = name

    # ----------------------------------------------------------------------
    def get_scan_parameters(self):
        return self._data['scanned_values']

    # ----------------------------------------------------------------------
    def get_axis_limits(self, space):

        new_limits = {}
        if space == 'real':
            new_limits[0] = [0, self._data['cube_shape'][2]-1]
            new_limits[1] = [0, self._data['cube_shape'][1]-1]
            if SETTINGS['displayed_param'] in self._data['scanned_values']:
                new_limits[2] = [min(self._data[SETTINGS['displayed_param']]),
                                 max(self._data[SETTINGS['displayed_param']])]
            else:
                new_limits[2] = [0, 0]

        return new_limits

    # ----------------------------------------------------------------------
    def get_scan_params(self):
        return self._data['scanned_values']

    # ----------------------------------------------------------------------
    def get_value_at_point(self, space, axis, pos):
        if space == 'real':
            real_axis = self._cube_axes_map[space][axis]
            if real_axis == 0:
                if SETTINGS['displayed_param'] in self._data['scanned_values']:
                    if 0 <= pos < len(self._data[SETTINGS['displayed_param']]):
                        return SETTINGS['displayed_param'], self._data[SETTINGS['displayed_param']][pos]
                return SETTINGS['displayed_param'], np.NaN
            else:
                return self._axes_names['real'][axis], pos

    # ----------------------------------------------------------------------
    def _get_roi_axis(self, plot_axis):
        if plot_axis == 0:
            if SETTINGS['displayed_param'] in self._data['scanned_values']:
                return self._data[SETTINGS['displayed_param']]
            else:
                return np.arange(0, self._data['cube_shape'][plot_axis])
        else:
            return np.arange(0, self._data['cube_shape'][plot_axis])

    # ----------------------------------------------------------------------
    def update_settings(self):
        for value in self._data['scanned_values']:
            if value not in SETTINGS['all_params']:
                SETTINGS['all_params'].append(value)

    # ----------------------------------------------------------------------
    def apply_settings(self):

        if SETTINGS['mask_mode'] == 'attached' and self._attached_mask is not None:
            self._pixel_mask = self._attached_mask > 0

        elif SETTINGS['mask_mode'] == 'file' and SETTINGS['loaded_mask'] is not None:
            self._pixel_mask = SETTINGS['loaded_mask'] > 0

        else:
            self._pixel_mask = None

        if MEMORY_MODE == 'ram':
            self._reload_detector_data()

            self._correction = np.ones(self._data['cube_shape'][0], dtype=np.float32)

            try:
                if SETTINGS['atten_correction'] == 'on':
                    if SETTINGS['atten_param'] in self._data['scanned_values']:
                        self._correction *= np.maximum(self._data[SETTINGS['atten_param']], 1)
            except Exception as err:
                self._data_pool.main_window.report_error("{}: cannot calculate atten correction: {}".format(self.my_name, err))

            try:
                if SETTINGS['inten_correction'] == 'on':
                    if SETTINGS['inten_param'] in self._data['scanned_values']:
                        self._correction *= np.max((1, self._data[SETTINGS['inten_param']][0]))/\
                                           np.maximum(self._data[SETTINGS['inten_param']], 1)
            except Exception as err:
                self._data_pool.main_window.report_error("{}: cannot calculate inten correction: {}".format(self.my_name, err))

            try:
                if self._pixel_mask is not None:
                    for frame in self._3d_cube:
                        frame[self._pixel_mask] = 0

                for frame, corr in zip(self._3d_cube, self._correction):
                        frame *= corr
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
                with h5py.File(self._original_file, 'r') as f:
                    if cut_axis == 0:
                        if SETTINGS['displayed_param'] not in self._data['scanned_values']:
                            return None
                        data = np.array(f['scan']['data'][self._data['cube_key']][value, :, :], dtype=np.float32)
                        if self._pixel_mask is not None:
                            data[self._pixel_mask] = 0
                        data *= self._correction[value]
                    elif cut_axis == 1:
                        data = f['scan']['data'][self._data['cube_key']][:, value, :]
                        if self._pixel_mask is not None:
                            cut_mask = self._pixel_mask[value, :]
                            for line, corr in zip(data, self._correction):
                                line[cut_mask] = 0
                        for line, corr in zip(data, self._correction):
                            line *= corr
                    else:
                        data = f['scan']['data'][self._data['cube_key']][:, :, value]
                        if self._pixel_mask is not None:
                            cut_mask = self._pixel_mask[:, value]
                            for line, corr in zip(data, self._correction):
                                line[cut_mask] = 0
                        for line, corr in zip(data, self._correction):
                            line *= corr

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
                if plot_axis == 0:
                    if SETTINGS['displayed_param'] not in self._data['scanned_values']:
                        return None, None

                    if cut_axis_1 == 1:
                        cube_cut = self._3d_cube[:,
                                                 sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                                 sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']]
                    else:
                        cube_cut = self._3d_cube[:,
                                                 sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                                 sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']]
                    cube_cut = np.sum(cube_cut, axis=1)
                    cube_cut = np.sum(cube_cut, axis=1)

                elif plot_axis == 1:
                    if cut_axis_1 == 0:
                        cube_cut = self._3d_cube[sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                                 :,
                                                 sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']]
                    else:
                        cube_cut = self._3d_cube[sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                                 :,
                                                 sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']]
                    cube_cut = np.sum(cube_cut, axis=2)
                    cube_cut = np.sum(cube_cut, axis=0)

                else:
                    if cut_axis_1 == 0:
                        cube_cut = self._3d_cube[sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                                 sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                                 :]
                    else:
                        cube_cut = self._3d_cube[sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                                 sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                                 :]
                    cube_cut = np.sum(cube_cut, axis=0)
                    cube_cut = np.sum(cube_cut, axis=0)

            else:
                with h5py.File(self._original_file, 'r') as f:
                    if plot_axis == 0:
                        if cut_axis_1 == 1:
                            cube_cut = np.array(f['scan']['data'][self._data['cube_key']][:,
                                                                                          sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                                                                          sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']],
                                                dtype=np.float32)
                            if self._pixel_mask is not None:
                                mask_cut = self._pixel_mask[sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                                            sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']]
                                for frame in cube_cut:
                                    frame[mask_cut] = 0
                        else:
                            cube_cut = np.array(f['scan']['data'][self._data['cube_key']][:,
                                                                                          sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                                                                          sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']],
                                                dtype=np.float32)
                            if self._pixel_mask is not None:
                                mask_cut = self._pixel_mask[sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                                            sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']]
                                for frame in cube_cut:
                                    frame[mask_cut] = 0

                        cube_cut = np.sum(cube_cut, axis=1)
                        cube_cut = np.sum(cube_cut, axis=1)
                        cube_cut *= self._correction

                    elif plot_axis == 1:
                        if cut_axis_1 == 0:
                            cube_cut = np.array(f['scan']['data'][self._data['cube_key']][sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                                                                          :,
                                                                                          sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']],
                                                dtype=np.float32)
                            if self._pixel_mask is not None:
                                for z in range(sect['roi_2_pos'], sect['roi_2_pos'] + sect['roi_2_width']):
                                    mask_cut = self._pixel_mask[:, z]
                                    for frame, corr in zip(cube_cut, self._correction[sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']]):
                                        frame[mask_cut, z] = 0
                                        frame *= corr
                        else:
                            cube_cut = np.array(f['scan']['data'][self._data['cube_key']][sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                                                                         :,
                                                                                         sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']],
                                                dtype=np.float32)
                            if self._pixel_mask is not None:
                                for z in range(sect['roi_1_pos'], sect['roi_1_pos'] + sect['roi_1_width']):
                                    mask_cut = self._pixel_mask[:, z]
                                    for frame, corr in zip(cube_cut, self._correction[sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']]):
                                        frame[mask_cut, z] = 0
                                        frame *= corr

                        cube_cut = np.sum(cube_cut, axis=2)
                        cube_cut = np.sum(cube_cut, axis=0)

                    else:
                        if cut_axis_1 == 0:
                            cube_cut = np.array(f['scan']['data'][self._data['cube_key']][sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                                                                          sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                                                                          :],
                                                dtype=np.float32)
                            if self._pixel_mask is not None:
                                for y in range(sect['roi_2_pos'], sect['roi_2_pos'] + sect['roi_2_width']):
                                    mask_cut = self._pixel_mask[y, :]
                                    for frame, corr in zip(cube_cut, self._correction[sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']]):
                                        frame[y, mask_cut] = 0
                                        frame *= corr

                        else:
                            cube_cut = np.array(f['scan']['data'][self._data['cube_key']][sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                                                                          sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                                                                          :],
                                                dtype=np.float32)
                            if self._pixel_mask is not None:
                                for y in range(sect['roi_1_pos'], sect['roi_1_pos'] + sect['roi_1_width']):
                                    mask_cut = self._pixel_mask[y, :]
                                    for frame, corr in zip(cube_cut, self._correction[sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']]):
                                        frame[y, mask_cut] = 0
                                        frame *= corr

                        cube_cut = np.sum(cube_cut, axis=0)
                        cube_cut = np.sum(cube_cut, axis=0)

            return self._get_roi_axis(plot_axis), cube_cut

        return None, None

# ----------------------------------------------------------------------
class ASAPOScanSetup(QtWidgets.QWidget):
    """
    settings = {'mask_mode': 'off',
                'loaded_mask': np.array([[], []]),
                'loaded_mask_info': {'file': ''},
                'atten_correction': 'on',
                'atten_param': 'atten',
                'inten_correction': 'on',
                'inten_param': 'eh_c01',
            }
    """

    # ----------------------------------------------------------------------
    def __init__(self, main_window, data_pool):
        """
        """
        super(ASAPOScanSetup, self).__init__()
        self._ui = Ui_LambdaSetup()
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
        elif SETTINGS['mask_mode'] == 'attached':
            self._ui.rb_attached.setChecked(True)
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

        self._ui.cmb_attenuator.addItems(SETTINGS['all_params'])
        self._ui.cmb_attenuator.setEnabled(SETTINGS['atten_correction'] == 'on')
        if SETTINGS['atten_param'] not in SETTINGS['all_params']:
            self._ui.cmb_attenuator.addItem(SETTINGS['atten_param'])
        refresh_combo_box(self._ui.cmb_attenuator, SETTINGS['atten_param'])
        self._ui.rb_atten_on.setChecked(SETTINGS['atten_correction'] == 'on')
        self._ui.rb_atten_off.setChecked(SETTINGS['atten_correction'] == 'off')

        self._ui.cmb_intensity.addItems(SETTINGS['all_params'])
        self._ui.cmb_intensity.setEnabled(SETTINGS['inten_correction'] == 'on')
        if SETTINGS['inten_param'] not in SETTINGS['all_params']:
            self._ui.cmb_intensity.addItem(SETTINGS['inten_param'])
        refresh_combo_box(self._ui.cmb_intensity, SETTINGS['inten_param'])
        self._ui.rb_inten_on.setChecked(SETTINGS['inten_correction'] == 'on')
        self._ui.rb_inten_off.setChecked(SETTINGS['inten_correction'] == 'off')

        self._ui.cmb_z_axis.addItems(SETTINGS['all_params'])
        if SETTINGS['displayed_param'] not in SETTINGS['all_params']:
            self._ui.cmb_z_axis.addItem(SETTINGS['displayed_param'])
        refresh_combo_box(self._ui.cmb_z_axis, SETTINGS['displayed_param'])

        self._ui.bg_intensity.buttonClicked.connect(
            lambda button: self._ui.cmb_intensity.setEnabled(button == self._ui.rb_inten_on))
        self._ui.bg_attenuator.buttonClicked.connect(
            lambda button: self._ui.cmb_attenuator.setEnabled(button == self._ui.rb_atten_on))

        self._ui.bg_mask_option.buttonClicked.connect(self.change_mode)
        self._ui.but_load_mask.clicked.connect(self.load_mask_from_file)

        self._main_plot.scene().sigMouseClicked.connect(self._mouse_clicked)

        try:
            self.restoreGeometry(QtCore.QSettings(APP_NAME).value("{}/geometry".format(WIDGET_NAME)))
        except Exception as err:
            self._main_window.log.error("{} : cannot restore geometry: {}".format(WIDGET_NAME, err))

    # ----------------------------------------------------------------------
    def get_name(self):
        return 'Lambda Scan Setup'

    # ----------------------------------------------------------------------
    def change_mode(self, button):
        self._ui.but_load_mask.setEnabled(False)

        if button == self._ui.rb_no_mask:
            SETTINGS['mask_mode'] = 'off'
            self._plot_2d.clear()
            return

        elif button == self._ui.rb_attached:
            SETTINGS['mask_mode'] = 'attached'
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

        SETTINGS['atten_param'] = str(self._ui.cmb_attenuator.currentText())
        if self._ui.rb_atten_on.isChecked():
            SETTINGS['atten_correction'] = 'on'
        elif self._ui.rb_atten_off.isChecked():
            SETTINGS['atten_correction'] = 'off'

        SETTINGS['inten_param'] = str(self._ui.cmb_intensity.currentText())
        if self._ui.rb_inten_on.isChecked():
            SETTINGS['inten_correction'] = 'on'
        elif self._ui.rb_inten_off.isChecked():
            SETTINGS['inten_correction'] = 'off'

        SETTINGS['displayed_param'] = str(self._ui.cmb_z_axis.currentText())

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
