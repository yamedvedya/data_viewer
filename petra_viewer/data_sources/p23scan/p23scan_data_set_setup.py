# Created by matveyev at 02.07.2022
from petra_viewer.data_sources.p23scan.p23scan_data_set import SETTINGS
from petra_viewer.data_sources.base_classes.base_2d_detector_setup import Base2DDetectorSetup
from petra_viewer.gui.datasource_setup_p23scan_ui import Ui_P23ScanSetup
from petra_viewer.utils.utils import refresh_combo_box

WIDGET_NAME = 'P23ScanScanSetup'


class P23ScanSetup(Base2DDetectorSetup):
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
        super(P23ScanSetup, self).__init__(main_window)

        self._my_ui.le_door_address.setText(SETTINGS['door_address'])

        self._my_ui.cmb_attenuator.addItems(SETTINGS['all_params'])
        self._my_ui.cmb_attenuator.setEnabled(SETTINGS['atten_correction'])
        if SETTINGS['atten_param'] not in SETTINGS['all_params']:
            self._my_ui.cmb_attenuator.addItem(SETTINGS['atten_param'])
        refresh_combo_box(self._my_ui.cmb_attenuator, SETTINGS['atten_param'])
        self._my_ui.rb_atten_on.setChecked(SETTINGS['atten_correction'])
        self._my_ui.rb_atten_off.setChecked(not SETTINGS['atten_correction'])

        self._my_ui.cmb_intensity.addItems(SETTINGS['all_params'])
        self._my_ui.cmb_intensity.setEnabled(SETTINGS['inten_correction'])
        if SETTINGS['inten_param'] not in SETTINGS['all_params']:
            self._my_ui.cmb_intensity.addItem(SETTINGS['inten_param'])
        refresh_combo_box(self._my_ui.cmb_intensity, SETTINGS['inten_param'])
        self._my_ui.rb_inten_on.setChecked(SETTINGS['inten_correction'])
        self._my_ui.rb_inten_off.setChecked(not SETTINGS['inten_correction'])

        self._my_ui.bg_intensity.buttonClicked.connect(
            lambda button: self._my_ui.cmb_intensity.setEnabled(button == self._my_ui.rb_inten_on))
        self._my_ui.bg_attenuator.buttonClicked.connect(
            lambda button: self._my_ui.cmb_attenuator.setEnabled(button == self._my_ui.rb_atten_on))

    # ----------------------------------------------------------------------
    def _get_my_ui_class(self):

        return Ui_P23ScanSetup

    # ----------------------------------------------------------------------
    def _my_settings(self):

        return SETTINGS

    # ----------------------------------------------------------------------
    def get_settings(self):

        settings = super(P23ScanSetup, self).get_settings()

        if self._my_ui.le_door_address.text() != '':
            settings['door_address'] = str(self._my_ui.le_door_address.text())

        if self._my_ui.rb_atten_on.isChecked():
            settings['atten_param'] = str(self._my_ui.cmb_attenuator.currentText())

        if self._my_ui.rb_atten_on.isChecked():
            settings['inten_param'] = str(self._my_ui.cmb_intensity.currentText())

        return {'P23SCAN': settings}

