# Created by matveyev at 22.02.2021

WIDGET_NAME = 'ROIsView'

import pickle

try:
    import PyTango
    has_pytango = True
except:
    has_pytango = False

from PyQt5 import QtWidgets, QtCore, QtGui

from data_viewer.widgets.abstract_widget import AbstractWidget
from data_viewer.gui.rois_view_ui import Ui_RoisView
from data_viewer.widgets.section_view import SectionView


# ----------------------------------------------------------------------
class RoisView(AbstractWidget):
    """
    """
    PEN_COUNTER = 0

    update_roi = QtCore.pyqtSignal(int)

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
        self.btn_add_active_tab.clicked.connect(self.add_roi)
        self._ui.tab_main.setCornerWidget(self.btn_add_active_tab, QtCore.Qt.TopLeftCorner)
        self._ui.tab_main.cornerWidget(QtCore.Qt.TopLeftCorner).setMinimumSize(self.btn_add_active_tab.sizeHint())

        self._ui.tab_main.tabCloseRequested.connect(self._close_tab)

        self._roi_widgets = {}
        self._opened_files = {}
        self._last_color = -1
        self.settings = {}

    # ----------------------------------------------------------------------
    def get_current_file(self):
        return self._parent.get_current_file()

    # ----------------------------------------------------------------------
    def set_settings(self, settings):

        self.settings.update(settings)

    # ----------------------------------------------------------------------
    def fetch_rois(self):
        if 'macro_server' in self.settings and has_pytango:
            data = pickle.loads(PyTango.DeviceProxy(self.settings['macro_server']).environment[1])['new']['DetectorROIs']
            for roi in data.values():
                last_id = self.add_roi()
                self._data_pool.set_section_axis(last_id, 0)
                self._data_pool.roi_parameter_changed(last_id, 1, 'pos',
                                                      self._data_pool.get_value_for_frame(self.get_current_file(),
                                                                                          1, roi[0][1]))
                self._data_pool.roi_parameter_changed(last_id, 1, 'width',
                                                      self._data_pool.get_value_for_frame(self.get_current_file(),
                                                                                          1, roi[0][3] - roi[0][1] + 1))
                self._data_pool.roi_parameter_changed(last_id, 2, 'pos',
                                                      self._data_pool.get_value_for_frame(self.get_current_file(),
                                                                                          2, roi[0][0]))
                self._data_pool.roi_parameter_changed(last_id, 2, 'width',
                                                      self._data_pool.get_value_for_frame(self.get_current_file(),
                                                                                          2,  roi[0][2] - roi[0][0] + 1))
                self._roi_widgets[last_id].roi_changed()
                self.update_roi.emit(last_id)

    # ----------------------------------------------------------------------
    def add_roi(self):
        idx, name, roi_dims = self._data_pool.add_new_roi()
        if idx is None:
            return

        self._parent.add_roi(idx)
        widget = SectionView(self, self._data_pool, idx, roi_dims)
        widget.update_roi.connect(lambda roi_id: self.update_roi.emit(roi_id))
        self._roi_widgets[idx] = widget
        self._ui.tab_main.insertTab(self._ui.tab_main.count(), self._roi_widgets[idx], 'ROI_{}'.format(name))
        self._ui.tab_main.setCurrentWidget(self._roi_widgets[idx])

        for file_name, color in self._opened_files.items():
            self._roi_widgets[idx].add_file(file_name, color)

        self.update_roi.emit(idx)

        return idx

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
    def current_folder(self):
        return self._parent.get_current_folder()

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
            widget.main_file_changed()
            widget.delete_file(file_name)

    # ----------------------------------------------------------------------
    def update_plots(self):
        for widget in self._roi_widgets.values():
            widget.update_limits()
            widget.update_plots()

    # ----------------------------------------------------------------------
    def units_changed(self):

        for widget in self._roi_widgets.values():
            widget.units_changed()

    # ----------------------------------------------------------------------
    def roi_changed(self, roi_id):

        self._roi_widgets[roi_id].roi_changed()

    # ----------------------------------------------------------------------
    def main_file_changed(self):
        for widget in self._roi_widgets.values():
            widget.main_file_changed()
