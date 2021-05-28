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
            self._plots[plot].setMenuEnabled(False)

            getattr(self._ui, f'gv_{plot}').setStyleSheet("")
            getattr(self._ui, f'gv_{plot}').setBackground('w')
            getattr(self._ui, f'gv_{plot}').setObjectName(f'gv_{plot}')

            getattr(self._ui, f'gv_{plot}').setCentralItem(self._plots[plot])
            getattr(self._ui, f'gv_{plot}').setRenderHints(getattr(self._ui, f'gv_{plot}').renderHints())

            self._plots[plot].scene().sigMouseClicked.connect(lambda event, source=plot:
                                                              self._mouse_clicked(event, source))

        self._ui.cmd_preview.clicked.connect(self._preview)
        self._ui.cmd_save.clicked.connect(self._save)
        self._ui.cmd_cancel.clicked.connect(self.close)

    # ----------------------------------------------------------------------
    def _mouse_clicked(self, event, source):
        if event.double():
            try:
                self._plots[source].autoRange()
            except:
                pass

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

        for plot in
            self._plots['xy']
        self._convert()
        if self._gridder is not None:
            try:
                xv, yv = _make_grid(self._gridder.xaxis, self._gridder.yaxis)
                self._color_meshes['xy'] = pg.PColorMeshItem(xv, yv, np.log(self._gridder.data.sum(2) + 1))
                self._plots['xy'].addItem(self._color_meshes['xy'])
                try:
                    self._plots['xy'].autoRange()
                except:
                    pass
            except:
                pass

            try:
                xv, zv = _make_grid(self._gridder.xaxis, self._gridder.zaxis)
                self._color_meshes['xz'] = pg.PColorMeshItem(xv, zv, np.log(self._gridder.data.sum(1)+1))
                self._plots['xz'].addItem(self._color_meshes['xz'])
                try:
                    self._plots['xz'].autoRange()
                except:
                    pass
            except:
                pass

            try:
                yv, zv = _make_grid(self._gridder.yaxis, self._gridder.zaxis)
                self._color_meshes['yz'] = pg.PColorMeshItem(yv, zv, np.log(self._gridder.data.sum(0) + 1))
                self._plots['yz'].addItem(self._color_meshes['yz'])
                try:
                    self._plots['yz'].autoRange()
                except:
                    pass
            except:
                pass

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
                       en=self._data_pool.get_entry_value(self._file_name, 'mnchrmtr'),
                       sampleor="y-")

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
                scan_angles[angle] = self._data_pool.get_entry_value(self._file_name, angle) - getattr(self._ui, f'dsb_shift_{angle}').value()
            except KeyError:
                scan_angles[angle] = - getattr(self._ui, f'dsb_shift_{angle}').value()


        qx, qy, qz = hxrd.Ang2Q.area(scan_angles['omega'],
                                     scan_angles['chi'],
                                     scan_angles['phi'],
                                     scan_angles['gamma'],
                                     scan_angles['delta'],
                                     en=self._data_pool.get_entry_value(self._file_name, 'mnchrmtr'),
                                     UB=hxrd._transform.matrix)

        bins = int(self._ui.sb_bin_x.value()), int(self._ui.sb_bin_y.value()), int(self._ui.sb_bin_z.value())
        self._gridder = xu.FuzzyGridder3D(*bins)
        self._gridder(qx, qy, qz, self._data_pool.get_roi_cut(self._file_name, roi_index))


# ----------------------------------------------------------------------
def _make_grid(axis1, axis2):
    one_step1 = axis1[1]-axis1[0]
    axis1 = axis1 - one_step1/2
    axis1 = np.append(axis1, axis1[-1] + one_step1)

    one_step2 = axis2[1]-axis2[0]
    axis2 = axis2 - one_step2/2
    axis2 = np.append(axis2, axis2[-1] + one_step2)

    xv, yv = np.meshgrid(axis1, axis2)

    return xv.T, yv.T

