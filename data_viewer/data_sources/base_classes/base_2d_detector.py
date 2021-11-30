# Created by matveyev at 20.05.2021

"""
Base class for images, obtained by 2D detectors
provide general functionality:

1) applying pixel mask to individual frame
2) excluding pixels based on flat filed detector map
3) filling detector gaps with interpolation of neighbor pixels
4) correction of intensity individual frame

"""

import numpy as np
import logging
from scipy import ndimage

from data_viewer.main_window import APP_NAME
from data_viewer.utils.utils import read_mask_file, read_ff_file
from data_viewer.data_sources.base_classes.base_data_set import BaseDataSet

logger = logging.getLogger(APP_NAME)


# ----------------------------------------------------------------------
def apply_base_settings(settings, SETTINGS):

    SETTINGS['enable_fill'] = False
    SETTINGS['fill_radius'] = False
    if 'fill_radius' in settings:
        try:
            SETTINGS['fill_radius'] = float(settings['fill_radius'])
            SETTINGS['enable_fill'] = True
        except:
            pass

    for param, default in zip(['min_ff', 'max_ff'], [0, 100]):
        SETTINGS[param] = default
        if param in settings:
            try:
                SETTINGS[param] = float(settings[param])
            except:
                pass

    for mode, funct in zip(['mask', 'ff'], [read_mask_file, read_ff_file]):
        SETTINGS[f'enable_{mode}'] = False
        SETTINGS[f'{mode}'] = None
        SETTINGS[f'{mode}_file'] = ''

        if f'{mode}' in settings:
            data = funct(settings[f'{mode}'])
            if data is not None:
                SETTINGS[f'enable_{mode}'] = True
                SETTINGS[f'{mode}'] = data
                SETTINGS[f'{mode}_file'] = settings[f'{mode}']


# ----------------------------------------------------------------------
class Base2DDetectorDataSet(BaseDataSet):
    
    def __init__(self, data_pool):
        super(Base2DDetectorDataSet, self).__init__(data_pool)
        
        self._need_apply_mask = True

    # ----------------------------------------------------------------------
    def _get_settings(self):
        raise RuntimeError('Non implemented')

    # ----------------------------------------------------------------------
    def _reload_data(self, frame_ids=None):
        raise RuntimeError('Non implemented')

    # ----------------------------------------------------------------------
    def _get_data_shape(self):
        raise RuntimeError('Non implemented')

    # ----------------------------------------------------------------------
    def _calculate_correction(self, data_shape, frame_ids=None):
        """
        some files can require correction for individual frames (e.g. for incoming beam intensity)

        :param data_shape: 3D data cube shape
        :param frame_ids: if not None: frame ids for which correction has to be calculated
        :return: np.array if correction factors
        """
        self._correction = np.ones(data_shape[0], dtype=np.float32)

    # ----------------------------------------------------------------------
    def _get_data(self, frame_id=None):
        """
        Get nD array of data with applied activated parameters
        :param frame_id: tuple, select requested frames_id
        :return: np.array
        """

        logger.debug(f"Request data with frame_id={frame_id}, mode={self._data_pool.memory_mode}")
        frame_id = np.arange(*frame_id) if frame_id is not None else None
        if self._data_pool.memory_mode == 'ram':
            # if since last reload program parameters were not changed - we just return already COPY of loaded data
            if not self._need_apply_mask:
                _data = np.copy(self._nD_data_array)
                if frame_id is not None:
                    _data = _data[frame_id]
                return _data
            else:
                self._nD_data_array = None
                _data = self._reload_data()
        else:
            self._nD_data_array = None
            _data = self._reload_data(frame_id)

        self.apply_corrections(_data, frame_id)

        if self._data_pool.memory_mode == 'ram':
            self._need_apply_mask = False
            self._nD_data_array = np.copy(_data)
            # Data from ram contain all frames_id
            if frame_id is not None:
                _data = _data[frame_id]

        return _data

    # ----------------------------------------------------------------------
    def apply_corrections(self, data, frame_id):
        """
        Apply several corrections to the data value.
        """
        logger.debug(f"Applying correction for {self.my_name}")

        _settings = self._get_settings()

        _pixel_mask = None
        _fill_weights = None

        # here we calculate pixel mask for selected set of options
        if _settings['enable_mask'] and _settings['mask'] is not None:
            _pixel_mask = _settings['mask'] > 0

        if _settings['enable_ff'] and _settings['ff'] is not None:
            _ff = np.copy(_settings['ff'])
            if _pixel_mask is None:
                _pixel_mask = (_ff < _settings['ff_min']) + (_ff > _settings['ff_max'])
            else:
                _pixel_mask += (_ff < _settings['ff_min']) + (_ff > _settings['ff_max'])

        # here we calculate pixel mask gap filling
        if _settings['enable_fill']:
            _fill_weights = ndimage.uniform_filter(1.-_pixel_mask, size=_settings['fill_radius'])

        self._calculate_correction(data.shape, frame_id)

        try:
            if _pixel_mask is not None:
                for frame in data:
                    frame[_pixel_mask] = 0

            if _settings['enable_ff'] and _settings['ff'] is not None:
                for ind in range(data.shape[0]):
                    data[ind] = data[ind]/_settings['ff']

            if _settings['enable_fill']:
                for ind in range(data.shape[0]):
                    frame_f = ndimage.uniform_filter(data[ind], size=_settings['fill_radius'])
                    if _pixel_mask is not None:
                        data[ind][_pixel_mask] = (frame_f/_fill_weights)[_pixel_mask]
                    else:
                        data[ind] = (frame_f/_fill_weights)

            for frame, corr in zip(data, self._correction):
                    frame *= corr

        except Exception as err:
            raise RuntimeError("{}: cannot apply mask: {}".format(self.my_name, err))

    # ----------------------------------------------------------------------
    def _cut_data(self, section, do_sum, output_dim):
        """
        return cut from data
        :param data: nD np.array
        :param section: array of tuples to define section: (axis, from, to)
        :param do_sum: if True - sums the section along all axes
        :return:
        """
        section_sorted = sorted(section)
        data = self._get_data((section_sorted[0][1], section_sorted[0][2]))

        axes_order = list(range(len(data.shape)))
        for ind, (axis, _, _) in enumerate(section):
            move_from = axes_order.index(axis)
            data = np.moveaxis(data, move_from, ind)
            del axes_order[move_from]
            axes_order.insert(ind, move_from)

        logger.debug(f"Data before cut {data.shape}, selection={section}, do_sum: {do_sum}, output_dim: {output_dim}")

        for ind, axis_slice in list(enumerate(section))[::-1]:
            axis, start, stop = axis_slice
            if axis > 0:
                start = max(start, 0)
                stop = min(stop, data.shape[ind])
                data = data.take(indices=range(start, stop), axis=ind)
            if do_sum and ind >= output_dim:
                data = np.sum(data, axis=ind)

        data = np.squeeze(data)

        if np.ndim(data) == 0:
            data = np.zeros(5)
        while np.ndim(data) < output_dim:
            data = data[..., np.newaxis]

        logger.debug(f"Data after cut {data.shape} ")
        return data