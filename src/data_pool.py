# Created by matveyev at 15.02.2021

import h5py
import os
import psutil
import time
import sys
import numpy as np

from collections import OrderedDict

from PyQt5 import QtCore, QtWidgets

from src.data_sources.lambda_scan import LambdaScan
if 'asapo_consumer' in sys.modules:
    from src.data_sources.asapo_scan import ASAPOScan
from src.utils.roi import ROI
from src.widgets.batch_progress import BatchProgress


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
        self.memory_mode = 'ram'

        self._axes_names = {'real': ['X', 'Y', 'Z']}

        self.axes_limits = {0: [0, 0],
                            1: [0, 0],
                            2: [0, 0]}

        self._files_data = {}
        self._files_history = []
        self._protected_files = []

        self._rois = OrderedDict()
        self._last_roi_index = -1

        self.settings = {'delimiter': ';',
                         'format': '%.6e'}

        self._batcher = None
        self._opener = None
        self._open_mgs = _open_file_dialog()

        self._progress = BatchProgress()
        self._progress.stop_batch.connect(self._interrupt_batch)

    # ----------------------------------------------------------------------
    def set_settings(self, settings):

        if 'max_open_files' in settings:
            self._max_num_files = int(settings['max_open_files'])

        if 'memory_mode' in settings:
            self.memory_mode = settings['memory_mode']

        if 'max_memory_usage' in settings:
            self._max_memory = int(settings['max_memory_usage'])

        if 'delimiter' in settings:
            if settings['delimiter'] == 'semicolumn':
                self.settings['delimiter'] = ';'

        if 'format' in settings:
            self.settings['format'] = '%' + settings['format']

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def open_stream(self, detector_name, stream_name):
        entry_name = '/'.join([detector_name, stream_name])
        if entry_name in self._files_data:
            self.log.error("File with this name already opened")
            return

        self._open_mgs.setText(f'Opening stream {stream_name}')
        self._open_mgs.show()
        self._opener = Opener(self, 'stream', {'detector_name': detector_name, 'stream_name': stream_name,
                                               'entry_name': entry_name}, self._open_mgs)
        self._opener.start()

    # ----------------------------------------------------------------------
    def open_file(self, file_name):
        entry_name = os.path.splitext(os.path.basename(file_name))[0]

        if entry_name in self._files_data:
            self.log.error("File with this name already opened")
            return

        self._open_mgs.setText(f'Opening file {file_name}')
        self._open_mgs.show()
        self._opener = Opener(self, 'file', {'file_name': file_name, 'entry_name': entry_name},
                              self._open_mgs)
        self._opener.start()

    # ----------------------------------------------------------------------
    def add_new_entry(self, entry_name, entry):

        if self._max_num_files is not None and self._max_num_files > 0:
            while len(self._files_data) >= self._max_num_files:
                if not self._get_first_to_close():
                    break

        elif self._max_memory is not None and self._max_memory > 0:
            while float(psutil.Process(os.getpid()).memory_info().rss) / (1024. * 1024.) >= self._max_memory:
                if not self._get_first_to_close():
                    break

        self._files_data[entry_name] = entry
        self._files_history.append(entry_name)
        self._get_all_axes_limits()
        for data_set in self._files_data.values():
            data_set.update_settings()

        self.new_file_added.emit(entry_name)

    # ----------------------------------------------------------------------
    def _get_first_to_close(self):
        for name in self._files_history:
            if name not in self._protected_files:
                self.close_file.emit(name)
                self.remove_file(name)
                return True

        return False

    # ----------------------------------------------------------------------
    def remove_file(self, name):
        del self._files_data[name]
        self._files_history.remove(name)
        self._get_all_axes_limits()
        self.file_deleted.emit(name)

    # ----------------------------------------------------------------------
    def protect_file(self, name, status):
        if status:
            if name not in self._protected_files:
                self._protected_files.append(name)
        else:
            if name in self._protected_files:
                self._protected_files.remove(name)

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
    def get_roi_axis_name(self, roi_ind, file):
        return self._files_data[file].file_axes_caption(self.space)[self._rois[roi_ind].get_param('axis')]

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
    def _interrupt_batch(self):
        self._batcher.interrupt_batch()

    # ----------------------------------------------------------------------
    def batch_process_rois(self, file_list, dir_name, file_type):

        self._progress.clear()
        self._progress.show()

        self._batcher = Batcher(self, self._progress, file_list, dir_name, file_type)
        self._batcher.start()

    # ----------------------------------------------------------------------
    def save_roi_to_file(self, file_type, save_name, header, data):
        if file_type == '.txt':
            np.savetxt(save_name, data, fmt=self.settings['format'],
                       delimiter=self.settings['delimiter'],
                       newline='\n', header=';'.join(header))

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


