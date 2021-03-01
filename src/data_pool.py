# Created by matveyev at 15.02.2021

import h5py
import os
import numpy as np
import threading
import time

from collections import OrderedDict

from PyQt5 import QtCore, QtWidgets

from src.data_sources.sardana_scan import SardanaScan
from src.utils.roi import ROI
from src.utils.utils import info_dialog


class DataPool(QtCore.QObject):

    new_file_added = QtCore.pyqtSignal(str)
    file_deleted = QtCore.pyqtSignal(str)

    update_parameter_list = QtCore.pyqtSignal()
    new_parameter_selected = QtCore.pyqtSignal()

    new_roi_range = QtCore.pyqtSignal(int)

    # ----------------------------------------------------------------------
    def __init__(self, parent, log):

        super(DataPool, self).__init__()

        self.main_window = parent
        self.log = log
        self.space = 'real'

        self._axes_names = {'real': ['X', 'Y', 'Z']}

        self.axes_limits = {0: [0, 0],
                            1: [0, 0],
                            2: [0, 0]}

        self.display_parameter = 'point_nb'
        self.possible_display_parameters = []

        self._files_data = {}

        self._rois = OrderedDict()
        self._last_roi_index = -1

        self._mask_info = {'mode': 'default',
                           'loaded_mask': np.array([[], []]),
                           'file': '',
                           'energy': None}

    # ----------------------------------------------------------------------
    def _get_all_axes_limits(self):
        new_limits = {0: [0, 0], 1: [0, 0], 2: [0, 0]}

        for data_set in self._files_data.values():
            file_limits = data_set.get_axis_limits(self.space)
            for axis, lim in new_limits.items():
                lim[0] = min(lim[0], file_limits[axis][0])
                lim[1] = max(lim[1], file_limits[axis][1])

        self.axes_limits = new_limits

    # ----------------------------------------------------------------------
    def _rescan_possible_scan_parameters(self):

        all_parameters = []
        for data_set in self._files_data.values():
            all_parameters += data_set.get_scan_params()
        self.possible_display_parameters = list(set(all_parameters))
        self.possible_display_parameters.sort()

        if self.display_parameter not in self.possible_display_parameters:
            if 'point_nb' in self.possible_display_parameters:
                self.display_parameter = 'point_nb'
            else:
                self.display_parameter = self.possible_display_parameters[0]

        self.update_parameter_list.emit()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def open_file(self, file_name):
        entry_name = os.path.splitext(os.path.basename(file_name))[0]

        if entry_name in self._files_data:
            self.log.error("File with this name already opened")
            self._open_file_error('File with this name already opened')
            return

        data_set = {'full_path': file_name,
                    'scanned_values': [],
                    '3d_cube': None}

        try:
            data_set['axes_list'] = []
            with h5py.File(file_name, 'r') as f:
                if 'scan' in f.keys():
                    self._files_data[entry_name] = SardanaScan(file_name, self, f)
                    self._files_data[entry_name].set_mask_info(self._mask_info)

            self._rescan_possible_scan_parameters()
            self._get_all_axes_limits()
            self.new_file_added.emit(entry_name)

        except Exception as err:
            self.main_window.report_error('Cannot open file', informative_text='Cannot open {}'.format(file_name),
                                          detailed_text=str(err))

    # ----------------------------------------------------------------------
    def remove_file(self, name):
        del self._files_data[name]
        self._rescan_possible_scan_parameters()
        self._get_all_axes_limits()
        self.file_deleted.emit(name)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def add_new_roi(self):
        self._last_roi_index += 1
        self._rois[self._last_roi_index] = ROI(self, self._last_roi_index)

        return self._last_roi_index, self.get_roi_name(self._last_roi_index)

    # ----------------------------------------------------------------------
    def get_roi_name(self, roi_index):
        for idx, key in enumerate(self._rois.keys()):
            if key == roi_index:
                return idx

        return None

    # ----------------------------------------------------------------------
    def delete_roi(self, roi_index):
        del self._rois[roi_index]

    # ----------------------------------------------------------------------
    def get_roi_plot(self, file, roi_idx):
        return self._files_data[file].get_roi_plot(self.space, self._rois[roi_idx].get_section_params())

    # ----------------------------------------------------------------------
    def set_section_axis(self, roi_idx, axis):

        self._rois[roi_idx].set_section_axis(axis)

    # ----------------------------------------------------------------------
    def roi_parameter_changed(self, roi_ind, section_axis, param, value):

        value = self._rois[roi_ind].roi_parameter_changed(section_axis, param, value, self.axes_limits)
        self.new_roi_range.emit(roi_ind)
        return value

    # ----------------------------------------------------------------------
    def get_roi_param(self, roi_ind, param):
        return self._rois[roi_ind].get_param(param)

    # ----------------------------------------------------------------------
    def get_roi_limits(self, roi_ind, section_axis):
        section_params = self._rois[roi_ind].get_section_params()

        if section_axis == 0:
            real_axis = section_params['axis']
        else:
            real_axis = section_params['roi_{}_axis'.format(section_axis)]

        axis_min = self.axes_limits[real_axis][0]
        axis_max = self.axes_limits[real_axis][1]

        return axis_min, axis_max - section_params['roi_{}_width'.format(section_axis)], \
               axis_max - axis_min - section_params['roi_{}_pos'.format(section_axis)]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def get_2d_cut(self, file, cut_axis, cut_value, x_axis, y_axis):
        return self._files_data[file].get_2d_cut(self.space, cut_axis, cut_value, x_axis, y_axis)

    # ----------------------------------------------------------------------
    def get_max_frame(self, file, axis):
        return self._files_data[file].get_max_frame(self.space, axis)

    # ----------------------------------------------------------------------
    def get_entry_value(self, file, entry):
        return self._files_data[file].get_entry(entry)

    # ----------------------------------------------------------------------
    def frame_for_point(self, file, axis, pos):
        return self._files_data[file].frame_for_point(self.space, axis, pos)

    # ----------------------------------------------------------------------
    def get_value_at_point(self, file, axis, pos):
        return self._files_data[file].get_value_at_point(self.space, axis, pos)

    # ----------------------------------------------------------------------
    def get_axes(self):
        return self._axes_names[self.space]

    # ----------------------------------------------------------------------
    def file_axes_caption(self, file):
        return self._files_data[file].file_axes_caption(self.space)

    # ----------------------------------------------------------------------
    def set_new_display_parameter(self, name):
        self.display_parameter = name
        self._get_all_axes_limits()
        self.new_parameter_selected.emit()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def get_attached_mask_for_file(self, file):
        return self._files_data[file].get_attached_mask_for_file()

    # ----------------------------------------------------------------------
    def get_default_mask_for_file(self, file):
        return self._files_data[file].get_default_mask_for_file()

    # ----------------------------------------------------------------------
    def set_mask_mode(self, file, mask_info, force_to_opened, force_for_future):

        if force_to_opened:
            for file in self._files_data.values():
                file.set_mask_info(mask_info)
        else:
            self._files_data[file].set_mask_info(mask_info)

        if force_for_future:
            self._mask_info = mask_info

    # ----------------------------------------------------------------------
    def get_mask_info(self, file):
        return self._files_data[file].get_mask_info()

    # ----------------------------------------------------------------------
    def get_dir(self, file):
        return self._files_data[file].my_dir
