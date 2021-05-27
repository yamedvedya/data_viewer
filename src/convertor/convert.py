# Created by matveyev at 10.05.2021

import xrayutilities as xu
import pyqtgraph as pg
import numpy as np

from PyQt5 import QtWidgets

import src.convertor.p23lib as p23lib
from src.gui.converter_ui import Ui_Converter
class Converter(QtWidgets.QMainWindow):

    def __init__(self, data_pool):
        super(Converter, self).__init__()
        self._ui = Ui_Converter()
        self._ui.setupUi(self)

        self._data_pool = data_pool

        self._file_name = None
        self._gridder = None

        plots = ['xy', 'xz', 'yz']
        self._plots = dict.fromkeys(plots)
        self._color_meshes = dict.fromkeys(plots)

        for plot in plots:
            self._plots[plot] = pg.PlotItem()
            self._plots[plot].showAxis('left', False)
            self._plots[plot].showAxis('bottom', False)
            self._plots[plot].setMenuEnabled(False)

            getattr(self._ui, f'gv_{plot}').setStyleSheet("")
            getattr(self._ui, f'gv_{plot}').setBackground('w')
            getattr(self._ui, f'gv_{plot}').setObjectName(f'gv_{plot}')

            getattr(self._ui, f'gv_{plot}').setCentralItem(self._plots[plot])
            getattr(self._ui, f'gv_{plot}').setRenderHints(getattr(self._ui, f'gv_{plot}').renderHints())

            self._color_meshes[plot] = pg.PColorMeshItem()
            self._plots[plot].addItem(self._color_meshes[plot])

        self._ui.cmd_preview.clicked.connect(self._preview)
        self._ui.cmd_save.clicked.connect(self._save)
        self._ui.cmd_cancel.clicked.connect(self.close)

    # ----------------------------------------------------------------------
    def show(self, file_name):
        self._ui.cmd_roi.clear()
        for ind in range(self._data_pool.roi_counts()):
            self._ui.cmd_roi.addItem(f'ROI_{ind}')

        self._file_name = file_name
        self._ui.sb_cen_x.setMaximum(self._data_pool.get_max_frame(self._file_name, 0))
        self._ui.sb_cen_y.setMaximum(self._data_pool.get_max_frame(self._file_name, 1))

        super(Converter, self).show()

    # ----------------------------------------------------------------------
    def _preview(self):
        self._convert()
        if self._gridder is not None:
            self._plots['xy'].setData(self._gridder.yaxis, self._gridder.zaxis, np.log(self._gridder.data.sum(0).T))
            self._plots['xy'].setData(self._gridder.yaxis, self._gridder.zaxis, np.log(self._gridder.data.sum(0).T))
            self._plots['xy'].setData(self._gridder.yaxis, self._gridder.zaxis, np.log(self._gridder.data.sum(0).T))

    # ----------------------------------------------------------------------
    def _save(self):
        pass

    # ----------------------------------------------------------------------
    def _convert(self):

        roi_index = self._data_pool.get_roi_index(self._ui.cmd_roi.currentIndex())
        if self._data_pool.get_roi_param(roi_index, 'axis') != 2:
            raise RuntimeError('Only sections along detector Z can be processed!')

        geometry = p23lib.P23SixC(omega=self._ui.chk_omega.isChecked(),
                                  omega_t=self._ui.chk_omega_t.isChecked(),
                                  chi=self._ui.chk_chi.isChecked(),
                                  phi=self._ui.chk_phi.isChecked(),
                                  mu=self._ui.chk_mu.isChecked())

        qconv = geometry.getQconversion()

        hxrd = xu.HXRD([1, 0, 0], [0, 0, 1],
                       geometry="real",
                       qconv=qconv,
                       en=self._data_pool.get_entry_value('energy'),
                       sampleor="y-")

        roi_index = self._data_pool.get_roi_index(self._ui.cmd_roi.currentIndex())

        roi_cut = (self._data_pool.get_roi_param(roi_index, 'roi_1_pos'),
                   self._data_pool.get_roi_param(roi_index, 'roi_1_pos') + self._data_pool.get_roi_param(roi_index, 'roi_1_width'),
                   self._data_pool.get_roi_param(roi_index, 'roi_2_pos'),
                   self._data_pool.get_roi_param(roi_index, 'roi_2_pos') + self._data_pool.get_roi_param(roi_index, 'roi_2_width'))

        hxrd.Ang2Q.init_area('y+',
                             'z-',
                             cch1=int(self._ui.sb_cen_x.value()),
                             cch2=int(self._ui.sb_cen_y.value()),
                             Nch1=int(self._data_pool.get_roi_param(roi_index, 'roi_1_width')),
                             Nch2=int(self._data_pool.get_roi_param(roi_index, 'roi_2_width')),
                             pwidth1=self._ui.dsb_size_x.value()*1e-6,
                             pwidth2=self._ui.dsb_size_y.value()*1e-6,
                             distance=self._ui.dsb_det_d.value(),
                             detrot=self._ui.dsb_det_r.value(),
                             tiltazimuth=self._ui.dsb_det_r.value(),
                             tilt=self._ui.dsb_det_r.value(),
                             roi=roi_cut)

        angles_set = ['omega', 'chi', 'phi', 'gamma', 'delta']
        scan_angles = dict.fromkeys(angles_set)
        for angle in angles_set:
            try:
                scan_angles[angle] = self._data_pool.get_entry_value(angle) - getattr(self._ui, f'dsb_shift_{angle}').value()
            except KeyError:
                scan_angles[angle] = - getattr(self._ui, f'dsb_shift_{angle}').value()


        qx, qy, qz = hxrd.Ang2Q.area(scan_angles['omega'],
                                     scan_angles['chi'],
                                     scan_angles['phi'],
                                     scan_angles['gamma'],
                                     scan_angles['delta'],
                                     en=self._data_pool.get_entry_value('energy'),
                                     UB=hxrd._transform.matrix)

        bins = int(self._ui.sb_bin_x.value()), int(self._ui.sb_bin_y.value()), int(self._ui.sb_bin_z.value())
        self._gridder = xu.FuzzyGridder3D(*bins)
        self._gridder(qx, qy, qz, self._data_pool.get_roi_cut(self._file_name, roi_index))
