# Created by matveyev at 18.02.2021

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
    def update_settings(self):
        pass

    # ----------------------------------------------------------------------
    def apply_settings(self):
        pass

    # ----------------------------------------------------------------------
    def file_axes_caption(self):
        return self._axes_names

    # ----------------------------------------------------------------------
    def get_entry(self, entry):
        return self._data[entry]

    # ----------------------------------------------------------------------
    def get_axis_limits(self):

        new_limits = {}
        for display_axis, cube_axis in self._cube_axes_map.items():
            new_limits[display_axis] = [0, self._data['cube_shape'][cube_axis] - 1]

        return new_limits

    # ----------------------------------------------------------------------
    def frame_for_point(self, axis, pos):
        real_axis = self._cube_axes_map[axis]
        axis_value = self._get_roi_axis(real_axis)
        return np.argmin(np.abs(axis_value-pos))

    # ----------------------------------------------------------------------
    def get_value_at_point(self, axis, pos):
        real_axis = self._cube_axes_map[axis]
        return self._axes_names[real_axis], pos

    # ----------------------------------------------------------------------
    def get_roi_cube(self, sect):
        pass

    # ----------------------------------------------------------------------
    def get_2d_cut(self, axis, cut_range, x_axis, y_axis):
        cut_axis = self._cube_axes_map[axis]

        if cut_axis == 0:
            data = self._3d_cube[cut_range[0]:cut_range[1], :, :]
        elif cut_axis == 1:
            data = self._3d_cube[:, cut_range[0]:cut_range[1], :]
        else:
            data = self._3d_cube[:, :, cut_range[0]:cut_range[1]]

        data = np.sum(data, axis=cut_axis)
        if self._cube_axes_map[x_axis] > self._cube_axes_map[y_axis]:
            return np.transpose(data)
        else:
            return data

    # ----------------------------------------------------------------------
    def get_max_frame(self, axis):
        cut_axis = self._cube_axes_map[axis]
        return self._data['cube_shape'][cut_axis] - 1

    # ----------------------------------------------------------------------
    def get_roi_cut(self, sect):
        _, cube_cut = self.get_roi_data(sect, False)
        return cube_cut

    # ----------------------------------------------------------------------
    def get_roi_plot(self, sect):
        return self.get_roi_data(sect, True)

    # ----------------------------------------------------------------------
    def get_roi_data(self, sect, do_sum):
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
        return np.arange(0, self._data['cube_shape'][plot_axis])