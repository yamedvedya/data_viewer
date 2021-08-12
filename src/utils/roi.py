# Created by matveyev at 22.02.2021
import numpy as np


class ROI(object):

    # ------------------------------------------------------------------
    def __init__(self, data_pool, my_id):

        self.my_id = my_id
        self._data_pool = data_pool

        self._section_params = {'axis_0': 0,
                                'dimensions': 1}

        self._saved_sections = {}

    # ------------------------------------------------------------------
    def set_section_axis(self, axis):

        self._saved_sections[self._section_params['axis_0']] = dict(self._section_params)
        if axis in self._saved_sections:
            self._section_params = dict(self._saved_sections[axis])
        else:
            self._section_params = {'axis_0': axis,
                                    'dimensions': 1}

            self._fill_axes(axis + 1)

    # ------------------------------------------------------------------
    def roi_parameter_changed(self, section_axis, param, value, axes_limits):

        value = int(value)
        if section_axis == 0:
            if param == 'pos':
                return axes_limits[self._section_params['axis_0']][0]
            else:
                return axes_limits[self._section_params['axis_0']][1] - \
                       axes_limits[self._section_params['axis_0']][0]

        real_axis = self._section_params['axis_{}'.format(section_axis)]
        if param == 'pos':
            value = max(value, axes_limits[real_axis][0])
            value = min(value,
                        axes_limits[real_axis][1] - self._section_params['axis_{}_width'.format(section_axis)])
        else:
            value = max(value, 1)
            value = min(value, axes_limits[real_axis][1] - self._section_params['axis_{}_pos'.format(section_axis)])

        self._section_params['axis_{}_{}'.format(section_axis, param)] = value
        return value

    # ------------------------------------------------------------------
    def get_section_params(self):
        return self._section_params

    # ------------------------------------------------------------------
    def get_param(self, param):
        if param in self._section_params:
            return self._section_params[param]
        else:
            self._fill_axes(int(param.split('_')[1]) + 1)

            return self._section_params[param]

    # ------------------------------------------------------------------
    def _fill_axes(self, new_dimensions):
        axes = list(np.arange(new_dimensions))

        for axis in range(self._section_params['dimensions']):
            axes.remove(self._section_params[f'axis_{axis}'])

        for axis_ind, new_axis in zip(range(self._section_params['dimensions'], new_dimensions), axes):
            self._section_params[f'axis_{axis_ind}'] = new_axis
            self._section_params[f'axis_{axis_ind}_pos'] = 0
            self._section_params[f'axis_{axis_ind}_width'] = 1

        self._section_params['dimensions'] = new_dimensions