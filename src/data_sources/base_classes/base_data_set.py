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

        self._section = None

        self._hist_lin = None
        self._hist_log = None
        self._hist_sqrt = None

        self._levels = None

    # ----------------------------------------------------------------------
    def save_section(self, section):
        for old, new in zip(self._section, section):
            old.update(new)

    # ----------------------------------------------------------------------
    def get_section(self):
        return self._section

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
    def get_file_dimension(self):
        """
        return nD cube dimensions
        :param file:
        :return: int
        """
        return len(self._data_shape)

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

        :return: list [max, ], limits for each axis
        """

        return [lim-1 for lim in self._data_shape]

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

        return self._cut_data(slices, do_sum, 1)

    # ----------------------------------------------------------------------
    def get_2d_picture(self):
        """

        returns 2D frame to be displayed in Frame viewer
        :return: 2D np.array

        """

        logger.debug(f"Request 2D picture")
        rest_axes = list(range(len(self._data_shape)))

        x_axis_ind = [ind for ind, sect in enumerate(self._section) if sect['axis'] == 'X'][0]
        section = [(x_axis_ind, self._section[x_axis_ind]['min'], self._section[x_axis_ind]['max'])]
        rest_axes.remove(x_axis_ind)

        y_axis_ind = [ind for ind, sect in enumerate(self._section) if sect['axis'] == 'Y'][0]
        section.append((y_axis_ind, self._section[y_axis_ind]['min'], self._section[y_axis_ind]['max']))
        rest_axes.remove(y_axis_ind)

        for axis in rest_axes:
            if self._section[axis]['integration']:
                section.append((axis, self._section[axis]['min'], self._section[axis]['max']))
            else:
                section.append((axis, self._section[axis]['min'], self._section[axis]['min'] + 1))

        data = self._cut_data(section, True, 2)

        if x_axis_ind > y_axis_ind:
            return np.transpose(data)
        else:
            return data

    # ----------------------------------------------------------------------
    def _cut_data(self, section, do_sum, output_dim):
        """
        return cut from data
        :param data: nD np.array
        :param section: array of tuples to define section: (axis, from, to)
        :param do_sum: if True - sums the section along all axes
        :return:
        """

        data = self._get_data()

        logger.debug(f"Data before cut {data.shape}, selection={section}, do_sum: {do_sum}, output_dim: {output_dim}")

        for axis_slice in sorted(section, reverse=True):
            axis, start, stop = axis_slice
            i = section.index(axis_slice)
            data = data.take(indices=range(start, stop), axis=axis)
            if do_sum and i >= output_dim:
                data = np.sum(data, axis=axis)

        data = np.squeeze(data)
        logger.debug(f"Data after cut {data.shape} ")
        return data

    # ----------------------------------------------------------------------
    def _get_roi_axis(self, plot_axis):
        """

        :param plot_axis: axis index
        :return: np.array of X coordinate for ROI plot
        """
        return np.arange(0, self._data_shape[plot_axis])

    # ----------------------------------------------------------------------
    def get_3d_cube(self, section):
        if section is None:
            return self._get_data()
        else:
            return self.get_roi_cut(section, False)

    # ----------------------------------------------------------------------
    def get_histogram(self, mode):
        if self._hist_lin is None:
            self._hist_lin, self._hist_log, self._hist_sqrt, self._levels = self._calculate_hist()

        if mode == 'lin':
            return self._hist_lin
        elif mode == 'log':
            return self._hist_log
        elif mode == 'sqrt':
            return self._hist_sqrt
        else:
            raise RuntimeError('Unknown hist mode')

    # ----------------------------------------------------------------------
    def get_levels(self, mode):
        if self._levels is None:
            self._hist_lin, self._hist_log, self._hist_sqrt, self._levels = self._calculate_hist()

        if mode == 'lin':
            return self._levels
        elif mode == 'log':
            return np.log(self._levels + 1)
        elif mode == 'sqrt':
            return np.sqrt(self._levels + 1)
        else:
            raise RuntimeError('Unknown hist mode')

    # ----------------------------------------------------------------------
    def _calculate_hist(self):

        original_data = self._get_data()

        hists = []

        for data in [original_data, np.log(original_data+1), np.sqrt(original_data+1)]:
            mn = np.nanmin(data).item()
            mx = np.nanmax(data).item()
            if mx == mn:
                # degenerate image, arange will fail
                mx += 1
            if np.isnan(mn) or np.isnan(mx):
                # the data are all-nan
                return None, None
            if data.dtype.kind in "ui":
                # For integer data, we select the bins carefully to avoid aliasing
                step = int(np.ceil((mx - mn) / 500.))
                bins = []
                if step > 0.0:
                    bins = np.arange(mn, mx + 1.01 * step, step, dtype=int)
            else:
                # for float data, let numpy select the bins.
                bins = np.linspace(mn, mx, 500)

            if len(bins) == 0:
                bins = np.asarray((mn, mx))

            data = data[np.isfinite(data)]
            hist = np.histogram(data, bins)

            hists.append((hist[1][:-1], hist[0]))

        return hists[0], hists[1], hists[2], np.array([np.min(original_data), np.max(original_data)])