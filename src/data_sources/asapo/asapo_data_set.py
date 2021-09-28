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
import logging

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
logger = logging.getLogger('3d_data_viewer')


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
        logger.debug(
            "Create new consumer (host=%s, path=%s, has_filesystem=%s, "
            "beamtime=%s, data_source=%s, token=%s, timeout=%i).",
            host, path, has_filesystem, beamtime, detector_name, token, 1000)

        self._setup_receiver(consumer, stream_name, detector_name)

        if self._data_pool.memory_mode == 'ram':
            self._nD_data_array = self._get_data()
            self._data_shape = self._nD_data_array.shape
        else:
            self._data_shape = self._get_data_shape()
        self._axes_names = ['message_ID'] + [f'dim_{i}' for i in range(1, len(self._data_shape))]
        self._data_pool.axes_limits = {i: [0, 0] for i in range(len(self._axes_names))}

        self._additional_data['frame_ID'] = np.arange(self._data_shape[0])
        self._additional_data['scanned_values'] = ['frame_ID']
        self._additional_data['metadata'] = []

    def _setup_receiver(self, consumer, stream_name, data_source):
        """
        Create and set parameters for receiver, which will be used to retrieve data from ASAPO.
        Currently there is no information in the ASAPO data_source about it content.
        Several try/except blocks stays to guess, how to retrieve data from given data_source.

        Parameters:
            consumer (asapo_consumer): ASAPO consumer
            stream_name (str): Stream name
            data_source (str): ASAPO data_source
        """
        try:
            self._mode = 'file'
            self.receiver = SerialAsapoReceiver(consumer)
            self.receiver.stream = stream_name
            self.receiver.data_source = data_source
            self.receiver.set_start_id(1)
            self.meta_only = False
            self.receiver.get_next(self.meta_only)
        except Exception as e:
            logger.debug(f"Setting mode=file fails: {e}")
            self._mode = 'dataset'
            self.receiver = SerialDatasetAsapoReceiver(consumer)
            self.receiver.stream = stream_name
            self.receiver.data_source = data_source
            self.meta_only = False
            try:
                self.receiver.set_start_id(1)
                self.receiver.get_next(self.meta_only)
            except Exception as e:
                logger.debug(f"Setting mode=dataset with meta_only=False fails: {e}")
                self.meta_only = True

        logger.info(f"Set mode '{self._mode}' and receiver: {self.receiver}")

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
            """
            de-Serialize numpy array (image) from ASAPO data based on ASAPO metadata.
            Default empty image of 2x2 is used to be compatible with the rest code of the package.
            Parameters:
                data (byte): data from ASAPO message
                meta_data (dict): metadata from ASAPO message
            Returns:
                image (np.ndarray): n-Dimensional np.array
            """
            def_img = np.zeros((2, 2), dtype=np.float32)
            if data is None:
                return def_img
            try:
                if self._mode == 'file':
                    return get_image(data, meta_data).astype(np.float32)
                else:
                    return get_image(data[0], meta_data[0]).astype(np.float32)
            except Exception as e:
                return def_img

        meta_list = []
        img_list = []
        if frame_ids is None:
            frame_ids = np.arange(self.receiver.get_current_size())

        for frame in frame_ids:
            self.receiver.set_start_id(frame + 1)
            data, meta_data = self.receiver.get_next(self.meta_only)
            meta_list.append(meta_data)
            img_list.append(_convert_image(data, meta_data))

        self._additional_data['metadata'] = meta_list
        img_array = np.stack(img_list)
        logger.debug(f"Retrieved image array {img_array.shape}")
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
