# Created by matveyev at 15.02.2021

WIDGET_NAME = 'FrameView'

import pyqtgraph as pg
import numpy as np
import logging
from PyQt5 import QtWidgets, QtCore

from src.main_window import APP_NAME
from src.widgets.abstract_widget import AbstractWidget
from src.widgets.view_2d import View2d
from src.widgets.axis_selector import AxisSelector
from src.widgets.cut_selector import CutSelector
from src.gui.frame_view_ui import Ui_FrameView


logger = logging.getLogger(APP_NAME)

# ----------------------------------------------------------------------
class FrameView(AbstractWidget):
    """
    """
    section_updated = QtCore.pyqtSignal(list, str)

    # ----------------------------------------------------------------------
    def __init__(self, parent, data_pool):
        """
        """
        super(FrameView, self).__init__(parent)
        self._ui = Ui_FrameView()
        self._ui.setupUi(self)

        self._main_view = View2d(self, 'main', data_pool)
        self._second_view = View2d(self, 'second', data_pool)
        self._second_view.hide()

        self._ui.view_layout.addWidget(self._main_view, 0)
        self._ui.view_layout.addWidget(self._second_view, 0)

        self._status_bar = QtWidgets.QStatusBar(self)
        self._ui.l_general.addWidget(self._status_bar, 0)

        self._coordinate_label = QtWidgets.QLabel("")
        self._status_bar.addPermanentWidget(self._coordinate_label)

        self.current_frames = [0, 0]
        self.level_mode = 'lin'
        self.auto_levels = True
        self.max_frame = 0

        self._axis_selectors = []
        self._axis_grid = QtWidgets.QVBoxLayout(self._ui.axis_selectors)
        self._axis_grid.setSpacing(0)
        self._axis_grid.setContentsMargins(0, 0, 0, 0)
        self._cut_selectors = []
        self._cut_grid = QtWidgets.QVBoxLayout(self._ui.cut_selectors)
        self._cut_grid.setSpacing(0)
        self._cut_grid.setContentsMargins(0, 0, 0, 0)

        self.hist = pg.HistogramLUTWidget(self)
        self.hist.setBackground('w')
        self.hist.item.setImageItem(self._main_view.plot_2d)
        self._ui.l_pic_setup.addWidget(self.hist, 1)

        self.data_pool = data_pool

        self.hist.scene().sigMouseClicked.connect(self._hist_mouse_clicked)
        self.hist.item.sigLevelsChanged.connect(self.switch_off_auto_levels)
        self.hist.item.sigLookupTableChanged.connect(self._new_lookup_table)
        self._ui.chk_auto_levels.clicked.connect(lambda state: self._toggle_auto_levels(state))

        self._ui.bg_level.buttonClicked.connect(lambda button: self._change_level_mode(button))

    # ----------------------------------------------------------------------
    def _update_layout(self, container, widgets):

        layout = container.layout()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item:
                w = layout.itemAt(i).widget()
                if w:
                    layout.removeWidget(w)
                    w.setVisible(False)

        for widget in widgets:
            layout.addWidget(widget)

    # ----------------------------------------------------------------------
    def _refresh_selectors(self):

        axes = []
        need_update = False
        if self._main_view.current_file is not None:
            axes = self.data_pool.get_file_axes(self._main_view.current_file)
            if len(axes) != len(self._axis_selectors):
                need_update = True
        else:
            need_update = True

        if need_update:
            self._axis_selectors = []
            self._cut_selectors = []
            for ind, axis in enumerate(axes):
                if ind == 0:
                    name = 'Y'
                elif ind == 1:
                    name = 'X'
                else:
                    name = f'Selector {ind-1}'
                widget = AxisSelector(self, ind, name)
                widget.set_new_axes(axes, ind)
                widget.new_selection.connect(self._new_axes)
                self._axis_selectors.append(widget)

                widget = CutSelector(self, ind)
                widget.new_cut.connect(self.update_image)
                # First two selectors constrain image shape
                if ind < 2:
                    widget.set_range_mode()
                self._cut_selectors.append(widget)

            self._update_layout(self._ui.axis_selectors, self._axis_selectors)
            self._update_layout(self._ui.cut_selectors, self._cut_selectors)

    def setup_selection(self, mode='ASAPO'):
        """
        Set starting position of selection suitable for given mode.
        ASAPO mode assumes that image from single ASAPO-message is shown.
        If ASAPO-message contain 1D image a small range of ASAPO-messages is shown
        """
        logger.debug(f"Setup frame_view selectors with mode: {mode}")
        if mode == 'ASAPO':
            if len(self.data_pool.axes_limits) >= 3:
                new_ind = np.roll(np.arange(len(self._axis_selectors)), -1)
                for i, axis_selector in enumerate(self._axis_selectors):
                    axis_selector.set_new_axis(new_ind[i])

    # ----------------------------------------------------------------------
    def add_file(self, file_name, move_from='second'):
        logger.debug(f"Add file {file_name}, view: {move_from}")
        if move_from == 'second':
            self._main_view.add_file(file_name)
            self.data_pool.protect_file(file_name, False)
        else:
            self._second_view.add_file(file_name)
            self.data_pool.protect_file(file_name, True)
        self._refresh_selectors()
        self.setup_selection()
        self._setup_limits()
        self.update_image()

    # ----------------------------------------------------------------------
    def roi_changed(self, roi_ind):
        self._main_view.roi_changed(roi_ind)
        self._second_view.roi_changed(roi_ind)

    # ----------------------------------------------------------------------
    def add_roi(self, idx):
        self._main_view.add_roi(idx)
        self._second_view.add_roi(idx)

    # ----------------------------------------------------------------------
    def file_closed_by_pool(self, file_name):
        self._main_view.file_closed_by_pool(file_name)
        self._second_view.file_closed_by_pool(file_name)

    # ----------------------------------------------------------------------
    def new_coordinate(self, source, x_name, x_value, y_name, y_value, pos):

        self._coordinate_label.setText('{}: {:3f}, {}: {:.3f}'.format(x_name, x_value, y_name, y_value))

        if source == 'main':
            self._second_view.move_marker(pos)
        else:
            self._main_view.move_marker(pos)

    # ----------------------------------------------------------------------
    def new_view_box(self, source, view_box):
        # print('New view box from {}, box {}'.format(source, view_box))
        if source == 'main':
            self._second_view.new_view_box(view_box)
        else:
            self._main_view.new_view_box(view_box)

    # ----------------------------------------------------------------------
    def delete_roi(self, idx):
        self._main_view.delete_roi(idx)
        self._second_view.delete_roi(idx)

    # ----------------------------------------------------------------------
    def _new_axes(self, id, old_axis, new_axis):

        for ind, selector in enumerate(self._axis_selectors):
            if selector.get_current_value() == new_axis and ind != id:
                selector.set_new_axis(old_axis)

        self._setup_limits()
        #self._main_view.new_axes()
        #self._second_view.new_axes()
        #self.update_image()

    # ----------------------------------------------------------------------
    def _new_lookup_table(self):
        self._second_view.new_lookup_table()

    # ----------------------------------------------------------------------
    def switch_off_auto_levels(self):
        self.auto_levels = False
        self._ui.chk_auto_levels.setChecked(False)
        self._second_view.new_levels()

    # ----------------------------------------------------------------------
    def _toggle_auto_levels(self, state):
        self.auto_levels = state
        self.update_image()
        self._ui.chk_auto_levels.setChecked(state)

    # ----------------------------------------------------------------------
    def _change_level_mode(self, button):
        if button == self._ui.rb_lin_level:
            self.level_mode = 'lin'
        else:
            self.level_mode = 'log'

        self.update_image()

    # ----------------------------------------------------------------------
    def _hist_mouse_clicked(self, event):
        if event.double():
            self._toggle_auto_levels(True)

    # ----------------------------------------------------------------------
    def get_current_axes(self):
        return {'x': self._axis_selectors[0].get_current_value(),
                'y': self._axis_selectors[1].get_current_value()}

    # ----------------------------------------------------------------------
    def get_cut_axis(self, cut_selector_id):
        return self._axis_selectors[cut_selector_id].get_current_value()

    # ----------------------------------------------------------------------
    def update_image(self):

        section = []
        for selector in self._cut_selectors:
            section.append(selector.get_section())
        logger.debug(f"Update image with sel {section}")

        self.hist.item.sigLevelsChanged.disconnect()
        self._main_view.update_image(self.get_current_axes(), section)
        self._second_view.update_image(self.get_current_axes(), section)
        self.hist.item.sigLevelsChanged.connect(self.switch_off_auto_levels)
        self.section_updated.emit(section, self._main_view.current_file)

    # ----------------------------------------------------------------------
    def _setup_limits(self):
        """
        Set ranges for all selectors
        """
        if self._main_view.current_file is None:
            return

        for selector in self._cut_selectors:
            selector.blockSignals(True)
            selector.setup_limits()
            selector.blockSignals(False)

    # ----------------------------------------------------------------------
    def get_value_for_frame(self, axis, frame):
        return self.data_pool.get_value_for_frame(self._main_view.current_file, axis, frame)

    # ----------------------------------------------------------------------
    def get_max_frame_along_axis(self, axis):
        return self.data_pool.get_max_frame_along_axis(self._main_view.current_file, axis)

    # ----------------------------------------------------------------------
    def get_frame_for_value(self, axis, value):
        return self.data_pool.get_frame_for_value(self._main_view.current_file, axis, value)

    # ----------------------------------------------------------------------
    def get_current_selection(self):
        sect = []
        for selector in self._cut_selectors:
            sect.append(selector.get_section())

        return sect

    # ----------------------------------------------------------------------
    def current_file(self):
        return self._main_view.current_file

    # ----------------------------------------------------------------------
    def new_main_file(self):
        """
        Update widget in case if main file was changed
        """
        if self._main_view.current_file is not None and self._main_view.previous_file is not None:

            self._refresh_selectors()
            self.setup_selection()
            self._setup_limits()
        self.update_image()
