# Created by matveyev at 18.02.2021

import numpy as np
import os


class AbstractDataFile(object):

    # ----------------------------------------------------------------------
    def __init__(self, file_name, data_pool, opened_file):

        self.my_name = os.path.splitext(os.path.basename(file_name))[0]
        self.my_dir = os.path.dirname(file_name)
        self._data_pool = data_pool
        self._data = {}
        self._spaces = ['real']
        self._mask_mode = 'default'
        self._attached_mask = np.array([[], []])
        self._loaded_mask = np.array([[], []])
        self._loaded_mask_info = {}
        self._axes_names = {'real': ['X', 'Y', 'Z']}
        self._cube_axes_map = {'real': {0: 0,
                                        1: 1,
                                        2: 2}}

        self._atten_correction = {'default': 'off', 'default_param': ''}
        self._inten_correction = {'default': 'off', 'default_param': ''}

    # ----------------------------------------------------------------------
    def get_scan_parameters(self):
        return []

    # ----------------------------------------------------------------------
    def get_atten_settings(self):
        return self._atten_correction

    # ----------------------------------------------------------------------
    def get_inten_settings(self):
        return self._inten_correction

    # ----------------------------------------------------------------------
    def set_atten_settings(self, settings):
        self._atten_correction.update(settings)

    # ----------------------------------------------------------------------
    def set_inten_settings(self, settings):
        self._inten_correction.update(settings)

    # ----------------------------------------------------------------------
    def set_mask_info(self, mask_mode, loaded_mask=None, loaded_mask_info=None):
        self._mask_mode = mask_mode
        if mask_mode == 'file':
            self._loaded_mask = loaded_mask
            self._loaded_mask_info = loaded_mask_info

    # ----------------------------------------------------------------------
    def apply_settings(self):
        pass

    # ----------------------------------------------------------------------
    def get_attached_mask_for_file(self):
        return self._attached_mask

    # ----------------------------------------------------------------------
    def get_default_mask_for_file(self):
        return []

    # ----------------------------------------------------------------------
    def get_loaded_mask_for_file(self):
        return self._loaded_mask, self._loaded_mask_info

    # ----------------------------------------------------------------------
    def get_mask_mode(self):
        return self._mask_mode

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
    def get_scan_params(self):
        return []

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
    def get_2d_cut(self, space, axis, value, x_axis, y_axis):
        if space in self._spaces:
            cut_axis = self._cube_axes_map[space][axis]

            if cut_axis == 0:
                data = self._3d_cube[value, :, :]
            elif cut_axis == 1:
                data = self._3d_cube[:, value, :]
            else:
                data = self._3d_cube[:, :, value]

            data = data.todense()
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
    def get_roi_plot(self, space, sect):
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
                cube_cut = np.sum(cube_cut, axis=0)
                cube_cut = np.sum(cube_cut, axis=0)

            cube_cut = cube_cut.todense()

            return self._get_roi_axis(plot_axis), cube_cut

        return 0, 0

    # ----------------------------------------------------------------------
    def _get_roi_axis(self, plot_axis):
        return np.arange(0, self._data['cube_shape'][plot_axis])