# Created by matveyev at 15.02.2021

import h5py
import os
import psutil
import time
import sys
import numpy as np
import traceback
import logging

from collections import OrderedDict

from PyQt5 import QtCore, QtWidgets

from src.data_sources.sardana.sardana_data_set import SardanaDataSet
if 'asapo_consumer' in sys.modules:
    from src.data_sources.asapo.asapo_data_set import ASAPODataSet

from src.data_sources.beamview.beam_view_data_set import BeamLineView
from src.data_sources.reciprocal.reciprocal_data_set import ReciprocalScan
from src.utils.roi import ROI
from src.widgets.batch_progress import BatchProgress
from src.main_window import APP_NAME

logger = logging.getLogger(APP_NAME)


class DataPool(QtCore.QObject):

    new_file_added = QtCore.pyqtSignal(str)
    file_deleted = QtCore.pyqtSignal(str)
    close_file = QtCore.pyqtSignal(str)
    file_updated = QtCore.pyqtSignal(str)

    roi_changed = QtCore.pyqtSignal(int)
    data_updated = QtCore.pyqtSignal()

    # ----------------------------------------------------------------------
    def __init__(self, parent):

        super(DataPool, self).__init__()

        self.main_window = parent

        self._lim_mode = 'no'
        self._max_num_files = None
        self._max_memory = None
        self.memory_mode = 'ram'

        self._files_data = {}
        self._files_history = []
        self._protected_files = []

        self._rois = OrderedDict()
        self._last_roi_key = -1

        self.settings = {'delimiter': ';',
                         'format': '%.6e'}

        self._batcher = None
        self._opener = None
        self._open_mgs = _open_file_dialog()

        self._progress = BatchProgress()
        self._progress.stop_batch.connect(self._interrupt_batch)

    # ----------------------------------------------------------------------
    def set_settings(self, settings):
        """
            this function is called during startup and everytime user changes settings
        """

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
    def report_error(self, title, informative_text, detailed_text):
        """
            this function reports error to the main window
        """

        self.main_window.report_error(title,
                                      informative_text=informative_text,
                                      detailed_text=detailed_text)

    # ----------------------------------------------------------------------
    #       Files/streams open/save section
    # ----------------------------------------------------------------------
    def open_stream(self, detector_name, stream_name, info):
        """
            called by signal from ASAPO browser
            since we don't want the GUI to freeze during stream load - we make an QThread, which in really reads data

            Parameters:
                detector_name (str): Name of ASAPO data source
                stream_name (str): Name of ASAPO stream
                info (dict): Properties of stream
        """

        # all opened files are entry to self._files_data dict
        # first we check, that this stream in not yet opened
        entry_name = '/'.join([detector_name, stream_name])
        if entry_name in self._files_data:
            self._files_data[entry_name].update_info(info)
            self.file_updated.emit(entry_name)
            logger.error("File with this name already opened")
            return

        self._start_opener('stream', f'Opening stream {stream_name}',
                           {'detector_name': detector_name, 'stream_name': stream_name, 'entry_name': entry_name})

    # ----------------------------------------------------------------------
    def update_stream(self, detector_name, stream_name, info):
        """
            called by signal from ASAPO browser
            since we don't want the GUI to freeze during stream load - we make an QThread, which in really reads data

            Parameters:
                detector_name (str): Name of ASAPO data source
                stream_name (str): Name of ASAPO stream
                info (dict): Properties of stream
        """
        entry_name = '/'.join([detector_name, stream_name])
        if entry_name in self._files_data:
            logger.debug(f"Update stream {entry_name}")
            self._files_data[entry_name].update_info(info)
            self.file_updated.emit(entry_name)

    # ----------------------------------------------------------------------
    def open_file(self, file_name):
        """
            called by signal from file browser

            since we don't want the GUI to freeze during stream load - we make an QThread, which in really reads data

        """

        # all opened files are entry to self._files_data dict
        # first we check, that this stream in not yet opened
        entry_name = os.path.splitext(os.path.basename(file_name))[0]
        if entry_name in self._files_data:
            logger.error("File with this name already opened")
            return

        if ".nxs" in file_name:
            self._start_opener('sardana', f'Opening file {file_name}',
                               {'file_name': file_name, 'entry_name': entry_name})
        elif ".h5" in file_name:
            self._start_opener('reciprocal', f'Opening file {file_name}',
                               {'file_name': file_name, 'entry_name': entry_name})
        elif '.dat' in file_name:
            self._start_opener('beamline', f'Opening folder {os.path.dirname(file_name)}',
                               {'file_name': file_name, 'entry_name': entry_name})

    # ----------------------------------------------------------------------
    def _start_opener(self, mode, user_msg, kwargs):
        """
        create popup message for user

        :param mode:
        :param user_msg: message in popup dialog
        :param kwargs:
        :return:
        """
        #
        logger.debug(f"Start opener with mode: {mode}, {user_msg}, {kwargs}")
        self._open_mgs.setText(user_msg)
        self._open_mgs.show()

        self._opener = Opener(self, mode, kwargs)
        self._opener.exception.connect(self.report_error)
        self._opener.done.connect(self._open_done)
        self._opener.start()

    # ----------------------------------------------------------------------
    def _open_done(self):
        """
            called by Opener, closes popup message
        """
        self._open_mgs.hide()

    # ----------------------------------------------------------------------
    def add_new_entry(self, entry_name, entry):
        """
            called from Opener, after the data are read, and add entry to the self._files_data

        """

        # first we check, that we do not overcome user limit to max opened files
        if self._max_num_files is not None and self._max_num_files > 0:
            while len(self._files_data) >= self._max_num_files:
                if not self._get_first_to_close():
                    break

        # or that we do not overcome user limit to memory use
        elif self._max_memory is not None and self._max_memory > 0:
            while float(psutil.Process(os.getpid()).memory_info().rss) / (1024. * 1024.) >= self._max_memory:
                if not self._get_first_to_close():
                    break

        self._files_data[entry_name] = entry

        # since the dict is not order according to the adding time and there are "protected" files,
        # we just track history of opened files in separate list. TODO: use OrderedDict
        self._files_history.append(entry_name)

        # than we need to update all axes rages and re-update all settings for all opened files
        self.get_all_axes_limits()
        for data_set in self._files_data.values():
            data_set.check_file_after_load()

        # now we read to notify the GUI about new added file
        self.new_file_added.emit(entry_name)

    # ----------------------------------------------------------------------
    def _get_first_to_close(self):
        """
            all files, moved to comparison are protected to be closed, so we return first non-protected from history
            :returns True is file was close, False if there is no file to be closed
        """

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
        self.file_deleted.emit(name)

    # ----------------------------------------------------------------------
    def protect_file(self, name, status):
        """
            when user moves file to comparison, we don not close it in automatic mode (max files opened, max memory)
        """

        if status:
            if name not in self._protected_files:
                self._protected_files.append(name)
        else:
            if name in self._protected_files:
                self._protected_files.remove(name)

    # ----------------------------------------------------------------------
    def save_converted(self, entry_name, gridder):
        """
            saves files after conversion to reciprocal space
        """

        file_name, ok = QtWidgets.QFileDialog.getSaveFileName(self.main_window, 'Select file name',
                                                              self.main_window.get_current_folder() + "/" + entry_name,
                                                              'HDF5 format {.h5};;')
        if ok:
            # since we automatically open saved file, file name has to be unique
            while file_name in self._files_data:
                file_name, ok = QtWidgets.QFileDialog.getSaveFileName(self.main_window, 'Select file name',
                                                                      self.main_window.get_current_folder() + "/" + entry_name,
                                                                      'HDF5 format {.h5};;')
            if not ok:
                return

        if not file_name.endswith('.h5'):
            file_name += '.h5'

        ReciprocalScan(self, gridder=gridder).save_file(file_name)
        self.open_file(file_name)

    # ----------------------------------------------------------------------
    #       ROIs plots section
    # ----------------------------------------------------------------------
    def roi_counts(self):
        return len(self._rois)

    # ----------------------------------------------------------------------
    def get_roi_key(self, roi_num):
        """
            :returns the key for Ns roi in dict
        """
        return list(self._rois.keys())[roi_num]

    # ----------------------------------------------------------------------
    def add_new_roi(self):
        """
            all ROI are kept in OrderedDict with unique key
        """
        self._last_roi_key += 1
        self._rois[self._last_roi_key] = ROI(self, self._last_roi_key)

        return self._last_roi_key, self.get_roi_index(self._last_roi_key)

    # ----------------------------------------------------------------------
    def get_roi_index(self, roi_key):
        for idx, key in enumerate(self._rois.keys()):
            if key == roi_key:
                return idx

        return None

    # ----------------------------------------------------------------------
    def delete_roi(self, roi_key):
        del self._rois[roi_key]

    # ----------------------------------------------------------------------
    def get_roi_cut(self, file, roi_key):
        """
            calculate 3D cut from the data cube, defined by the ROI[roi_key]
            :returns 3d np.array
        """
        return self._files_data[file].get_roi_cut(self._rois[roi_key].get_section_params())

    # ----------------------------------------------------------------------
    def get_roi_plot(self, file, roi_key):
        """
            calculate 1D plot from the data cube, defined by the ROI[roi_key]
            :returns two 1D np.arrays (X, Y)
        """
        return self._files_data[file].get_roi_plot(self._rois[roi_key].get_section_params())

    # ----------------------------------------------------------------------
    def set_section_axis(self, roi_key, axis):

        logger.debug(f"data_pool.set_section_axis: roi_key {roi_key}, axis: {axis}")
        self._rois[roi_key].set_section_axis(axis)
        self.roi_changed.emit(roi_key)

    # ----------------------------------------------------------------------
    def roi_parameter_changed(self, roi_key, section_axis, param, value):
        """
            function checks if the requested ROI`s value is valid. If value is valid - returns it,
            if not, returns the most close valid one
            :param roi_key - key for ROIs dict,
            :param section_axis - which axes is modified,
            :param param - 'width', 'pos'
            :param value - requested by user value
            :returns accepted value
        """
        logger.debug(f"data_pool.set_section_axis: roi_key {roi_key}, section_axis: {section_axis}, param: {param}, value: {value}")

        axis_lim = self.get_all_axes_limits()
        if axis_lim is not None:
            value = self._rois[roi_key].roi_parameter_changed(section_axis, param, value, axis_lim)
            return value
        else:
            return None

    # ----------------------------------------------------------------------
    def get_roi_axis_name(self, roi_key, file):
        """
            :returns axis name, along which ROI is calculated, for particular file
        """
        return self._files_data[file].get_file_axes()[self._rois[roi_key].get_param('axis_0')]

    # ----------------------------------------------------------------------
    def get_roi_param(self, roi_key, param):
        """
            :param roi_key
            :param param: 'axis_0' - axis along which roi has to be plotted;
            'axis_1', 'axis_1_pos', 'axis_1_width' - cut parameters
            ...
            'axis_N', 'axis_N_pos', 'axis_N_width' - cut parameters

            :returns requested value
        """
        return self._rois[roi_key].get_param(param)

    # ----------------------------------------------------------------------
    def get_roi_limits(self, roi_key, section_axis):
        """
            :returns max and min values for particular axis and ROI if all files have the same dims, else None, None
        """
        section_params = self._rois[roi_key].get_section_params()
        real_axis = section_params['axis_{}'.format(section_axis)]

        axis_lim = self.get_all_axes_limits()
        if axis_lim is not None:
            axis_min = axis_lim[real_axis][0]
            axis_max = axis_lim[real_axis][1]

            return axis_min, axis_max - section_params['axis_{}_width'.format(section_axis)], \
                   axis_max - axis_min - section_params['axis_{}_pos'.format(section_axis)]

        else:
            return None, None, None

    # ----------------------------------------------------------------------
    #       ROIs batch processing section
    # ----------------------------------------------------------------------
    def _interrupt_batch(self):
        self._batcher.interrupt_batch()

    # ----------------------------------------------------------------------
    def _new_batch_file(self, fname, progress):
        self._progress.add_values(fname, progress)

    # ----------------------------------------------------------------------
    def _new_batch_done(self):
        self._progress.hide()

    # ----------------------------------------------------------------------
    def batch_process_rois(self, file_list, dir_name, file_type):
        """

        :param file_list: list of files to be processed
        :param dir_name: output directory
        :param file_type: output file type
        :return:

        """
        # first we reset progress bar
        self._progress.clear()
        self._progress.show()

        self._batcher = Batcher(self, file_list, dir_name, file_type)
        self._batcher.exception.connect(self.report_error)
        self._batcher.new_file.connect(self._new_batch_file)
        self._batcher.done.connect(self._new_batch_done)
        self._batcher.start()

    # ----------------------------------------------------------------------
    def save_roi_to_file(self, file_type, save_name, header, data):
        """
        called from Batcher to save processed data
        :param file_type:
        :param save_name:
        :param header:
        :param data:
        :return:
        """
        if file_type == '.txt':
            np.savetxt(save_name, data, fmt=self.settings['format'],
                       delimiter=self.settings['delimiter'],
                       newline='\n', header=';'.join(header))

    # ----------------------------------------------------------------------
    #       2D frames section
    # ----------------------------------------------------------------------
    def get_2d_picture(self, file):
        """
        returns 2D frame to be displayed in Frame viewer
        :param file: key for self._files_data
        :param section: list of tuples (section axes, from, to)
        :return: 2D np.array
        """
        logger.debug(f"Return 2D image: for file {file}")
        return self._files_data[file].get_2d_picture()

    # ----------------------------------------------------------------------
    def get_section(self, file):
        """
        Return previous sections of files
        """
        return self._files_data[file].get_section()

    # ----------------------------------------------------------------------
    def save_section(self, file, section):
        """
        Saves sections of files
        :param section: dict with section
        """
        return self._files_data[file].save_section(section)

    # ----------------------------------------------------------------------
    def get_max_frame_along_axis(self, file, axis):
        """

        :param file: key for self._files_data
        :param axis:
        :return: maximum value along requested axis
        """
        return self._files_data[file].get_max_frame_along_axis(axis)

    # ----------------------------------------------------------------------
    def get_additional_data(self, file, entry):
        """
        for some file types we can store additional information
        :param file:
        :param entry:
        :return: if file has requested entry - returns it, else None
        """
        return self._files_data[file].get_additional_data(entry)

    # ----------------------------------------------------------------------
    def get_frame_for_value(self, file, axis, pos):
        """
        for some file types user can select the displayed unit for some axis
        e.g. for Sardana scan we can display point_nb, or motor position etc...

        here we return the frame number along this axis for particular unit value

        :param file:
        :param axis:
        :param pos:
        :return:
        """
        return self._files_data[file].get_frame_for_value(axis, pos)

    # ----------------------------------------------------------------------
    def get_value_for_frame(self, file, axis, pos):
        """
        for some file types user can select the displayed unit for some axis
        e.g. for Sardana scan we can display point_nb, or motor position etc...

        here we return the unit value along this axis for particular frame number
        :param file:
        :param axis:
        :param pos:
        :return:
        """
        return self._files_data[file].get_value_for_frame(axis, pos)

    # ----------------------------------------------------------------------
    def get_file_axes(self, file):
        """
        some files can have own axes captions
        :param file:
        :return: dict {axis_index: axis_name}
        """
        return self._files_data[file].get_file_axes()

    # ----------------------------------------------------------------------
    def get_file_axis_limits(self, file):
        """
        Return axis limits of given file
        :param file:
        :return: dict {axis_index: axis_limits}
        """
        return self._files_data[file].get_axis_limits()

    # ----------------------------------------------------------------------
    def get_all_axes_limits(self):
        """
        recalculates the limits for all files
        :return:
        """

        main_file = self.main_window.get_current_file()
        if main_file is None:
            return None

        main_file_dim = self._files_data[main_file].get_file_dimension()

        new_limits = [[0, 0] for _ in range(main_file_dim)]

        for data_set in self._files_data.values():
            if data_set.get_file_dimension() != main_file_dim:
                continue

            for axis, max_frame in enumerate(data_set.get_axis_limits()):
                _, min_v = data_set.get_value_for_frame(axis, 0)
                new_limits[axis][0] = min(new_limits[axis][0], min_v)

                _, max_v = data_set.get_value_for_frame(axis, max_frame - 1)
                new_limits[axis][1] = max(new_limits[axis][1], max_v)

        return new_limits

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def apply_settings(self):
        for data in self._files_data.values():
            data.apply_settings()

        self.data_updated.emit()


