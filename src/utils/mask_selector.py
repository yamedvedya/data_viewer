# Created by matveyev at 19.02.2021

WIDGET_NAME = 'MaskSetup'

import pyqtgraph as pg
import os
import numpy as np

from PyQt5 import QtWidgets, QtCore
from pyqtgraph.graphicsItems.GradientEditorItem import Gradients

from src.gui.mask_selector_ui import Ui_MaskSelector

from src.utils.utils import read_mask_file
from src.main_window import APP_NAME


# ----------------------------------------------------------------------
class MaskSelector(QtWidgets.QDialog):
    """
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent, data_pool):
        """
        """
        super(MaskSelector, self).__init__()
        self._ui = Ui_MaskSelector()
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

        self._current_file = self._parent.files_inspector.current_file
        self._mask_info = self._data_pool.get_mask_info(self._current_file)

        if self._mask_info['mode'] == 'default':
            self._ui.rb_default.setChecked(True)
            mask = self._data_pool.get_default_mask_for_file(self._current_file)
        elif self._mask_info['mode'] == 'no':
            self._ui.rb_no_mask.setChecked(True)
            mask = []
        elif self._mask_info['mode'] == 'attached':
            self._ui.rb_attached.setChecked(True)
            mask = self._data_pool.get_attached_mask_for_file(self._current_file)
        else:
            self._ui.rb_file.setChecked(True)
            self._ui.lb_mask_file.setText(self._mask_info['file'])
            mask = self._mask_info['loaded_mask']

        self._plot_2d = pg.ImageItem()
        self._plot_2d.setImage(image=mask)
        self._plot_2d.setLookupTable(pg.ColorMap(*zip(*Gradients['grey']["ticks"])).getLookupTable())
        self._main_plot.addItem(self._plot_2d)

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
            self._mask_info['mode'] = 'no'
            self._plot_2d.clear()
            return
        elif button == self._ui.rb_attached:
            self._mask_info['mode'] = 'attached'
            mask = self._data_pool.get_attached_mask_for_file(self._current_file)
        elif button == self._ui.rb_file:
            self._mask_info['mode'] = 'loaded'
            mask = self._mask_info['loaded_mask']
            self._ui.but_load_mask.setEnabled(True)
        else:
            self._mask_info['mode'] = 'default'
            mask = self._data_pool.get_default_mask_for_file(self._current_file)

        try:
            self._plot_2d.setImage(mask, autoLevels=True)
        except Exception as err:
            self._parent.log.error("{} : cannot display mask geometry: {}".format(WIDGET_NAME, err))
            self._plot_2d.clear()

    # ----------------------------------------------------------------------
    def load_mask_from_file(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file with mask',
                                                             self._data_pool.get_dir(self._parent.files_inspector.current_file))

        if file_name:
            mask_info = read_mask_file(file_name)
            if 'loaded_mask' in mask_info:
                self._plot_2d.setImage(mask_info['loaded_mask'], autoLevels=True)
                self._ui.lb_mask_file.setText(mask_info['file'])
                self._mask_info = mask_info

    # ----------------------------------------------------------------------
    def accept(self):
        self._data_pool.set_mask_mode(self._current_file, self._mask_info,
                                      self._ui.chk_force_mask_opened.isChecked(), self._ui.chk_use_for_new.isChecked())
        QtCore.QSettings(APP_NAME).setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())
        super(MaskSelector, self).accept()

    # ----------------------------------------------------------------------
    def reject(self):
        QtCore.QSettings(APP_NAME).setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())
        super(MaskSelector, self).reject()

    # ----------------------------------------------------------------------
    def _mouse_clicked(self, event):
        """
        """
        if event.double():
            try:
                self._main_plot.autoRange()
            except:
                pass
