# Created by matveyev at 09.11.2021

import numpy as np

from src.data_sources.sardana.sardana_data_set import SardanaDataSet

__all__ = ['Sardana3DSin', 'Sardana3DPeak']

# # --------------------------------------------------------------------
# class __TestDataSet(object):
#     pass


# --------------------------------------------------------------------
class __Fake3DSardana(SardanaDataSet):

    x_dim = None
    y_dim = None
    z_dim = None

    my_name = None

    # ----------------------------------------------------------------------
    def __init__(self, data_pool):
        super(SardanaDataSet, self).__init__(data_pool)

        self._axes_names = ['scan point', 'detector X', 'detector Y']

        self._additional_data['scanned_values'] = ['omega', 'point_nb']
        self._additional_data['omega'] = np.linspace(1, 2, self.z_dim)
        self._additional_data['point_nb'] = np.arange(self.z_dim)

        self.__original_data = self._generate_fake_data()

        if self._data_pool.memory_mode == 'ram':
            self._nD_data_array = self._get_data()
            self._data_shape = self._nD_data_array.shape
        else:
            self._data_shape = self._get_data_shape()

        self._section = ({'axis': '', 'integration': False, 'min': 0, 'max': self._data_shape[0], 'step': 1,
                          'range_limit': self._data_shape[0]},
                         {'axis': 'Y', 'integration': False, 'min': 0, 'max': self._data_shape[1], 'step': 1,
                          'range_limit': self._data_shape[1]},
                         {'axis': 'X', 'integration': False, 'min': 0, 'max': self._data_shape[2], 'step': 1,
                          'range_limit': self._data_shape[2]})

    # ----------------------------------------------------------------------
    def _reload_data(self, frame_ids=None):
        if frame_ids is None:
            return np.copy(self.__original_data)
        else:
            return np.copy(self.__original_data[frame_ids])

    # ----------------------------------------------------------------------
    def _get_data_shape(self):

        return self.z_dim, self.y_dim, self.x_dim

    # ----------------------------------------------------------------------
    def _generate_fake_data(self):
        raise RuntimeError('Not implemented')

    # ----------------------------------------------------------------------
    def get_info(self):
        return self.my_name, '3D', f'{self.z_dim}x{self.y_dim}x{self.x_dim}'


# ----------------------------------------------------------------------
class Sardana3DSin(__Fake3DSardana):

    x_dim = 200
    y_dim = 100
    z_dim = 11

    my_name = 'Sardana3DSin'

    # ----------------------------------------------------------------------
    def _generate_fake_data(self):

        frame = np.zeros((self.y_dim, self.x_dim))
        for ind in range(self.y_dim):
            frame[ind] = np.sin(np.linspace(0, np.pi, self.x_dim))
        for ind in range(self.x_dim):
            frame[:, ind] *= np.sin(np.linspace(0, np.pi, self.y_dim))

        data_cube = np.zeros((self.z_dim, self.y_dim, self.x_dim))
        for ind, scale in enumerate(np.sin(np.linspace(0, np.pi, self.z_dim))):
            data_cube[ind] = frame * scale

        data_cube -= np.min(data_cube)

        return data_cube


# ----------------------------------------------------------------------
class Sardana3DPeak(__Fake3DSardana):

    x_dim = 151
    y_dim = 101
    z_dim = 21

    my_name = 'Sardana3DPeak'

    # ----------------------------------------------------------------------
    def _generate_fake_data(self):

        y, x = np.meshgrid(np.linspace(-75, 75, 151), np.linspace(-50, 50, 101))

        mean, sigma = 2, 6
        frame = np.exp(-((np.sqrt(x * x + y * y * 4) - mean) ** 2 / (2.0 * sigma ** 2)))*100

        data_cube = np.zeros((self.z_dim, self.y_dim, self.x_dim))
        for ind, scale in enumerate(np.power(np.sin(np.linspace(0, np.pi, self.z_dim)), 4)):
            data_cube[ind] = frame * scale

        data_cube -= np.min(data_cube)

        return data_cube