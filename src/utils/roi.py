# Created by matveyev at 22.02.2021

class ROI(object):

    # ------------------------------------------------------------------
    def __init__(self, data_pool, my_id):

        self.my_id = my_id
        self._data_pool = data_pool

        self._section_params = {'axis': 2,
                               'roi_1_axis': 0,
                               'roi_1_pos': 0,
                               'roi_1_width': 1,
                               'roi_2_axis': 1,
                               'roi_2_pos': 0,
                               'roi_2_width': 1}

        self._saved_sections = {0: dict(self._section_params),
                                1: dict(self._section_params),
                                2: dict(self._section_params)}

        self._saved_sections[0]['axis'] = 0
        self._saved_sections[0]['roi_1_axis'] = 1
        self._saved_sections[0]['roi_2_axis'] = 2

        self._saved_sections[1]['axis'] = 1
        self._saved_sections[1]['roi_1_axis'] = 0
        self._saved_sections[1]['roi_2_axis'] = 2

    # ------------------------------------------------------------------
    def set_section_axis(self, axis):

        self._saved_sections[self._section_params['axis']] = dict(self._section_params)
        self._section_params = dict(self._saved_sections[axis])

    # ------------------------------------------------------------------
    def roi_parameter_changed(self, section_axis, param, value, axes_limits):

        value = int(value)
        if section_axis == 0:
            if param == 'pos':
                return axes_limits[self._section_params['axis']][0]
            else:
                return axes_limits[self._section_params['axis']][1] - \
                       axes_limits[self._section_params['axis']][0]

        real_axis = self._section_params['roi_{}_axis'.format(section_axis)]
        if param == 'pos':
            value = max(value, axes_limits[real_axis][0])
            value = min(value,
                        axes_limits[real_axis][1] - self._section_params['roi_{}_width'.format(section_axis)])
        else:
            value = max(value, 1)
            value = min(value, axes_limits[real_axis][1] - self._section_params['roi_{}_pos'.format(section_axis)])

        self._section_params['roi_{}_{}'.format(section_axis, param)] = value
        return value

    # ------------------------------------------------------------------
    def get_section_params(self):
        return self._section_params

    # ------------------------------------------------------------------
    def get_param(self, param):
        return self._section_params[param]