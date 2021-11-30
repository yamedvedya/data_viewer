# Created by matveyev at 13.08.2021
from petra_viewer.data_sources.asapo.asapo_data_set import SETTINGS
from petra_viewer.data_sources.base_classes.base_2d_detector_setup import Base2DDetectorSetup
from petra_viewer.gui.datasource_setup_asapo_ui import Ui_ASAPOImageSetup

WIDGET_NAME = 'ASAPOScanSetup'


class ASAPOScanSetup(Base2DDetectorSetup):

    # ----------------------------------------------------------------------
    def _my_ui(self):

        return Ui_ASAPOImageSetup()

    # ----------------------------------------------------------------------
    def _my_settings(self):

        return SETTINGS

    # ----------------------------------------------------------------------
    def get_settings(self):

        settings = super(ASAPOScanSetup, self).get_settings()

        settings.update({'max_streams': str(self._ui.sp_max_streams.value()),
                         'max_messages': str(self._ui.sp_max_messages.value())})

        if str(self._ui.le_host.text()) != '' and str(self._ui.le_beamtime.text()) != '' \
                and str(self._ui.le_token.text()) != '' and str(self._ui.le_detectors.text()) != '':
            settings.update({'host': str(self._ui.le_host.text()),
                             'path': str(self._ui.le_path.text()),
                             'has_filesystem': str(self._ui.chk_filesystem.isChecked()),
                             'beamtime': str(self._ui.le_beamtime.text()),
                             'token': str(self._ui.le_token.text()),
                             'detectors': str(self._ui.le_detectors.text())})

        return {'ASAPO': settings}
