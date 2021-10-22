# Created by matveyev at 04.08.2021

from PyQt5 import QtWidgets, QtCore
import logging

from src.main_window import APP_NAME
from src.gui.array_selector_ui import Ui_Form


logger = logging.getLogger(APP_NAME)


class CutSelector(QtWidgets.QWidget):

    new_cut = QtCore.pyqtSignal()
    new_axis = QtCore.pyqtSignal(int, int)

    def __init__(self, my_id, axis_name='Dim', axis_choice=[]):
        """
        """
        super(CutSelector, self).__init__()
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self._ui.sl_range.setVisible(False)
        self._ui.axis_label.setText(axis_name)
        self._ui.cmb_selector.addItems(axis_choice)
        self._ui.cmb_selector.setCurrentIndex(my_id)
        self.current_axis = my_id
        self.axis_label = axis_name

        self._my_id = my_id
        self._max_frame = 0

        self.limit_range = 0  # Limit maximum range in range slider
        if self.current_axis < len(axis_choice):
            self._switch_only_range_mode(True)

        # Connect signals
        self._ui.sl_frame.valueChanged.connect(self._update_from_frame_slider)
        self._ui.sl_range.sliderMoved.connect(self._update_from_range_slider)

        self._ui.chk_integration_mode.clicked.connect(self._switch_integration_mode)

        self._ui.but_first.clicked.connect(lambda: self._update_from_navigation_buttons('first'))
        self._ui.but_previous.clicked.connect(lambda: self._update_from_navigation_buttons('previous'))
        self._ui.but_next.clicked.connect(lambda: self._update_from_navigation_buttons('next'))
        self._ui.but_last.clicked.connect(lambda: self._update_from_navigation_buttons('last'))

        self._ui.sp_value_from.valueChanged.connect(self._update_from_sp)
        self._ui.sp_value_to.valueChanged.connect(self._update_from_sp)

        self._ui.cmb_selector.currentIndexChanged.connect(self._new_axis_selected)

    def _new_axis_selected(self, new_axis):
        self.new_axis.emit(new_axis, self.current_axis)

    def get_current_axis(self):
        return self._ui.cmb_selector.currentIndex()

    def set_axis(self, new_axis):
        self._ui.cmb_selector.blockSignals(True)
        self._ui.cmb_selector.setCurrentIndex(new_axis)
        self.current_axis = new_axis
        if new_axis < self._ui.cmb_selector.count():
            self._switch_only_range_mode(True)
        else:
            self._switch_only_range_mode(False)
        self._ui.cmb_selector.blockSignals(False)

    def _switch_only_range_mode(self, state):
        """
        This mode is used to select 2D sub-array inside of 2D image array.
        Slider returns upper and lower value. Integration mode is not available.
        """
        self._ui.chk_integration_mode.setChecked(state)
        if state:
            self._ui.chk_integration_mode.hide()
        else:
            self._ui.chk_integration_mode.show()
        self._switch_integration_mode(state)

    def _switch_integration_mode(self, state):

        self._ui.sl_frame.setVisible(not state)
        self._ui.sl_range.setVisible(state)
        self._ui.sp_value_to.setVisible(state)
        self._ui.lb_to.setVisible(state)

    def _update_from_frame_slider(self, value):
        """
        Set value of range slider and spin_boxes
        """
        self._set_spin_boxes(value, value)
        self._set_slider_value(value, value)
        self.new_cut.emit()

    def _update_from_range_slider(self, z_min, z_max):
        """
        Set value of range slider and spin_boxes
        """
        z_min, z_max = self._apply_range_limit(z_min, z_max)
        self._set_spin_boxes(z_min, z_max)
        self._set_slider_value(z_min, z_max)
        self.new_cut.emit()

    def _update_from_navigation_buttons(self, mode):
        """
        Process button_clink on navigation buttons
        """
        z_min = self._ui.sl_range.low()
        z_max = self._ui.sl_range.high()

        new_min = z_min
        new_max = z_max

        if mode == 'first':
            new_min = 0
        elif mode == 'previous':
            new_min -= 1
            new_max -= 1
        elif mode == 'next':
            new_min += 1
            new_max += 1
        elif mode == 'last':
            new_max = self._max_frame
            if self._get_mode() != 'integration':
                new_min = self._max_frame

        new_max = min(max(0, new_max), self._max_frame)
        new_min = min(max(0, new_min), self._max_frame)
        new_min, new_max = self._apply_range_limit(new_min, new_max)

        self._set_spin_boxes(new_min, new_max)
        self._set_slider_value(new_min, new_max)
        self.new_cut.emit()

    def _update_from_sp(self):
        """
        Set values to slider given in the SpinBox.
        """
        z_min = self._ui.sp_value_from.value()
        z_max = self._ui.sp_value_to.value()
        z_min, z_max = self._apply_range_limit(z_min, z_max)
        self._set_slider_value(z_min, z_max)
        self._set_spin_boxes(z_min, z_max)
        self.new_cut.emit()

    def _set_slider_value(self, z_min, z_max):
        """
        Set values to slider.
        """
        self.block_signals(True)
        self._ui.sl_frame.setValue(z_min)
        self._ui.sl_range.setLow(z_min)
        self._ui.sl_range.setHigh(z_max)
        self.block_signals(False)

    def _set_spin_boxes(self, z_min, z_max):
        """
        Set value of spin_boxes sp_value_from, sp_value_to and sp_step
        """
        self.block_signals(True)
        decimals = 0 if int(z_min) == z_min and int(z_max) == z_max else 4

        self._ui.sp_value_from.setValue(z_min)
        self._ui.sp_value_to.setValue(z_max)
        self._ui.sp_value_from.setValue(z_min)

        self._ui.sp_value_from.setDecimals(decimals)
        self._ui.sp_value_to.setDecimals(decimals)
        self._ui.sp_step.setDecimals(decimals)
        if decimals == 0:
            self._ui.sp_step.setMinimum(1)
        else:
            self._ui.sp_step.setMinimum(0.0001)
        self.block_signals(False)

    def _apply_range_limit(self, z_min, z_max):
        z_min = max(0, min(z_min, z_max))
        if 0 < self.limit_range - 1 < (z_max - z_min):
            z_max = self.limit_range + z_min - 1
        return z_min, z_max

    def setup_limits(self, max_frame):
        """
        Set limits to sliders and spin_boxes
        """
        self.block_signals(True)
        logger.debug(f"Setup_limits of {max_frame} for {self._my_id}")

        self._ui.sl_frame.setMaximum(max_frame)
        self._ui.sl_range.setMaximum(max_frame)
        self._ui.sl_range.setMinimum(0)
        self._ui.sp_value_to.setMaximum(max_frame)
        self._ui.sp_value_from.setMaximum(max_frame)
        self._max_frame = max_frame

        self.block_signals(False)

    def get_id(self):
        return self._my_id

    def get_section(self):
        """
        Get selector parameters
        """
        ret = {'axis': self.current_axis,
               'axis_label': self.axis_label,
               'id': self._my_id,
               'mode': self._get_mode(),
               'step': int(self._ui.sp_step.value()),
               'min': int(self._ui.sl_range.low()),
               'max': int(self._ui.sl_range.high()),
               'range_limit': self.limit_range}
        return ret

    def _get_mode(self):
        return 'integration' if self._ui.chk_integration_mode.isChecked() else 'single'

    def set_section(self, selection):
        """
        Set selection.
        """
        self.block_signals(True)

        if selection['axis'] < self._ui.cmb_selector.count():
            self._switch_only_range_mode(True)
        else:
            self._switch_only_range_mode(False)
            selection['max'] = selection['min']

        self.limit_range = selection['range_limit']
        self._ui.sp_step.setValue(selection['step'])
        self._set_slider_value(selection['min'], selection['max'])
        self._set_spin_boxes(selection['min'], selection['max'])
        self.set_axis(selection['axis'])

    def block_signals(self, flag):
        self._ui.sl_frame.blockSignals(flag)
        self._ui.sl_range.blockSignals(flag)
        self._ui.sp_step.blockSignals(flag)
        self._ui.sp_value_from.blockSignals(flag)
        self._ui.sp_value_to.blockSignals(flag)
        self._ui.chk_integration_mode.blockSignals(flag)
