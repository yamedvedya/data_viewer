# Created by matveyev at 18.02.2021

import h5py
import os
import logging

import numpy as np


from petra_viewer.main_window import APP_NAME
from petra_viewer.data_sources.base_classes.base_2d_detector import Base2DDetectorDataSet, apply_base_settings, BASE_SETTINGS

SETTINGS = {'max_frames_in_dataset': 1000,
            }

SETTINGS.update(dict(BASE_SETTINGS))


# ----------------------------------------------------------------------
def apply_settings_p11scan(settings):
    if 'max_frames_in_dataset' in settings:
        SETTINGS['max_frames_in_dataset'] = int(settings['max_frames_in_dataset'])

    apply_base_settings(settings, SETTINGS)


logger = logging.getLogger(APP_NAME)


# ----------------------------------------------------------------------
class P11ScanDataSet(Base2DDetectorDataSet):

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

        self._opened_file = None

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
    def _get_settings(self):
        return SETTINGS

    # ----------------------------------------------------------------------
    def get_metadata(self):

        return self._additional_data

    # ----------------------------------------------------------------------
    def _prepare_for_bunch_reading(self):

        if self._opened_file is None:
            self._opened_file = h5py.File(self._original_file, 'r')

    # ----------------------------------------------------------------------
    def _finish_bunch_reading(self):

        if self._opened_file is not None:
            self._opened_file.close()
            self._opened_file = None

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
        else:

            need_to_close = False
            if self._opened_file is None:
                opened_file = h5py.File(self._original_file, 'r')
                need_to_close = True
            else:
                opened_file = self._opened_file
            scan_data = opened_file['entry']['data']

            start_id = frame_ids[0]
            stop_id = frame_ids[-1]

            for frame_id in frame_ids:
                if frame_id in self._frames_buffer:
                    start_id += 1
                    if cube is None:
                        cube = np.copy(self._frames_buffer[frame_id][np.newaxis, :])
                    else:
                        cube = np.concatenate((cube, self._frames_buffer[frame_id][np.newaxis, :]), 0)
                else:
                    break

            # for frame_id in frame_ids[::-1]:
            #     if frame_id in self._frames_buffer:
            #         stop_id -= 1
            #     else:
            #         break

            if stop_id >= start_id:
                reading_finished = False
                while not reading_finished:
                    current_dataset = (start_id // SETTINGS["max_frames_in_dataset"]) + 1
                    start_frame_in_dataset = start_id % SETTINGS["max_frames_in_dataset"]
                    stop_frame_in_dataset = stop_id % SETTINGS["max_frames_in_dataset"]
                    dataset = f'data_{current_dataset:06d}'
                    ids = start_id

                    for ids in np.arange(start_id, stop_id+1):
                        if (ids // SETTINGS["max_frames_in_dataset"]) + 1 != current_dataset:
                            start_id = ids
                            stop_frame_in_dataset = SETTINGS["max_frames_in_dataset"]
                            break

                    data = np.array(scan_data[dataset][start_frame_in_dataset:stop_frame_in_dataset+1],
                                    dtype=np.float32)

                    if len(data.shape) < 3:
                        data = data[np.newaxis, :]

                    if cube is None:
                        cube = data
                    else:
                        cube = np.concatenate((cube, data), 0)

                    reading_finished = ids >= stop_id

            # for frame_id in frame_ids:
            #     if frame_id in self._frames_buffer:
            #         start_id += 1
            #         if cube is None:
            #             cube = np.copy(self._frames_buffer[frame_id][np.newaxis, :])
            #         else:
            #             cube = np.concatenate((cube, self._frames_buffer[frame_id][np.newaxis, :]), 0)


            if need_to_close:
                opened_file.close()

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

        if self._data_pool.frame_buffer:
            for frame_id, frame in zip(frame_ids, data):
                if frame_id not in self._frames_buffer:
                    self._frames_in_buffer.append(frame_id)
                    if len(self._frames_in_buffer) > self._data_pool.frame_buffer:
                        del self._frames_buffer[self._frames_in_buffer.pop(0)]
                    self._frames_buffer[frame_id] = frame