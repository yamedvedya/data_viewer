# Created by matveyev at 18.02.2021

"""
General class for opened file/stream
"""

import numpy as np


class AbstractDataFile(object):

    # ----------------------------------------------------------------------
    def __init__(self, data_pool):

        self.my_name = ''
        self._data_pool = data_pool
        self._data = {}
        self._axes_names = ['X', 'Y', 'Z']
        self._cube_axes_map = {0: 0,
                               1: 1,
                               2: 2}

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
        for display_axis, cube_axis in self._cube_axes_map.items():
            new_limits[display_axis] = [0, self._data['cube_shape'][cube_axis] - 1]

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

        real_axis = self._cube_axes_map[axis]
        axis_value = self._get_roi_axis(real_axis)
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

        real_axis = self._cube_axes_map[axis]
        return self._axes_names[real_axis], pos

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
            cut_axis = self._cube_axes_map[axis]
            data = data.take(indices=range(start, stop + 1), axis=cut_axis)
            data = np.sum(data, axis=cut_axis)

        if self._cube_axes_map[frame_sect['x']] > self._cube_axes_map[frame_sect['y']]:
            return np.transpose(data)
        else:
            return data

    # ----------------------------------------------------------------------
    def get_max_frame(self, axis):
        """

        :param axis:
        :return: maximum index along axis
        """
        cut_axis = self._cube_axes_map[axis]
        return self._data['cube_shape'][cut_axis] - 1

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

        plot_axis = self._cube_axes_map[sect['axis']]
        cut_axis_1 = self._cube_axes_map[sect['roi_1_axis']]

        if plot_axis == 0:
            if cut_axis_1 == 1:
                cube_cut = self._3d_cube[:,
                                         sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                         sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']]
            else:
                cube_cut = self._3d_cube[:,
                                         sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                         sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']]
            if do_sum:
                cube_cut = np.sum(cube_cut, axis=1)
                cube_cut = np.sum(cube_cut, axis=1)

        elif plot_axis == 1:
            if cut_axis_1 == 0:
                cube_cut = self._3d_cube[sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                         :,
                                         sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']]
            else:
                cube_cut = self._3d_cube[sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                         :,
                                         sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']]
            if do_sum:
                cube_cut = np.sum(cube_cut, axis=2)
                cube_cut = np.sum(cube_cut, axis=0)

        else:
            if cut_axis_1 == 0:
                cube_cut = self._3d_cube[sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                         sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']
                                         :]
            else:
                cube_cut = self._3d_cube[sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                         sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']
                                         :]
            if do_sum:
                cube_cut = np.sum(cube_cut, axis=0)
                cube_cut = np.sum(cube_cut, axis=0)

        return self._get_roi_axis(plot_axis), cube_cut

    # ----------------------------------------------------------------------
    def _get_roi_axis(self, plot_axis):
        """

        :param plot_axis: axis index
        :return: np.array of X coordinate for ROI plot
        """
        return np.arange(0, self._data['cube_shape'][plot_axis])