# ----------------------------------------------------------------------
class Opener(QtCore.QThread):
    """
    separate QThread, that reads new file
    """

    exception = QtCore.pyqtSignal(str, str, str)
    done = QtCore.pyqtSignal()

    # ----------------------------------------------------------------------
    def __init__(self, data_pool, mode, params):
        super(Opener, self).__init__()

        self.data_pool = data_pool
        self.mode = mode
        self.params = params

    # ----------------------------------------------------------------------
    def run(self):
        try:
            if self.mode == 'sardana':
                finished = False
                while not finished:
                    try:
                        with h5py.File(self.params['file_name'], 'r') as f:
                            new_file = SardanaDataSet(self.data_pool, self.params['file_name'], f)
                            new_file.apply_settings()
                            self.data_pool.add_new_entry(self.params['entry_name'], new_file)
                            finished = True

                    except OSError as err:
                        if 'Resource temporarily unavailable' in str(err.args):
                            time.sleep(0.5)
                            print('Waiting for file {}'.format(self.params['file_name']))
                        else:
                            self.exception.emit('Cannot open file',
                                                'Cannot open {}'.format(self.params['file_name']),
                                                self._make_err_msg(err))
                            finished = True

            elif self.mode == 'stream':
                new_file = ASAPODataSet(self.params['detector_name'], self.params['stream_name'], self.data_pool)
                new_file.apply_settings()
                self.data_pool.add_new_entry(self.params['entry_name'], new_file)

            elif self.mode == 'reciprocal':
                with h5py.File(self.params['file_name'], 'r') as f:
                    new_file = ReciprocalScan(self.data_pool, self.params['file_name'], f)
                    new_file.apply_settings()
                    self.data_pool.add_new_entry(self.params['entry_name'], new_file)

            elif self.mode == 'beamline':
                new_file = BeamLineView(self.data_pool, self.params['file_name'])
                new_file.apply_settings()
                self.data_pool.add_new_entry(self.params['entry_name'], new_file)

        except Exception as err:
            self.exception.emit(f'Cannot open {self.mode}',
                                f'Cannot open {self.params["entry_name"]}',
                                self._make_err_msg(err)+traceback.format_exc())

        self.done.emit()

    # ----------------------------------------------------------------------
    def _make_err_msg(self, err):
        """

        :param err:
        :return:
        """
        error_msg = f'{err.__class__.__module__}.{err.__class__.__name__}: {err}'
        error_cause = err.__cause__
        while error_cause is not None:
            error_msg += f'\n\nCaused by {error_cause.__class__.__module__}.{error_cause.__class__.__name__}: {error_cause}'
            error_cause = error_cause.__cause__

        return error_msg


