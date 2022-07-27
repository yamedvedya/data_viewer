# Created by matveyev at 02.07.2022
from petra_viewer.data_sources.p11scan.p11scan_data_set import SETTINGS
from petra_viewer.data_sources.base_classes.base_2d_detector_setup import Base2DDetectorSetup
from petra_viewer.gui.datasource_setup_p11scan_ui import Ui_P11ScanSetup

WIDGET_NAME = 'P11ScanScanSetup'


class P11ScanScanSetup(Base2DDetectorSetup):
    """
    SETTINGS = {'enable_mask': False,
                'loaded_mask': None,
                'loaded_mask_info': {'file': ''},
                'enable_ff': False,
                'loaded_ff': None,
                'loaded_ff_info': {'file': ''},
                'enable_fill': False,
                'fill_radius': 7,
                'atten_correction': 'on',
                'atten_param': 'atten',
                'inten_correction': 'on',
                'inten_param': 'eh_c01',
                }
    """

    # ----------------------------------------------------------------------
    def __init__(self, main_window):
        """
        """
        super(P11ScanScanSetup, self).__init__(main_window)
        
        self._my_ui.sp_max_frames_in_dataset.setValue(SETTINGS['max_frames_in_dataset'])

    # ----------------------------------------------------------------------
    def _get_my_ui_class(self):

        return Ui_P11ScanSetup

    # ----------------------------------------------------------------------
    def _my_settings(self):

        return SETTINGS

    # ----------------------------------------------------------------------
    def get_settings(self):

        settings = super(P11ScanScanSetup, self).get_settings()

        settings['max_frames_in_dataset'] = str(self._my_ui.sp_max_frames_in_dataset.value())

        return {'P11SCAN': settings}

