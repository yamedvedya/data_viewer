# Created by matveyev at 22.02.2021

WIDGET_NAME = 'ROIsView'

from PyQt5 import QtWidgets, QtCore, QtGui
from src.gui.rois_view_ui import Ui_RoisView

from src.widgets.section_view import SectionView

# ----------------------------------------------------------------------
class RoisView(QtWidgets.QWidget):
    """
    """
    PEN_COUNTER = 0

    # ----------------------------------------------------------------------
    def __init__(self, parent, data_pool):
        """
        """
        super(RoisView, self).__init__()
        self._ui = Ui_RoisView()
        self._ui.setupUi(self)

        self._parent = parent
        self._data_pool = data_pool

        self.btn_add_active_tab = QtWidgets.QToolButton(self)
        self.btn_add_active_tab.setIcon(QtGui.QIcon(":/icon/plus_small.png"))
        self.btn_add_active_tab.clicked.connect(self._add_roi)
        self._ui.tab_main.setCornerWidget(self.btn_add_active_tab, QtCore.Qt.TopLeftCorner)

        self._ui.tab_main.tabCloseRequested.connect(self._close_tab)

        self._roi_widgets = {}
        self._opened_files = {}
        self._last_color = -1
        self._add_roi()

    # ----------------------------------------------------------------------
    def _add_roi(self):
        idx, name = self._data_pool.add_new_roi()
        self._parent.add_roi(idx)
        self._roi_widgets[idx] = SectionView(self, self._data_pool, idx)
        self._ui.tab_main.insertTab(self._ui.tab_main.count(), self._roi_widgets[idx], 'ROI_{}'.format(name))
        self._ui.tab_main.setCurrentWidget(self._roi_widgets[idx])

        for file_name, color in self._opened_files.items():
            self._roi_widgets[idx].add_file(file_name, color)

    # ----------------------------------------------------------------------
    def _close_tab(self, idx):
        widget = self._ui.tab_main.widget(idx)

        roi_id = widget.my_id
        self._data_pool.delete_roi(roi_id)
        self._parent.delete_roi(roi_id)

        self._ui.tab_main.removeTab(idx)
        del self._roi_widgets[roi_id]

        if self._ui.tab_main.count() < 1:
            self._add_roi()

        for idx in range(self._ui.tab_main.count()):
            self._ui.tab_main.setTabText(idx, 'ROI_{}'.format(self._ui.tab_main.widget(idx).refresh_name()))

    # ----------------------------------------------------------------------
    def add_file(self, file_name):
        self._opened_files[file_name] = self._last_color + 1
        self._last_color += 1
        for widget in self._roi_widgets.values():
            widget.add_file(file_name, self._last_color)

    # ----------------------------------------------------------------------
    def delete_file(self, file_name):
        del self._opened_files[file_name]

        for widget in self._roi_widgets.values():
            widget.delete_file(file_name)

    # ----------------------------------------------------------------------
    def update_limits(self):
        for widget in self._roi_widgets.values():
            widget.update_limits()

    # ----------------------------------------------------------------------
    def update_plots(self):
        for widget in self._roi_widgets.values():
            widget.update_plots()

    # ----------------------------------------------------------------------
    def new_roi_range(self, roi_id):
        self._roi_widgets[roi_id].new_roi_range()

    # ----------------------------------------------------------------------
    def load_ui_settings(self, settings):
        try:
            self.restoreGeometry(settings.value("{}/geometry".format(WIDGET_NAME)))
        except Exception as err:
            self._parent.log.error("{} : cannot restore geometry: {}".format(WIDGET_NAME, err))
    # ----------------------------------------------------------------------
    def save_ui_settings(self, settings):
        settings.setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())