# ----------------------------------------------------------------------
class Batcher(QtCore.QThread):

    """
    separate QThread, that calculates ROIs for list of files
    """

    exception = QtCore.pyqtSignal(str, str, str)
    new_file = QtCore.pyqtSignal(str, float)
    done = QtCore.pyqtSignal()

    #----------------------------------------------------------------------
    def __init__(self, data_pool, file_list, dir_name, file_type):
        super(Batcher, self).__init__()
        self.file_list = file_list
        self.dir_name = dir_name
        self.file_type = file_type

        self.data_pool = data_pool

        self._stop_batch = False

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
                            self.new_file.emit(file_name, ind/total_files)
                            new_file = SardanaDataSet(self.data_pool, file_name, f)
                            new_file.apply_settings()
                            for ind, roi in self.data_pool._rois.items():
                                x_axis, y_axis = new_file.get_roi_plot(roi.get_section_params())
                                header = [new_file.file_axes_caption()[roi.get_param('axis_0')], 'ROI_value']
                                save_name = ''.join(os.path.splitext(os.path.basename(file_name))[:-1]) + \
                                            "_ROI_{}".format(ind) + self.file_type
                                self.data_pool.save_roi_to_file(self.file_type,
                                                                os.path.join(self.dir_name, save_name),
                                                                header,
                                                                np.transpose(np.vstack((x_axis, y_axis))))

                except Exception as err:
                    error_msg = f'{err.__class__.__module__}.{err.__class__.__name__}: {err}'
                    error_cause = err.__cause__
                    while error_cause is not None:
                        error_msg += f'\n\nCaused by {error_cause.__class__.__module__}.{error_cause.__class__.__name__}: {error_cause}'
                        error_cause = error_cause.__cause__

                    self.exception.emit('Cannot calculate ROI',
                                        'Cannot calculate ROI for {}'.format(file_name),
                                        error_msg)
            else:
                break

        self.done.emit()


# ----------------------------------------------------------------------
def _open_file_dialog():
    """
        displays popup message during file open
    :return:
    """
    open_mgs = QtWidgets.QMessageBox()
    open_mgs.setModal(False)
    open_mgs.setIcon(QtWidgets.QMessageBox.Information)
    open_mgs.setWindowTitle("Opening ...")
    open_mgs.setStandardButtons(QtWidgets.QMessageBox.NoButton)
    return open_mgs
