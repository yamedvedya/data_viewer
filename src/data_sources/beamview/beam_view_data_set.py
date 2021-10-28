# Created by matveyev

import h5py
import os
import re
import numpy as np

from src.data_sources.base_classes.base_data_set import BaseDataSet

SETTINGS = {
            }


class BeamLineView(BaseDataSet):

    # ----------------------------------------------------------------------
    def __init__(self, data_pool, file_name=None):
        super(BeamLineView, self).__init__(data_pool)

        self._original_folder = os.path.dirname(file_name)
        self._file_name = re.split(r"\d+mm", os.path.splitext(os.path.basename(file_name))[0])[0]

        self._axes_names = ['X', 'Y', 'Z']

        self._additional_data['scanned_values'] = ['Z']

        if self._data_pool.memory_mode == 'ram':
            self._nD_data_array = self._get_data()
            self._data_shape = self._nD_data_array.shape
        else:
            self._data_shape = self._get_data_shape()

        self._section = []
        for axis in [0, 1, 2]:
            self._section.append({'axis': axis, 'integration': False,
                                  'min': 0, 'max': self._data_shape[axis] - 1, 'step': 1,
                                  'range_limit': self._data_shape[axis] - 1})

    # ----------------------------------------------------------------------
    def _get_data(self):
        decorated_file_list = self._get_file_list()
        return np.stack([np.loadtxt(os.path.join(self._original_folder, file_name))
                         for _, file_name in decorated_file_list], axis=2)

    # ----------------------------------------------------------------------
    def _get_data_shape(self):
        decorated_file_list = self._get_file_list()
        cube = np.loadtxt(os.path.join(self._original_folder, decorated_file_list[0][1]))

        return cube.shape[0], cube.shape[1], len(decorated_file_list)

    # ----------------------------------------------------------------------
    def _get_file_list(self):
        file_list = [f for f in os.listdir(self._original_folder) if (f.endswith('.dat') and self._file_name in f)]
        decorated_file_list = [(int(f.strip('mm.dat').strip(self._file_name)), f) for f in file_list]
        decorated_file_list.sort()

        self._additional_data['Z'] = np.array([distance for distance, _ in decorated_file_list])

        return decorated_file_list
