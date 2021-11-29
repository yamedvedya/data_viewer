# Created by matveyev at 30.03.2021

import sys
import os
from pathlib import Path
import configparser

from PyQt5 import QtWidgets, QtCore
from distutils.util import strtobool
from data_viewer.utils.utils import refresh_combo_box, check_settings

from data_viewer.data_sources.sardana.sardana_data_set_setup import SardanaScanSetup
if 'asapo_consumer' in sys.modules:
    from data_viewer.data_sources.asapo.asapo_data_set_setup import ASAPOScanSetup

from data_viewer.gui.settings_ui import Ui_Settings
from data_viewer.main_window import APP_NAME

WIDGET_NAME = 'ProgramSetup'


class ProgramSetup(QtWidgets.QDialog):

    # ----------------------------------------------------------------------
    def __init__(self, main_window):
        """
        """
        super(ProgramSetup, self).__init__()
        self._ui = Ui_Settings()
        self._ui.setupUi(self)

        self._main_window = main_window

        self._ui.cmd_sav_profile.clicked.connect(self._save_settings)
        self._ui.cmd_load_profile.clicked.connect(self._load_settings)

        self._display_settings()

    # ----------------------------------------------------------------------
    def _display_settings(self):
        self.settings = self._main_window.settings

        self._data_sources = []

        for widget in ['cube', 'roi']:
            getattr(self._ui, f'chk_{widget}').setChecked(widget in self.settings['WIDGETS']['visualization'])

        for ftype in ['asapo', 'sardana', 'beamline', 'tests']:
            getattr(self._ui, f'chk_{ftype}').setChecked(ftype in self.settings['WIDGETS']['file_types'])

        if 'DATA_POOL' in self.settings:
            if 'memory_mode' in self.settings['DATA_POOL']:
                if self.settings['DATA_POOL']['memory_mode'] == 'ram':
                    refresh_combo_box(self._ui.cmb_memory_mode, 'RAM')
                else:
                    refresh_combo_box(self._ui.cmb_memory_mode, 'DRIVE/ASAPO')

            if 'max_open_files' in self.settings['DATA_POOL']:
                self._ui.sp_lim_num.setValue(int(self.settings['DATA_POOL']['max_open_files']))

            if 'max_memory_usage' in self.settings['DATA_POOL']:
                self._ui.sb_lim_mem.setValue(int(self.settings['DATA_POOL']['max_memory_usage']))

            if 'export_file_delimiter' in self.settings['DATA_POOL']:
                self._ui.le_separator.setText(self.settings['DATA_POOL']['export_file_delimiter'])

            if 'export_file_format' in self.settings['DATA_POOL']:
                self._ui.le_format.setText(self.settings['DATA_POOL']['export_file_format'])

        if 'FRAME_VIEW' in self.settings:

            for setting in ['axes', 'axes_titles', 'grid', 'cross', 'aspect']:
                if f'display_{setting}' in self.settings['FRAME_VIEW']:
                    getattr(self._ui, f'chk_{setting}').setChecked(strtobool(self.settings['FRAME_VIEW'][f'display_{setting}']))

            if 'backend' in self.settings['FRAME_VIEW']:
                refresh_combo_box(self._ui.cmb_backend, str(self.settings['FRAME_VIEW']['backend']))

            if 'levels' in self.settings['FRAME_VIEW']:
                refresh_combo_box(self._ui.cmd_default_hist, str(self.settings['FRAME_VIEW']['levels']))

        if 'CUBE_VIEW' in self.settings:
            for setting in ['slices', 'borders']:
                if setting in self.settings['CUBE_VIEW']:
                    getattr(self._ui, f'sp_{setting}').setValue(int(self.settings['CUBE_VIEW'][setting]))

            for setting in ['smooth', 'white_background']:
                if setting in self.settings['CUBE_VIEW']:
                    getattr(self._ui, f'chk_{setting}').setChecked(strtobool(self.settings['CUBE_VIEW'][setting]))

        if self._main_window.configuration['sardana'] or self._main_window.configuration['tests']:
            widget = SardanaScanSetup(self._main_window)
            self._data_sources.append(widget)
            self._ui.tb_sources.addTab(widget, 'Sardana')

        if self._main_window.configuration['asapo'] or self._main_window.configuration['tests']:
            widget = ASAPOScanSetup(self._main_window)
            self._data_sources.append(widget)
            self._ui.tb_sources.addTab(widget, 'ASAPO')

    # ----------------------------------------------------------------------
    def _get_settings(self):

        settings = {'WIDGETS': {'visualization': '', 'file_types': ''}}
        cmd = []
        for widget in ['cube', 'roi']:
            if getattr(self._ui, f'chk_{widget}').isChecked():
                cmd.append(widget)

        settings['WIDGETS']['visualization'] = ';'.join(cmd)

        cmd = []
        for widget in ['asapo', 'sardana', 'beamline', 'tests']:
            if getattr(self._ui, f'chk_{widget}').isChecked():
                cmd.append(widget)

        settings['WIDGETS']['file_types'] = ';'.join(cmd)

        settings['DATA_POOL'] = {'max_open_files': str(self._ui.sp_lim_num.value()),
                                 'max_memory_usage': str(self._ui.sb_lim_mem.value()),
                                 'export_file_delimiter': str(self._ui.le_separator.text()),
                                 'export_file_format': str(self._ui.le_format.text()),
                                 'memory_mode': 'ram' if self._ui.cmb_memory_mode.currentText() == 'RAM' else 'drive'}

        settings['FRAME_VIEW'] = {'backend': self._ui.cmb_backend.currentText(),
                                  'levels': self._ui.cmd_default_hist.currentText()}

        for setting in ['axes', 'axes_titles', 'grid', 'cross', 'aspect']:
            settings['FRAME_VIEW'][f'display_{setting}'] = str(getattr(self._ui, f'chk_{setting}').isChecked())

        settings['CUBE_VIEW'] = {}
        for setting in ['slices', 'borders']:
            settings['CUBE_VIEW'][setting] = str(getattr(self._ui, f'sp_{setting}').value())

        for setting in ['smooth', 'white_background']:
            settings['CUBE_VIEW'][setting] = str(getattr(self._ui, f'chk_{setting}').isChecked())

        for widget in self._data_sources:
            source_settings = widget.get_settings()
            if source_settings != {}:
                settings.update(source_settings)

        return settings

    # ----------------------------------------------------------------------
    def accept(self):

        self.settings.update(self._get_settings())

        self._main_window.apply_settings()

        QtCore.QSettings(APP_NAME).setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())

        super(ProgramSetup, self).accept()

    # ----------------------------------------------------------------------
    def reject(self):

        QtCore.QSettings(APP_NAME).setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())

        super(ProgramSetup, self).reject()

    # ----------------------------------------------------------------------
    def _save_settings(self):

        settings = configparser.ConfigParser()
        settings.update(self._get_settings())

        file = QtWidgets.QFileDialog.getSaveFileName(self, 'Save as...',
                                                     os.path.join(str(Path.home()), '.petra_viewer'),
                                                     'INI settings (*.ini)')
        if file[0]:
            with open(file[0] + '.ini', 'w') as configfile:
                settings.write(configfile)

    # ----------------------------------------------------------------------
    def _load_settings(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, 'Load settings...',
                                                     os.path.join(str(Path.home()), '.petra_viewer'),
                                                     'INI settings (*.ini)')
        if file[0]:
            settings = configparser.ConfigParser()
            settings.read(file[0])
            if check_settings(settings):
                self._main_window.set_settings(settings)

            self._ui.tb_sources.clear()
            self._display_settings()

