# Created by matveyev at 06.05.2021

from PyQt5 import QtCore, QtWidgets

from src.gui.batch_ui import Ui_batch


# ----------------------------------------------------------------------
class BatchProgress(QtWidgets.QDialog):

    stop_batch = QtCore.pyqtSignal()

    # ----------------------------------------------------------------------
    def __init__(self):
        super(BatchProgress, self).__init__()

        self._ui = Ui_batch()
        self._ui.setupUi(self)

    # ----------------------------------------------------------------------
    def add_values(self, text, progress):
        self._ui.tx_status.append(text)
        self._ui.pb_progress.setValue(progress*100)

    # ----------------------------------------------------------------------
    def reject(self):
        self.stop_batch.emit()
        self.close()