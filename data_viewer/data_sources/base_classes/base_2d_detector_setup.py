# Created by matveyev at 13.08.2021
import logging
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore
from pyqtgraph.graphicsItems.GradientEditorItem import Gradients

from data_viewer.main_window import APP_NAME
from data_viewer.utils.utils import read_mask_file, read_ff_file

WIDGET_NAME = ''
logger = logging.getLogger(APP_NAME)


class Base2DDetectorSetup(QtWidgets.QWidget):
    """
    General class, which provides GUI interface to setup parameters

    These are common parameters:

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
        super(Base2DDetectorSetup, self).__init__()

        self._ui = self._get_ui()
        self._ui.setupUi(self)

        self._main_window = main_window
        self._data_pool = data_pool

        # pyqtgraph instance to display pixel mask
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

        self._plot_2d = pg.ImageItem()
        self._plot_2d.setLookupTable(pg.ColorMap(*zip(*Gradients['grey']["ticks"])).getLookupTable())
        self._main_plot.addItem(self._plot_2d)

        # display current setting
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

        self._display_mask()

        # signals from interface
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
            logger.error("{} : cannot restore geometry: {}".format(WIDGET_NAME, err))

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
        """
        load mask of flat filed mask form file

        :param mode: 'mask' or 'ff' (flat filed)
        :return:
        """
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
        """
        calculated mask for current setting and displays it
        :return:
        """

        _mask = self._calculate_mask()

        if _mask is not None:
            try:
                self._plot_2d.setImage(_mask, autoLevels=True)
            except Exception as err:
                logger.error("{} : cannot display mask geometry: {}".format(WIDGET_NAME, err))
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
