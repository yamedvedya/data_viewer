# Created by matveyev at 18.02.2021

MEMORY_MODE = 'ram' #'disk' or 'ram'

WIDGET_NAME = 'LambdaScanSetup'

import h5py
import os

import numpy as np

from src.gui.lambda_setup_ui import Ui_LambdaSetup
from src.utils.utils import refresh_combo_box
from src.data_sources.abstract_data_file import AbstractDataFile
from src.data_sources.abstract_2d_detector import DetectorImage, DetectorImageSetup, MEMORY_MODE

SETTINGS = {'enable_mask': False,
            'mask': None,
            'mask_file': '',
            'enable_ff': False,
            'ff': None,
            'ff_file': '',
            'ff_min': 0,
            'ff_max': 100,
            'enable_fill': False,
            'fill_radius': 7,
            'displayed_param': 'point_nb',
            'all_params': [],
            'atten_correction': 'on',
            'atten_param': 'atten',
            'inten_correction': 'on',
            'inten_param': 'eh_c01',
            }


class LambdaScan(AbstractDataFile, DetectorImage):

    # ----------------------------------------------------------------------
    def __init__(self, file_name, data_pool, opened_file):
        super(LambdaScan, self).__init__(data_pool)

        self.my_name = os.path.splitext(os.path.basename(file_name))[0]

        self._original_file = file_name
        self._spaces = ['real']
        self._axes_names = {'real': ['detector X', 'detector Y', 'scan point']}
        self._cube_axes_map = {'real': {0: 2,
                                        1: 1,
                                        2: 0}}

        self._data['scanned_values'] = []
        scan_data = opened_file['scan']['data']

        #TODO: TEMP! Fix scans!
        self._scan_length = None
        for key in scan_data.keys():
            if key != 'lmbd' and len(scan_data[key].shape) == 1:
                if self._scan_length is None:
                    self._scan_length = len(scan_data[key][...])
                if len(scan_data[key][...]) == self._scan_length:
                    self._data['scanned_values'].append(key)
                    self._data[key] = np.array(scan_data[key][...])

        for key in scan_data.keys():
            if key == 'lmbd':
                self._detector = 'lmbd'
                self._detector_folder = os.path.join(os.path.dirname(opened_file.filename),
                                                     os.path.splitext(os.path.basename(opened_file.filename))[0], 'lmbd')

                self._need_apply_mask = True
                cube = self._get_data()
                self._data['cube_shape'] = cube.shape

                if MEMORY_MODE == 'ram':
                    self._3d_cube = cube

        if 'point_nb' not in self._data['scanned_values']:
            self._data['scanned_values'].append('point_nb')
            self._data['point_nb'] = np.arange(self._data['cube_shape'][0])

    # ----------------------------------------------------------------------
    def _get_settings(self):
        return SETTINGS

    # ----------------------------------------------------------------------
    def _reload_data(self):

        file_lists = [f for f in os.listdir(self._detector_folder) if f.endswith('.nxs')]
        file_lists.sort()

        if len(file_lists) > 0:
            source_file = h5py.File(os.path.join(self._detector_folder, file_lists[0]), 'r')
            cube = np.array(source_file['entry']['instrument']['detector']['data'], dtype=np.float32)

            for name in file_lists[1:]:
                source_file = h5py.File(os.path.join(self._detector_folder, name), 'r')
                cube = np.vstack((cube, np.array(source_file['entry']['instrument']['detector']['data'],
                                                 dtype=np.float32)))

            cube = cube[:self._scan_length, :, :]
            return np.array(cube, dtype=np.float32)

        else:
            raise RuntimeError('No lmbd file found')

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
    def _get_correction(self):

        self._correction = np.ones(self._data['cube_shape'][0], dtype=np.float32)

        try:
            if SETTINGS['atten_correction'] == 'on':
                if SETTINGS['atten_param'] in self._data['scanned_values']:
                    self._correction *= np.maximum(self._data[SETTINGS['atten_param']], 1)
        except Exception as err:
            if self._data_pool is not None:
                self._data_pool.report_error("{}: cannot calculate atten correction: {}".format(self.my_name, err))

        try:
            if SETTINGS['inten_correction'] == 'on':
                if SETTINGS['inten_param'] in self._data['scanned_values']:
                    self._correction *= np.max((1, self._data[SETTINGS['inten_param']][0])) / \
                                        np.maximum(self._data[SETTINGS['inten_param']], 1)

        except Exception as err:
            if self._data_pool is not None:
                self._data_pool.report_error("{}: cannot calculate inten correction: {}".format(self.my_name, err))

    # ----------------------------------------------------------------------
    def apply_settings(self):

        self._need_apply_mask = True

    # ----------------------------------------------------------------------
    def get_2d_cut(self, space, axis, value, x_axis, y_axis):

        if SETTINGS['displayed_param'] not in self._data['scanned_values']:
            return None

        return self._get_image(space, axis, value, x_axis, y_axis)

    # ----------------------------------------------------------------------
    def get_roi_plot(self, space, sect):

        if SETTINGS['displayed_param'] not in self._data['scanned_values']:
            return None, None

        return self._get_plot(space, sect)

# ----------------------------------------------------------------------
class LambdaScanSetup(DetectorImageSetup):
    """
    SETTINGS = {'enable_mask': False,
                'loaded_mask': None,
                'loaded_mask_info': {'file': ''},
                'enable_ff': False,
                'loaded_ff': None,
                'loaded_ff_info': {'file': ''},
                'enable_fill': False,
                'fill_radius': 7,
                'atten_correction': 'on',
                'atten_param': 'atten',
                'inten_correction': 'on',
                'inten_param': 'eh_c01',
                'displayed_param': 'point_nb',
                'all_params': [],
                }
    """

    # ----------------------------------------------------------------------
    def __init__(self, main_window, data_pool):
        """
        """
        super(LambdaScanSetup, self).__init__( main_window, data_pool)

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

    # ----------------------------------------------------------------------
    def _get_ui(self):

        return Ui_LambdaSetup()

    # ----------------------------------------------------------------------
    def get_name(self):
        return 'Lambda Scan Setup'

    # ----------------------------------------------------------------------
    def get_settings(self):

        return SETTINGS

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

        super(LambdaScanSetup, self).accept()
