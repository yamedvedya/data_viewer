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
from scipy import ndimage

from src.data_sources.base_classes.base_data_set import BaseDataSet


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
        return 3D data cube with applied activated parameters
        :param frame_id: if not None: indicate cut from 3D cube along first axis
        :return: np.array
        """
        if self._data_pool.memory_mode == 'ram':
            # if since last reload program parameters were not changed - we just return already COPY of loaded data
            if not self._need_apply_mask:
                return np.copy(self._nD_data_array)
            else:
                self._nD_data_array = None
                _data = self._reload_data()
        else:
            self._nD_data_array = None
            _data = self._reload_data(frame_id)

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

        self._calculate_correction(_data.shape, frame_id)

        try:
            if _pixel_mask is not None:
                for frame in _data:
                    frame[_pixel_mask] = 0

            if _settings['enable_ff'] and _settings['ff'] is not None:
                for ind in range(_data.shape[0]):
                    _data[ind] = _data[ind]/_settings['ff']

            if _settings['enable_fill']:
                for ind in range(_data.shape[0]):
                    frame_f = ndimage.uniform_filter(_data[ind], size=_settings['fill_radius'])
                    if _pixel_mask is not None:
                        _data[ind][_pixel_mask] = (frame_f/_fill_weights)[_pixel_mask]
                    else:
                        _data[ind] = (frame_f/_fill_weights)

            for frame, corr in zip(_data, self._correction):
                    frame *= corr

        except Exception as err:
            raise RuntimeError("{}: cannot apply mask: {}".format(self.my_name, err))

        if self._data_pool.memory_mode == 'ram':
            self._need_apply_mask = False
            self._nD_data_array = np.copy(_data)

        return _data

    # ----------------------------------------------------------------------
    def get_2d_picture(self, frame_axes, section):
        """

        this function is overridden due to _get_data can already do partial load and saves resources
        :param frame_axes: {'X': index of X axis, 'Y': index of Y axis in frame viewer}
        :param section: list of tuples (section axes, from, to)
        :return: 2D np.array

        """

        section.sort(key=lambda tup: tup[0])
        if self._data_pool.memory_mode != 'ram' and section[0][0] == 0:
            data = self._cut_data(self._get_data((section[0][0], section[0][1])), section, True)
        else:
            data = self._cut_data(self._get_data(), section, True)

        for axis, start, stop in section[::-1]:
            data = data.take(indices=range(start, stop + 1), axis=axis)
            data = np.sum(data, axis=axis)

        if frame_axes['x'] > frame_axes['y']:
            return np.transpose(data)
        else:
            return data
