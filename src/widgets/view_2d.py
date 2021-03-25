# Created by matveyev at 24.03.2021

import pyqtgraph as pg
import numpy as np

from PyQt5 import QtWidgets, QtCore, QtGui

from src.utils.image_marker import ImageMarker
from src.gui.view_2d_ui import Ui_View2D

class View2d(QtWidgets.QWidget):

    # ----------------------------------------------------------------------
    def __init__(self, parent, type, data_pool):
        """
        """
        super(View2d, self).__init__()
        self._ui = Ui_View2D()
        self._ui.setupUi(self)

        self._parent = parent
        self._type = type
        self.data_pool = data_pool

        self._my_files = []
        self.current_file = None

        self._tb_files = QtWidgets.QTabBar(self)
        self._tb_files.setObjectName("tb_main")
        self._tb_files.setTabsClosable(True)
        self._tb_files.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._tb_files.customContextMenuRequested.connect(self._move_tab_menu)
        self._ui.v_layout.insertWidget(0, self._tb_files, 0)

        self._main_plot = pg.PlotItem()
        self._main_plot.showAxis('left', False)
        self._main_plot.showAxis('bottom', False)
        self._main_plot.setMenuEnabled(False)

        self._ui.gv_main.setStyleSheet("")
        self._ui.gv_main.setBackground('w')
        self._ui.gv_main.setObjectName("gvMain")

        self._ui.gv_main.setCentralItem(self._main_plot)
        self._ui.gv_main.setRenderHints(self._ui.gv_main.renderHints())

        self._main_plot.getViewBox().setAspectLocked()

        self.plot_2d = pg.ImageItem()
        self._main_plot.addItem(self.plot_2d)

        self._center_cross = ImageMarker(0, 0, self._main_plot)

        self._rois = {}

        self._tb_files.tabCloseRequested.connect(self._close_file)
        self._tb_files.currentChanged.connect(self._switch_file)

        self._main_plot.scene().sigMouseMoved.connect(self._mouse_moved)
        self._main_plot.scene().sigMouseClicked.connect(self._mouse_clicked)
        self._main_plot.scene().sigMouseHover.connect(self._mouse_hover)

        self._main_plot.getViewBox().sigRangeChanged.connect(self._range_changed)

    # ----------------------------------------------------------------------
    def _move_tab_menu(self, pos):

        if self._type == 'main' and len(self._my_files) == 1:
            return

        menu = QtWidgets.QMenu()
        if self._type == 'main':
            action = QtWidgets.QAction('Move to compare')
        else:
            action = QtWidgets.QAction('Move to main')

        menu.addAction(action)

        action = menu.exec_(self.mapToGlobal(pos))

        if action:
            index = self._tb_files.currentIndex()
            self._parent.add_file(self._my_files[index], self._type)
            del self._my_files[index]
            self.current_file = None
            self._tb_files.removeTab(index)

            if self._type == 'second' and len(self._my_files) == 0:
                self.hide()

    # ----------------------------------------------------------------------
    def _range_changed(self, view_box):
        self._parent.new_view_box(self._type, view_box)

    # ----------------------------------------------------------------------
    def new_view_box(self, view_box):
        self._main_plot.getViewBox().sigRangeChanged.disconnect()
        self._main_plot.getViewBox().setRange(view_box.viewRect())
        self._main_plot.getViewBox().sigRangeChanged.connect(self._range_changed)

    # ----------------------------------------------------------------------
    def add_file(self, file_name):
        new_index = self._tb_files.count()
        self._my_files.insert(new_index, file_name)
        self._tb_files.insertTab(new_index, '{}'.format(file_name))
        self._tb_files.setCurrentIndex(new_index)

        if self._type == 'second':
            self.show()

    # ----------------------------------------------------------------------
    def new_lookup_table(self):
        if self.plot_2d.image is not None:
            self.plot_2d.setLookupTable(self._parent.hist.item.getLookupTable(self.plot_2d.image))

    # ----------------------------------------------------------------------
    def new_levels(self):
        self.plot_2d.setLevels(self._parent.hist.item.getLevels())

    # ----------------------------------------------------------------------
    def _close_file(self, index):
        self.data_pool.remove_file(self._my_files[index])
        del self._my_files[index]
        self.current_file = None
        self._tb_files.removeTab(index)

        if self._type == 'second' and len(self._my_files) == 0:
            self.hide()

    # ----------------------------------------------------------------------
    def add_roi(self,idx):
        roi_id = self.data_pool.get_roi_name(idx)
        self._rois[idx] = (pg.RectROI([0, 0], [1, 1], pen=(0, 9)),
                           pg.TextItem(text='ROI {}'.format(roi_id), color=(255, 0, 0)),
                           idx)

        self._rois[idx][1].setFont(QtGui.QFont("Arial", 10))
        self._rois[idx][0].sigRegionChanged.connect(lambda rect, id=idx: self._roi_changed(id, rect))
        self._main_plot.addItem(self._rois[idx][0])
        self._main_plot.addItem(self._rois[idx][1])

    # ----------------------------------------------------------------------
    def delete_roi(self, idx):
        self._main_plot.removeItem(self._rois[idx][0])
        self._main_plot.removeItem(self._rois[idx][1])
        del self._rois[idx]

        for _, label, my_id in self._rois.values():
            label.setText('ROI {}'.format(self.data_pool.get_roi_name(my_id)))

    # ----------------------------------------------------------------------
    def new_roi_range(self, roi_ind):
        self._rois[roi_ind][0].sigRegionChanged.disconnect()

        if self._parent.current_axes['x'] == self.data_pool.get_roi_param(roi_ind, 'axis'):
            x_pos = self.data_pool.axes_limits[self._parent.current_axes['x']][0]
            x_width = self.data_pool.axes_limits[self._parent.current_axes['x']][1] - \
                        self.data_pool.axes_limits[self._parent.current_axes['x']][0]

        elif self._parent.current_axes['x'] == self.data_pool.get_roi_param(roi_ind, 'roi_1_axis'):
            x_pos = self.data_pool.get_roi_param(roi_ind, 'roi_1_pos')
            x_width = self.data_pool.get_roi_param(roi_ind, 'roi_1_width')

        else:
            x_pos = self.data_pool.get_roi_param(roi_ind, 'roi_2_pos')
            x_width = self.data_pool.get_roi_param(roi_ind, 'roi_2_width')

        if self._parent.current_axes['y'] == self.data_pool.get_roi_param(roi_ind, 'axis'):
            y_pos = self.data_pool.axes_limits[self._parent.current_axes['y']][0]
            y_width = self.data_pool.axes_limits[self._parent.current_axes['y']][1] - \
                        self.data_pool.axes_limits[self._parent.current_axes['y']][0]

        elif self._parent.current_axes['y'] == self.data_pool.get_roi_param(roi_ind, 'roi_1_axis'):
            y_pos = self.data_pool.get_roi_param(roi_ind, 'roi_1_pos')
            y_width = self.data_pool.get_roi_param(roi_ind, 'roi_1_width')

        else:
            y_pos = self.data_pool.get_roi_param(roi_ind, 'roi_2_pos')
            y_width = self.data_pool.get_roi_param(roi_ind, 'roi_2_width')

        self._rois[roi_ind][0].setPos([x_pos, y_pos])
        self._rois[roi_ind][0].setSize([x_width, y_width])
        self._rois[roi_ind][1].setPos(x_pos + x_width, y_pos + y_width)
        self._rois[roi_ind][0].sigRegionChanged.connect(lambda rect, idx=roi_ind: self._roi_changed(idx, rect))

    # ----------------------------------------------------------------------
    def _roi_changed(self, roi_ind, rect):
        if self._parent.current_axes['x'] == self.data_pool.get_roi_param(roi_ind, 'axis'):
            x_axis = 0
        elif self._parent.current_axes['x'] == self.data_pool.get_roi_param(roi_ind, 'roi_1_axis'):
            x_axis = 1
        else:
            x_axis = 2

        if self._parent.current_axes['y'] == self.data_pool.get_roi_param(roi_ind, 'axis'):
            y_axis = 0
        elif self._parent.current_axes['y'] == self.data_pool.get_roi_param(roi_ind, 'roi_1_axis'):
            y_axis = 1
        else:
            y_axis = 2

        pos, size = rect.pos(), rect.size()
        accepted_x_pos = self.data_pool.roi_parameter_changed(roi_ind, x_axis, 'pos', int(pos.x()))
        accepted_x_width = self.data_pool.roi_parameter_changed(roi_ind, x_axis, 'width', int(size.x()))

        accepted_y_pos = self.data_pool.roi_parameter_changed(roi_ind, y_axis, 'pos', int(pos.y()))
        accepted_y_width = self.data_pool.roi_parameter_changed(roi_ind, y_axis, 'width', int(size.y()))

        self._rois[roi_ind][0].sigRegionChanged.disconnect()
        self._rois[roi_ind][0].setPos([accepted_x_pos, accepted_y_pos])
        self._rois[roi_ind][0].setSize([accepted_x_width, accepted_y_width])

        self._rois[roi_ind][1].setPos(accepted_x_pos + accepted_x_width, accepted_y_pos + accepted_y_width)
        self._rois[roi_ind][0].sigRegionChanged.connect(lambda rect, id=roi_ind: self._roi_changed(roi_ind, rect))

    # ----------------------------------------------------------------------
    def new_axes(self):
        for idx in range(len(self._rois)):
            self.new_roi_range(idx)

    # ----------------------------------------------------------------------
    def _mouse_moved(self, pos):
        if self._main_plot.sceneBoundingRect().contains(pos):
            pos = self._main_plot.vb.mapSceneToView(pos)

            self._center_cross.setPos(pos)

            if self.current_file is None:
                return

            x_name, x_value = self.data_pool.get_value_at_point(self.current_file, self._parent.current_axes['x'],
                                                                int(pos.x()))
            y_name, y_value = self.data_pool.get_value_at_point(self.current_file, self._parent.current_axes['y'],
                                                                int(pos.y()))

            self._parent.new_coordinate(self._type, x_name, x_value, y_name, y_value, pos)

    # ----------------------------------------------------------------------
    def move_marker(self, pos):
        self._center_cross.setPos(pos)

    # ----------------------------------------------------------------------
    def _mouse_clicked(self, event):
        """
        """
        if event.double():
            try:
                self._main_plot.autoRange()
            except:
                pass

    # ----------------------------------------------------------------------
    def _mouse_hover(self, event):
        pass

    # ----------------------------------------------------------------------
    def _switch_file(self, index):

        z_value = None
        if self.current_file is not None:
            _, z_value = self.data_pool.get_value_at_point(self.current_file, self._parent.current_axes['z'],
                                                           self._parent.current_frame)

        if index > -1:
            self.current_file = self._my_files[index]
        else:
            self.current_file = None

        if self._type == 'main':
            self._parent.new_main_file(z_value)

    # ----------------------------------------------------------------------
    def update_image(self):

        if self.current_file is None:
            return

        data_to_display = self.data_pool.get_2d_cut(self.current_file, self._parent.current_axes['z'],
                                                    self._parent.current_frame, self._parent.current_axes['x'],
                                                    self._parent.current_axes['y'])

        if self._parent.level_mode == 'log':
            data_to_display = np.log(data_to_display + 1)

        self.plot_2d.setImage(data_to_display, autoLevels=self._parent.auto_levels)



