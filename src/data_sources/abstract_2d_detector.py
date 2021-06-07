# Created by matveyev at 20.05.2021

import pyqtgraph as pg
import numpy as np
from scipy import ndimage

from pyqtgraph.graphicsItems.GradientEditorItem import Gradients

from PyQt5 import QtWidgets, QtCore

from src.main_window import APP_NAME
from src.utils.utils import read_mask_file, read_ff_file

WIDGET_NAME = ''

# ----------------------------------------------------------------------
class DetectorImage():

    # ----------------------------------------------------------------------
    def _get_settings(self):
        raise RuntimeError('Non implemented')

    # ----------------------------------------------------------------------
    def _reload_data(self, frame_ids=None):
        raise RuntimeError('Non implemented')

    # ----------------------------------------------------------------------
    def _get_cube_shape(self):
        raise RuntimeError('Non implemented')

    # ----------------------------------------------------------------------
    def _get_correction(self, cube_shape, frame_ids=None):

        self._correction = np.ones(cube_shape[0], dtype=np.float32)

    # ----------------------------------------------------------------------
    def _get_data(self, frame_id=None):

        if self._data_pool.memory_mode == 'ram':
            if not self._need_apply_mask:
                return np.copy(self._3d_cube)
            else:
                self._3d_cube = None
                _data = self._reload_data()
        else:
            self._3d_cube = None
            _data = self._reload_data(frame_id)

        _settings = self._get_settings()

        _pixel_mask = None
        _fill_weights = None

        if _settings['enable_mask'] and _settings['mask'] is not None:
            _pixel_mask = _settings['mask'] > 0

        if _settings['enable_ff'] and _settings['ff'] is not None:
            _ff = np.copy(_settings['ff'])
            if _pixel_mask is None:
                _pixel_mask = (_ff < _settings['ff_min']) + (_ff > _settings['ff_max'])
            else:
                _pixel_mask += (_ff < _settings['ff_min']) + (_ff > _settings['ff_max'])

        if _settings['enable_fill']:
            _fill_weights = ndimage.uniform_filter(1.-_pixel_mask, size=_settings['fill_radius'])

        self._get_correction(_data.shape, frame_id)

        try:
            if _pixel_mask is not None:
                for frame in _data:
                    frame[_pixel_mask] = 0

            if _settings['enable_ff'] and _settings['ff'] is not None:
                for ind in range(_data.shape[0]):
                    _data[ind] = _data[ind]/_settings['ff']

            if _settings['enable_fill']:
                for ind in range(_data.shape[0]):
                    frame_f = ndimage.uniform_filter(_data[ind], size=_settings['fill_radius'])
                    if _pixel_mask is not None:
                        _data[ind][_pixel_mask] = (frame_f/_fill_weights)[_pixel_mask]
                    else:
                        _data[ind] = (frame_f/_fill_weights)

            for frame, corr in zip(_data, self._correction):
                    frame *= corr

        except Exception as err:
            raise RuntimeError("{}: cannot apply mask: {}".format(self.my_name, err))

        if self._data_pool.memory_mode == 'ram':
            self._need_apply_mask = False
            self._3d_cube = np.copy(_data)

        return _data

    # ----------------------------------------------------------------------
    def _get_2d_cut(self, axis, cut_range, x_axis, y_axis):

        cut_axis = self._cube_axes_map[axis]

        if cut_axis == 0 and self._data_pool.memory_mode != 'ram':
            data = self._get_data(cut_range)
        else:
            data = self._get_data()
            if cut_axis == 0:
                data = data[cut_range[0]:cut_range[1], :, :]
            elif cut_axis == 1:
                data = data[:, cut_range[0]:cut_range[1], :]
            else:
                data = data[:, :, cut_range[0]:cut_range[1]]
        data = np.sum(data, axis=cut_axis)

        if self._cube_axes_map[x_axis] > self._cube_axes_map[y_axis]:
            return np.transpose(data)
        else:
            return data

    # ----------------------------------------------------------------------
    def _get_roi_data(self, sect, do_sum):

        plot_axis = self._cube_axes_map[sect['axis']]
        cut_axis_1 = self._cube_axes_map[sect['roi_1_axis']]

        data = self._get_data()
        if plot_axis == 0:
            if cut_axis_1 == 1:
                data = data[:,
                            sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                            sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']]
            else:
                data = data[:,
                            sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                            sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']]
            if do_sum:
                data = np.sum(data, axis=1)
                data = np.sum(data, axis=1)

        elif plot_axis == 1:
            if cut_axis_1 == 0:
                data = data[sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                            :,
                            sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width']]
            else:
                data = data[sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                            :,
                            sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width']]
            if do_sum:
                data = np.sum(data, axis=2)
                data = np.sum(data, axis=0)

        else:
            if cut_axis_1 == 0:
                data = data[sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                            sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                            :]
            else:
                data = data[sect['roi_2_pos']:sect['roi_2_pos'] + sect['roi_2_width'],
                            sect['roi_1_pos']:sect['roi_1_pos'] + sect['roi_1_width'],
                            :]
            if do_sum:
                data = np.sum(data, axis=0)
                data = np.sum(data, axis=0)

        return self._get_roi_axis(plot_axis), data


# ----------------------------------------------------------------------
class DetectorImageSetup(QtWidgets.QWidget):
    """
    SETTINGS = {'enable_mask': False,
                'mask': None,
                'mask_file': '',
                'enable_ff': False,
                'ff': None,
                'ff_file': '',
                'ff_min': 0,
                'ff_max': 100,
                'enable_fill': False,
                'fill_radius': 7,
                'displayed_param': 'frame_ID',
                }
    """

    # ----------------------------------------------------------------------
    def __init__(self, main_window, data_pool):
        """
        """
        super(DetectorImageSetup, self).__init__()

        self._ui = self._get_ui()
        self._ui.setupUi(self)

        self._main_window = main_window
        self._data_pool = data_pool

        self._main_plot = pg.PlotItem()
        self._main_plot.showAxis('left', False)
        self._main_plot.showAxis('bottom', False)
        self._main_plot.setMenuEnabled(False)

        self._ui.gv_main.setStyleSheet("")
        self._ui.gv_main.setBackground('w')
        self._ui.gv_main.setObjectName("gvMain")

        self._ui.gv_main.setCentralItem(self._main_plot)
        self._ui.gv_main.setRenderHints(self._ui.gv_main.renderHints())

        self._main_plot.getViewBox().setAspectLocked()

        _settings = self.get_settings()

        self._old_settings = dict(_settings)

        for param in ['mask', 'ff']:
            if _settings[f'enable_{param}']:
                getattr(self._ui, f'rb_{param}_on').setChecked(True)
                getattr(self._ui, f'but_load_{param}').setChecked(True)
                getattr(self._ui, f'lb_{param}_file').setText(_settings[f'{param}_file'])
            else:
                getattr(self._ui, f'rb_{param}_off').setChecked(True)

        self._ui.dsb_ff_from.setValue(_settings['ff_min'])
        self._ui.dsb_ff_to.setValue(_settings['ff_max'])

        if _settings['enable_fill']:
            self._ui.rb_fill_on.setChecked(True)
            self._ui.sb_fill.setEnabled(True)
            self._ui.sb_fill.setValue(_settings['fill_radius'])
        else:
            self._ui.rb_fill_off.setChecked(True)

        self._plot_2d = pg.ImageItem()
        self._plot_2d.setLookupTable(pg.ColorMap(*zip(*Gradients['grey']["ticks"])).getLookupTable())
        self._main_plot.addItem(self._plot_2d)

        self._display_mask()

        self._ui.bg_mask_option.buttonClicked.connect(lambda button: self.change_mode(button, 'mask'))
        self._ui.bg_ff_option.buttonClicked.connect(lambda button: self.change_mode(button, 'ff'))
        self._ui.bg_fill_option.buttonClicked.connect(self.change_fill)

        self._ui.but_load_mask.clicked.connect(lambda: self.load_from_file('mask'))
        self._ui.but_load_ff.clicked.connect(lambda: self.load_from_file('ff'))

        self._ui.dsb_ff_from.valueChanged.connect(lambda value, mode='min': self._new_ff_limit(value, mode))
        self._ui.dsb_ff_to.valueChanged.connect(lambda value, mode='max': self._new_ff_limit(value, mode))

        self._main_plot.scene().sigMouseClicked.connect(self._mouse_clicked)

        try:
            self.restoreGeometry(QtCore.QSettings(APP_NAME).value("{}/geometry".format(WIDGET_NAME)))
        except Exception as err:
            self._main_window.log.error("{} : cannot restore geometry: {}".format(WIDGET_NAME, err))

    # ----------------------------------------------------------------------
    def _get_ui(self):
        raise RuntimeError('Non implemented')

    # ----------------------------------------------------------------------
    def get_name(self):
        raise RuntimeError('Non implemented')

    # ----------------------------------------------------------------------
    def get_settings(self):
        raise RuntimeError('Non implemented')

    # ----------------------------------------------------------------------
    def change_fill(self, button):
        _settings = self.get_settings()

        if button == self._ui.rb_fill_off:
            _settings['enable_fill'] = False
            self._ui.sb_fill.setEnabled(False)
        else:
            _settings['enable_fill'] = True
            self._ui.sb_fill.setEnabled(True)

    # ----------------------------------------------------------------------
    def change_mode(self, button, mode):

        _settings = self.get_settings()

        if button == getattr(self._ui, f'rb_{mode}_off'):
            _settings[f'enable_{mode}'] = False
            getattr(self._ui, f'but_load_{mode}').setEnabled(False)
        else:
            if _settings[f'{mode}'] is None:
                if not self.load_from_file(mode):
                    _settings[f'enable_{mode}'] = False
                    getattr(self._ui, f'but_load_{mode}').setEnabled(False)
                    return
            _settings[f'enable_{mode}'] = True


            getattr(self._ui, f'but_load_{mode}').setEnabled(True)
            self._ui.lb_mask_file.setText(_settings[f'{mode}_file'])

        self._display_mask()

    # ----------------------------------------------------------------------
    def load_from_file(self, mode):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, f'Open file with {mode}',
                                                             self._main_window.get_current_folder())

        if file_name:
            if mode =='mask':
                data = read_mask_file(file_name)
            else:
                data = read_ff_file(file_name)

            if data is not None:
                _settings = self.get_settings()
                _settings[f'{mode}'] = data
                _settings[f'{mode}_file'] = file_name
                getattr(self._ui, f'lb_{mode}_file').setText(file_name)

                return True

        return False

    # ----------------------------------------------------------------------
    def _new_ff_limit(self, value, lim):
        _settings = self.get_settings()
        _settings[f'ff_{lim}'] = value
        self._display_mask()

    # ----------------------------------------------------------------------
    def _display_mask(self):

        _mask = self._calculate_mask()

        if _mask is not None:
            try:
                self._plot_2d.setImage(_mask, autoLevels=True)
            except Exception as err:
                self._main_window.log.error("{} : cannot display mask geometry: {}".format(WIDGET_NAME, err))
                self._plot_2d.clear()
        else:
            self._plot_2d.clear()

    # ----------------------------------------------------------------------
    def _calculate_mask(self):

        _mask = None

        _settings = self.get_settings()

        if _settings['enable_mask']:
            _mask = np.copy(_settings['mask'])
            _mask = _mask > 0

        if _settings['enable_ff']:
            _ff = np.copy(_settings['ff'])
            if _mask is None:
                _mask = (_ff < _settings['ff_min']) + (_ff > _settings['ff_max'])
            else:
                _mask += (_ff < _settings['ff_min']) + (_ff > _settings['ff_max'])

        return _mask

    # ----------------------------------------------------------------------
    def accept(self):

        QtCore.QSettings(APP_NAME).setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())

    # ----------------------------------------------------------------------
    def reject(self):

        _settings = self.get_settings()

        for key in _settings.keys():
            _settings[key] = self._old_settings[key]

        QtCore.QSettings(APP_NAME).setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())

    # ----------------------------------------------------------------------
    def _mouse_clicked(self, event):
        """
        """
        if event.double():
            try:
                self._main_plot.autoRange()
            except:
                pass

