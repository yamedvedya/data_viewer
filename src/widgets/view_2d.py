# Created by matveyev at 24.03.2021

import pyqtgraph as pg
import numpy as np

from distutils.util import strtobool

from PyQt5 import QtWidgets, QtCore, QtGui

from src.utils.image_marker import ImageMarker
from src.gui.view_2d_ui import Ui_View2D


class View2d(QtWidgets.QWidget):

    # ----------------------------------------------------------------------
    def __init__(self, frame_viewer, type, data_pool):
        """
        """
        super(View2d, self).__init__()
        self._ui = Ui_View2D()
        self._ui.setupUi(self)

        self._frame_viewer = frame_viewer
        self._type = type
        self.data_pool = data_pool

        self._my_files = []
        self.current_file = None
        self.previous_file = None

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
        self._main_plot.getViewBox().setMouseMode(pg.ViewBox.RectMode)

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
    def set_settings(self, settings):
        self._main_plot.showAxis('left', strtobool(settings['display_axes']))
        self._main_plot.showAxis('bottom', strtobool(settings['display_axes']))
        self._main_plot.showLabel('left', strtobool(settings['display_axes_titles']))
        self._main_plot.showLabel('bottom', strtobool(settings['display_axes_titles']))

    # ----------------------------------------------------------------------
    def block_signals(self, flag):
        self._tb_files.blockSignals(flag)
        if flag:
            self._main_plot.scene().sigMouseMoved.disconnect()
            self._main_plot.scene().sigMouseClicked.disconnect()
            self._main_plot.scene().sigMouseHover.disconnect()

            self._main_plot.getViewBox().sigRangeChanged.disconnect()
        else:
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
            self._frame_viewer.add_file(self._my_files[index], self._type)
            del self._my_files[index]
            self.current_file = None
            self._tb_files.removeTab(index)

            if len(self._my_files) == 0:
                self.hide()

    # ----------------------------------------------------------------------
    def _range_changed(self, view_box):
        self._frame_viewer.new_view_box(self._type, view_box)

    # ----------------------------------------------------------------------
    def new_view_box(self, view_box):
        self._main_plot.getViewBox().sigRangeChanged.disconnect()
        self._main_plot.getViewBox().setRange(view_box.viewRect())
        self._main_plot.getViewBox().sigRangeChanged.connect(self._range_changed)

    # ----------------------------------------------------------------------
    def add_file(self, file_name):

        self.block_signals(True)

        new_index = self._tb_files.count()
        self._my_files.insert(new_index, file_name)
        self._tb_files.insertTab(new_index, '{}'.format(file_name))
        self._tb_files.setCurrentIndex(new_index)
        self.current_file = file_name

        self.show()

        self.block_signals(False)

    # ----------------------------------------------------------------------
    def new_lookup_table(self):
        if self.plot_2d.image is not None:
            self.plot_2d.setLookupTable(self._frame_viewer.hist.item.getLookupTable(self.plot_2d.image))

    # ----------------------------------------------------------------------
    def new_levels(self):
        self.plot_2d.setLevels(self._frame_viewer.hist.item.getLevels())

    # ----------------------------------------------------------------------
    def _close_file(self, index):
        self.data_pool.remove_file(self._my_files[index])
        del self._my_files[index]
        self.current_file = None
        self._tb_files.removeTab(index)

        if len(self._my_files) == 0:
            self.hide()

    # ----------------------------------------------------------------------
    def file_closed_by_pool(self, file_name):
        if file_name in self._my_files:
            index = self._my_files.index(file_name)
            del self._my_files[index]
            if self.current_file == file_name:
                self.current_file = None
            self._tb_files.removeTab(index)

            if len(self._my_files) == 0:
                self.hide()

    # ----------------------------------------------------------------------
    def add_roi(self,idx):
        roi_id = self.data_pool.get_roi_index(idx)
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
            label.setText('ROI {}'.format(self.data_pool.get_roi_index(my_id)))

    # ----------------------------------------------------------------------
    def roi_changed(self, roi_ind):
        self._rois[roi_ind][0].sigRegionChanged.disconnect()

        current_axes = self._frame_viewer.get_current_axes()

        x_pos, y_pos = 0, 0
        x_width, y_width = 1, 1

        if current_axes['x'] == self.data_pool.get_roi_param(roi_ind, 'axis_0'):
            x_pos = self.data_pool.axes_limits[current_axes['x']][0]
            x_width = self.data_pool.axes_limits[current_axes['x']][1] - self.data_pool.axes_limits[current_axes['x']][0]
        else:
            axis = 1
            while axis < 100:
                if current_axes['x'] == self.data_pool.get_roi_param(roi_ind, f'axis_{axis}'):
                    x_pos = self.data_pool.get_roi_param(roi_ind, f'axis_{axis}_pos')
                    x_width = self.data_pool.get_roi_param(roi_ind, f'axis_{axis}_width')
                    break
                axis += 1

        if current_axes['y'] == self.data_pool.get_roi_param(roi_ind, 'axis_0'):
            y_pos = self.data_pool.axes_limits[current_axes['y']][0]
            y_width = self.data_pool.axes_limits[current_axes['y']][1] - self.data_pool.axes_limits[current_axes['y']][0]
        else:
            axis = 1
            while axis < 100:
                if current_axes['y'] == self.data_pool.get_roi_param(roi_ind, f'axis_{axis}'):
                    y_pos = self.data_pool.get_roi_param(roi_ind, f'axis_{axis}_pos')
                    y_width = self.data_pool.get_roi_param(roi_ind, f'axis_{axis}_width')
                    break
                axis += 1

        self._rois[roi_ind][0].setPos([x_pos, y_pos])
        self._rois[roi_ind][0].setSize([x_width, y_width])
        self._rois[roi_ind][1].setPos(x_pos + x_width, y_pos + y_width)
        self._rois[roi_ind][0].sigRegionChanged.connect(lambda rect, idx=roi_ind: self._roi_changed(idx, rect))

    # ----------------------------------------------------------------------
    def _roi_changed(self, roi_ind, rect):

        current_axes = self._frame_viewer.get_current_axes()

        pos, size = rect.pos(), rect.size()
        accepted_x_pos = self.data_pool.roi_parameter_changed(roi_ind, current_axes['x'], 'pos', int(pos.x()))
        accepted_x_width = self.data_pool.roi_parameter_changed(roi_ind, current_axes['x'], 'width', int(size.x()))

        accepted_y_pos = self.data_pool.roi_parameter_changed(roi_ind, current_axes['y'], 'pos', int(pos.y()))
        accepted_y_width = self.data_pool.roi_parameter_changed(roi_ind, current_axes['y'], 'width', int(size.y()))

        self._rois[roi_ind][0].sigRegionChanged.disconnect()
        self._rois[roi_ind][0].setPos([accepted_x_pos, accepted_y_pos])
        self._rois[roi_ind][0].setSize([accepted_x_width, accepted_y_width])

        self._rois[roi_ind][1].setPos(accepted_x_pos + accepted_x_width, accepted_y_pos + accepted_y_width)
        self._rois[roi_ind][0].sigRegionChanged.connect(lambda rect, id=roi_ind: self._roi_changed(roi_ind, rect))

    # ----------------------------------------------------------------------
    def new_axes(self, labels):

        self._main_plot.setLabel('left', labels[0])
        self._main_plot.setLabel('bottom', labels[1])

        for idx in range(len(self._rois)):
            self.roi_changed(idx)

    # ----------------------------------------------------------------------
    def _mouse_moved(self, pos):

        if self._main_plot.sceneBoundingRect().contains(pos):
            pos = self._main_plot.vb.mapSceneToView(pos)

            self._center_cross.setPos(pos)

            if self.current_file is None:
                return

            current_axes = self._frame_viewer.get_current_axes()

            x_name, x_value = self.data_pool.get_value_for_frame(self.current_file, current_axes['x'], int(pos.x()))
            y_name, y_value = self.data_pool.get_value_for_frame(self.current_file, current_axes['y'], int(pos.y()))

            self._frame_viewer.new_coordinate(self._type, x_name, x_value, y_name, y_value, pos)

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

        self.previous_file = self.current_file

        if index > -1:
            self.current_file = self._my_files[index]
        else:
            self.current_file = None

        if self._type == 'main':
            self._frame_viewer.new_main_file()

    # ----------------------------------------------------------------------
    def update_image(self, frame_sect, section):

        if self.current_file is None:
            self.plot_2d.clear()
            return

        data_to_display = self.data_pool.get_2d_picture(self.current_file, frame_sect, section)

        if data_to_display is None:
            self.plot_2d.clear()
            return

        if self._frame_viewer.level_mode == 'log':
            data_to_display = np.log(data_to_display + 1)

        self.plot_2d.setImage(data_to_display, autoLevels=self._frame_viewer.auto_levels)

        for ind in range(len(self._rois)):
            self.roi_changed(ind)



