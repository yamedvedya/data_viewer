# Created by matveyev at 15.02.2021

import h5py
import os
import psutil
import time

from collections import OrderedDict

from PyQt5 import QtCore

from src.data_sources.lambda_scan import LambdaScan
from src.utils.roi import ROI


class DataPool(QtCore.QObject):

    new_file_added = QtCore.pyqtSignal(str)
    file_deleted = QtCore.pyqtSignal(str)
    close_file = QtCore.pyqtSignal(str)

    new_roi_range = QtCore.pyqtSignal(int)
    data_updated = QtCore.pyqtSignal()

    # ----------------------------------------------------------------------
    def __init__(self, parent, log):

        super(DataPool, self).__init__()

        self.main_window = parent
        self.log = log
        self.space = 'real'

        self._lim_mode = 'no'
        self._max_num_files = None
        self._max_memory = None

        self._axes_names = {'real': ['X', 'Y', 'Z']}

        self.axes_limits = {0: [0, 0],
                            1: [0, 0],
                            2: [0, 0]}

        self._files_data = {}
        self._files_history = []

        self._rois = OrderedDict()
        self._last_roi_index = -1

        self._settings = {}

    # ----------------------------------------------------------------------
    def set_settings(self, settings):

        if 'max_open_files' in settings:
            self._max_num_files = int(settings['max_open_files'])

        if 'max_memory_usage' in settings:
            self._max_memory = int(settings['max_memory_usage'])

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def open_file(self, file_name):
        entry_name = os.path.splitext(os.path.basename(file_name))[0]

        if entry_name in self._files_data:
            self.log.error("File with this name already opened")
            self._open_file_error('File with this name already opened')
            return

        finished = False
        while not finished:
            try:
                with h5py.File(file_name, 'r') as f:
                    if 'scan' in f.keys():
                        new_file = LambdaScan(file_name, self, f)
                        new_file.apply_settings()

                if self._max_num_files is not None and self._max_num_files > 0:
                    while len(self._files_data) >= self._max_num_files:
                        self.close_file.emit(self._files_history[0])
                        self.remove_file(self._files_history[0])
                elif self._max_memory is not None and self._max_memory > 0:
                    while float(psutil.Process(os.getpid()).memory_info().rss) / (1024. * 1024.) >= self._max_memory:
                        self.close_file.emit(self._files_history[0])
                        self.remove_file(self._files_history[0])

                self._files_data[entry_name] = new_file
                self._files_history.append(entry_name)
                self._get_all_axes_limits()
                for data_set in self._files_data.values():
                    data_set.update_settings()

                self.new_file_added.emit(entry_name)
                finished = True

            except OSError as err:
                if 'Resource temporarily unavailable' in str(err.args):
                    time.sleep(0.5)
                    print('Waiting for file {}'.format(file_name))

            except Exception as err:
                self.main_window.report_error('Cannot open file', informative_text='Cannot open {}'.format(file_name),
                                              detailed_text=str(err))
                finished = True

    # ----------------------------------------------------------------------
    def remove_file(self, name):
        del self._files_data[name]
        self._files_history.remove(name)
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
    def _get_all_axes_limits(self):
        new_limits = {0: [0, 0], 1: [0, 0], 2: [0, 0]}

        for data_set in self._files_data.values():
            file_limits = data_set.get_axis_limits(self.space)
            for axis, lim in new_limits.items():
                lim[0] = min(lim[0], file_limits[axis][0])
                lim[1] = max(lim[1], file_limits[axis][1])

        self.axes_limits = new_limits

    # ----------------------------------------------------------------------
    def set_space(self, space):
        # self.space = space
        pass

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def apply_settings(self):
        for data in self._files_data.values():
            data.apply_settings()

        self.data_updated.emit()
