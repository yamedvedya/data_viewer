# Created by matveyev at 18.02.2021

"""
Class for ASAPO stream
inherit from AbstractDataFile and DetectorImage

after creation loads all frames from stream and merges data from them to one 3D cube [frameID, X, Y]
and apply current parameters (maks, flat field etc)

if user change parameters - reloads data from stream, makes new cube and applies new parameters
"""

import numpy as np
from distutils.util import strtobool

import asapo_consumer
import configparser

from src.data_sources.base_classes.base_2d_detector import Base2DDetectorDataSet

from AsapoWorker.asapo_receiver import SerialDatasetAsapoReceiver, SerialAsapoReceiver
from AsapoWorker.data_handler import get_image

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
            'displayed_param': 'frame_ID',
            }


class ASAPODataSet(Base2DDetectorDataSet):

    # ----------------------------------------------------------------------
    def __init__(self, detector_name, stream_name, data_pool):
        super(ASAPODataSet, self).__init__(data_pool)

        self.my_name = stream_name
        self._detector_name = detector_name

        # read the current settings
        settings = configparser.ConfigParser()
        settings.read('./settings.ini')

        host = settings['ASAPO']['host']
        path = settings['ASAPO']['path']
        has_filesystem = strtobool(settings['ASAPO']['has_filesystem'])
        beamtime = settings['ASAPO']['beamtime']
        token = settings['ASAPO']['token']

        consumer = asapo_consumer.create_consumer(host, path, has_filesystem, beamtime, detector_name, token, 1000)

        # TODO autodetect mode
        if settings['ASAPO']['mode'] == 'file':
            self._mode = 'file'
            self.receiver = SerialAsapoReceiver(consumer)
        else:
            self._mode = 'dataset'
            self.receiver = SerialDatasetAsapoReceiver(consumer)

        # save source for reload
        self.receiver.stream = stream_name
        self.receiver.data_source = detector_name

        # only one option
        self._additional_data['scanned_values'] = ['frame_ID']

        if self._data_pool.memory_mode == 'ram':
            self._nD_data_array = self._get_data()
            self._data_shape = self._nD_data_array.shape
        else:
            self._data_shape = self._get_data_shape()
        self._axes_names = ['message_ID'] + [f'dim_{i}' for i in range(1, len(self._data_shape))]
        self._data_pool.axes_limits = {i: [0, 0] for i in range(len(self._axes_names))}

        self._additional_data['frame_ID'] = np.arange(self._data_shape[0])
        self._metadata_list = []

    # ----------------------------------------------------------------------
    def _get_settings(self):
        return SETTINGS

    # -------------------------------------------------------------------
    def _reload_data(self, frame_ids=None):
        """
        reloads stream
        :param frame_ids: if not None: frames to be loaded
        :return: np.array, 3D data cube
        """
        def _convert_image(data, meta_data):
            if data is None:
                return np.zeros((0, 0), dtype=np.float32)
            try:
                if self._mode == 'file':
                    return get_image(data, meta_data).astype(np.float32)
                else:
                    return get_image(data[0], meta_data[0]).astype(np.float32)
            except Exception as e:
                # ToDo add log message
                print(e)
                return np.zeros((0, 0), dtype=np.float32)

        meta_list = []
        img_list = []
        if frame_ids is None:
            frame_ids = np.arange(self.receiver.get_current_size())

        for frame in frame_ids:
            self.receiver.set_start_id(frame+1)
            data, meta_data = self.receiver.get_next(False)
            meta_list.append(meta_data)
            img_list.append(_convert_image(data, meta_data))

        self._metadata_list = meta_list
        return np.stack(img_list)

    # ----------------------------------------------------------------------
    def _get_data_shape(self):
        """
        in case user select 'disk' mode (data is not kept in memory) - we calculate data shape without loading all data
        :return: tuple with data shape

        """

        frame = self._reload_data([0])
        return self.receiver.get_current_size(), frame.shape[1:]

    # ----------------------------------------------------------------------
    def apply_settings(self):
        self._need_apply_mask = True
