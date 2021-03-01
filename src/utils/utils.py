# Created by matveyev at 15.02.2021

import h5py
import os
import numpy as np

from PyQt5 import QtCore, QtWidgets


# ----------------------------------------------------------------------
class FileFilter(QtCore.QSortFilterProxyModel):

    new_version = True

    # ----------------------------------------------------------------------
    def filterAcceptsRow(self, source_row, source_parent):
        if self.new_version:
            return super(FileFilter, self).filterAcceptsRow(source_row, source_parent)
        else:
            match = False
            my_index = self.sourceModel().index(source_row, 0, source_parent)
            for row in range(self.sourceModel().rowCount(my_index)):
                match |= self.filterAcceptsRow(row, my_index)

            match |= super(FileFilter, self).filterAcceptsRow(source_row, source_parent)

            return match

# ----------------------------------------------------------------------
def refresh_combo_box(combo, text):
    idx = combo.findText(text)
    if idx != -1:
        combo.setCurrentIndex(idx)
        return True
    else:
        combo.setCurrentIndex(0)
        return False

# ----------------------------------------------------------------------
def get_text_coordinates(plot_item, size, position='tl'):

    [[x_min, x_max], [y_min, y_max]] = plot_item.viewRange()

    dx = abs(x_max - x_min) * 0.05
    dy = abs(y_max - y_min) * 0.05

    if position == 'tl':
      textx = x_min + dx
      texty = y_max - dy
    elif position == 'tr':
      textx = x_max - dx - size.width() * plot_item.getViewBox().viewPixelSize()[0]
      texty = y_max - dy
    elif position == 'bl':
      textx = x_max + dx
      texty = y_min + dy + size.height() * plot_item.getViewBox().viewPixelSize()[1]
    elif position == 'br':
      textx = x_max - dx - size.width() * plot_item.getViewBox().viewPixelSize()[0]
      texty = y_min + dy + size.height() * plot_item.getViewBox().viewPixelSize()[1]

    return QtCore.QPointF(textx, texty)


# ----------------------------------------------------------------------
def read_mask_file(file_name):
    mask, mask_info = None, None
    try:
        with h5py.File(file_name, 'r') as f:
            mask = np.array(f['Mask_file'])
            mask_info = {'file': os.path.basename(file_name), 'energy': float(f['Energy_for_acqusition'][...])}
    except:
        pass

    return mask, mask_info

# ----------------------------------------------------------------------
def info_dialog(text):
    msg = QtWidgets.QMessageBox()
    msg.setModal(False)
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText(text)
    msg.setWindowTitle("Info")
    msg.show()
    return msg