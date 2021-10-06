# Created by matveyev at 18.02.2021

"""
General class for opened file/stream
"""

import numpy as np
import logging

from src.main_window import APP_NAME

logger = logging.getLogger(APP_NAME)


class BaseDataSet(object):

    # ----------------------------------------------------------------------
    def __init__(self, data_pool):

        self.my_name = ''
        self._data_pool = data_pool
        self._additional_data = {}
        self._axes_names = ['X', 'Y', 'Z']

        # this is main array, which stores data
        self._nD_data_array = np.array([])
        # user can select mode, where data are not kept in memory. We need to have at least information about data shape
        self._data_shape = []

        # here we keep some auxiliary data: scanned motors, etc
        self._additional_data = {}

    # ----------------------------------------------------------------------
    def _get_data(self):
        return self._nD_data_array

    # ----------------------------------------------------------------------
    def check_file_after_load(self):
        pass

    # ----------------------------------------------------------------------
    def apply_settings(self):
        pass

    # ----------------------------------------------------------------------
    def get_file_axes(self):
        """
        some files can have own axes captions
        :param file:
        :return: dict {axis_index: axis_name}
        """
        return self._axes_names

    # ----------------------------------------------------------------------
    def get_additional_data(self, entry):
        """
        for some file types we can store additional information
        :param file:
        :param entry:
        :return: if file has requested entry - returns it, else None
        """
        return self._additional_data[entry]

    # ----------------------------------------------------------------------
    def get_axis_limits(self):
        """

        :return: dict {axis_index: [min, max]}, limits for each axis
        """
        new_limits = {}
        for axis_ind in range(len(self._axes_names)):
            new_limits[axis_ind] = [0, self._data_shape[axis_ind] - 1]

        return new_limits

    # ----------------------------------------------------------------------
    def get_frame_for_value(self, axis, pos):
        """
        for some file types user can select the displayed unit for some axis
        e.g. for Sardana scan we can display point_nb, or motor position etc...

        here we return the frame number along this axis for particular unit value

        :param axis: axis index
        :param pos: unit value
        :return: frame index
        """

        axis_value = self._get_roi_axis(axis)
        return np.argmin(np.abs(axis_value-pos))

    # ----------------------------------------------------------------------
    def get_value_for_frame(self, axis, pos):
        """
        for some file types user can select the displayed unit for some axis
        e.g. for Sardana scan we can display point_nb, or motor position etc...

        here we return the unit value along this axis for particular frame number

        :param axis: axis index
        :param pos: frame index
        :return: unit value
        """

        return self._axes_names[axis], pos

    # ----------------------------------------------------------------------
    def get_max_frame_along_axis(self, axis):
        """

        :param axis:
        :return: maximum index along axis
        """
        return self._data_shape[axis] - 1

    # ----------------------------------------------------------------------
    def get_roi_plot(self, sect):
        """

        :param sect: ROI parameters
        :return: X and Y of ROI plot
        """
        logger.debug(f"Request roi plot with section {sect}")
        return self._get_roi_axis(sect['axis_0']), self.get_roi_cut(sect, True)

    # ----------------------------------------------------------------------
    def get_roi_cut(self, sect, do_sum=False):
        """
        returns ROI cut from data cube
        :param sect: ROI parameters
        :param do_sum: if True - return 1D plot, in False - return 3D cut
        :return: np.arrays: X and
        """

        if len(self._data_shape) > sect['dimensions']:
            return 0, 0

        slices = [(sect['axis_0'], 0, self._data_shape[sect['axis_0']])] # [(axis, from, to), etc]
        for axis in range(1, len(self._data_shape)):
            slices.append((sect[f'axis_{axis}'], sect[f'axis_{axis}_pos'],
                           sect[f'axis_{axis}_pos'] + sect[f'axis_{axis}_width']))

        return self._cut_data(self._get_data((self._data_shape[sect['axis_0']],)), slices, do_sum, 1)

    # ----------------------------------------------------------------------
    def get_2d_picture(self, frame_sect, section):
        """

        returns 2D frame to be displayed in Frame viewer
        :param frame_axes: {'X': index of X axis, 'Y': index of Y axis in frame viewer}
        :param section: list of tuples (section axes, from, to)
        :return: 2D np.array

        """
        data = self._cut_data(self._get_data(), section, True, 2)

        if frame_sect['x'] > frame_sect['y']:
            return np.transpose(data)
        else:
            return data

    # ----------------------------------------------------------------------
    def _cut_data(self, data, section, do_sum, output_dim):
        """
        return cut from data
        :param data: nD np.array
        :param section: array of tuples to define section: (axis, from, to)
        :param do_sum: if True - sums the section along all axes
        :return:
        """
        logger.debug(f"Data before cut {data.shape}, selection={section}, do_sum: {do_sum}")

        for axis_slice in sorted(section, reverse=True):
            axis, start, stop = axis_slice
            i = section.index(axis_slice)
            if axis > 0:
                data = data.take(indices=range(start, stop + 1), axis=axis)
            if do_sum and i >= output_dim:
                data = np.sum(data, axis=axis)

        data = np.squeeze(data)
        # ToDo Remove this temporary fix
        if np.ndim(data) == 0:
            data = np.zeros(5)[:, None]
        if np.ndim(data) == 1 and output_dim == 2:
            data = data[:, None]
        return data

    # ----------------------------------------------------------------------
    def _get_roi_axis(self, plot_axis):
        """

        :param plot_axis: axis index
        :return: np.array of X coordinate for ROI plot
        """
        return np.arange(0, self._data_shape[plot_axis])