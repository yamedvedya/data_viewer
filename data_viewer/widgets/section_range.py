# Created by matveyev at 11.08.2021

from PyQt5 import QtWidgets, QtCore, QtGui

from data_viewer.utils.range_slider import RangeSlider
from data_viewer.gui.section_range_ui import Ui_SectionRange


# ----------------------------------------------------------------------
class SectionRange(QtWidgets.QWidget):
    """
    """

    update_roi = QtCore.pyqtSignal(int)

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
    def enable_me(self, flag):
        self._ui.sb_pos.setEnabled(flag)
        self._ui.sb_width.setEnabled(flag)
        self.sld.setEnabled(flag)

    # ----------------------------------------------------------------------
    def refresh_view(self):
        self._block_signals(True)
        if self._parent.get_current_file():
            self._ui.lb_axis.setText(self._data_pool.get_file_axes(self._parent.get_current_file())
                                     [self._data_pool.get_roi_param(self._roi_id, f'axis_{self._my_id}')])

            self._update_limits()
            self._update_value()
        else:
            self._ui.lb_axis.setText('')

        self._block_signals(False)

    # ----------------------------------------------------------------------
    def _update_limits(self):
        axis_min, axis_max, max_pos, max_width = self._data_pool.get_roi_limits(self._roi_id, self._my_id)
        self._ui.sb_pos.setMinimum(axis_min)
        self._ui.sb_pos.setMaximum(max_pos)

        self._ui.sb_width.setMaximum(max_width)

        self.sld.setMinimum(axis_min)
        self.sld.setMaximum(axis_max)

    # ----------------------------------------------------------------------
    def _update_value(self):
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

        self.sld.setLow(self._data_pool.get_roi_param(self._roi_id, f'axis_{self._my_id}_pos'))
        self.sld.setHigh(self._data_pool.get_roi_param(self._roi_id, f'axis_{self._my_id}_pos') +
                         self._data_pool.get_roi_param(self._roi_id, f'axis_{self._my_id}_width'))

        self._update_limits()

        self._block_signals(False)

        self.update_roi.emit(self._roi_id)
        self._parent.update_plots()

    # ----------------------------------------------------------------------
    def _new_slider_range(self, vmin, vmax):

        self._block_signals(True)

        accepted_pos = self._data_pool.roi_parameter_changed(self._roi_id, self._my_id, 'pos', vmin)
        self._ui.sb_pos.setValue(accepted_pos)

        accepted_width = self._data_pool.roi_parameter_changed(self._roi_id, self._my_id, 'width', vmax - vmin)
        self._ui.sb_width.setValue(accepted_width)

        self._update_limits()

        self._block_signals(False)

        self.update_roi.emit(self._roi_id)
        self._parent.update_plots()

    # ----------------------------------------------------------------------
    def _block_signals(self, flag):
        self.sld.blockSignals(flag)
        self._ui.sb_pos.blockSignals(flag)
        self._ui.sb_width.blockSignals(flag)
        # self._data_pool.blockSignals(flag)
