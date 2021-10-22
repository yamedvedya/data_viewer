# Created by matveyev at 15.02.2021

WIDGET_NAME = 'FrameView'

import logging
from PyQt5 import QtWidgets, QtCore

from src.main_window import APP_NAME
from src.widgets.abstract_widget import AbstractWidget
from src.widgets.view_2d import View2d
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
        self._shape_label = QtWidgets.QLabel("")
        self._status_bar.addPermanentWidget(self._coordinate_label)
        self._status_bar.addPermanentWidget(self._shape_label)

        self.current_frames = [0, 0]
        self.level_mode = 'lin'
        self.auto_levels = True
        self.max_frame = 0

        self._cut_selectors = []
        self._cut_grid = QtWidgets.QVBoxLayout(self._ui.cut_selectors)
        self._cut_grid.setSpacing(0)
        self._cut_grid.setContentsMargins(0, 0, 0, 0)

        self.data_pool = data_pool

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
            if len(axes) != len(self._cut_selectors):
                need_update = True
        else:
            need_update = True

        if need_update:
            self._cut_selectors = []
            for ind, axis in enumerate(axes):
                widget = CutSelector(ind, axis, ['X', 'Y'])
                widget.new_cut.connect(self.update_image)
                widget.new_axis.connect(self._new_axes)
                self._cut_selectors.append(widget)
            self._update_layout(self._ui.cut_selectors, self._cut_selectors)

    # ----------------------------------------------------------------------
    def set_settings(self, settings):
        try:
            self._main_view.set_settings(settings)
            self._second_view.set_settings(settings)

        except Exception as err:
            self._parent.log.error("{} : cannot apply settings: {}".format(WIDGET_NAME, err), exc_info=True)

    # ----------------------------------------------------------------------
    def add_file(self, file_name, move_from='second'):
        logger.debug(f"Add file {file_name}, view: {move_from}")
        if move_from == 'second':
            self._main_view.add_file(file_name)
            self.data_pool.protect_file(file_name, False)
        else:
            self._second_view.add_file(file_name)
            self.data_pool.protect_file(file_name, True)

        self.new_main_file()

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

        self._coordinate_label.setText(f'{x_name}: {x_value}, {y_name}: {y_value}')

        if source == 'main':
            self._second_view.move_marker(pos)
        else:
            self._main_view.move_marker(pos)

    # ----------------------------------------------------------------------
    def new_view_box(self, source, view_box):
        if source == 'main':
            self._second_view.new_view_box(view_box)
        else:
            self._main_view.new_view_box(view_box)

    # ----------------------------------------------------------------------
    def delete_roi(self, idx):
        self._main_view.delete_roi(idx)
        self._second_view.delete_roi(idx)

    # ----------------------------------------------------------------------
    def _new_axes(self, new_axis, old_axis):
        """
        Process selection of new axis in cut_selector
        """
        axes_labels = {}
        for selector in self._cut_selectors:
            if selector.current_axis == new_axis:
                selector.set_axis(old_axis)
            elif selector.current_axis == old_axis:
                selector.set_axis(new_axis)
            axes_labels[selector.current_axis] = selector.axis_label

        self._update_axes(axes_labels)
        self.update_image()

    # ----------------------------------------------------------------------
    def _update_axes(self, axes_labels):
        self._main_view.new_axes(axes_labels)
        self._second_view.new_axes(axes_labels)

    # ----------------------------------------------------------------------
    def _new_lookup_table(self):
        self._second_view.new_lookup_table()

    # ----------------------------------------------------------------------
    def switch_off_auto_levels(self):
        self.auto_levels = False
        #self._ui.chk_auto_levels.setChecked(False)
        self._second_view.new_levels()

    # ----------------------------------------------------------------------
    def _toggle_auto_levels(self, state):
        self.auto_levels = state
        self.update_image()
        #self._ui.chk_auto_levels.setChecked(state)

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
        selection = self.get_current_selection()
        selection = sorted(selection, key=lambda d: d['axis'])
        return {'x': selection[0]['id'],
                'y': selection[1]['id']}

    # ----------------------------------------------------------------------
    def update_image(self):

        selection = self.get_current_selection()
        logger.debug(f"Saving selection {selection} for file {self._main_view.current_file}")
        self.data_pool.save_section(self._main_view.current_file, selection)

        section = []
        for i, sect in enumerate(sorted(selection, key=lambda d: d['axis'])):
            section.append((sect['id'], sect['min'], sect['max']))
        logger.debug(f"Update image with sel {section}")

        self._main_view.update_image(self.get_current_axes(), section)
        self._second_view.update_image(self.get_current_axes(), section)
        self.section_updated.emit(section, self._main_view.current_file)

    # ----------------------------------------------------------------------
    def _setup_limits(self):
        """
        Set ranges for all selectors
        """
        if self._main_view.current_file is None:
            return

        limits = self.data_pool.get_file_axis_limits(self._main_view.current_file)
        for selector in self._cut_selectors:
            selector.setup_limits(limits[selector.get_id()][1])

        shape = [lim[1] + 1 for lim in limits.values()]
        self._shape_label.setText(f"Data shape: {shape}")

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

    def update_file(self, file_key):
        """
        Update widget parameters to reflect changes in the data shape _refresh_selectorsof given stream.
        """
        if self._main_view.current_file == file_key and file_key is not None:
            self._setup_limits()

            sections = self.data_pool.get_section(self._main_view.current_file)
            logger.debug(f"Setup frame_view selectors with section: {sections}")
            for section, cut_selector in zip(sections, self._cut_selectors):
                cut_selector.set_section(section)

            axes_labels = [s['axis_label'] for s in sorted(sections, key=lambda d: d['axis'])]
            self._update_axes(axes_labels)
            self.update_image()

    # ----------------------------------------------------------------------
    def new_main_file(self):
        """
        Update widget in case if main file was changed
        """
        self._refresh_selectors()
        self.update_file(self._main_view.current_file)
