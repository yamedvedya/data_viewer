# Created by matveyev at 18.02.2021

import numpy as np


class AbstractDataFile(object):

    # ----------------------------------------------------------------------
    def __init__(self, data_pool):

        self.my_name = ''
        self._data_pool = data_pool
        self._data = {}
        self._spaces = ['real']
        self._axes_names = {'real': ['X', 'Y', 'Z']}
        self._cube_axes_map = {'real': {0: 0,
                                        1: 1,
                                        2: 2}}

    # ----------------------------------------------------------------------
    def update_settings(self):
        pass

    # ----------------------------------------------------------------------
    def apply_settings(self):
        pass

    # ----------------------------------------------------------------------
    def file_axes_caption(self, space):
        if space in self._axes_names:
            return self._axes_names[space]

        return ['', '', '']

    # ----------------------------------------------------------------------
    def get_entry(self, entry):
        return self._data[entry]

    # ----------------------------------------------------------------------
    def get_axis_limits(self, space):

        new_limits = {}
        if space in self._spaces:
            for display_axis, cube_axis in self._cube_axes_map[space].items():
                new_limits[display_axis] = [0, self._data['cube_shape'][cube_axis] - 1]

        return new_limits

    # ----------------------------------------------------------------------
    def frame_for_point(self, space, axis, pos):
        if space in self._spaces:
            real_axis = self._cube_axes_map[space][axis]
            axis_value = self._get_roi_axis(real_axis)
            return np.argmin(np.abs(axis_value-pos))

    # ----------------------------------------------------------------------
    def get_value_at_point(self, space, axis, pos):
        if space in self._spaces:
            real_axis = self._cube_axes_map[space][axis]
            return self._axes_names[space][real_axis], pos

    # ----------------------------------------------------------------------
    def get_roi_cube(self, space, sect):
        pass

    # ----------------------------------------------------------------------
    def get_2d_cut(self, space, axis, value, x_axis, y_axis):
        if space in self._spaces:
            cut_axis = self._cube_axes_map[space][axis]

            if cut_axis == 0:
                data = self._3d_cube[value, :, :]
            elif cut_axis == 1:
                data = self._3d_cube[:, value, :]
            else:
                data = self._3d_cube[:, :, value]

            if self._cube_axes_map[space][x_axis] > self._cube_axes_map[space][y_axis]:
                return np.transpose(data)
            else:
                return data

        else:
            return []

    # ----------------------------------------------------------------------
    def get_max_frame(self, space, axis):
        if space in self._spaces:
            cut_axis = self._cube_axes_map[space][axis]
            return self._data['cube_shape'][cut_axis] - 1

        return 0

    # ----------------------------------------------------------------------
    def get_roi_cut(self, space, sect):
        _, cube_cut = self.get_roi_data(space, sect, False)
        return cube_cut

    # ----------------------------------------------------------------------
    def get_roi_plot(self, space, sect):
        return self.get_roi_data(space, sect, True)

    # ----------------------------------------------------------------------
    def get_roi_data(self, space, sect, do_sum):
        if space in self._spaces:
            plot_axis = self._cube_axes_map[space][sect['axis']]
            cut_axis_1 = self._cube_axes_map[space][sect['roi_1_axis']]

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

        return 0, 0

    # ----------------------------------------------------------------------
    def _get_roi_axis(self, plot_axis):
        return np.arange(0, self._data['cube_shape'][plot_axis])