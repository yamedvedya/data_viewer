# Created by matveyev at 30.03.2021

import configparser

from PyQt5 import QtWidgets, QtCore
from distutils.util import strtobool
from src.utils.utils import refresh_combo_box

from src.gui.settings_ui import Ui_Settings
from src.main_window import APP_NAME

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

        settings = configparser.ConfigParser()
        settings.read('./settings.ini')

        if 'FILE_BROWSER' in settings:
            if 'door_address' in settings['FILE_BROWSER']:
                self._ui.le_door_address.setText(settings['FILE_BROWSER']['door_address'])

        if 'DATA_POOL' in settings:
            if 'memory_mode' in settings['DATA_POOL']:
                if settings['DATA_POOL']['memory_mode'] == 'ram':
                    refresh_combo_box(self._ui.cmb_memory_mode, 'RAM')
                else:
                    refresh_combo_box(self._ui.cmb_memory_mode, 'DRIVE/ASAPO')

            if 'max_open_files' in settings['DATA_POOL']:
                self._ui.sp_lim_num.setValue(int(settings['DATA_POOL']['max_open_files']))

            if 'max_memory_usage' in settings['DATA_POOL']:
                self._ui.sb_lim_mem.setValue(int(settings['DATA_POOL']['max_memory_usage']))

            if 'delimiter' in settings['DATA_POOL']:
                self._ui.le_separator.setText(settings['DATA_POOL']['delimiter'])

            if 'format' in settings['DATA_POOL']:
                self._ui.le_format.setText(settings['DATA_POOL']['format'])

        if 'ASAPO' in settings:

            if 'host' in settings['ASAPO']:
                self._ui.le_host.setText(settings['ASAPO']['host'])

            if 'path' in settings['ASAPO']:
                self._ui.le_path.setText(settings['ASAPO']['path'])

            if 'has_filesystem' in settings['ASAPO']:
                self._ui.chk_filesystem.setChecked(strtobool(settings['ASAPO']['has_filesystem']))

            if 'beamtime' in settings['ASAPO']:
                self._ui.le_beamtime.setText(settings['ASAPO']['beamtime'])

            if 'token' in settings['ASAPO']:
                self._ui.le_token.setText(settings['ASAPO']['token'])

            if 'detectors' in settings['ASAPO']:
                self._ui.le_detectors.setText(settings['ASAPO']['detectors'])

            if 'max_streams' in settings['ASAPO']:
                self._ui.sp_max_streams.setValue(int(settings['ASAPO']['max_streams']))

    # ----------------------------------------------------------------------
    def accept(self):

        settings = configparser.ConfigParser()
        settings.read('./settings.ini')
        if str(self._ui.le_door_address.text()) != '':
            settings['FILE_BROWSER'] = {'door_address': str(self._ui.le_door_address.text())}

        if self._ui.cmb_memory_mode.currentText() == 'RAM':
            settings['DATA_POOL'] = {'memory_mode': 'ram'}
        else:
            settings['DATA_POOL'] = {'memory_mode': 'drive'}

        settings['DATA_POOL'].update({'max_open_files': str(self._ui.sp_lim_num.value()),
                                      'max_memory_usage': str(self._ui.sb_lim_mem.value()),
                                      'delimiter': str(self._ui.le_separator.text()),
                                      'format': str(self._ui.le_format.text())})

        if str(self._ui.le_host.text()) != '' and str(self._ui.le_beamtime.text()) != '' \
                and str(self._ui.le_token.text()) != '' and str(self._ui.le_detectors.text()) != '':
            settings['ASAPO'] = {'host': str(self._ui.le_host.text()),
                                 'path': str(self._ui.le_path.text()),
                                 'has_filesystem': str(self._ui.chk_filesystem.isChecked()),
                                 'beamtime': str(self._ui.le_beamtime.text()),
                                 'token': str(self._ui.le_token.text()),
                                 'detectors': str(self._ui.le_detectors.text()),
                                 'max_streams': str(self._ui.sp_max_streams.value())}

        self._main_window.apply_settings(settings)

        with open('./settings.ini', 'w') as configfile:
            settings.write(configfile)

        QtCore.QSettings(APP_NAME).setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())

        super(ProgramSetup, self).accept()

    # ----------------------------------------------------------------------
    def reject(self):

        QtCore.QSettings(APP_NAME).setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())

        super(ProgramSetup, self).reject()