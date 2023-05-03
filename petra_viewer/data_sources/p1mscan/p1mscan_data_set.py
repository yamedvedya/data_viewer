# Created by matveyev at 03.05.2023

import h5py
import fabio
import os

import numpy as np

from petra_viewer.data_sources.base_classes.base_2d_detector import Base2DDetectorDataSet, apply_base_settings, BASE_SETTINGS

EXTENSION = ".cbf"

SETTINGS = {'door_address': None,
            'atten_correction': True,
            'atten_param': 'atten',
            'inten_correction': True,
            'inten_param': 'eh_c01',
            'all_params': []
            }

SETTINGS.update(dict(BASE_SETTINGS))


# ----------------------------------------------------------------------
def apply_settings_p1mscan(settings):
    if 'door_address' in settings:
        SETTINGS['door_address'] = settings['door_address']
    else:
        SETTINGS['door_address'] = None

    for param, param2, default in zip(['atten_param', 'inten_param'],
                                      ['atten_correction', 'inten_correction'],
                                      ['atten', 'eh_c01']):
        if param in settings:
            SETTINGS[param] = settings[param]
            SETTINGS[param2] = True
        else:
            SETTINGS[param] = default
            SETTINGS[param2] = False

    apply_base_settings(settings, SETTINGS)


# ----------------------------------------------------------------------
class P1MScanDataSet(Base2DDetectorDataSet):

    # ----------------------------------------------------------------------
    def __init__(self, data_pool, file_name):
        super(P1MScanDataSet, self).__init__(data_pool)

        self.my_folder = os.path.dirname(file_name)
        self.base_name = "_".join(os.path.splitext(os.path.basename(file_name))[0].split("_")[:-1])

        self._possible_axes_units = [{}, {}, {}]

        if self._data_pool.memory_mode == 'ram':
            self._nD_data_array = self._get_data()
            self._data_shape = self._nD_data_array.shape
        else:
            self._data_shape = self._get_data_shape()

        self._possible_axes_units[0] = {'point_nb': np.arange(self._data_shape[0])}
        self._possible_axes_units[1] = {'detector Y': np.arange(self._data_shape[1])}
        self._possible_axes_units[2] = {'detector X': np.arange(self._data_shape[2])}

        self._axes_units = ['point_nb', 'detector Y', 'detector X']
        self._axis_units_is_valid = [True, True, True]

    # ----------------------------------------------------------------------
    def _set_default_section(self):
        self._section = ({'axis': 'Z', 'integration': False, 'min': 0, 'max': self._data_shape[0] - 1, 'step': 1,
                          'range_limit': self._data_shape[0]},
                         {'axis': 'Y', 'integration': False, 'min': 0, 'max': self._data_shape[1] - 1, 'step': 1,
                          'range_limit': self._data_shape[1]},
                         {'axis': 'X', 'integration': False, 'min': 0, 'max': self._data_shape[2] - 1, 'step': 1,
                          'range_limit': self._data_shape[2]})

    # ----------------------------------------------------------------------
    def _get_settings(self):
        return SETTINGS

    # ----------------------------------------------------------------------
    def get_metadata(self):

        return self._additional_data

    # ----------------------------------------------------------------------
    def _reload_data(self, frame_ids=None):
        """
        reloads p23scan data
        :param frame_ids: if not None: frames to be loaded
        :return: np.array, 3D data cube
        """

        file_lists = self._get_file_list()

        if len(file_lists) > 0:
            if frame_ids is not None:
                files_to_load = [file_lists[frame_ids[0]]]
                for frame in frame_ids[1:]:
                    files_to_load.append(file_lists[frame_ids[frame]])
            else:
                files_to_load = file_lists

            cube = np.array(fabio.open(os.path.join(self.my_folder, files_to_load[0])).data,
                            dtype=np.float32)[np.newaxis, :]

            for name in files_to_load[1:]:
                cube = np.vstack((cube,
                                  np.array(fabio.open(os.path.join(self.my_folder, name)).data,
                                           dtype=np.float32)[np.newaxis, :]))

            return cube
        else:
            raise RuntimeError('No p1m file found')

    # ----------------------------------------------------------------------
    def _get_data_shape(self):
        """
        in case user select 'disk' mode (data is not kept in memory) - we calculate data shape without loading all data
        :return: tuple with data shape
        """

        file_lists = self._get_file_list()
        frame = self._reload_data([0])
        return len(file_lists), frame[0], frame[1]

    # ----------------------------------------------------------------------
    def _get_file_list(self):
        file_lists = [f for f in os.listdir(self.my_folder) if f.endswith(EXTENSION) and self.base_name in f]
        file_lists.sort()

        return file_lists

    # ----------------------------------------------------------------------
    def _calculate_correction(self, data_shape, frame_ids):

        self._correction = np.ones(data_shape[0], dtype=np.float32)

        try:
            if SETTINGS['atten_correction']:
                if SETTINGS['atten_param'] in self._possible_axes_units[0]:
                    if frame_ids is not None:
                        self._correction *= np.maximum(self._possible_axes_units[0][SETTINGS['atten_param']][frame_ids], 1)
                    else:
                        self._correction *= np.maximum(self._possible_axes_units[0][SETTINGS['atten_param']], 1)
        except Exception as err:
            raise RuntimeError("{}: cannot calculate atten correction: {}".format(self.my_name, err))

        try:
            if SETTINGS['inten_correction']:
                if SETTINGS['inten_param'] in self._possible_axes_units[0]:
                    if frame_ids is not None:
                        self._correction *= np.max((1, self._possible_axes_units[0][SETTINGS['inten_param']][0])) / \
                                            np.maximum(self._possible_axes_units[0][SETTINGS['inten_param']][frame_ids], 1)
                    else:
                        self._correction *= np.max((1, self._possible_axes_units[0][SETTINGS['inten_param']][0])) / \
                                            np.maximum(self._possible_axes_units[0][SETTINGS['inten_param']], 1)

        except Exception as err:
            raise RuntimeError("{}: cannot calculate inten correction: {}".format(self.my_name, err))

    # ----------------------------------------------------------------------
    def _corrections_required(self):
        if super(P1MScanDataSet, self)._corrections_required():
            return True

        if SETTINGS['atten_correction']:
            return True

        if SETTINGS['inten_correction']:
            return True

        return False

