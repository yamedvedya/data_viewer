# Created by matveyev at 30.03.2021

import configparser

from PyQt5 import QtWidgets, QtCore

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
            if 'max_open_files' in settings['DATA_POOL']:
                self._ui.sp_lim_num.setValue(int(settings['DATA_POOL']['max_open_files']))

            if 'max_memory_usage' in settings['DATA_POOL']:
                self._ui.sb_lim_mem.setValue(int(settings['DATA_POOL']['max_memory_usage']))

        if 'ASAPO' in settings:
            if 'host' in settings['ASAPO']:
                self._ui.le_host.setText(settings['ASAPO']['host'])

            if 'beamtime' in settings['ASAPO']:
                self._ui.le_beamtime.setText(settings['ASAPO']['beamtime'])

            if 'token' in settings['ASAPO']:
                self._ui.le_token.setText(settings['ASAPO']['token'])

            if 'detectors' in settings['ASAPO']:
                self._ui.le_detectors.setText(settings['ASAPO']['detectors'])

    # ----------------------------------------------------------------------
    def accept(self):

        settings = configparser.ConfigParser()
        settings.read('./settings.ini')
        settings['FILE_BROWSER'] = {'door_address': str(self._ui.le_door_address.text())}

        settings['DATA_POOL'] = {'max_open_files': str(self._ui.sp_lim_num.value()),
                                 'max_memory_usage': str(self._ui.sb_lim_mem.value())}

        settings['ASAPO'] = {'host': str(self._ui.le_host.text()),
                             'beamtime': str(self._ui.le_beamtime.text()),
                             'token': str(self._ui.le_token.text()),
                             'detectors': str(self._ui.le_detectors.text())}

        self._main_window.apply_settings(settings)

        with open('./settings.ini', 'w') as configfile:
            settings.write(configfile)

        QtCore.QSettings(APP_NAME).setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())

        super(ProgramSetup, self).accept()

    # ----------------------------------------------------------------------
    def reject(self):

        QtCore.QSettings(APP_NAME).setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())

        super(ProgramSetup, self).reject()