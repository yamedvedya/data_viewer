# Created by matveyev at 30.03.2021

import configparser

from PyQt5 import QtWidgets, QtCore
from distutils.util import strtobool
from data_viewer.utils.utils import refresh_combo_box

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

        settings = configparser.ConfigParser()
        settings.read('./settings.ini')

        if 'SARDANA_SCANS' in settings:
            if 'door_address' in settings['SARDANA_SCANS']:
                self._ui.le_door_address.setText(settings['SARDANA_SCANS']['door_address'])

            if 'default_mask' in settings['SARDANA_SCANS']:
                self._ui.gb_sardana_default_mask.setChecked(True)
                self._ui.le_sardana_mask_file.setText(settings['SARDANA_SCANS']['default_mask'])

            if 'default_ff' in settings['SARDANA_SCANS']:
                self._ui.gb_sardana_default_mask.setChecked(True)
                self._ui.le_sardana_ff_file.setText(settings['SARDANA_SCANS']['default_ff'])

                if 'min_ff' in settings['SARDANA_SCANS']:
                    self._ui.dsp_sardana_ff_min.setValue(float(settings['SARDANA_SCANS']['min_ff']))

                if 'max_ff' in settings['SARDANA_SCANS']:
                    self._ui.dsp_sardana_ff_max.setValue(float(settings['SARDANA_SCANS']['max_ff']))

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

            if 'export_file_delimiter' in settings['DATA_POOL']:
                self._ui.le_separator.setText(settings['DATA_POOL']['export_file_delimiter'])

            if 'export_file_format' in settings['DATA_POOL']:
                self._ui.le_format.setText(settings['DATA_POOL']['export_file_format'])

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

            if 'max_messages' in settings['ASAPO']:
                self._ui.sp_max_messages.setValue(int(settings['ASAPO']['max_messages']))

            if 'default_mask' in settings['ASAPO']:
                self._ui.gb_asapo_default_mask.setChecked(True)
                self._ui.le_asapo_mask_file.setText(settings['ASAPO']['default_mask'])

            if 'default_ff' in settings['ASAPO']:
                self._ui.gb_asapo_default_mask.setChecked(True)
                self._ui.le_asapo_ff_file.setText(settings['ASAPO']['default_ff'])

                if 'min_ff' in settings['ASAPO']:
                    self._ui.dsp_asapo_ff_min.setValue(float(settings['ASAPO']['min_ff']))

                if 'max_ff' in settings['ASAPO']:
                    self._ui.dsp_asapo_ff_max.setValue(float(settings['ASAPO']['max_ff']))

        if 'FRAME_VIEW' in settings:

            for setting in ['axes', 'axes_titles', 'grid', 'cross', 'aspect']:
                if f'display_{setting}' in settings['FRAME_VIEW']:
                    getattr(self._ui, f'chk_{setting}').setChecked(strtobool(settings['FRAME_VIEW'][f'display_{setting}']))

            if 'backend' in settings['FRAME_VIEW']:
                refresh_combo_box(self._ui.cmb_backend, str(settings['FRAME_VIEW']['backend']))

        if 'CUBE_VIEW' in settings:

            for setting in ['slices', 'borders']:
                if setting in settings['CUBE_VIEW']:
                    getattr(self._ui, f'sp_{setting}').setValue(int(settings['CUBE_VIEW'][setting]))

            for setting in ['smooth', 'white_background']:
                if setting in settings['CUBE_VIEW']:
                    getattr(self._ui, f'chk_{setting}').setChecked(strtobool(settings['CUBE_VIEW'][setting]))

    @staticmethod
    # ----------------------------------------------------------------------
    def _set_or_make_filed(settings, root_filed, fields, values):
        if root_filed in settings:
            settings[root_filed].update({field: value for field, value in zip(fields, values)})
        else:
            settings[root_filed] = {field: value for field, value in zip(fields, values)}

        return settings

    # ----------------------------------------------------------------------
    def accept(self):

        settings = configparser.ConfigParser()
        settings.read('./settings.ini')

        if str(self._ui.le_door_address.text()) != '':
            settings = self._set_or_make_filed(settings, 'SARDANA_SCANS',
                                               ['door_address'], [str(self._ui.le_door_address.text())])

        if self._ui.gb_sardana_default_mask.isChecked():
            settings = self._set_or_make_filed(settings, 'SARDANA_SCANS',
                                               ['default_mask'], [str(self._ui.le_sardana_mask_file.text())])

        if self._ui.gb_sardana_default_ff.isChecked():
            settings = self._set_or_make_filed(settings, 'SARDANA_SCANS',
                                               ['door_address', 'min_ff', 'max_ff'],
                                               [str(self._ui.le_door_address.text()),
                                                str(self._ui.dsp_sardana_ff_min.value()),
                                                str(self._ui.dsp_sardana_ff_max.value())])

        settings['DATA_POOL'] = {'max_open_files': str(self._ui.sp_lim_num.value()),
                                 'max_memory_usage': str(self._ui.sb_lim_mem.value()),
                                 'export_file_delimiter': str(self._ui.le_separator.text()),
                                 'export_file_format': str(self._ui.le_format.text()),
                                 'memory_mode':'ram' if self._ui.cmb_memory_mode.currentText() == 'RAM' else 'drive'}

        settings['ASAPO'] = {'max_streams': str(self._ui.sp_max_streams.value()),
                             'max_messages': str(self._ui.sp_max_messages.value())}

        if str(self._ui.le_host.text()) != '' and str(self._ui.le_beamtime.text()) != '' \
                and str(self._ui.le_token.text()) != '' and str(self._ui.le_detectors.text()) != '':

            settings['ASAPO'].update({'host': str(self._ui.le_host.text()),
                                      'path': str(self._ui.le_path.text()),
                                      'has_filesystem': str(self._ui.chk_filesystem.isChecked()),
                                      'beamtime': str(self._ui.le_beamtime.text()),
                                      'token': str(self._ui.le_token.text()),
                                      'detectors': str(self._ui.le_detectors.text())})

        if self._ui.gb_sardana_default_mask.isChecked():
            settings['ASAPO']['default_mask'] = str(self._ui.le_asapo_mask_file.text())

        if self._ui.gb_sardana_default_ff.isChecked():
            settings['ASAPO']['default_ff'] = str(self._ui.le_asapo_ff_file.text())
            settings['ASAPO']['min_ff'] = str(self._ui.dsp_asapo_ff_min.value())
            settings['ASAPO']['max_ff'] = str(self._ui.dsp_asapo_ff_max.value())

        for setting in ['axes', 'axes_titles', 'grid', 'cross', 'aspect']:
            settings = self._set_or_make_filed(settings, 'FRAME_VIEW',
                                               [f'display_{setting}'], [str(getattr(self._ui, f'chk_{setting}').isChecked())])

        if 'backend' in settings['FRAME_VIEW']:
            settings['FRAME_VIEW']['backend'] = self._ui.cmb_backend.currentText()

        for setting in ['slices', 'borders']:
            settings = self._set_or_make_filed(settings, 'CUBE_VIEW',
                                               [setting], [str(getattr(self._ui, f'sp_{setting}').value())])

        for setting in ['smooth', 'white_background']:
            settings['CUBE_VIEW'][setting] = str(getattr(self._ui, f'chk_{setting}').isChecked())

        self._main_window.apply_settings(settings)

        with open('./settings.ini', 'w') as configfile:
            settings.write(configfile)

        QtCore.QSettings(APP_NAME).setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())

        super(ProgramSetup, self).accept()

    # ----------------------------------------------------------------------
    def reject(self):

        QtCore.QSettings(APP_NAME).setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())

        super(ProgramSetup, self).reject()