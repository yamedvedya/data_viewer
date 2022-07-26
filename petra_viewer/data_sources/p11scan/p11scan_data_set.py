# Created by matveyev at 18.02.2021

import h5py
import os
import logging

import numpy as np


from petra_viewer.main_window import APP_NAME
from petra_viewer.data_sources.base_classes.base_2d_detector import Base2DDetectorDataSet

logger = logging.getLogger(APP_NAME)


# ----------------------------------------------------------------------
class P11ScanDataSet(Base2DDetectorDataSet):

    MAX_FRAMES_IN_DATASET = 1000
    MAX_FRAMES_IN_BUFFER = 20

    MAX_FRAME_LOAD_IN_CYCLE = 10

    # ----------------------------------------------------------------------
    def __init__(self, data_pool, file_name):
        super(P11ScanDataSet, self).__init__(data_pool)

        self.my_name = os.path.splitext(os.path.basename(file_name))[0]
        self._original_file = file_name
        self._possible_axes_units = [{}, {}, {}]
        self._scan_length = None
        self._additional_data = {}

        self._need_apply_mask = False

        if self._data_pool.memory_mode == 'ram':
            self._nD_data_array = self._get_data()
            self._data_shape = self._nD_data_array.shape
        else:
            self._data_shape = self._get_data_shape()

        with h5py.File(self._original_file, 'r') as opened_file:
            scan_data = opened_file['entry']

            for key in scan_data.keys():
                if key != 'data':
                    self._additional_data[key] = {}
                    self._parce_metadata(scan_data[key], self._additional_data[key])

        self._possible_axes_units[0]['point_nb'] = np.arange(self._data_shape[0])
        self._possible_axes_units[1] = {'detector X': np.arange(self._data_shape[1])}
        self._possible_axes_units[2] = {'detector Y': np.arange(self._data_shape[2])}

        self._axes_units = ['point_nb', 'detector X', 'detector Y']
        self._axis_units_is_valid = [True, True, True]

        self._frames_buffer = {}
        self._frames_in_buffer = []

        print(f'Init finished: self._data_shape: {self._data_shape}')

    # ----------------------------------------------------------------------
    def _parce_metadata(self, entry, branch):
        if isinstance(entry, h5py.Dataset):
            my_name = entry.name.split('/')[-1]
            if len(entry.shape) == 1 and entry.shape[0] == self._data_shape[0]:
                self._possible_axes_units[0][my_name] = entry[()]
            else:
                try:
                    branch[my_name] = entry[()].decode()
                except:
                    branch[my_name] = entry[()]
        else:
            for key in entry.keys():
                branch[key] = {}
                self._parce_metadata(entry[key], branch[key])

    # ----------------------------------------------------------------------
    def _set_default_section(self):
        self._section = ({'axis': 'Z', 'integration': False, 'min': 0, 'max': self._data_shape[0] - 1, 'step': 1,
                          'range_limit': self._data_shape[0]},
                         {'axis': 'Y', 'integration': False, 'min': 0, 'max': self._data_shape[1] - 1, 'step': 1,
                          'range_limit': self._data_shape[1]},
                         {'axis': 'X', 'integration': False, 'min': 0, 'max': self._data_shape[2] - 1, 'step': 1,
                          'range_limit': self._data_shape[2]})

    # ----------------------------------------------------------------------
    def _corrections_required(self):

        return False

    # ----------------------------------------------------------------------
    def apply_corrections(self, data, frame_id=None):

        pass

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

        cube = None

        if frame_ids is None:
            with h5py.File(self._original_file, 'r') as opened_file:
                scan_data = opened_file['entry']['data']
                for data_set in scan_data.keys():
                    if cube is None:
                        cube = np.array(data_set, dtype=np.float32)
                    else:
                        cube = np.concatenate((cube, np.array(data_set, dtype=np.float32)), 0)
            frame_ids = np.arange(cube.shape[0])
        else:
            for frame_id in frame_ids:
                if frame_id in self._frames_buffer:
                    data = self._frames_buffer[frame_id][np.newaxis, :]
                else:
                    with h5py.File(self._original_file, 'r') as opened_file:
                        scan_data = opened_file['entry']['data']
                        dataset = f'data_{(frame_id // self.MAX_FRAMES_IN_DATASET) + 1:06d}'
                        frame_in_dataset = frame_id % self.MAX_FRAMES_IN_DATASET
                        data = np.array(scan_data[dataset][frame_in_dataset], dtype=np.float32)[np.newaxis, :]
                if cube is None:
                    cube = data
                else:
                    cube = np.concatenate((cube, data), 0)

        self._save_data_in_buffer(frame_ids, cube)

        return cube

    # ----------------------------------------------------------------------
    def _get_data_shape(self):
        """
        in case user select 'disk' mode (data is not kept in memory) - we calculate data shape without loading all data
        :return: tuple with data shape
        """

        shape = [0, 0, 0]

        with h5py.File(self._original_file, 'r') as opened_file:
            scan_data = opened_file['entry']['data']
            for data_set in scan_data.keys():
                dataset_shape = scan_data[data_set].shape
                shape[0] += dataset_shape[0]
                shape[1:] = dataset_shape[1:]

        return shape

    # ----------------------------------------------------------------------
    def _save_data_in_buffer(self, frame_ids, data):
        for frame_id, frame in zip(frame_ids, data):
            if frame_id not in self._frames_buffer:
                self._frames_in_buffer.append(frame_id)
                if len(self._frames_in_buffer) > self.MAX_FRAMES_IN_BUFFER:
                    del self._frames_buffer[self._frames_in_buffer.pop(0)]
                self._frames_buffer[frame_id] = frame