# Created by matveyev at 18.02.2021

WIDGET_NAME = 'ASAPOScanSetup'

import numpy as np
from scipy import ndimage

import asapo_consumer
import configparser

from src.gui.asapo_image_setup_ui import Ui_ASAPOImageSetup
from src.data_sources.abstract_data_file import AbstractDataFile
from src.data_sources.abstract_2d_detector import DetectorImage, DetectorImageSetup, MEMORY_MODE

from AsapoWorker.asapo_receiver import SerialDatasetAsapoReceiver
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


class ASAPOScan(AbstractDataFile, DetectorImage):

    # ----------------------------------------------------------------------
    def __init__(self, detector_name, stream_name, data_pool):
        super(ASAPOScan, self).__init__(data_pool)

        self.my_name = stream_name
        self._detector_name = detector_name
        self._spaces = ['real']
        self._axes_names = {'real': ['frame_ID', 'detector X', 'detector Y']}
        self._cube_axes_map = {'real': {0: 2,
                                        1: 1,
                                        2: 0}}

        settings = configparser.ConfigParser()
        settings.read('./settings.ini')

        host = settings['ASAPO']['host']
        beamtime = settings['ASAPO']['beamtime']
        token = settings['ASAPO']['token']

        self.receiver = SerialDatasetAsapoReceiver(asapo_consumer.create_consumer(host, "", False,
                                                                                  beamtime, detector_name,
                                                                                  token, 1000))

        self.receiver.stream = stream_name
        self.receiver.data_source = detector_name

        self._data['scanned_values'] = ['frame_ID']

        cube = self._reload_data()
        self._data['cube_shape'] = cube.shape

        if MEMORY_MODE == 'ram':
            self._3d_cube = cube

        self._data['frame_ID'] = np.arange(self._data['cube_shape'][0])

        self._need_apply_mask = True

    # ----------------------------------------------------------------------
    def _get_settings(self):
        return SETTINGS

    # -------------------------------------------------------------------
    def _reload_data(self):

        self.receiver.set_start_id(1)
        data, meta_data = self.receiver.get_next(False)
        cube = get_image(data[0], meta_data[0])[np.newaxis, :]
        for _ in range(1, self.receiver.get_current_size()):
            data, meta_data = self.receiver.get_next(False)
            cube = np.vstack((cube, get_image(data[0], meta_data[0])[np.newaxis, :]))

        return np.array(cube, dtype=np.float32)

    # ----------------------------------------------------------------------
    def apply_settings(self):

        self._need_apply_mask = True

    # ----------------------------------------------------------------------
    def get_2d_cut(self, space, axis, value, x_axis, y_axis):

        return self._get_image(space, axis, value, x_axis, y_axis)

    # ----------------------------------------------------------------------
    def get_roi_plot(self, space, sect):

        return self._get_plot(space, sect)

# ----------------------------------------------------------------------
class ASAPOScanSetup(DetectorImageSetup):

    # ----------------------------------------------------------------------
    def _get_ui(self):

        return Ui_ASAPOImageSetup()

    # ----------------------------------------------------------------------
    def get_name(self):

        return 'ASAPO Scan Setup'

    # ----------------------------------------------------------------------
    def get_settings(self):

        return SETTINGS