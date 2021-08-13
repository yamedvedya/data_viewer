# Created by matveyev at 13.08.2021
from src.data_sources.sardana.sardana_data_set import SETTINGS
from src.data_sources.base_classes.base_2d_detector_setup import Base2DDetectorSetup
from src.gui.lambda_setup_ui import Ui_LambdaSetup
from src.utils.utils import refresh_combo_box

WIDGET_NAME = 'SardanaScanSetup'


class SardanaScanSetup(Base2DDetectorSetup):
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
                'displayed_param': 'point_nb',
                'all_params': [],
                }
    """

    # ----------------------------------------------------------------------
    def __init__(self, main_window, data_pool):
        """
        """
        super(SardanaScanSetup, self).__init__(main_window, data_pool)

        self._ui.cmb_attenuator.addItems(SETTINGS['all_params'])
        self._ui.cmb_attenuator.setEnabled(SETTINGS['atten_correction'] == 'on')
        if SETTINGS['atten_param'] not in SETTINGS['all_params']:
            self._ui.cmb_attenuator.addItem(SETTINGS['atten_param'])
        refresh_combo_box(self._ui.cmb_attenuator, SETTINGS['atten_param'])
        self._ui.rb_atten_on.setChecked(SETTINGS['atten_correction'] == 'on')
        self._ui.rb_atten_off.setChecked(SETTINGS['atten_correction'] == 'off')

        self._ui.cmb_intensity.addItems(SETTINGS['all_params'])
        self._ui.cmb_intensity.setEnabled(SETTINGS['inten_correction'] == 'on')
        if SETTINGS['inten_param'] not in SETTINGS['all_params']:
            self._ui.cmb_intensity.addItem(SETTINGS['inten_param'])
        refresh_combo_box(self._ui.cmb_intensity, SETTINGS['inten_param'])
        self._ui.rb_inten_on.setChecked(SETTINGS['inten_correction'] == 'on')
        self._ui.rb_inten_off.setChecked(SETTINGS['inten_correction'] == 'off')

        self._ui.cmb_z_axis.addItems(SETTINGS['all_params'])
        if SETTINGS['displayed_param'] not in SETTINGS['all_params']:
            self._ui.cmb_z_axis.addItem(SETTINGS['displayed_param'])
        refresh_combo_box(self._ui.cmb_z_axis, SETTINGS['displayed_param'])

        self._ui.bg_intensity.buttonClicked.connect(
            lambda button: self._ui.cmb_intensity.setEnabled(button == self._ui.rb_inten_on))
        self._ui.bg_attenuator.buttonClicked.connect(
            lambda button: self._ui.cmb_attenuator.setEnabled(button == self._ui.rb_atten_on))

    # ----------------------------------------------------------------------
    def _get_ui(self):

        return Ui_LambdaSetup()

    # ----------------------------------------------------------------------
    def get_name(self):
        return 'Lambda Scan Setup'

    # ----------------------------------------------------------------------
    def get_settings(self):

        return SETTINGS

    # ----------------------------------------------------------------------
    def accept(self):

        SETTINGS['atten_param'] = str(self._ui.cmb_attenuator.currentText())
        if self._ui.rb_atten_on.isChecked():
            SETTINGS['atten_correction'] = 'on'
        elif self._ui.rb_atten_off.isChecked():
            SETTINGS['atten_correction'] = 'off'

        SETTINGS['inten_param'] = str(self._ui.cmb_intensity.currentText())
        if self._ui.rb_inten_on.isChecked():
            SETTINGS['inten_correction'] = 'on'
        elif self._ui.rb_inten_off.isChecked():
            SETTINGS['inten_correction'] = 'off'

        SETTINGS['displayed_param'] = str(self._ui.cmb_z_axis.currentText())

        super(SardanaScanSetup, self).accept()