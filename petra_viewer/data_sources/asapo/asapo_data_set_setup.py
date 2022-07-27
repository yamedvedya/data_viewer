# Created by matveyev at 13.08.2021
from petra_viewer.data_sources.asapo.asapo_data_set import SETTINGS
from petra_viewer.data_sources.base_classes.base_2d_detector_setup import Base2DDetectorSetup
from petra_viewer.gui.datasource_setup_asapo_ui import Ui_ASAPOSetup

WIDGET_NAME = 'ASAPOScanSetup'


class ASAPOScanSetup(Base2DDetectorSetup):

    # ----------------------------------------------------------------------
    def __init__(self, main_window):
        """
        """
        super(ASAPOScanSetup, self).__init__(main_window)

        self._my_ui.le_host.setText(SETTINGS['host'])
        self._my_ui.le_path.setText(SETTINGS['path'])

        self._my_ui.chk_filesystem.setChecked(SETTINGS['has_filesystem'])

        self._my_ui.le_beamtime.setText(SETTINGS['beamtime'])
        self._my_ui.le_token.setText(SETTINGS['token'])
        self._my_ui.le_detectors.setText(SETTINGS['detectors'])

        self._my_ui.sp_max_messages.setValue(SETTINGS['max_messages'])
        self._my_ui.sp_max_streams.setValue(SETTINGS['max_streams'])

    # ----------------------------------------------------------------------
    def _get_my_ui_class(self):

        return Ui_ASAPOSetup

    # ----------------------------------------------------------------------
    def _my_settings(self):

        return SETTINGS

    # ----------------------------------------------------------------------
    def get_settings(self):

        settings = super(ASAPOScanSetup, self).get_settings()

        settings.update({'max_streams': str(self._my_ui.sp_max_streams.value()),
                         'max_messages': str(self._my_ui.sp_max_messages.value()),
                         'host': str(self._my_ui.le_host.text()),
                         'path': str(self._my_ui.le_path.text()),
                         'has_filesystem': str(self._my_ui.chk_filesystem.isChecked()),
                         'beamtime': str(self._my_ui.le_beamtime.text()),
                         'token': str(self._my_ui.le_token.text()),
                         'detectors': str(self._my_ui.le_detectors.text())})

        return {'ASAPO': settings}
