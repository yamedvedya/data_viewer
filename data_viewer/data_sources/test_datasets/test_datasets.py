# Created by matveyev at 09.11.2021

import numpy as np
import configparser

from data_viewer.data_sources.sardana.sardana_data_set import SardanaDataSet
from data_viewer.data_sources.asapo.asapo_data_set import ASAPODataSet

__all__ = ['Sardana3DSin', 'Sardana3DPeak', 'ASAPO2DPeak', 'ASAPO3DPeak']

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

        self._section = ({'axis': '', 'integration': False, 'min': 0, 'max': self._data_shape[0] - 1, 'step': 1,
                          'range_limit': self._data_shape[0]},
                         {'axis': 'Y', 'integration': False, 'min': 0, 'max': self._data_shape[1] - 1, 'step': 1,
                          'range_limit': self._data_shape[1]},
                         {'axis': 'X', 'integration': False, 'min': 0, 'max': self._data_shape[2] - 1, 'step': 1,
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


# --------------------------------------------------------------------
class __FakeNDASAPO(ASAPODataSet):

    dims = []

    my_name = None

    # ----------------------------------------------------------------------
    def __init__(self, data_pool):
        super(ASAPODataSet, self).__init__(data_pool)

        settings = configparser.ConfigParser()
        settings.read('./settings.ini')
        self.max_messages = int(settings['ASAPO']['max_messages'])

        self.__original_data = self._generate_fake_data()

        if self._data_pool.memory_mode == 'ram':
            self._nD_data_array = self._get_data()
            self._data_shape = list(self._nD_data_array.shape)
        else:
            self._data_shape = self._get_data_shape()

        self._axes_names = ['message_ID'] + [f'dim_{i}' for i in range(1, len(self._data_shape))]

        self._additional_data['metadata'] = [{'_id': ind, 'data_source': self.my_name}
                                             for ind in range(self._data_shape[0])]

        self._additional_data['already_loaded_ids'] = list(range(self._data_shape[0]))

        self._additional_data['frame_ID'] = np.arange(self._data_shape[0])
        self._additional_data['scanned_values'] = ['frame_ID']

        self._section = []
        axis = ['' for _ in range(len(self._data_shape))]
        axis[-1] = 'X'
        if len(axis) > 1:
            axis[-2] = 'Y'
        if len(axis) > 2:
            axis[-3] = 'Z'

        for i, axis in enumerate(axis):
            if i == 0:
                range_limit = self.max_messages
            else:
                range_limit = 0
            self._section.append({'axis': axis, 'integration': False, 'min': 0, 'max': self._data_shape[i] - 1,
                                  'step': 1, 'range_limit': range_limit})

    # ----------------------------------------------------------------------
    def _reload_data(self, frame_ids=None):
        if frame_ids is None:
            return np.copy(self.__original_data)
        else:
            return np.copy(self.__original_data[frame_ids])

    # ----------------------------------------------------------------------
    def _get_data_shape(self):

        return self.dims

    # ----------------------------------------------------------------------
    def _generate_fake_data(self):
        raise RuntimeError('Not implemented')

    # ----------------------------------------------------------------------
    def get_info(self):
        return self.my_name, f'{len(self.dims)}D', 'x'.join([str(dim) for dim in self.dims])


# ----------------------------------------------------------------------
class ASAPO2DPeak(__FakeNDASAPO):

    dims = [101, 151]

    my_name = 'ASAPO2DPeak'

    # ----------------------------------------------------------------------
    def _generate_fake_data(self):
        y, x = np.meshgrid(np.linspace(-75, 75, 151), np.linspace(-50, 50, 101))

        mean, sigma = 2, 6
        data_cube = np.exp(-((np.sqrt(x * x + y * y * 4) - mean) ** 2 / (2.0 * sigma ** 2))) * 100

        data_cube -= np.min(data_cube)

        return data_cube


# ----------------------------------------------------------------------
class ASAPO3DPeak(__FakeNDASAPO):

    dims = [21, 101, 151]

    my_name = 'ASAPO3DPeak'

    # ----------------------------------------------------------------------
    def _generate_fake_data(self):

        y, x = np.meshgrid(np.linspace(-75, 75, 151), np.linspace(-50, 50, 101))

        mean, sigma = 2, 6
        frame = np.exp(-((np.sqrt(x * x + y * y * 4) - mean) ** 2 / (2.0 * sigma ** 2)))*100

        data_cube = np.zeros(self.dims)
        for ind, scale in enumerate(np.power(np.sin(np.linspace(0, np.pi, self.dims[0])), 4)):
            data_cube[ind] = frame * scale

        data_cube -= np.min(data_cube)

        return data_cube