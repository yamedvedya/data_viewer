# Created by matveyev at 04.08.2021

from PyQt5 import QtWidgets, QtCore
import logging

from src.main_window import APP_NAME
from src.gui.cut_selector_ui import Ui_CutSelector
from src.utils.range_slider import RangeSlider


logger = logging.getLogger(APP_NAME)


# ----------------------------------------------------------------------
class CutSelector(QtWidgets.QWidget):

    new_cut = QtCore.pyqtSignal()

    # ----------------------------------------------------------------------
    def __init__(self, parent, my_id, force_integration):
        """
        """
        super(CutSelector, self).__init__()
        self._parent = parent

        self._ui = Ui_CutSelector()
        self._ui.setupUi(self)

        self._my_id = my_id
        self._max_frame = 0

        self.sld = RangeSlider(QtCore.Qt.Horizontal, self)
        self._ui.h_layout.insertWidget(4, self.sld, 0)
        self.sld.sliderMoved.connect(self._display_new_frame)
        self.sld.setVisible(False)

        self._force_integration = force_integration
        if force_integration:
            self._set_only_range_mode()

        self._ui.sl_frame.valueChanged.connect(lambda value: self._display_new_frame(value, value))

        self._ui.chk_integration_mode.clicked.connect(self._switch_integration_mode)

        self._ui.but_first.clicked.connect(lambda: self._switch_frame('first'))
        self._ui.but_previous.clicked.connect(lambda: self._switch_frame('previous'))
        self._ui.but_next.clicked.connect(lambda: self._switch_frame('next'))
        self._ui.but_last.clicked.connect(lambda: self._switch_frame('last'))

        self._ui.sp_value_from.valueChanged.connect(self._go_to_value)
        self._ui.sp_value_to.valueChanged.connect(self._go_to_value)

        self.display_value()

    # ------------------------------------------------------------------
    def get_id(self):
        return self._my_id

    # ----------------------------------------------------------------------
    def _set_only_range_mode(self):
        """
        This mode is used to select 2D sub-array inside of 2D image array.
        Slider returns upper and lower value. Integration mode is not available.
        """
        max_frame = self._parent.get_max_frame_along_axis(self._parent.get_cut_axis(self._my_id))

        self._ui.sl_frame.setVisible(False)
        self.sld.setVisible(True)

        self.sld.setLow(0)
        self._ui.sp_value_from.setValue(0)

        self._ui.sp_value_to.setValue(max_frame)
        self.sld.setHigh(max_frame)

        self._ui.chk_integration_mode.setChecked(True)
        self._ui.chk_integration_mode.hide()

        self._ui.lb_to.setVisible(True)
        self._ui.sp_value_to.setVisible(True)

    # ------------------------------------------------------------------
    def _switch_integration_mode(self, state):

        self._ui.sl_frame.setVisible(not state)
        self.sld.setVisible(state)
        if state:
            self._display_new_frame(self.sld.low(), self.sld.high())
        else:
            self._display_new_frame(self._ui.sl_frame.value(), self._ui.sl_frame.value())

        self._ui.sp_value_to.setVisible(state)
        self._ui.lb_to.setVisible(state)

    # ----------------------------------------------------------------------
    def _display_new_frame(self, z_min, z_max):

        self.block_signals(True)

        max_frame = self._parent.get_max_frame_along_axis(self._parent.get_cut_axis(self._my_id))

        current_frames = [min(max(z_min, 0), max_frame), min(max(z_max, 0), max_frame)]
        self.sld.setLow(current_frames[0])
        self.sld.setHigh(current_frames[1])
        self._ui.sl_frame.setValue(current_frames[0])

        self.display_value()
        self.new_cut.emit()

    # ----------------------------------------------------------------------
    def _go_to_value(self):

        z_min = self._parent.get_frame_for_value(self._parent.get_cut_axis(self._my_id), self._ui.sp_value_from.value())
        z_max = self._parent.get_frame_for_value(self._parent.get_cut_axis(self._my_id), self._ui.sp_value_to.value())

        self.block_signals(True)
        self._ui.sl_frame.setValue(z_min)
        self.sld.setLow(z_min)
        self.sld.setHigh(z_max)
        self.display_value()

    # ----------------------------------------------------------------------
    def _switch_frame(self, mode):

        shift = 0

        section = self.get_section()

        current_frame = self._parent.get_frame_for_value(self._parent.get_cut_axis(self._my_id), section['min'])
        new_frame = self._parent.get_frame_for_value(self._parent.get_cut_axis(self._my_id),
                                                     section['min'] + self._ui.sp_step.value())

        if mode == 'first':
            shift = -section['min']
        elif mode == 'previous':
            shift = current_frame - new_frame
        elif mode == 'next':
            shift = new_frame - current_frame
        elif mode == 'last':
            if section['mode'] == 'integration':
                shift = self._max_frame - section['max']
            else:
                shift = self._max_frame - section['min']

        if section['mode'] == 'integration':
            self._display_new_frame(section['min'] + shift, section['max'] + shift)
        else:
            self._display_new_frame(section['min'] + shift, section['min'] + shift)

    # ----------------------------------------------------------------------
    def setup_limits(self):

        self.block_signals(True)

        max_frame = self._parent.get_max_frame_along_axis(self._parent.get_cut_axis(self._my_id))
        logger.debug(f"Setup_limits of {max_frame} for {self._my_id}")

        self._ui.sl_frame.setMaximum(max_frame)
        self.sld.setMaximum(max_frame)
        self._max_frame = max_frame

        self.block_signals(False)

    # ----------------------------------------------------------------------
    def display_value(self):

        self.block_signals(True)
        if self._ui.chk_integration_mode.isChecked():
            z_name, z_min = self._parent.get_value_for_frame(self._parent.get_cut_axis(self._my_id), self.sld.low())
            _,      z_max = self._parent.get_value_for_frame(self._parent.get_cut_axis(self._my_id), self.sld.high())

            self._ui.lb_value.setText(f'{z_name}: from')

            decimals = 0 if int(z_min) == z_min and int(z_max) == z_max else 4

            self._ui.sp_value_from.setValue(z_min)
            self._ui.sp_value_to.setValue(z_max)

        else:
            z_name, z_value = self._parent.get_value_for_frame(self._parent.get_cut_axis(self._my_id),
                                                               self._ui.sl_frame.value())

            decimals = 0 if int(z_value) == z_value else 4

            self._ui.lb_value.setText(f'{z_name}:')
            self._ui.sp_value_from.setValue(z_value)

        self._ui.sp_value_from.setDecimals(decimals)
        self._ui.sp_value_to.setDecimals(decimals)
        self._ui.sp_step.setDecimals(decimals)
        if decimals == 0:
            self._ui.sp_step.setMinimum(1)
        else:
            self._ui.sp_step.setMinimum(0.0001)

        self.block_signals(False)

    # ----------------------------------------------------------------------
    def get_section(self):
        ret = {'axis': self._parent.get_cut_axis(self._my_id),
               'mode': 'integration' if self._ui.chk_integration_mode.isChecked() else 'single',
               'step': self._ui.sp_step.value()}

        if self._ui.chk_integration_mode.isChecked():
            ret['min'] = self.sld.low()
            ret['max'] = self.sld.high()
        else:
            ret['min'] = self._ui.sl_frame.value()
            ret['max'] = self._ui.sl_frame.value()

        return ret

    # ----------------------------------------------------------------------
    def new_file(self, selection):

        self.block_signals(True)

        new_state = selection['mode'] == 'single'

        if not self._force_integration:
            self._ui.chk_integration_mode.setChecked(not new_state)

            self._ui.sl_frame.setVisible(new_state)
            self.sld.setVisible(not new_state)
            self._ui.sp_value_to.setVisible(not new_state)
            self._ui.lb_to.setVisible(not new_state)

        self.sld.setLow(selection['min'])
        self.sld.setHigh(selection['max'])
        self._ui.sl_frame.setValue(selection['min'])

        self._ui.sp_value_from.setValue(selection['min'])
        self._ui.sp_value_to.setValue(selection['max'])
        self._ui.sp_step.setValue(selection['step'])

        self.display_value()

    # ----------------------------------------------------------------------
    def block_signals(self, flag):
        self._ui.sl_frame.blockSignals(flag)
        self._ui.sp_step.blockSignals(flag)
        self._ui.sp_value_from.blockSignals(flag)
        self._ui.sp_value_to.blockSignals(flag)
        self._ui.chk_integration_mode.blockSignals(flag)
        self.sld.blockSignals(flag)
