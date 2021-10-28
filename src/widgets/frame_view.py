# Created by matveyev at 15.02.2021

WIDGET_NAME = 'FrameView'

import logging
from PyQt5 import QtWidgets, QtCore

from src.main_window import APP_NAME
from src.widgets.abstract_widget import AbstractWidget
from src.widgets.view_2d import View2d
from src.gui.frame_view_ui import Ui_FrameView


logger = logging.getLogger(APP_NAME)


# ----------------------------------------------------------------------
class FrameView(AbstractWidget):
    """
    """
    section_updated = QtCore.pyqtSignal()

    # ----------------------------------------------------------------------
    def __init__(self, parent, data_pool):
        """
        """
        super(FrameView, self).__init__(parent)
        self._ui = Ui_FrameView()
        self._ui.setupUi(self)

        self._ui.cut_selectors.new_cut.connect(self.update_image)
        self._ui.cut_selectors.new_axis.connect(self._update_axes)

        self._main_view = View2d(self, 'main', data_pool)
        self._second_view = View2d(self, 'second', data_pool)
        self._second_view.hide()

        self._ui.view_layout.addWidget(self._main_view, 0)
        self._ui.view_layout.addWidget(self._second_view, 0)

        self._status_bar = QtWidgets.QStatusBar(self)
        self._ui.v_layout.addWidget(self._status_bar, 0)

        self._shape_label = QtWidgets.QLabel("")
        self._status_bar.addPermanentWidget(self._shape_label)

        self.current_frames = [0, 0]
        self.level_mode = 'lin'
        self.auto_levels = True
        self.max_frame = 0

        self._cut_grid = QtWidgets.QVBoxLayout(self._ui.cut_selectors)
        self._cut_grid.setSpacing(0)
        self._cut_grid.setContentsMargins(0, 0, 0, 0)

        self.data_pool = data_pool

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
    def new_coordinate(self, source, pos):

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
    def get_current_axes(self):
        selection = self._ui.cut_selectors.get_current_selection()

        return {'x': [ind for ind, sect in enumerate(selection) if sect['axis'] == 'X'][0],
                'y': [ind for ind, sect in enumerate(selection) if sect['axis'] == 'Y'][0]}

    # ----------------------------------------------------------------------
    def update_image(self):

        selection = self._ui.cut_selectors.get_current_selection()
        logger.debug(f"Saving selection {selection} for file {self._main_view.current_file}")
        self.data_pool.save_section(self._main_view.current_file, selection)

        logger.debug(f"Update image with sel {selection}")

        self._main_view.update_image()
        self._second_view.update_image()
        self.section_updated.emit()

    # ----------------------------------------------------------------------
    def _setup_limits(self):
        """
        Set ranges for all selectors
        """
        if self._main_view.current_file is None:
            return

        limits = self.data_pool.get_file_axis_limits(self._main_view.current_file)
        self._ui.cut_selectors.set_limits(limits)

        self._shape_label.setText(f"Data shape: {limits}")

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
    def current_file(self):
        return self._main_view.current_file

    # ----------------------------------------------------------------------
    def update_file(self, file_key):
        """
        Update widget parameters to reflect changes in the data shape _refresh_selectors of given stream.
        """
        if self._main_view.current_file == file_key and file_key is not None:
            self._setup_limits()

            sections = self.data_pool.get_section(self._main_view.current_file)
            axes_names = self.data_pool.get_file_axes(self._main_view.current_file)
            logger.debug(f"Setup frame_view selectors with section: {sections}")
            self._ui.cut_selectors.set_section(sections)

            axes_labels = [name for s, name in zip(sections, axes_names) if s['axis'] == 'X']
            axes_labels += [name for s, name in zip(sections, axes_names) if s['axis'] == 'Y']
            self._update_axes(axes_labels)
            self.update_image()

    # ----------------------------------------------------------------------
    def new_main_file(self):
        """
        Update widget in case if main file was changed
        """
        self._ui.cut_selectors.refresh_selectors(self.data_pool.get_file_axes(self._main_view.current_file))
        self.update_file(self._main_view.current_file)
