# Created by matveyev at 11.08.2021

from PyQt5 import QtWidgets, QtCore, QtGui

from src.utils.range_slider import RangeSlider
from src.gui.section_range_ui import Ui_SectionRange


# ----------------------------------------------------------------------
class SectionRange(QtWidgets.QWidget):
    """
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent, data_pool, roi_id, my_id):
        super(SectionRange, self).__init__()

        self._ui = Ui_SectionRange()
        self._ui.setupUi(self)

        self._my_id = my_id
        self._roi_id = roi_id
        self._data_pool = data_pool
        self._parent = parent

        self.sld = RangeSlider(QtCore.Qt.Horizontal, self)
        self._ui.v_layout.insertWidget(4, self.sld, 0)
        self.sld.sliderMoved.connect(self._new_slider_range)

        self._ui.sb_pos.valueChanged.connect(lambda value: self._roi_value_changed('pos', int(value)))
        self._ui.sb_width.valueChanged.connect(lambda value: self._roi_value_changed('width', int(value)))

    # ----------------------------------------------------------------------
    def refresh_view(self):
        self._block_signals(True)
        self._ui.lb_axis.setText(self._data_pool.get_file_axes(self._parent.get_current_file())
                                 [self._data_pool.get_roi_param(self._roi_id, f'axis_{self._my_id}')])

        pos_min, pos_max, width_max = self._data_pool.get_roi_limits(self._roi_id, self._my_id)
        self.set_min_max(pos_min, pos_max, width_max)
        self.update_value()
        self._block_signals(False)

    # ----------------------------------------------------------------------
    def set_min_max(self, pos_min, pos_max, width_max):
        if not pos_min <= int(self._ui.sb_pos.value()) <= pos_max:
            self._roi_value_changed('pos', max(min(int(self._ui.sb_pos.value()), pos_max), pos_min))

        self._ui.sb_pos.setMinimum(pos_min)
        self._ui.sb_pos.setMaximum(pos_max)

        if self._ui.sb_width.value() >= width_max:
            self._roi_value_changed('width', min(int(self._ui.sb_width.value()), width_max))

        self._ui.sb_width.setMaximum(width_max)

        self.sld.setMinimum(pos_min)
        self.sld.setMaximum(pos_min + width_max)

    # ----------------------------------------------------------------------
    def update_value(self):
        self._ui.sb_pos.setValue(self._data_pool.get_roi_param(self._roi_id, f'axis_{self._my_id}_pos'))
        self._ui.sb_width.setValue(self._data_pool.get_roi_param(self._roi_id, f'axis_{self._my_id}_width'))

        self.sld.setLow(self._data_pool.get_roi_param(self._roi_id, f'axis_{self._my_id}_pos'))
        self.sld.setHigh(self._data_pool.get_roi_param(self._roi_id, f'axis_{self._my_id}_pos') +
                         self._data_pool.get_roi_param(self._roi_id, f'axis_{self._my_id}_width'))

    # ----------------------------------------------------------------------
    def _roi_value_changed(self, param, value):
        self._block_signals(True)
        accepted_value = self._data_pool.roi_parameter_changed(self._roi_id, self._my_id, param, value)
        getattr(self._ui, f'sb_{param}').setValue(accepted_value)
        self._block_signals(False)
        self._parent.update_plots()

    # ----------------------------------------------------------------------
    def _new_slider_range(self, vmin, vmax):
        self._block_signals(True)
        accepted_pos = self._data_pool.roi_parameter_changed(self._roi_id, self._my_id, 'pos', vmin)
        self._ui.sb_pos.setValue(accepted_pos)
        accepted_width = self._data_pool.roi_parameter_changed(self._roi_id, self._my_id, 'width', vmax - vmin)
        self._ui.sb_width.setValue(accepted_width)
        self._block_signals(False)

        self._parent.update_plots()

    # ----------------------------------------------------------------------
    def _block_signals(self, flag):
        self.sld.blockSignals(flag)
        self._ui.sb_pos.blockSignals(flag)
        self._ui.sb_width.blockSignals(flag)
        self._data_pool.blockSignals(flag)
