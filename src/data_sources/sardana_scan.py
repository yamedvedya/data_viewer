# Created by matveyev at 18.02.2021

MEMORY_MODE = 'ram' #'disk' or 'ram'

import h5py
import numpy as np

from src.data_sources.abstract_data_file import AbstractDataFile


class SardanaScan(AbstractDataFile):

    # ----------------------------------------------------------------------
    def __init__(self, file_name, data_pool, opened_file):
        super(SardanaScan, self).__init__(file_name, data_pool, opened_file)

        self._original_file = file_name
        self._spaces = ['real']
        self._axes_names = {'real': ['detector X', 'detector Y', 'scan point']}
        self._cube_axes_map = {'real': {0: 2,
                                        1: 1,
                                        2: 0}}

        self._data['scanned_values'] = []

        scan_data = opened_file['scan']['data']
        for key in scan_data.keys():
            if len(scan_data[key].shape) > 1:
                self._data['cube_key'] = key
                self._data['cube_shape'] = scan_data[key].shape
                if MEMORY_MODE == 'ram':
                    self._data['3d_cube'] = scan_data[key][...]

                if scan_data[key].file.filename is not None:
                    try:
                        source_file = h5py.File(scan_data[key].file.filename, 'r')
                        self._data['pixel_mask'] = \
                            np.array(source_file['entry']['instrument']['detector']['pixel_mask'])[0, :, :]
                    except:
                        pass

            elif len(scan_data[key][...]) > 1:
                self._data['scanned_values'].append(key)
                self._data[key] = scan_data[key][...]

    # ----------------------------------------------------------------------
    def get_axis_limits(self, space):

        new_limits = {}
        if space == 'real':
            new_limits[0] = [0, self._data['cube_shape'][2]-1]
            new_limits[1] = [0, self._data['cube_shape'][1]-1]
            if self._data_pool.display_parameter in self._data['scanned_values']:
                new_limits[2] = [min(self._data[self._data_pool.display_parameter]),
                                 max(self._data[self._data_pool.display_parameter])]
            else:
                new_limits[2] = [0, 0]

        return new_limits

    # ----------------------------------------------------------------------
    def get_scan_params(self):
        return self._data['scanned_values']

    # ----------------------------------------------------------------------
    def get_value_at_point(self, space, axis, pos):
        if space == 'real':
            real_axis = self._cube_axes_map[space][axis]
            if real_axis == 0:
                if self._data_pool.display_parameter in self._data['scanned_values']:
                    if 0 <= pos < len(self._data[self._data_pool.display_parameter]):
                        return self._data_pool.display_parameter, self._data[self._data_pool.display_parameter][pos]
                    else:
                        return self._data_pool.display_parameter, np.NaN
            else:
                return self._axes_names['real'][axis], pos

    # ----------------------------------------------------------------------
    def _get_roi_axis(self, plot_axis):
        if plot_axis == 0:
            if self._data_pool.display_parameter in self._data['scanned_values']:
                return self._data[self._data_pool.display_parameter]
            else:
                return np.arange(0, self._data['cube_shape'][plot_axis])
        else:
            return np.arange(0, self._data['cube_shape'][plot_axis])

    # ----------------------------------------------------------------------
    def get_default_mask_for_file(self):
        return self._data['pixel_mask']

    # ----------------------------------------------------------------------
    def _apply_mask(self):

        try:
            if self._mask_info['mode'] in ['default', 'attached']:
                self._pixel_mask = self._data['pixel_mask'] > 0

            elif self._mask_info['mode'] == 'file' and 'loaded_mask' in self._data:
                self._pixel_mask = self._data['loaded_mask'] > 0

            else:
                self._pixel_mask = None

            if MEMORY_MODE == 'ram':
                with h5py.File(self._original_file, 'r') as f:
                    self._data['3d_cube'] = f['scan']['data'][self._data['cube_key']][...]

                if self._pixel_mask is not None:
                    for frame in self._data['3d_cube']:
                        frame[self._pixel_mask] = 0

        except Exception as err:
            self._data_pool.main_window.report_error("{}: cannot apply mask: {}".format(self.my_name, err))

    # ----------------------------------------------------------------------
    def get_2d_cut(self, space, axis, value, x_axis, y_axis):
        if space in self._spaces:
            cut_axis = self._cube_axes_map[space][axis]

            if MEMORY_MODE == 'ram':
                if cut_axis == 0:
                    data = self._data['3d_cube'][value, :, :]
                elif cut_axis == 1:
                    data = self._data['3d_cube'][:, value, :]
                else:
                    data = self._data['3d_cube'][:, :, value]

            else:
                with h5py.File(self._original_file, 'r') as f:
                    if cut_axis == 0:
                        data = f['scan']['data'][self._data['cube_key']][value, :, :]
                        if self._pixel_mask is not None:
                            data[self._pixel_mask] = 0
                    elif cut_axis == 1:
                        data = f['scan']['data'][self._data['cube_key']][:, value, :]
                        if self._pixel_mask is not None:
                            cut_mask = self._pixel_mask[value, :]
                            for line in data:
                                line[cut_mask] = 0
                    else:
                        data = f['scan']['data'][self._data['cube_key']][:, :, value]
                        if self._pixel_mask is not None:
                            cut_mask = self._pixel_mask[:, value]
                            for line in data:
                                line[cut_mask] = 0

            if self._cube_axes_map[space][x_axis] > self._cube_axes_map[space][y_axis]:
                return np.transpose(data)
            else:
                return data

        else:
            return []

    # ----------------------------------------------------------------------
    def get_roi_plot(self, space, sect):
        if space in self._spaces:
            plot_axis = self._cube_axes_map[space][sect['axis']]
            cut_axis_1 = self._cube_axes_map[space][sect['roi_1_axis']]

            if MEMORY_MODE == 'ram':
                if plot_axis == 0:
                    if cut_axis_1 == 1:
                        cube_cut = self._data['3d_cube'][:,
                                                         sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                                         sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']]
                    else:
                        cube_cut = self._data['3d_cube'][:,
                                                         sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                                         sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']]
                    cube_cut = np.sum(cube_cut, axis=1)
                    cube_cut = np.sum(cube_cut, axis=1)

                elif plot_axis == 1:
                    if cut_axis_1 == 0:
                        cube_cut = self._data['3d_cube'][sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                                         :,
                                                         sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']]
                    else:
                        cube_cut = self._data['3d_cube'][sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                                         :,
                                                         sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']]
                    cube_cut = np.sum(cube_cut, axis=2)
                    cube_cut = np.sum(cube_cut, axis=0)

                else:
                    if cut_axis_1 == 0:
                        cube_cut = self._data['3d_cube'][sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                                         sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                                         :]
                    else:
                        cube_cut = self._data['3d_cube'][sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                                         sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                                         :]
                    cube_cut = np.sum(cube_cut, axis=0)
                    cube_cut = np.sum(cube_cut, axis=0)

            else:
                with h5py.File(self._original_file, 'r') as f:
                    if plot_axis == 0:
                        if cut_axis_1 == 1:
                            cube_cut = f['scan']['data'][self._data['cube_key']][:,
                                                                                 sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                                                                 sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']]
                            if self._pixel_mask is not None:
                                mask_cut = self._pixel_mask[sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                                            sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']]
                                for frame in cube_cut:
                                    frame[mask_cut] = 0
                        else:
                            cube_cut = f['scan']['data'][self._data['cube_key']][:,
                                                                                 sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                                                                 sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']]
                            if self._pixel_mask is not None:
                                mask_cut = self._pixel_mask[sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                                            sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']]
                                for frame in cube_cut:
                                    frame[mask_cut] = 0

                        cube_cut = np.sum(cube_cut, axis=1)
                        cube_cut = np.sum(cube_cut, axis=1)

                    elif plot_axis == 1:
                        if cut_axis_1 == 0:
                            cube_cut = f['scan']['data'][self._data['cube_key']][sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                                                                 :,
                                                                                 sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']]
                            if self._pixel_mask is not None:
                                for z in range(sect['roi_2_pos'], sect['roi_2_pos'] + sect['roi_2_width']):
                                    mask_cut = self._pixel_mask[:, z]
                                    for frame in cube_cut:
                                        frame[mask_cut, z] = 0

                        else:
                            cube_cut = f['scan']['data'][self._data['cube_key']][sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                                                                 :,
                                                                                 sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']]
                            if self._pixel_mask is not None:
                                for z in range(sect['roi_1_pos'], sect['roi_1_pos'] + sect['roi_1_width']):
                                    mask_cut = self._pixel_mask[:, z]
                                    for frame in cube_cut:
                                        frame[mask_cut, z] = 0

                        cube_cut = np.sum(cube_cut, axis=2)
                        cube_cut = np.sum(cube_cut, axis=0)

                    else:
                        if cut_axis_1 == 0:
                            cube_cut = f['scan']['data'][self._data['cube_key']][sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                                                                 sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                                                                 :]
                            if self._pixel_mask is not None:
                                for y in range(sect['roi_2_pos'], sect['roi_2_pos'] + sect['roi_2_width']):
                                    mask_cut = self._pixel_mask[y, :]
                                    for frame in cube_cut:
                                        frame[y, mask_cut] = 0

                        else:
                            cube_cut = f['scan']['data'][self._data['cube_key']][sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                                                                                 sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                                                                                 :]
                            if self._pixel_mask is not None:
                                for y in range(sect['roi_1_pos'], sect['roi_1_pos'] + sect['roi_1_width']):
                                    mask_cut = self._pixel_mask[y, :]
                                    for frame in cube_cut:
                                        frame[y, mask_cut] = 0

                        cube_cut = np.sum(cube_cut, axis=0)
                        cube_cut = np.sum(cube_cut, axis=0)

            return self._get_roi_axis(plot_axis), cube_cut

        return 0, 0
