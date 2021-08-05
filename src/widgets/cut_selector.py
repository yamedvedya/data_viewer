# Created by matveyev at 04.08.2021

from PyQt5 import QtWidgets, QtCore

from src.gui.cut_selector_ui import Ui_CutSelector
from src.utils.range_slider import RangeSlider


# ----------------------------------------------------------------------
class CutSelector(QtWidgets.QWidget):

    new_cut = QtCore.pyqtSignal()

    # ----------------------------------------------------------------------
    def __init__(self, parent, my_id):
        """
        """
        super(CutSelector, self).__init__()
        self._parent = parent

        self._ui = Ui_CutSelector()
        self._ui.setupUi(self)

        self._my_id = my_id

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

        self.display_value()

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

        self.block_signals(True)

        max_frame = self._parent.get_max_frame(self._my_id)

        current_frames = [min(max(z_min, 0), max_frame), min(max(z_max, 0), max_frame)]
        self.sld.setLow(current_frames[0])
        self.sld.setHigh(current_frames[1])
        self._ui.sl_frame.setValue(current_frames[0])

        self.display_value()
        self.new_cut.emit()
        self.block_signals(False)

    # ----------------------------------------------------------------------
    def setup_limits(self):

        self.block_signals(True)
        need_update = False
        max_frame = self._parent.get_max_frame(self._my_id)
        if max_frame > self._ui.sl_frame.value():
            need_update = True

        self._ui.sl_frame.setMaximum(max_frame)
        self.sld.setMaximum(max_frame)

        if need_update:
            if self._ui.chk_integration_mode.isChecked():
                self._display_new_frame(self.sld.low(), self.sld.high())
            else:
                self._display_new_frame(self._ui.sl_frame.value(), self._ui.sl_frame.value())

        self.display_value()

        self.block_signals(False)

    # ----------------------------------------------------------------------
    def display_value(self):

        current_frames = (self.sld.low(), self.sld.high())
        if self._ui.chk_integration_mode.isChecked():
            z_name, z_min = self._parent.get_value_at_point(self._my_id, current_frames[0])
            _,      z_max = self._parent.get_value_at_point(self._my_id, current_frames[1])

            self._ui.lb_value.setText(f'{z_name}: from {z_min:3f} to {z_max:3f}')
        else:
            z_name, z_value = self._parent.get_value_at_point(self._my_id, current_frames[0])

            self._ui.lb_value.setText('{}: {:3f}'.format(z_name, z_value))

    # ----------------------------------------------------------------------
    def get_section(self):
        if self._ui.chk_integration_mode.isChecked():
            return self._my_id, self.sld.low(), self.sld.high()
        else:
            return self._my_id, self._ui.sl_frame.value(), self._ui.sl_frame.value()

    # ----------------------------------------------------------------------
    def new_file(self, z_min, z_max):

        if z_min is not None:
            frame = self.data_pool.frame_for_value(self._main_view.current_file, self._my_id, z_min)
            self._ui.sl_frame.setValue(frame)
            self.sld.setLow(frame)

        if z_max is not None:
            frame = self.data_pool.frame_for_value(self._main_view.current_file, self._my_id, z_max)
            self.sld.setHigh(frame)

        self.display_z_value()

    # ----------------------------------------------------------------------
    def _switch_frame(self, type):
        shift = 0

        if type == 'first':
            shift = -self.sld.low()
        elif type == 'previous':
            shift = -1
        elif type == 'next':
            shift = 1
        elif type == 'last':
            shift = self.max_frame - self.sld.high()

        self._display_new_frame(self.sld.low() + shift, self.sld.high() + shift)

    # ----------------------------------------------------------------------
    def block_signals(self, flag):
        self._ui.sl_frame.blockSignals(flag)
        self.sld.blockSignals(flag)
