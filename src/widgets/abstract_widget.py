# Created by matveyev at 14.04.2021

from PyQt5 import QtWidgets

WIDGET_NAME = None


# ----------------------------------------------------------------------
class AbstractWidget(QtWidgets.QWidget):

    def __init__(self):
        super(AbstractWidget, self).__init__()

    # ----------------------------------------------------------------------
    def load_ui_settings(self, settings):
        try:
            self.restoreGeometry(settings.value("{}/geometry".format(WIDGET_NAME)))
        except Exception as err:
            self._parent.log.error("{} : cannot restore geometry: {}".format(WIDGET_NAME, err))

    # ----------------------------------------------------------------------
    def save_ui_settings(self, settings):
        settings.setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())
