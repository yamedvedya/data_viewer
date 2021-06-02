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

        self._convert()
        if self._gridder is not None:
            for sect, coor in (('xy', 2),
                               ('xz', 1),
                               ('yz', 0)):
                try:
                    axis1, axis2 = _make_grid(getattr(self._gridder,f'{sect[0]}axis'),
                                              getattr(self._gridder,f'{sect[1]}axis'))
                    if self._color_meshes[sect] is None:
                        self._color_meshes[sect] = pg.PColorMeshItem(axis1, axis2, np.log(self._gridder.data.sum(coor) + 1))
                        self._plots[sect].addItem(self._color_meshes[sect])
                    else:
                        self._color_meshes[sect].setData(axis1, axis2, np.log(self._gridder.data.sum(coor) + 1))
                    try:
                        self._plots[sect].autoRange()
                    except:
                        pass
                except:
                    pass

    # ----------------------------------------------------------------------
    def _save(self):
        if self._gridder is None:
            self._convert()

        self._data_pool.save_converted(self._file_name, self._gridder)

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
                       en=int(self._data_pool.get_entry_value(self._file_name, 'mnchrmtr')),
                       sampleor="y-")

        hxrd.Ang2Q.init_area('y+',
                             'z-',
                             cch1=int(self._ui.sb_cen_x.value()),
                             cch2=int(self._ui.sb_cen_y.value()),
                             Nch1=int(self._data_pool.get_roi_param(roi_index, 'roi_2_width')),
                             Nch2=int(self._data_pool.get_roi_param(roi_index, 'roi_1_width')),
                             pwidth1=self._ui.dsb_size_x.value()*1e-6,
                             pwidth2=self._ui.dsb_size_y.value()*1e-6,
                             distance=self._ui.dsb_det_d.value(),
                             detrot=self._ui.dsb_det_r.value(),
                             tiltazimuth=self._ui.dsb_det_rt.value(),
                             tilt=self._ui.dsb_det_t.value())

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

