# Created by matveyev at 17.02.2021

from PyQt5 import QtCore, QtGui

import weakref
import numpy as np
import pyqtgraph as pg

import src.lookandfeel as lookandfeel

# ----------------------------------------------------------------------
class SectionPlot(QtCore.QObject):
    PENCOUNTER = 0

    # Base class for the x_data and beamline parameter plots

    # ----------------------------------------------------------------------
    def __init__(self, plot_item, name, normalized, color):
        super(SectionPlot, self).__init__()

        self.plot_item = weakref.ref(plot_item)

        self.plot = plot_item.plot([], name=name,
                                   pen=pg.mkPen(color=lookandfeel.PLOT_COLORS[color % len(lookandfeel.PLOT_COLORS)]))

        SectionPlot.PENCOUNTER += 1

        self.x_data = np.array([])
        self.y_data = np.array([])

        self._is_visible = True

        self.tooltip = pg.TextItem(text=name, color=(0, 0, 0))
        self.tooltip.setFont(QtGui.QFont("Arial", 9))
        self.tooltip.hide()
        self.plot_item().addItem(self.tooltip)

        self.scan_data = None

        self.plot_is_normalized = normalized

    # ----------------------------------------------------------------------
    def get_data(self):
        return self.plot.getData()

    # ----------------------------------------------------------------------
    def get_all_data(self):
        if self.scan_data is not None:
            return self.plots[0].getData(), self.scan_data[0]
        else:
            return self.plots[0].getData(), None

    # ----------------------------------------------------------------------
    def empty(self):
        return len(self.plot.getData()[0]) < 1

    # ----------------------------------------------------------------------
    def set_visible(self, flag):
        self.plot.setVisible(flag)
        if not flag:
            self.tooltip.setVisible(flag)

    # ----------------------------------------------------------------------
    def release(self):
        self.plot_item().removeItem(self.plot)
        self.plot_item().removeItem(self.tooltip)
        self.plot_item().legend.removeItemByAddress(self.plot)

    # ----------------------------------------------------------------------
    def show_tool_tip(self, flag, pos=None):
        if flag:
            self.tooltip.setColor(self.plot.opts["pen"].color())
            self.tooltip.setPos(pos.x(), pos.y())
            self.tooltip.show()
        else:
            self.tooltip.hide()

    # ----------------------------------------------------------------------
    def distance_y(self, pos):
        x, y = self.plot.getData()
        if np.min(x) <= pos.x() and pos.x() <= np.max(x):
            x_idx = np.argmin(np.abs(x - pos.x()))
            return np.abs(pos.y() - y[x_idx])

        return 1e+8

    # ----------------------------------------------------------------------
    def range_y(self):
        _, y = self.plot.getData()
        return np.abs(np.max(y) - np.min(y))

    # ----------------------------------------------------------------------
    def normalize_plot(self, status):
        self.plot_is_normalized = status
        if status:
            if len(self.y_data):
                dy = np.max(self.y_data) - np.min(self.y_data)
                if dy > 0:
                    y = (self.y_data - np.min(self.y_data)) / dy
                    self.plot.setData(self.x_data, y)

        else:
            try:
                if len(self.y_data):
                    self.plot.setData(self.x_data, self.y_data)
            except:
                pass

    # ----------------------------------------------------------------------
    def update_plot(self, x, y):

        self.x_data = x
        self.y_data = y

        if self.plot_is_normalized:
            dy = np.max(y) - np.min(y)
            if dy > 0:
                y = (y - np.min(y)) / dy
            else:
                y = y/np.max(y)

        self.plot.setData(self.x_data, y)