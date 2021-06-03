# Created by matveyev at 15.02.2021

WIDGET_NAME = 'FrameView'

import pyqtgraph as pg

from PyQt5 import QtWidgets, QtCore

from src.widgets.abstract_widget import AbstractWidget
from src.widgets.view_2d import View2d
from src.utils.range_slider import RangeSlider
from src.gui.frame_view_ui import Ui_FrameView

# ----------------------------------------------------------------------
class FrameView(AbstractWidget):
    """
    """

    section_axes_map = {'Y vs. X': {'x': 0, 'y': 1, 'z': 2},
                        'X vs. Y': {'x': 1, 'y': 0, 'z': 2},
                        'Z vs. X': {'x': 0, 'y': 2, 'z': 1},
                        'X vs. Z': {'x': 2, 'y': 0, 'z': 1},
                        'Z vs. Y': {'x': 1, 'y': 2, 'z': 0},
                        'Y vs. Z': {'x': 2, 'y': 1, 'z': 0}}

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
        self._ui.gv_layout.addWidget(self._status_bar, 0)

        self._coordinate_label = QtWidgets.QLabel("")
        self._status_bar.addPermanentWidget(self._coordinate_label)

        self._opened_files = []

        self.current_frames = [0, 0]
        self.level_mode = 'lin'
        self.auto_levels = True
        self.max_frame = 0

        self.hist = pg.HistogramLUTWidget(self)
        self.hist.setBackground('w')
        self.hist.item.setImageItem(self._main_view.plot_2d)
        self._ui.g_layout.addWidget(self.hist, 5, 0, 1, 2)

        self.data_pool = data_pool

        self._ui.cb_section.addItems(list(self.section_axes_map.keys()))
        self._ui.cb_section.currentTextChanged.connect(self._new_axes)

        self.current_axes = self.section_axes_map[str(self._ui.cb_section.currentText())]

        self.sld = RangeSlider(QtCore.Qt.Horizontal, self)
        self._ui.h_layout.insertWidget(1, self.sld, 0)
        self.sld.sliderMoved.connect(self._display_new_frame)
        self.sld.setVisible(False)
        self._ui.sl_frame.valueChanged.connect(lambda value: self._display_new_frame(value, value))

        self._ui.chk_integration_mode.clicked.connect(self._switch_integration_mode)

        self._ui.but_first.clicked.connect(lambda: self._switch_frame('first'))
        self._ui.but_previous.clicked.connect(lambda: self._switch_frame('previous'))
        self._ui.but_next.clicked.connect(lambda: self._switch_frame('next'))
        self._ui.but_last.clicked.connect(lambda: self._switch_frame('last'))

        self.hist.scene().sigMouseClicked.connect(self._hist_mouse_clicked)
        self.hist.item.sigLevelsChanged.connect(self.switch_off_auto_levels)
        self.hist.item.sigLookupTableChanged.connect(self._new_lookup_table)
        self._ui.chk_auto_levels.clicked.connect(lambda state: self._toggle_auto_levels(state))

        self._ui.bg_level.buttonClicked.connect(lambda button: self._change_level_mode(button))

    # ----------------------------------------------------------------------
    def add_file(self, file_name, move_from='second'):
        if move_from == 'second':
            self._main_view.add_file(file_name)
            self.data_pool.protect_file(file_name, False)
        else:
            self._second_view.add_file(file_name)
            self.data_pool.protect_file(file_name, True)

    # ----------------------------------------------------------------------
    def new_roi_range(self, roi_ind):
        self._main_view.new_roi_range(roi_ind)
        self._second_view.new_roi_range(roi_ind)

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
    def _new_axes(self, text):
        self.current_axes = self.section_axes_map[str(text)]
        self._setup_limits()
        self.display_z_value()
        self.update_image()
        self._main_view.new_axes()
        self._second_view.new_axes()

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
    def update_image(self):
        self.hist.item.sigLevelsChanged.disconnect()
        self.display_z_value()
        self._main_view.update_image()
        self._second_view.update_image()
        self.hist.item.sigLevelsChanged.connect(self.switch_off_auto_levels)

    # ----------------------------------------------------------------------
    def _setup_limits(self):
        if self._main_view.current_file is None:
            return

        self.max_frame = self.data_pool.get_max_frame(self._main_view.current_file, self.current_axes['z'])
        self._ui.sl_frame.setMaximum(self.max_frame)
        self.sld.setMaximum(self.max_frame)

    # ----------------------------------------------------------------------
    def display_z_value(self):
        if self._main_view.current_file is None:
            self._ui.lb_value.setText('')
            return

        if self._ui.chk_integration_mode.isChecked():
            z_name, z_min = self.data_pool.get_value_at_point(self._main_view.current_file, self.current_axes['z'],
                                                              self.current_frames[0])
            _, z_max = self.data_pool.get_value_at_point(self._main_view.current_file, self.current_axes['z'],
                                                         self.current_frames[1])

            self._ui.lb_value.setText(f'{z_name}: from {z_min:3f} to {z_max:3f}')
        else:
            z_name, z_value = self.data_pool.get_value_at_point(self._main_view.current_file, self.current_axes['z'],
                                                                self.current_frames[0])

            self._ui.lb_value.setText('{}: {:3f}'.format(z_name, z_value))

    # ------------------------------------------------------------------
    def _switch_integration_mode(self, state):
        self._ui.sl_frame.setVisible(not state)
        self.sld.setVisible(state)
        if state:
            self._display_new_frame(self.sld.low(), self.sld.high())
        else:
            self._display_new_frame(self._ui.sl_frame.value(), self._ui.sl_frame.value())
    # ----------------------------------------------------------------------
    def _display_new_frame(self, z_min, z_max):
        self._block_signals(True)

        self.current_frames = [min(max(z_min, 0), self.max_frame), min(max(z_max, 0), self.max_frame)]
        self.sld.setLow(self.current_frames[0])
        self.sld.setHigh(self.current_frames[1])
        self._ui.sl_frame.setValue(self.current_frames[0])

        self.display_z_value()
        self._block_signals(False)
        self.update_image()

    # ----------------------------------------------------------------------
    def current_file(self):
        return self._main_view.current_file

    # ----------------------------------------------------------------------
    def new_main_file(self, z_min, z_max):

        if self._main_view.current_file is not None:
            axes_names = self.data_pool.file_axes_caption(self._main_view.current_file)
            self._ui.lb_axes_captions.setText('X axis: {}, Y axis: {}, Z axis: {}'.format(axes_names[0],
                                                                                          axes_names[1],
                                                                                          axes_names[2]))

            self._setup_limits()
            if z_min is not None:
                self.current_frames[0] = self.data_pool.frame_for_point(self._main_view.current_file,
                                                                    self.current_axes['z'], z_min)
                self._ui.sl_frame.setValue(self.current_frames[0])
                self.sld.setLow(self.current_frames[0])

            if z_max is not None:
                self.current_frames[1] = self.data_pool.frame_for_point(self._main_view.current_file,
                                                                    self.current_axes['z'], z_max)
                self.sld.setHigh(self.current_frames[1])
        else:
            self._ui.lb_axes_captions.setText('')
            self._ui.sl_frame.setValue(0)

        self.display_z_value()
        self.update_image()

    # ----------------------------------------------------------------------
    def _switch_frame(self, type):
        shift = 0

        if type == 'first':
            shift = -self.current_frames[0]
        elif type == 'previous':
            shift = -1
        elif type == 'next':
            shift = 1
        elif type == 'last':
            shift = self.max_frame - self.current_frames[1]

        self._display_new_frame(self.current_frames[0] + shift, self.current_frames[1] + shift)

    # ----------------------------------------------------------------------
    def _block_signals(self, flag):
        self._ui.sl_frame.blockSignals(flag)
        self._ui.cb_section.blockSignals(flag)