# ----------------------------------------------------------------------
class Opener(QtCore.QThread):

    # ----------------------------------------------------------------------
    def __init__(self, data_pool, mode, params, msg_box):
        super(Opener, self).__init__()

        self.data_pool = data_pool
        self.mode = mode
        self.params = params
        self.msg_box = msg_box

    # ----------------------------------------------------------------------
    def run(self):
        if self.mode == 'file':
            finished = False
            while not finished:
                try:
                    with h5py.File(self.params['file_name'], 'r') as f:
                        if 'scan' in f.keys():
                            new_file = LambdaScan(self.params['file_name'], self.data_pool, f)
                            new_file.apply_settings()
                        self.data_pool.add_new_entry(self.params['entry_name'], new_file)
                        finished = True

                except OSError as err:
                    if 'Resource temporarily unavailable' in str(err.args):
                        time.sleep(0.5)
                        print('Waiting for file {}'.format(self.params['file_name']))

                except Exception as err:
                    self.data_pool.main_window.report_error('Cannot open file',
                                                            informative_text='Cannot open {}'.format(self.params['file_name']),
                                                            detailed_text=str(err))
                    finished = True

        elif self.mode == 'stream':
            try:
                new_file = ASAPOScan(self.params['detector_name'], self.params['stream_name'], self.data_pool)
                new_file.apply_settings()
                self.data_pool.add_new_entry(self.params['entry_name'], new_file)

            except Exception as err:
                self.data_pool.main_window.report_error('Cannot open stream',
                                                        informative_text='Cannot open {}'.format(self.params['entry_name']),
                                                        detailed_text=str(err))

        self.msg_box.hide()


# ----------------------------------------------------------------------
class Batcher(QtCore.QThread):
    def __init__(self, data_pool, progress, file_list, dir_name, file_type):
        super(Batcher, self).__init__()
        self.file_list = file_list
        self.dir_name = dir_name
        self.file_type = file_type

        self.data_pool = data_pool

        self._stop_batch = False
        self._progress = progress

    # ----------------------------------------------------------------------
    def interrupt_batch(self):
        self._stop_batch = True

    # ----------------------------------------------------------------------
    def run(self):
        total_files = len(self.file_list )
        for ind, file_name in enumerate(self.file_list):
            if not self._stop_batch:
                try:
                    with h5py.File(file_name, 'r') as f:
                        if 'scan' in f.keys():
                            self._progress.add_values(file_name, ind/total_files)
                            new_file = LambdaScan(file_name, self.data_pool, f)
                            new_file.apply_settings()
                            for ind, roi in self.data_pool._rois.items():
                                x_axis, y_axis = new_file.get_roi_plot(self.data_pool.space, roi.get_section_params())
                                header = [new_file.file_axes_caption(self.data_pool.space)[roi.get_param('axis')], 'ROI_value']
                                save_name = ''.join(os.path.splitext(os.path.basename(file_name))[:-1]) + \
                                            "_ROI_{}".format(ind) + self.file_type
                                self.data_pool.save_roi_to_file(self.file_type,
                                                                os.path.join(self.dir_name, save_name),
                                                                header,
                                                                np.transpose(np.vstack((x_axis, y_axis))))

                except Exception as err:
                    self.data_pool.main_window.report_error('Cannot calculate ROI',
                                                      informative_text='Cannot calculate ROI for {}'.format(file_name),
                                                      detailed_text=str(err))
            else:
                break

        self._progress.hide()


# ----------------------------------------------------------------------
def _open_file_dialog():
    open_mgs = QtWidgets.QMessageBox()
    open_mgs.setModal(False)
    open_mgs.setIcon(QtWidgets.QMessageBox.Information)
    open_mgs.setWindowTitle("Opening ...")
    open_mgs.setStandardButtons(QtWidgets.QMessageBox.NoButton)
    return open_mgs
