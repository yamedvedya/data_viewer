# Created by matveyev at 15.02.2021

WIDGET_NAME = 'FileInspector'
color_maps = ('grey', 'thermal', 'bipolar')

import pyqtgraph as pg
import numpy as np

from PyQt5 import QtWidgets, QtCore, QtGui
from pyqtgraph.graphicsItems.GradientEditorItem import Gradients
from src.gui.files_inspector_ui import Ui_FilesInspector

from src.utils.utils import refresh_combo_box

# ----------------------------------------------------------------------
class FilesInspector(QtWidgets.QWidget):
    """
    """

    section_names = {'real': {'Y vs. X': {'x': 0, 'y': 1, 'z': 2},
                              'X vs. Y': {'x': 1, 'y': 0, 'z': 2},
                              'Z vs. X': {'x': 0, 'y': 2, 'z': 1},
                              'X vs. Z': {'x': 2, 'y': 0, 'z': 1},
                              'Z vs. Y': {'x': 1, 'y': 2, 'z': 0},
                              'Y vs. Z': {'x': 2, 'y': 1, 'z': 0}}}

    # ----------------------------------------------------------------------
    def __init__(self, parent, data_pool):
        """
        """
        super(FilesInspector, self).__init__()
        self._ui = Ui_FilesInspector()
        self._ui.setupUi(self)

        self._tb_files = QtWidgets.QTabBar(self)
        self._tb_files.setObjectName("tb_files")
        self._tb_files.setTabsClosable(True)
        self._ui.v_layout.insertWidget(0, self._tb_files, 0)

        self._status_bar = QtWidgets.QStatusBar(self)
        self._ui.verticalLayout.addWidget(self._status_bar, 0)

        self._coordinate_label = QtWidgets.QLabel("")
        self._status_bar.addPermanentWidget(self._coordinate_label)

        self._opened_files = []

        self._main_plot = pg.PlotItem()
        # self._main_plot.showGrid(True, True)
        self._main_plot.showAxis('left', False)
        self._main_plot.showAxis('bottom', False)
        self._main_plot.setMenuEnabled(False)

        self._ui.gv_main.setStyleSheet("")
        self._ui.gv_main.setBackground('w')
        self._ui.gv_main.setObjectName("gvMain")

        self._ui.gv_main.setCentralItem(self._main_plot)
        self._ui.gv_main.setRenderHints(self._ui.gv_main.renderHints())

        self._main_plot.getViewBox().setAspectLocked()

        self.current_frame = 0
        self.current_file = None
        self.level_mode = 'lin'
        self.auto_levels = True
        self.max_frame = 0

        self._plot_2d = pg.ImageItem()
        self._plot_2d.setLookupTable(pg.ColorMap(*zip(*Gradients[color_maps[0]]["ticks"])).getLookupTable())
        self._main_plot.addItem(self._plot_2d)

        self._center_cross = ImageMarker(0, 0, self._main_plot)

        self._rois = {}

        self._hist = pg.HistogramLUTWidget(self)
        self._hist.setBackground('w')
        self._hist.item.setImageItem(self._plot_2d)
        self._ui.g_layout.addWidget(self._hist, 6, 0, 1, 2)

        self._ui.cb_color_map.addItems(color_maps)

        self._parent = parent
        self.data_pool = data_pool

        self._ui.cb_section.addItems(list(self.section_names[self.data_pool.space].keys()))
        self._ui.cb_section.currentTextChanged.connect(self._new_axes)

        self.current_axes = self.section_names[self.data_pool.space][str(self._ui.cb_section.currentText())]

        self._ui.sl_frame.valueChanged.connect(lambda value: self._display_new_frame(value))

        self._ui.but_first.clicked.connect(lambda: self._switch_frame('first'))
        self._ui.but_previous.clicked.connect(lambda: self._switch_frame('previous'))
        self._ui.but_next.clicked.connect(lambda: self._switch_frame('next'))
        self._ui.but_last.clicked.connect(lambda: self._switch_frame('last'))

        self._tb_files.tabCloseRequested.connect(self._close_file)
        self._tb_files.currentChanged.connect(self._switch_file)

        self._main_plot.scene().sigMouseMoved.connect(self._mouse_moved)
        self._main_plot.scene().sigMouseClicked.connect(self._mouse_clicked)
        self._main_plot.scene().sigMouseHover.connect(self._mouse_hover)

        self._hist.scene().sigMouseClicked.connect(self._hist_mouse_clicked)
        self._hist.item.sigLevelsChanged.connect(self.switch_off_auto_levels)
        self._ui.chk_auto_levels.clicked.connect(lambda state: self._toggle_auto_levels(state))

        self._ui.bg_level.buttonClicked.connect(lambda button: self._change_level_mode(button))
        self._ui.cb_color_map.currentTextChanged.connect(lambda map: self._change_color_map(map))

    # ----------------------------------------------------------------------
    def add_file(self, file_name):
        new_index = self._tb_files.count()
        self._opened_files.insert(0, file_name)
        self._tb_files.insertTab(new_index, '{}'.format(file_name))
        self._tb_files.setCurrentIndex(new_index)

    # ----------------------------------------------------------------------
    def new_roi_range(self, roi_ind):
        self._rois[roi_ind][0].sigRegionChanged.disconnect()

        if self.current_axes['x'] == self.data_pool.get_roi_param(roi_ind, 'axis'):
            x_pos = self.data_pool.axes_limits[self.current_axes['x']][0]
            x_width = self.data_pool.axes_limits[self.current_axes['x']][1] - \
                        self.data_pool.axes_limits[self.current_axes['x']][0]

        elif self.current_axes['x'] == self.data_pool.get_roi_param(roi_ind, 'roi_1_axis'):
            x_pos = self.data_pool.get_roi_param(roi_ind, 'roi_1_pos')
            x_width = self.data_pool.get_roi_param(roi_ind, 'roi_1_width')

        else:
            x_pos = self.data_pool.get_roi_param(roi_ind, 'roi_2_pos')
            x_width = self.data_pool.get_roi_param(roi_ind, 'roi_2_width')

        if self.current_axes['y'] == self.data_pool.get_roi_param(roi_ind, 'axis'):
            y_pos = self.data_pool.axes_limits[self.current_axes['y']][0]
            y_width = self.data_pool.axes_limits[self.current_axes['y']][1] - \
                        self.data_pool.axes_limits[self.current_axes['y']][0]

        elif self.current_axes['y'] == self.data_pool.get_roi_param(roi_ind, 'roi_1_axis'):
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
    def add_roi(self, idx):
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
    def _roi_changed(self, roi_ind, rect):
        if self.current_axes['x'] == self.data_pool.get_roi_param(roi_ind, 'axis'):
            x_axis = 0
        elif self.current_axes['x'] == self.data_pool.get_roi_param(roi_ind, 'roi_1_axis'):
            x_axis = 1
        else:
            x_axis = 2

        if self.current_axes['y'] == self.data_pool.get_roi_param(roi_ind, 'axis'):
            y_axis = 0
        elif self.current_axes['y'] == self.data_pool.get_roi_param(roi_ind, 'roi_1_axis'):
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
    def _new_axes(self, text):
        self.current_axes = self.section_names[self.data_pool.space][str(text)]
        self._setup_limits()
        self.display_z_value()
        self._update_image()
        for idx, _ in range(len(self._rois)):
            self.new_roi_range(idx)

    # ----------------------------------------------------------------------
    def _change_color_map(self, map):
        self._plot_2d.setLookupTable(pg.ColorMap(*zip(*Gradients[map]["ticks"])).getLookupTable())

    # ----------------------------------------------------------------------
    def switch_off_auto_levels(self):
        self.auto_levels = False
        self._ui.chk_auto_levels.setChecked(False)

    # ----------------------------------------------------------------------
    def _toggle_auto_levels(self, state):
        self.auto_levels = state
        self._update_image()
        self._ui.chk_auto_levels.setChecked(state)

    # ----------------------------------------------------------------------
    def _change_level_mode(self, button):
        if button == self._ui.rb_lin_level:
            self.level_mode = 'lin'
        else:
            self.level_mode = 'log'

        self._update_image()

    # ----------------------------------------------------------------------
    def _mouse_moved(self, pos):
        if self._main_plot.sceneBoundingRect().contains(pos):
            pos = self._main_plot.vb.mapSceneToView(pos)

            self._center_cross.setPos(pos)

            if self.current_file is None:
                return

            x_name, x_value = self.data_pool.get_value_at_point(self.current_file, self.current_axes['x'], int(pos.x()))
            y_name, y_value = self.data_pool.get_value_at_point(self.current_file, self.current_axes['y'], int(pos.y()))

            self._coordinate_label.setText('{}: {:3f}, {}: {:.3f}'.format(x_name, x_value, y_name, y_value))

    # ----------------------------------------------------------------------
    def _hist_mouse_clicked(self, event):
        if event.double():
            self._toggle_auto_levels(True)

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
    def _close_file(self, index):
        self.data_pool.remove_file(self._opened_files[index])
        del self._opened_files[index]
        self._tb_files.removeTab(index)

    # ----------------------------------------------------------------------
    def _update_image(self):
        if self.current_file is None:
            return

        data_to_display = self.data_pool.get_2d_cut(self.current_file, self.current_axes['z'], self.current_frame,
                                                    self.current_axes['x'], self.current_axes['y'])

        if self.level_mode == 'log':
            data_to_display = np.log(data_to_display + 1)

        self._hist.item.sigLevelsChanged.disconnect()
        self._plot_2d.setImage(data_to_display, autoLevels=self.auto_levels)
        self._hist.item.sigLevelsChanged.connect(self.switch_off_auto_levels)

    # ----------------------------------------------------------------------
    def _setup_limits(self):
        if self.current_file is None:
            return

        self.max_frame = self.data_pool.get_max_frame(self.current_file, self.current_axes['z'])
        self._ui.sl_frame.setMaximum(self.max_frame)

    # ----------------------------------------------------------------------
    def _switch_file(self, index):
        z_value = None
        if self.current_file is not None:
            _, z_value = self.data_pool.get_value_at_point(self.current_file, self.current_axes['z'],
                                                           self.current_frame)

        self.current_file = self._opened_files[index]

        axes_names = self.data_pool.file_axes_caption(self.current_file)
        self._ui.lb_axes_captions.setText('X axis: {}, Y axis: {}, Z axis: {}'.format(axes_names[0],
                                                                                      axes_names[1],
                                                                                      axes_names[2]))

        self._setup_limits()
        if z_value is not None:
            self.current_frame = self.data_pool.frame_for_point(self.current_file, self.current_axes['z'], z_value)
            self._ui.sl_frame.setValue(self.current_frame)

        self.display_z_value()
        self._update_image()

    # ----------------------------------------------------------------------
    def display_z_value(self):
        if self.current_file is None:
            return

        z_name, z_value = self.data_pool.get_value_at_point(self.current_file, self.current_axes['z'],
                                                            self.current_frame)
        self._ui.lb_value.setText('{}: {:3f}'.format(z_name, z_value))

    # ----------------------------------------------------------------------
    def _display_new_frame(self, frame):
        self._block_signals(True)
        self.current_frame = min(max(frame, 0), self.max_frame)
        self._ui.sl_frame.setValue(self.current_frame)
        self.display_z_value()
        self._block_signals(False)
        self._update_image()

    # ----------------------------------------------------------------------
    def _switch_frame(self, type):
        if type == 'first':
            self._display_new_frame(0)
        elif type == 'previous':
            self._display_new_frame(self.current_frame - 1)
        elif type == 'next':
            self._display_new_frame(self.current_frame + 1)
        elif type == 'last':
            self._display_new_frame(self.max_frame)

    # ----------------------------------------------------------------------
    def _block_signals(self, flag):
        self._ui.sl_frame.blockSignals(flag)
        self._ui.cb_section.blockSignals(flag)
        self._tb_files.blockSignals(flag)

    # ----------------------------------------------------------------------
    def load_ui_settings(self, settings):
        try:
            self.restoreGeometry(settings.value("{}/geometry".format(WIDGET_NAME)))
        except Exception as err:
            self._parent.log.error("{} : cannot restore geometry: {}".format(WIDGET_NAME, err))

    # ----------------------------------------------------------------------
    def save_ui_settings(self, settings):
        settings.setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())


# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
class ImageMarker(object):
    """Infinite lines cross
    """

    # ----------------------------------------------------------------------
    def __init__(self, x, y, image_view):
        super(ImageMarker, self).__init__()

        self.image_view = image_view

        pen = pg.mkPen('y', width=1, style=QtCore.Qt.DotLine)

        self._marker_v = pg.InfiniteLine(pos=x, pen=pen)
        self.image_view.addItem(self._marker_v, ignoreBounds=True)

        self._marker_h = pg.InfiniteLine(pos=y, angle=0, pen=pen)
        self.image_view.addItem(self._marker_h, ignoreBounds=True)

    # ----------------------------------------------------------------------
    def setPos(self, pos):
        """
        """
        self._marker_v.setPos(pos.x())
        self._marker_h.setPos(pos.y())

    # ----------------------------------------------------------------------
    def pos(self):
        """
        """
        return self._marker_v.pos().x(), self._marker_h.pos().y()

    # ----------------------------------------------------------------------
    def setVisible(self, flag):
        """
        """
        self._marker_v.setVisible(flag)
        self._marker_h.setVisible(flag)

    # ----------------------------------------------------------------------
    def visible(self):
        """
        """
        return self._marker_v.isVisible() and self._marker_h.isVisible()

    # ----------------------------------------------------------------------
    def delete_me(self):
        self.image_view.removeItem(self._marker_h)
        self.image_view.removeItem(self._marker_v)