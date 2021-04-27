# Created by matveyev at 19.02.2021

WIDGET_NAME = 'ImageSetup'

import sys

from PyQt5 import QtWidgets, QtCore

from src.data_sources.lambda_scan import LambdaScanSetup
if 'asapo_consumer' in sys.modules:
    from src.data_sources.asapo_scan import ASAPOScanSetup
    has_asapo = True
else:
    has_asapo = False

from src.gui.image_setup_ui import Ui_ImageSetup
from src.main_window import APP_NAME

class ImageSetup(QtWidgets.QDialog):

    # ----------------------------------------------------------------------
    def __init__(self, parent, data_pool):
        """
        """
        super(ImageSetup, self).__init__()
        self._ui = Ui_ImageSetup()
        self._ui.setupUi(self)

        self._parent = parent
        self._data_pool = data_pool

        self._widgets = [LambdaScanSetup(parent, data_pool)]
        if has_asapo:
            self._widgets.append(ASAPOScanSetup(parent, data_pool))

        for widget in self._widgets:
            self._ui.tb_settings.addTab(widget, widget.get_name())

    # ----------------------------------------------------------------------
    def accept(self):
        for widget in self._widgets:
            widget.accept()

        self._data_pool.apply_settings()

        QtCore.QSettings(APP_NAME).setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())

        super(ImageSetup, self).accept()

    # ----------------------------------------------------------------------
    def reject(self):
        for widget in self._widgets:
            widget.reject()

        self._data_pool.apply_settings()

        QtCore.QSettings(APP_NAME).setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())

        super(ImageSetup, self).reject()


