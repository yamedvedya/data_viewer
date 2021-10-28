# Created by matveyev at 04.08.2021

from PyQt5 import QtWidgets, QtCore
import logging

from src.widgets.array_selector import ArraySelector
from src.main_window import APP_NAME
from src.gui.cut_selector_ui import Ui_CutSelector


logger = logging.getLogger(APP_NAME)


class CutSelector(QtWidgets.QWidget):

    new_cut = QtCore.pyqtSignal()
    new_axis = QtCore.pyqtSignal(list)

    def __init__(self, parent):
        """
        """
        super(CutSelector, self).__init__()
        self._ui = Ui_CutSelector()
        self._ui.setupUi(self)

        self._x_buttons_group = QtWidgets.QButtonGroup()
        self._x_buttons_group.setExclusive(True)

        self._y_buttons_group = QtWidgets.QButtonGroup()
        self._y_buttons_group.setExclusive(True)

        self._array_selectors = []
        self._integration_boxes = []
        self._x_buttons = []
        self._y_buttons = []

        self._axes_labels = []

        self._ui.cut_selectors.setLayout(QtWidgets.QGridLayout(self._ui.cut_selectors))
        self._ui.cut_selectors.layout().setContentsMargins(0, 0, 0, 0)
        self._new_layout()

        self._last_axes = {}

    # ----------------------------------------------------------------------
    def _new_layout(self):
        for button in self._x_buttons_group.buttons():
            self._x_buttons_group.removeButton(button)

        for button in self._y_buttons_group.buttons():
            self._y_buttons_group.removeButton(button)

        layout = self._ui.cut_selectors.layout()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item:
                w = layout.itemAt(i).widget()
                if w:
                    layout.removeWidget(w)
                    w.setVisible(False)

        label = QtWidgets.QLabel('Axis', self)
        label.setAlignment(QtCore.Qt.AlignHCenter)
        layout.addWidget(label, 0, 0)

        label = QtWidgets.QLabel('X', self)
        label.setAlignment(QtCore.Qt.AlignHCenter)
        layout.addWidget(label, 0, 1)

        label = QtWidgets.QLabel('Y', self)
        label.setAlignment(QtCore.Qt.AlignHCenter)
        layout.addWidget(label, 0, 2)

        label = QtWidgets.QLabel('', self)
        label.setAlignment(QtCore.Qt.AlignHCenter)
        layout.addWidget(label, 0, 3)
        layout.setColumnStretch(3, 1)

        label = QtWidgets.QLabel('Integration', self)
        label.setAlignment(QtCore.Qt.AlignHCenter)
        layout.addWidget(label, 0, 4)

    # ----------------------------------------------------------------------
    def refresh_selectors(self, axes):
        self._new_layout()

        layout = self._ui.cut_selectors.layout()

        self._array_selectors = []
        self._integration_boxes = []
        self._x_buttons = []
        self._y_buttons = []

        self._axes_labels = axes

        for ind, axis in enumerate(axes):
            label = QtWidgets.QLabel(axis, self)
            label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            layout.addWidget(label, ind + 1, 0)

            rb = QtWidgets.QRadioButton(self)
            rb.clicked.connect(lambda state, ax='X', id=ind: self._new_axes(ax, id))
            layout.addWidget(rb, ind + 1, 1)
            self._x_buttons_group.addButton(rb)
            self._x_buttons.append(rb)

            rb = QtWidgets.QRadioButton(self)
            rb.clicked.connect(lambda state, ax='Y', id=ind: self._new_axes(ax, id))
            layout.addWidget(rb, ind + 1, 2)
            self._y_buttons_group.addButton(rb)
            self._y_buttons.append(rb)

            selector = ArraySelector(ind)
            selector.new_cut.connect(lambda: self.new_cut.emit())
            layout.addWidget(selector, ind + 1, 3)
            self._array_selectors.append(selector)

            chk_box = QtWidgets.QCheckBox(self)
            chk_box.clicked.connect(lambda state, id=ind: self._integration_changed(state, id))
            layout.addWidget(chk_box, ind + 1, 4)
            self._integration_boxes.append(chk_box)

    # ----------------------------------------------------------------------
    def _integration_changed(self, state, ind):
        self._array_selectors[ind].switch_integration_mode(state)
        self.new_cut.emit()

    # ----------------------------------------------------------------------
    def _new_axes(self, axis, ind):

        self.block_signals(True)

        if axis == 'X' and self._last_axes['Y'] == ind:
            self._y_buttons[self._last_axes['X']].setChecked(True)
        elif axis == 'Y' and self._last_axes['X'] == ind:
            self._x_buttons[self._last_axes['Y']].setChecked(True)

        labels = ['', '']
        for ind, (name, x_but, y_but, array_selector, integration_box) in enumerate(zip(self._axes_labels,
                                                                                        self._x_buttons_group.buttons(),
                                                                                        self._y_buttons_group.buttons(),
                                                                                        self._array_selectors,
                                                                                        self._integration_boxes)):
            if x_but.isChecked() or y_but.isChecked():
                array_selector.switch_integration_mode(True)
                integration_box.setVisible(False)
                if x_but.isChecked():
                    self._last_axes['X'] = ind
                    labels[0] = name
                else:
                    self._last_axes['Y'] = ind
                    labels[1] = name
            else:
                array_selector.switch_integration_mode(integration_box.isChecked())
                integration_box.setVisible(True)

        self.block_signals(False)

        self.new_axis.emit(labels)
        self.new_cut.emit()

    # ----------------------------------------------------------------------
    def set_limits(self, limits):
        for limit, selector in zip(limits, self._array_selectors):
            selector.setup_limits(limit)

    # ----------------------------------------------------------------------
    def get_current_selection(self):
        section = []
        for x_but, y_but, array_selector, integration_box in zip(self._x_buttons_group.buttons(),
                                                                 self._y_buttons_group.buttons(),
                                                                 self._array_selectors,
                                                                 self._integration_boxes):

            if x_but.isChecked():
                axis = 'X'
            elif y_but.isChecked():
                axis = 'Y'
            else:
                axis = ''

            f_min, f_max = array_selector.get_values()
            section.append({'axis': axis,
                            'integration': integration_box.isChecked(),
                            'min': f_min,
                            'max': f_max})

        return section

    # ----------------------------------------------------------------------
    def set_section(self, selections):
        """
        Set selection.
        """
        self.block_signals(True)

        self._last_axes = {}

        for ind, (x_but, y_but, array_selector, integration_box, section) in enumerate(zip(self._x_buttons_group.buttons(),
                                                                                           self._y_buttons_group.buttons(),
                                                                                           self._array_selectors,
                                                                                           self._integration_boxes,
                                                                                           selections)):
            x_but.setChecked(section['axis'] == 'X')
            y_but.setChecked(section['axis'] == 'Y')
            self._last_axes[section['axis']] = ind

            integration_box.setChecked(section['integration'])
            integration_box.setVisible(section['axis'] not in ['X', 'Y'])
            array_selector.set_section(section)

        self.block_signals(False)

    # ----------------------------------------------------------------------
    def block_signals(self, flag):

        for widget in self._x_buttons + self._y_buttons + self._array_selectors + self._integration_boxes:
            widget.blockSignals(flag)

