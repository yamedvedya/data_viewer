# Created by matveyev at 13.08.2021
from src.data_sources.asapo.asapo_data_set import SETTINGS
from src.data_sources.base_classes.base_2d_detector_setup import Base2DDetectorSetup
from src.gui.asapo_image_setup_ui import Ui_ASAPOImageSetup

WIDGET_NAME = 'ASAPOScanSetup'


class ASAPOScanSetup(Base2DDetectorSetup):

    # ----------------------------------------------------------------------
    def _get_ui(self):

        return Ui_ASAPOImageSetup()

    # ----------------------------------------------------------------------
    def get_name(self):

        return 'ASAPO Scan Setup'

    # ----------------------------------------------------------------------
    def get_settings(self):

        return SETTINGS