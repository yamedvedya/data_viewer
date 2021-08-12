# Created by matveyev at 18.02.2021

"""
General class for opened file/stream
"""

import numpy as np


class BaseDataSet(object):

    # ----------------------------------------------------------------------
    def __init__(self, data_pool):

        self.my_name = ''
        self._data_pool = data_pool
        self._data = {}
        self._axes_names = ['X', 'Y', 'Z']

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
    def get_entry(self, entry):
        """
        for some file types we can store additional information
        :param file:
        :param entry:
        :return: if file has requested entry - returns it, else None
        """

        return self._data[entry]

    # ----------------------------------------------------------------------
    def get_axis_limits(self):
        """

        :return: dict {axis_index: [min, max]}, limits for each axis
        """
        new_limits = {}
        for axis_ind in range(len(self._axes_names)):
            new_limits[axis_ind] = [0, self._data['cube_shape'][axis_ind] - 1]

        return new_limits

    # ----------------------------------------------------------------------
    def frame_for_value(self, axis, pos):
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
    def value_for_frame(self, axis, pos):
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
    def get_2d_cut(self, frame_sect, section):
        """

        returns 2D frame to be displayed in Frame viewer
        :param frame_axes: {'X': index of X axis, 'Y': index of Y axis in frame viewer}
        :param section: list of tuples (section axes, from, to)
        :return: 2D np.array

        """

        section.sort(key=lambda tup: tup[0])
        data = self._3d_cube

        for axis, start, stop in section[::-1]:
            data = data.take(indices=range(start, stop + 1), axis=axis)
            data = np.sum(data, axis=axis)

        if frame_sect['x'] > frame_sect['y']:
            return np.transpose(data)
        else:
            return data

    # ----------------------------------------------------------------------
    def get_max_frame(self, axis):
        """

        :param axis:
        :return: maximum index along axis
        """
        return self._data['cube_shape'][axis] - 1

    # ----------------------------------------------------------------------
    def get_roi_cut(self, sect):
        """

        :param sect: ROI parameters
        :return: np.array, 3D cut from data cube
        """
        _, cube_cut = self.get_roi_data(sect, False)
        return cube_cut

    # ----------------------------------------------------------------------
    def get_roi_plot(self, sect):
        """

        :param sect: ROI parameters
        :return: np.array, 1D plot
        """
        return self.get_roi_data(sect, True)

    # ----------------------------------------------------------------------
    def get_roi_data(self, sect, do_sum):
        """
        gets ROI cut from data cube
        :param sect: ROI parameters
        :param do_sum: if True - return 1D plot, in False - return 3D cut
        :return: np.array
        """

        data = self._get_data()
        if len(data.shape) > sect['dimensions']:
            return 0, 0

        slices = []
        for axis in range(1, len(data.shape)):
            slices.append((sect[f'axis_{axis}'], sect[f'axis_{axis}_pos'],
                           sect[f'axis_{axis}_pos'] + sect[f'axis_{axis}_width']))

        slices.sort(key=lambda tup: tup[0])
        for axis, start, stop in slices[::-1]:
            data = data.take(indices=range(start, stop + 1), axis=axis)
            if do_sum:
                data = np.sum(data, axis=axis)

        return self._get_roi_axis(sect['axis_0']), data

    # ----------------------------------------------------------------------
    def _get_roi_axis(self, plot_axis):
        """

        :param plot_axis: axis index
        :return: np.array of X coordinate for ROI plot
        """
        return np.arange(0, self._data['cube_shape'][plot_axis])