# Created by matveyev

import h5py

import numpy as np

from src.data_sources.base_classes.base_data_set import BaseDataSet

SETTINGS = {
            }

class ReciprocalScan(BaseDataSet):

    # ----------------------------------------------------------------------
    def __init__(self, data_pool, file_name=None, opened_file=None, gridder=None):
        super(ReciprocalScan, self).__init__(data_pool)

        self._original_file = file_name
        self._axes_names = ['Qx', 'Qy', 'Qz']

        self._additional_data['scanned_values'] = ['Qz']

        if gridder is not None:
            self._x_axis = np.copy(gridder.xaxis)
            self._y_axis = np.copy(gridder.yaxis)
            self._z_axis = np.copy(gridder.zaxis)
            self._nD_data_array = np.copy(gridder.data)

        elif opened_file is not None:
            if self._data_pool.memory_mode == 'ram':
                self._nD_data_array = self._get_data()
                self._data_shape = self._nD_data_array.shape
            else:
                self._data_shape = self._get_data_shape()

        self._additional_data['Qz'] = np.arange(self._data_shape[0])

        self._section = ({'axis': 0, 'mode': 'single', 'min': 0, 'max': self._x_axis[-1],
                          'step': self._x_axis[1] - self._x_axis[0]},
                         {'axis': 1, 'mode': 'single', 'min': 0, 'max': self._y_axis[-1],
                          'step': self._y_axis[1] - self._y_axis[0]},
                         {'axis': 2, 'mode': 'single', 'min': 0, 'max': self._z_axis[-1],
                          'step': self._z_axis[1] - self._z_axis[0]})

    # ----------------------------------------------------------------------
    def _get_data(self):
        source_file = h5py.File(self._original_file, 'r')
        self._x_axis = np.copy(source_file['reciprocal_scan']['x_axis'])
        self._y_axis = np.copy(source_file['reciprocal_scan']['y_axis'])
        self._z_axis = np.copy(source_file['reciprocal_scan']['z_axis'])
        return np.array(source_file['reciprocal_scan']['3d_cube'], dtype=np.float32)

    # ----------------------------------------------------------------------
    def _get_data_shape(self):
        source_file = h5py.File(self._original_file, 'r')
        return len(source_file['reciprocal_scan']['x_axis']), len(source_file['reciprocal_scan']['y_axis']), \
               len(source_file['reciprocal_scan']['z_axis'])
    
    # ----------------------------------------------------------------------
    def save_file(self, file_name):

        with h5py.File(file_name, 'w') as hf:
            group = hf.create_group('reciprocal_scan')
            group.create_dataset('x_axis', data=self._x_axis)
            group.create_dataset('y_axis', data=self._y_axis)
            group.create_dataset('z_axis', data=self._z_axis)
            group.create_dataset('3d_cube', data=self._nD_data_array)
