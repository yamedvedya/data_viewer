# Created by matveyev at 18.02.2021

import h5py
import os

import numpy as np

from src.utils.fio_reader import fioReader
from src.data_sources.base_classes.base_2d_detector import Base2DDetectorDataSet

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


class SardanaDataSet(Base2DDetectorDataSet):

    # ----------------------------------------------------------------------
    def __init__(self, data_pool, file_name, opened_file):
        super(SardanaDataSet, self).__init__(data_pool)

        self.my_name = os.path.splitext(os.path.basename(file_name))[0]

        self._original_file = file_name
        self._axes_names = ['scan point', 'detector X', 'detector Y']

        self._additional_data['scanned_values'] = []
        scan_data = opened_file['scan']['data']

        # first we load scan data from .fio
        if os.path.isfile(os.path.splitext(file_name)[0] + '.fio'):
            fio_file = fioReader(os.path.splitext(file_name)[0] + '.fio')
            for key, value in fio_file.parameters.items():
                try:
                    self._additional_data[key] = float(value)
                except:
                    self._additional_data[key] = value

        # if user did ct after scan, Lambda saves ten as scan frames, we ignore them
        self._scan_length = None
        for key in scan_data.keys():

            # if this is 1D array - we add it to possible scan axes
            if key != 'lmbd' and len(scan_data[key].shape) == 1:
                if self._scan_length is None:
                    self._scan_length = len(scan_data[key][...])
                if len(scan_data[key][...]) == self._scan_length:
                    self._additional_data['scanned_values'].append(key)
                self._additional_data[key] = np.array(scan_data[key][...])

        for key in scan_data.keys():
            # up to now only one type of scans - Lambda scans
            if key == 'lmbd':
                self._detector = 'lmbd'
                self._detector_folder = os.path.join(os.path.dirname(opened_file.filename),
                                                     os.path.splitext(os.path.basename(opened_file.filename))[0], 'lmbd')

                if self._data_pool.memory_mode == 'ram':
                    self._nD_data_array = self._get_data()
                    self._data_shape = self._nD_data_array.shape
                else:
                    self._data_shape = self._get_data_shape()

        # point_nb - default axis, had to always be, it not - add it
        if 'point_nb' not in self._additional_data['scanned_values']:
            self._additional_data['scanned_values'].append('point_nb')
            self._additional_data['point_nb'] = np.arange(self._data_shape[0])

        self._section = ({'axis': '', 'integration': False, 'min': 0, 'max': self._data_shape[0] - 1, 'step': 1,
                          'range_limit': self._data_shape[0] - 1},
                         {'axis': 'X', 'integration': False, 'min': 0, 'max': self._data_shape[1] - 1, 'step': 1,
                          'range_limit': self._data_shape[1] - 1},
                         {'axis': 'Y', 'integration': False, 'min': 0, 'max': self._data_shape[2] - 1, 'step': 1,
                          'range_limit': self._data_shape[2] - 1})

    # ----------------------------------------------------------------------
    def check_file_after_load(self):

        for value in self._additional_data['scanned_values']:
            if value not in SETTINGS['all_params']:
                SETTINGS['all_params'].append(value)

    # ----------------------------------------------------------------------
    def _get_settings(self):
        return SETTINGS

    # ----------------------------------------------------------------------
    def _reload_data(self, frame_ids=None):
        """
        reloads sardana data
        :param frame_ids: if not None: frames to be loaded
        :return: np.array, 3D data cube
        """

        file_lists = [f for f in os.listdir(self._detector_folder) if f.endswith('.nxs')]
        file_lists.sort()

        if len(file_lists) > 0:
            if frame_ids is not None:
                files_to_load = [file_lists[frame_ids[0]]]
                for frame in frame_ids[1:]:
                    try:
                        files_to_load.append(file_lists[frame_ids[frame]])
                    except:
                        pass
                _need_cut = False
            else:
                files_to_load = file_lists
                _need_cut = True

            source_file = h5py.File(os.path.join(self._detector_folder, files_to_load[0]), 'r')
            cube = np.array(source_file['entry']['instrument']['detector']['data'], dtype=np.float32)

            for name in files_to_load[1:]:
                source_file = h5py.File(os.path.join(self._detector_folder, name), 'r')
                cube = np.vstack((cube, np.array(source_file['entry']['instrument']['detector']['data'],
                                                 dtype=np.float32)))

            if _need_cut:
                cube = cube[:self._scan_length, :, :]

            return np.array(cube, dtype=np.float32)
        else:
            raise RuntimeError('No lmbd file found')

    # ----------------------------------------------------------------------
    def _get_data_shape(self):
        """
        in case user select 'disk' mode (data is not kept in memory) - we calculate data shape without loading all data
        :return: tuple with data shape
        """

        file_lists = [f for f in os.listdir(self._detector_folder) if f.endswith('.nxs')]
        file_lists.sort()

        if len(file_lists) > 1:
            frame = self._reload_data([0])
            return len(file_lists), frame[0], frame[1]
        else:
            source_file = h5py.File(os.path.join(self._detector_folder, file_lists[0]), 'r')
            return source_file['entry']['instrument']['detector']['data'].shape

    # ----------------------------------------------------------------------
    def get_value_for_frame(self, axis, pos):

        real_axis = self._cube_axes_map[axis]
        if real_axis == 0:
            if SETTINGS['displayed_param'] in self._additional_data['scanned_values']:
                if 0 <= pos < len(self._additional_data[SETTINGS['displayed_param']]):
                    return SETTINGS['displayed_param'], self._additional_data[SETTINGS['displayed_param']][pos]
            return SETTINGS['displayed_param'], np.NaN
        else:
            return self._axes_names[axis], pos

    # ----------------------------------------------------------------------
    def _get_roi_axis(self, plot_axis):

        if plot_axis == 0:
            if SETTINGS['displayed_param'] in self._additional_data['scanned_values']:
                return self._additional_data[SETTINGS['displayed_param']]
            else:
                return np.arange(0, self._data_shape[plot_axis])
        else:
            return np.arange(0, self._data_shape[plot_axis])

    # ----------------------------------------------------------------------
    def _calculate_correction(self, data_shape, frame_ids=None):

        self._correction = np.ones(data_shape[0], dtype=np.float32)

        try:
            if SETTINGS['atten_correction'] == 'on':
                if SETTINGS['atten_param'] in self._additional_data['scanned_values']:
                    if frame_ids is not None:
                        self._correction *= np.maximum(self._additional_data[SETTINGS['atten_param']][frame_ids], 1)
                    else:
                        self._correction *= np.maximum(self._additional_data[SETTINGS['atten_param']], 1)
        except Exception as err:
            raise RuntimeError("{}: cannot calculate atten correction: {}".format(self.my_name, err))

        try:
            if SETTINGS['inten_correction'] == 'on':
                if SETTINGS['inten_param'] in self._additional_data['scanned_values']:
                    if frame_ids is not None:
                        self._correction *= np.max((1, self._additional_data[SETTINGS['inten_param']][0])) / \
                                            np.maximum(self._additional_data[SETTINGS['inten_param']][frame_ids], 1)
                    else:
                        self._correction *= np.max((1, self._additional_data[SETTINGS['inten_param']][0])) / \
                                            np.maximum(self._additional_data[SETTINGS['inten_param']], 1)

        except Exception as err:
            raise RuntimeError("{}: cannot calculate inten correction: {}".format(self.my_name, err))

    # ----------------------------------------------------------------------
    def apply_settings(self):

        self._need_apply_mask = True

    # ----------------------------------------------------------------------
    def get_2d_picture(self):

        if SETTINGS['displayed_param'] not in self._additional_data['scanned_values']:
            return None

        return super(SardanaDataSet, self).get_2d_picture()

    # ----------------------------------------------------------------------
    def get_roi_cut(self, sect, do_sum=False):

        if SETTINGS['displayed_param'] not in self._additional_data['scanned_values']:
            return None, None

        return super(SardanaDataSet, self).get_roi_cut(sect, do_sum)

    # ----------------------------------------------------------------------
    def get_roi_plot(self, sect):

        if SETTINGS['displayed_param'] not in self._additional_data['scanned_values']:
            return None, None

        return super(SardanaDataSet, self).get_roi_plot(sect)


# ----------------------------------------------------------------------
