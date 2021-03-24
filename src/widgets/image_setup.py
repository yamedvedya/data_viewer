# Created by matveyev at 19.02.2021

WIDGET_NAME = 'MaskSetup'

import pyqtgraph as pg
import numpy as np

from PyQt5 import QtWidgets, QtCore
from pyqtgraph.graphicsItems.GradientEditorItem import Gradients

from src.gui.image_setup_ui import Ui_ImageSetup

from src.utils.utils import read_mask_file, refresh_combo_box
from src.main_window import APP_NAME


# ----------------------------------------------------------------------
class ImageSetup(QtWidgets.QDialog):
    """
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent, data_pool):
        """
        """
        super(ImageSetup, self).__init__()
        self._ui = Ui_ImageSetup()
        self._ui.setupUi(self)

        self._parent = parent
        self._data_pool = data_pool

        self._main_plot = pg.PlotItem()
        self._main_plot.showAxis('left', False)
        self._main_plot.showAxis('bottom', False)
        self._main_plot.setMenuEnabled(False)

        self._ui.gv_main.setStyleSheet("")
        self._ui.gv_main.setBackground('w')
        self._ui.gv_main.setObjectName("gvMain")

        self._ui.gv_main.setCentralItem(self._main_plot)
        self._ui.gv_main.setRenderHints(self._ui.gv_main.renderHints())

        self._main_plot.getViewBox().setAspectLocked()

        self._current_file = self._parent.files_inspector.current_file #TODO !!!!!!!!!!!!!!!!!!!!
        self._mask_mode = self._data_pool.get_mask_mode(self._current_file)
        self._mask_info = {}

        if self._mask_mode == 'no':
            self._ui.rb_no_mask.setChecked(True)
            self._mask = np.array([[], []])
        elif self._mask_mode == 'default':
            self._ui.rb_default.setChecked(True)
            self._mask = self._data_pool.get_default_mask_for_file(self._current_file)
        elif self._mask_mode == 'attached':
            self._ui.rb_attached.setChecked(True)
            self._mask = self._data_pool.get_attached_mask_for_file(self._current_file)
        else:
            self._ui.rb_file.setChecked(True)
            self._ui.but_load_mask.setEnabled(True)
            self._mask, self._mask_info = self._data_pool.get_loaded_mask_for_file(self._current_file)
            if 'file' in self._mask_info:
                self._ui.lb_mask_file.setText(self._mask_info['file'])

        self._plot_2d = pg.ImageItem()
        self._plot_2d.setImage(np.copy(self._mask), autoLevels=True)
        self._plot_2d.setLookupTable(pg.ColorMap(*zip(*Gradients['grey']["ticks"])).getLookupTable())
        self._main_plot.addItem(self._plot_2d)

        self._ui.cmb_intensity.addItems(self._data_pool.get_scan_parameters(self._current_file))
        self._ui.cmb_attenuator.addItems(self._data_pool.get_scan_parameters(self._current_file))

        settings = self._data_pool.get_atten_settings(self._current_file)
        self._ui.lb_defalut_atten.setText('{}: {}'.format(settings['default'], settings['default_param']))
        refresh_combo_box(self._ui.cmb_attenuator, settings['param'])
        self._ui.rb_atten_deafult.setChecked(settings['state'] == 'default')
        self._ui.rb_atten_on.setChecked(settings['state'] == 'on')
        self._ui.rb_atten_off.setChecked(settings['state'] == 'off')

        settings = self._data_pool.get_inten_settings(self._current_file)
        self._ui.lb_defalut_intensity.setText('{}: {}'.format(settings['default'], settings['default_param']))
        refresh_combo_box(self._ui.cmb_intensity, settings['param'])
        self._ui.rb_inten_deafult.setChecked(settings['state'] == 'default')
        self._ui.rb_inten_on.setChecked(settings['state'] == 'on')
        self._ui.rb_inten_off.setChecked(settings['state'] == 'off')

        self._ui.bg_intensity.buttonClicked.connect(
            lambda button: self._ui.cmb_intensity.setEnabled(button == self._ui.rb_inten_param_special))
        self._ui.bg_attenuator.buttonClicked.connect(
            lambda button: self._ui.cmb_attenuator.setEnabled(button == self._ui.rb_atten_param_special))

        self._ui.bg_mask_option.buttonClicked.connect(self.change_mode)
        self._ui.but_load_mask.clicked.connect(self.load_mask_from_file)

        self._main_plot.scene().sigMouseClicked.connect(self._mouse_clicked)

        try:
            self.restoreGeometry(QtCore.QSettings(APP_NAME).value("{}/geometry".format(WIDGET_NAME)))
        except Exception as err:
            self._parent.log.error("{} : cannot restore geometry: {}".format(WIDGET_NAME, err))

    # ----------------------------------------------------------------------
    def change_mode(self, button):
        self._ui.but_load_mask.setEnabled(False)
        if button == self._ui.rb_no_mask:
            self._mask_mode = 'no'
            self._plot_2d.clear()
            return
        elif button == self._ui.rb_attached:
            self._mask_mode = 'attached'
            self._mask = self._data_pool.get_attached_mask_for_file(self._current_file)
        elif button == self._ui.rb_file:
            self._mask_mode = 'file'
            self._mask, self._mask_info = self._data_pool.get_loaded_mask_for_file(self._current_file)
            if self._mask.shape[1] == 0:
                self.load_mask_from_file()
            self._ui.but_load_mask.setEnabled(True)
            if 'file' in self._mask_info:
                self._ui.lb_mask_file.setText(self._mask_info['file'])
        else:
            self._mask_mode = 'default'
            self._mask = self._data_pool.get_default_mask_for_file(self._current_file)

        try:
            self._plot_2d.setImage(np.copy(self._mask), autoLevels=True)
        except Exception as err:
            self._parent.log.error("{} : cannot display mask geometry: {}".format(WIDGET_NAME, err))
            self._plot_2d.clear()

    # ----------------------------------------------------------------------
    def load_mask_from_file(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file with mask',
                                                             self._data_pool.get_dir(self._parent.files_inspector.current_file)) # TODO !!!!!!!!!!!!!!

        if file_name:
            mask, mask_info = read_mask_file(file_name)
            if mask is not None:
                self._mask = mask
                self._mask_info = mask_info
                self._plot_2d.setImage(np.copy(mask), autoLevels=True)
                self._ui.lb_mask_file.setText(mask_info['file'])

    # ----------------------------------------------------------------------
    def accept(self):
        if self._mask_mode == 'file':
            self._data_pool.set_mask(self._current_file, self._mask_mode,
                                     self._ui.chk_force_mask_opened.isChecked(),
                                     self._ui.chk_use_for_new.isChecked(),
                                     self._mask, self._mask_info)
        else:
            self._data_pool.set_mask(self._current_file, self._mask_mode,
                                     self._ui.chk_force_mask_opened.isChecked(),
                                     self._ui.chk_use_for_new.isChecked())

        settings = {'param': str(self._ui.cmb_attenuator.currentText())}
        if self._ui.rb_atten_deafult.isChecked():
            settings['state'] = 'default'
        elif self._ui.rb_atten_on.isChecked():
            settings['state'] = 'on'
        elif self._ui.rb_atten_off.isChecked():
            settings['state'] = 'off'

        self._data_pool.set_atten_settings(self._current_file, settings, self._ui.chk_force_mask_opened.isChecked(),
                                           self._ui.chk_use_for_new.isChecked())

        settings = {'param': str(self._ui.cmb_intensity.currentText())}
        if self._ui.rb_inten_deafult.isChecked():
            settings['state'] = 'default'
        elif self._ui.rb_inten_on.isChecked():
            settings['state'] = 'on'
        elif self._ui.rb_inten_off.isChecked():
            settings['state'] = 'off'

        self._data_pool.set_inten_settings(self._current_file, settings, self._ui.chk_force_mask_opened.isChecked(),
                                           self._ui.chk_use_for_new.isChecked())

        self._data_pool.apply_settings(self._current_file, self._ui.chk_force_mask_opened.isChecked())

        QtCore.QSettings(APP_NAME).setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())
        super(ImageSetup, self).accept()

    # ----------------------------------------------------------------------
    def reject(self):
        QtCore.QSettings(APP_NAME).setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())
        super(ImageSetup, self).reject()

    # ----------------------------------------------------------------------
    def _mouse_clicked(self, event):
        """
        """
        if event.double():
            try:
                self._main_plot.autoRange()
            except:
                pass
