# Created by matveyev at 19.02.2021

WIDGET_NAME = 'DataBrowser'
import pyqtgraph.opengl as gl

from PyQt5 import QtWidgets, QtCore, QtGui
from src.gui.cube_view_ui import Ui_CubeView

# ----------------------------------------------------------------------
class CubeView(QtWidgets.QWidget):
    """
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent, data_pool):
        """
        """
        super(CubeView, self).__init__()
        self._ui = Ui_CubeView()
        self._ui.setupUi(self)

        self._parent = parent
        self._data_pool = data_pool

        self.view_widget = gl.GLViewWidget()
        self.view_widget.orbit(256, 256)
        self.view_widget.setCameraPosition(0, 0, 0)
        self.view_widget.opts['distance'] = 200
        self._ui.horizontalLayout.addWidget(self.view_widget)

    # ----------------------------------------------------------------------
    def load_ui_settings(self, settings):
        try:
            self.restoreGeometry(settings.value("{}/geometry".format(WIDGET_NAME)))
        except Exception as err:
            self._parent.log.error("{} : cannot restore geometry: {}".format(WIDGET_NAME, err))

    # ----------------------------------------------------------------------
    def save_ui_settings(self, settings):
        settings.setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())