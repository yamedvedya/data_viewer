# Created by matveyev at 22.02.2021

WIDGET_NAME = 'ROIsView'

from PyQt5 import QtWidgets, QtCore, QtGui

from src.widgets.abstract_widget import AbstractWidget
from src.gui.rois_view_ui import Ui_RoisView
from src.widgets.section_view import SectionView


# ----------------------------------------------------------------------
class RoisView(AbstractWidget):
    """
    """
    PEN_COUNTER = 0

    # ----------------------------------------------------------------------
    def __init__(self, parent, data_pool):
        """
        """
        super(RoisView, self).__init__(parent)
        self._ui = Ui_RoisView()
        self._ui.setupUi(self)

        self._data_pool = data_pool
        self._parent = parent

        self.btn_add_active_tab = QtWidgets.QToolButton(self)
        self.btn_add_active_tab.setIcon(QtGui.QIcon(":/icon/plus_small.png"))
        self.btn_add_active_tab.clicked.connect(self._add_roi)
        self._ui.tab_main.setCornerWidget(self.btn_add_active_tab, QtCore.Qt.TopLeftCorner)

        self._ui.tab_main.tabCloseRequested.connect(self._close_tab)

        self._roi_widgets = {}
        self._opened_files = {}
        self._last_color = -1
        self._add_roi()

        self.settings = {}

    # ----------------------------------------------------------------------
    def get_current_file(self):
        return self._parent.get_current_file()

    # ----------------------------------------------------------------------
    def set_settings(self, settings):

        self.settings.update(settings)

    # ----------------------------------------------------------------------
    def _add_roi(self):
        idx, name = self._data_pool.add_new_roi()
        self._parent.add_roi(idx)
        self._roi_widgets[idx] = SectionView(self, self._parent.file_browser, self._data_pool, idx)
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
    def update_plots(self):
        for widget in self._roi_widgets.values():
            widget.update_limits()

        for widget in self._roi_widgets.values():
            widget.update_plots()

    # ----------------------------------------------------------------------
    def roi_changed(self, roi_id):
        self._roi_widgets[roi_id].roi_changed()
