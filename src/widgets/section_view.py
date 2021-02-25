# Created by matveyev at 15.02.2021

WIDGET_NAME = 'SectionView'

import pyqtgraph as pg
import icons_rc

from PyQt5 import QtWidgets, QtCore, QtGui
from src.gui.section_viewer_ui import Ui_SectionView

from src.utils.section_plot import SectionPlot
from src.utils.cursors import CrosshairCursor, Ruler
from src.utils.range_slider import RangeSlider
from src.utils.legend_item import addLegend

import src.lookandfeel as lookandfeel

# ----------------------------------------------------------------------
class SectionView(QtWidgets.QWidget):
    """
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent, data_pool, my_id):
        """
        """
        super(SectionView, self).__init__()
        self._ui = Ui_SectionView()
        self._ui.setupUi(self)
        self._init_tool_bar()

        self.parent = parent
        self.data_pool = data_pool
        self.my_id = my_id

        self.sld_1 = RangeSlider(QtCore.Qt.Horizontal, self)
        self._ui.v_layout.insertWidget(7, self.sld_1, 0)
        self.sld_2 = RangeSlider(QtCore.Qt.Horizontal, self)
        self._ui.v_layout.insertWidget(15, self.sld_2, 0)

        self._main_plot = pg.PlotItem()
        self._main_plot.showGrid(True, True)
        self._main_plot.setMenuEnabled(False)

        self._ui.gv_main.setStyleSheet("")
        self._ui.gv_main.setBackground('w')
        self._ui.gv_main.setObjectName("gvMain")

        self._ui.gv_main.setCentralItem(self._main_plot)
        self._ui.gv_main.setRenderHints(self._ui.gv_main.renderHints())

        self.scanplot_items = {}
        self._normalized = False

        self._cross = CrosshairCursor(self._main_plot)
        self._cross.setVisible(False)
        self._ruler = Ruler(self._main_plot)
        self._ruler.setEnabled(False)

        self.range_line_from = pg.InfiniteLine(angle=90, movable=False)
        self.range_line_from.sigPositionChanged.connect(
            lambda: self._ui.dsp_cut_from.setValue(self.range_line_from.value()))
        self.range_line_to = pg.InfiniteLine(angle=90, movable=False)
        self.range_line_to.sigPositionChanged.connect(
            lambda: self._ui.dsp_cut_to.setValue(self.range_line_to.value()))

        self._main_plot.addItem(self.range_line_from, ignoreBounds=True)
        self._main_plot.addItem(self.range_line_to, ignoreBounds=True)

        self._legend = addLegend(self._main_plot)
        self._legend.hide()

        self.fit_style_cnt = 0

        self._ui.cb_section_axis.addItems(self.data_pool.get_axes())
        self._ui.cb_section_axis.setCurrentIndex(self.data_pool.get_roi_param(self.my_id, 'axis'))

        self._ui.lb_axis_1.setText('{} ROI'.format(self.data_pool.get_axes()
                                                   [self.data_pool.get_roi_param(self.my_id, 'roi_1_axis')]))
        self._ui.lb_axis_2.setText('{} ROI'.format(self.data_pool.get_axes()
                                                   [self.data_pool.get_roi_param(self.my_id, 'roi_2_axis')]))

        self._ui.cb_section_axis.currentIndexChanged.connect(self._set_new_section_axis)

        for axis in [1, 2]:
            for param in ['pos', 'width']:
                getattr(self._ui, 'sb_{}_{}'.format(axis, param)).valueChanged.connect(
                    lambda value, a=axis, p=param: self._roi_value_changed(a, p, int(value)))

        self._main_plot.scene().sigMouseMoved.connect(self._mouse_moved)
        self._main_plot.scene().sigMouseClicked.connect(self._mouse_clicked)
        # self._main_plot.scene().sigMouseHover.connect(self._mouse_hover)

        self._ui.dsp_cut_from.valueChanged.connect(lambda value, x='from': self._check_cut(x, value))
        self._ui.dsp_cut_to.valueChanged.connect(lambda value, x='to': self._check_cut(x, value))
        self._ui.bg_cut_range.buttonClicked.connect(lambda selection: self._cut_range(selection))
        self._main_plot.sigXRangeChanged.connect(self._new_range)

    # ----------------------------------------------------------------------
    def refresh_name(self):
        return self.data_pool.get_roi_name(self.my_id)

    # ----------------------------------------------------------------------
    def new_roi_range(self):
        self._block_signals(True)

        self._ui.sb_1_pos.setValue(self.data_pool.get_roi_param(self.my_id, 'roi_1_pos'))
        self._ui.sb_1_width.setValue(self.data_pool.get_roi_param(self.my_id, 'roi_1_width'))

        self._ui.sb_2_pos.setValue(self.data_pool.get_roi_param(self.my_id, 'roi_2_pos'))
        self._ui.sb_2_width.setValue(self.data_pool.get_roi_param(self.my_id, 'roi_2_width'))

        self._block_signals(False)

        self._update_plots()

    # ----------------------------------------------------------------------
    def update_limits(self):

        pos_min, pos_max, width_max = self.data_pool.get_roi_limits(self.my_id, 1)
        self._ui.sb_1_pos.setMinimum(pos_min)
        self._ui.sb_1_pos.setMaximum(pos_max)
        self._ui.sb_1_width.setMaximum(width_max)

        pos_min, pos_max, width_max = self.data_pool.get_roi_limits(self.my_id, 2)
        self._ui.sb_2_pos.setMinimum(pos_min)
        self._ui.sb_2_pos.setMaximum(pos_max)
        self._ui.sb_2_width.setMaximum(width_max)

        self._roi_value_changed(1, 'pos', self._ui.sb_1_pos.value())
        self._roi_value_changed(1, 'width', self._ui.sb_1_width.value())
        self._roi_value_changed(2, 'pos', self._ui.sb_2_pos.value())
        self._roi_value_changed(2, 'width', self._ui.sb_2_width.value())

    # ----------------------------------------------------------------------
    def add_file(self, file_name, color):
        self.scanplot_items[file_name] = SectionPlot(self._main_plot, file_name, self._normalized, color)
        x, y = self.data_pool.get_roi_plot(file_name, self.my_id)
        self.scanplot_items[file_name].update_plot(x, y)
        self.update_limits()

    # ----------------------------------------------------------------------
    def delete_file(self, file_name):
        self.scanplot_items[file_name].release()
        del self.scanplot_items[file_name]
        self.update_limits()

    # ----------------------------------------------------------------------
    def _update_plots(self):
        for file_name, plot_item in self.scanplot_items.items():
            x, y = self.data_pool.get_roi_plot(file_name, self.my_id)
            plot_item.update_plot(x, y)

    # ----------------------------------------------------------------------
    def _normalize_plots(self, state):
        self._normalized = state
        for plot in self.scanplot_items.values():
            plot.normalize_plot(state)

    # ----------------------------------------------------------------------
    def _set_new_section_axis(self, axis):
        self.data_pool.set_section_axis(self.my_id, axis)

        self._ui.sb_1_pos.setMinimum(-1e6)
        self._ui.sb_1_pos.setMaximum(1e6)
        self._ui.sb_1_width.setMaximum(1e6)

        self._ui.sb_1_pos.setValue(self.data_pool.get_roi_param(self.my_id, 'roi_1_pos'))
        self._ui.sb_1_width.setValue(self.data_pool.get_roi_param(self.my_id, 'roi_1_width'))

        self._ui.sb_2_pos.setMinimum(-1e6)
        self._ui.sb_2_pos.setMaximum(1e6)
        self._ui.sb_2_width.setMaximum(1e6)

        self._ui.sb_1_pos.setValue(self.data_pool.get_roi_param(self.my_id, 'roi_2_pos'))
        self._ui.sb_1_width.setValue(self.data_pool.get_roi_param(self.my_id, 'roi_2_width'))

        self._ui.lb_axis_1.setText('{} ROI'.format(self.data_pool.get_axes()
                                                   [self.data_pool.get_roi_param(self.my_id, 'roi_1_axis')]))
        self._ui.lb_axis_2.setText('{} ROI'.format(self.data_pool.get_axes()
                                                   [self.data_pool.get_roi_param(self.my_id, 'roi_2_axis')]))
        self._update_plots()
        self.update_limits()

    # ----------------------------------------------------------------------
    def _block_signals(self, flag):
        self._ui.cb_section_axis.blockSignals(flag)
        for axis in [1, 2]:
            for param in ['pos', 'width']:
                getattr(self._ui, 'sb_{}_{}'.format(axis, param)).blockSignals(flag)

    # ----------------------------------------------------------------------
    def _roi_value_changed(self, axis, param, value):
        self._block_signals(True)
        accepted_value = self.data_pool.roi_parameter_changed(self.my_id, axis, param, value)
        getattr(self._ui, 'sb_{}_{}'.format(axis, param)).setValue(accepted_value)
        self._block_signals(False)

        self._update_plots()

    # ----------------------------------------------------------------------
    def _mouse_moved(self, pos):
        if self._main_plot.sceneBoundingRect().contains(pos):
            pos = self._main_plot.vb.mapSceneToView(pos)

            axis_name = self.data_pool.get_axes()[self.data_pool.get_roi_param(self.my_id, 'axis')]

            self._cross.setPos(axis_name, pos.x(), pos.y())
            self._ruler.mouseMoved(pos.x(), pos.y())

            self._ui.lb_status.setText('{}: {:3f}, Value: {:.3f}'.format(axis_name, pos.x(), pos.y()))

    # ----------------------------------------------------------------------
    def _mouse_clicked(self, event):
        """
        """
        if event.double():
            try:
                self._main_plot.autoRange()
            except:
                pass

        pos = event.scenePos()
        if self._main_plot.sceneBoundingRect().contains(pos):
            pos = self._main_plot.vb.mapSceneToView(pos)
            self._ruler.mouseClicked(pos.x(), pos.y())

            for _, scan_plot in self.scanplot_items.items():
                scan_plot.show_tool_tip(False)

            closest_plot = self.closest_plot(pos)
            if closest_plot:
                closest_plot.showTooltip(True, pos)

    # ----------------------------------------------------------------------
    def _new_range(self):
        if self._ui.rb_range_all.isChecked():
            min, max = self._main_plot.getAxis('bottom').range
            self._ui.dsp_cut_from.setValue(min)
            self._ui.dsp_cut_to.setValue(max)

    # ----------------------------------------------------------------------
    def _cut_range(self, selection):
        fit_all = selection.objectName() == 'rb_range_all'
        self._fit_all = fit_all
        self._ui.dsp_cut_from.setEnabled(not fit_all)
        self._ui.dsp_cut_to.setEnabled(not fit_all)
        self.range_line_from.setMovable(not fit_all)
        self.range_line_to.setMovable(not fit_all)
        self._new_range()

    # ----------------------------------------------------------------------
    def _check_cut(self, type, value):
        if type == 'from':
            self.range_line_from.setValue(value)

            to = self._ui.dsp_cut_to.value()
            if to < value:
                self._ui.dsp_cut_to.setValue(value)
                self.range_line_to.setValue(value)

        elif type == 'to':
            self.range_line_to.setValue(value)

            start = self._ui.dsp_cut_from.value()
            if start > value:
                self._ui.dsp_cut_from.setValue(value)
                self.range_line_from.setValue(value)

    # ----------------------------------------------------------------------
    def closest_plot(self, pos, threshold=0.05):
        closest_plot = None
        min_distance = 1e+6
        y_epsilon = 1e-6

        for _, plot in self.scanplot_items.items():
            y_distance = plot.distance_y(pos)
            y_range = plot.range_y()
            if y_distance < min_distance and (y_distance / y_range < threshold):
                #or (y_range < y_epsilon and y_distance < threshold)):
                closest_plot = plot
                min_distance = y_distance

        return closest_plot

    # ----------------------------------------------------------------------
    def _make_fit(self, type):
        fit_style = lookandfeel.FIT_STYLES[self.fit_style_cnt %
                                           len(lookandfeel.FIT_STYLES)]
        self.fit_style_cnt = (self.fit_style_cnt + 1) % len(lookandfeel.FIT_STYLES)

        # fit all visible plots in a given x range
        if self._ui.rb_range_all.isChecked():
            [[x_min, x_max], [y_min, y_max]] = self.plot_item.viewRange()
        else:
            x_min = self._ui.dsp_cut_to.value()
            x_max = self._ui.dsp_cut_from.value()

        for key, plot in self.scanplot_items.items():  # only visible plots TODO
            [x, y], all_x = plot.getAllData()

            if self.xinfo == 'binding':
                x = plot.excitation - x
                x_max, x_min = plot.excitation - x_min, plot.excitation - x_max

            # crop data into visible range
            selected = [idx for idx, v in enumerate(x) if (v >= x_min and v <= x_max)]
            x = np.array([x[idx] for idx in selected])
            y = np.array([y[idx] for idx in selected])

            if len(x) < 100:
                x_fit = np.linspace(np.min(x), np.max(x), 100)
                y_fit = np.interp(x_fit, x, y, x[0], x[-1])
            else:
                x_fit = x
                y_fit = y

            if key not in self.fits:
                self.fits[key] = []
            else:
                for _, fitplot in self.fits[key]:
                    self.plot_item.removeItem(fitplot)
                    self.legend.removeItem(fitplot.name())
                    self.legend.updateSize()

            y_fit, label, fit_res = make_fit(x_fit, y_fit, function,
                                             plot.excitation if self.xinfo == 'binding' else None)
            if fit_res is not None and all_x is not None:
                fit_res[0] = np.append(fit_res[0], [np.interp(fit_res[0], all_x[:, 0], all_x[:, i]) for i in
                                                    range(1, all_x.shape[1])])
            label = os.path.splitext(os.path.basename(key[0]))[0] + ' ' + key[2].split('_')[-1] + ': ' + label
            self.log.info("{}, {}".format(key, label))

            fitplot = self.plot_item.plot([], name=label, pen=pg.mkPen(**fit_style))
            if self.xinfo == 'binding':
                x_fit = plot.excitation - x_fit
            fitplot.setData(x_fit, y_fit)

            self.fits[key].append((fitplot, function, fit_res))

        if not self.legend:
            self.legend = addLegend(self.plot_item)
            self.legend.show()

        for plot in self.scanplot_items.values():
            plot.showHideSweeps()

    # ----------------------------------------------------------------------
    def _delete_fits(self):
        pass

    # ----------------------------------------------------------------------
    def _save_picture(self):
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save as')
        if file_name:
            pix = QtGui.QPixmap(self._ui.gv_main.size())
            self._ui.gv_main.render(pix)
            pix.save(file_name)

    # ----------------------------------------------------------------------
    def _copy_to_clipboard(self):
        QtWidgets.qApp.clipboard().setPixmap(self._ui.gv_main.grab())

    # ----------------------------------------------------------------------
    def _print_plot(self):
        return
        try:
            printer_name = "hascpp22"
            tmp_file = os.path.join("_trash", "scan_print.png")
            pix = QtGui.QPixmap(self._ui.gv_main.size())
            self._ui.gv_main.render(pix)
            pix.save(tmp_file)
            os.system("lpr -o scaling=55 -o media=A4 -P {} {}".format(printer_name, tmp_file))
            os.remove(tmp_file)
        except Exception as err:
            self.parent.log.eroor('Error while printing: {}'.format(err))

    # ----------------------------------------------------------------------
    def _init_tool_bar(self):
        toolbar = QtWidgets.QToolBar("Main toolbar", self)
        # toolbar.setObjectName('main_tool_bar')

        print_action = toolbar.addAction(QtGui.QIcon(QtGui.QPixmap(":/icon/print.png")), "Print")
        print_action.triggered.connect(self._print_plot)

        action = toolbar.addAction(QtGui.QIcon(QtGui.QPixmap(":/icon/copy.png")), "Copy to Clipboard")
        action.triggered.connect(self._copy_to_clipboard)

        action = toolbar.addAction(QtGui.QIcon(QtGui.QPixmap(":/icon/save.png")), "Save")
        action.triggered.connect(self._save_picture)

        toolbar.addSeparator()

        action_grid = toolbar.addAction(QtGui.QIcon(QtGui.QPixmap(":/icon/grid.png")), "Grid")
        action_grid.setCheckable(True)
        action_grid.setChecked(True)
        action_grid.toggled.connect(lambda flag: self._main_plot.showGrid(flag, flag, alpha=0.25))

        action_cross = toolbar.addAction(QtGui.QIcon(QtGui.QPixmap(":/icon/cross.png")), "Crosshair Cursor")
        action_cross.setCheckable(True)
        action_cross.setChecked(False)
        action_cross.toggled.connect(lambda state: self._cross.setVisible(state))

        action_ruler = toolbar.addAction(QtGui.QIcon(QtGui.QPixmap(":/icon/ruler.png")), "Distance Measurement")
        action_ruler.setCheckable(True)
        action_ruler.setChecked(False)
        action_ruler.toggled.connect(lambda state: self._ruler.setEnabled(state))

        toolbar.addSeparator()

        button = QtWidgets.QToolButton(self)
        button.setText("Fit")
        self._make_fit_menu(button)
        toolbar.addWidget(button)

        normalize_button = QtWidgets.QToolButton(self)
        normalize_button.setText("Normalize")
        normalize_button.setCheckable(True)
        normalize_button.setChecked(False)
        normalize_button.clicked.connect(lambda state: self._normalize_plots(state))
        toolbar.addWidget(normalize_button)

        toolbar.addSeparator()

        action_legend = toolbar.addAction("Legend")
        action_legend.setCheckable(True)
        action_legend.setChecked(False)
        action_legend.toggled.connect(lambda state: self._legend.setVisible(state))
        action_legend.setToolTip("Show Legend")

        self._ui.v_layout_2.insertWidget(0, toolbar, 0)

    # ----------------------------------------------------------------------
    def _make_save_menu(self, button):
        menu = QtWidgets.QMenu(parent=button)
        action = menu.addAction("As Image")
        action.triggered.connect(self.saveAsImage)
        action = menu.addAction("As Text")
        action.triggered.connect(self.saveAsText)
        button.setMenu(menu)
        button.setPopupMode(QtWidgets.QToolButton.InstantPopup)

    # ----------------------------------------------------------------------
    def _make_fit_menu(self, button):
        menu = QtWidgets.QMenu(parent=button)
        action = menu.addAction("Linear")
        action.triggered.connect(lambda: self._make_fit("linear"))
        action = menu.addAction("Gaussian")
        action.triggered.connect(lambda: self._make_fit("gaussian"))
        action = menu.addAction("Lorentzian")
        action.triggered.connect(lambda: self._make_fit("lorentzian"))
        action = menu.addAction("FWHM")
        action.triggered.connect(lambda: self._make_fit("fwhm"))
        menu.addSeparator()
        action = menu.addAction("Delete All")
        action.triggered.connect(self._delete_fits)
        button.setMenu(menu)
        button.setPopupMode(QtWidgets.QToolButton.InstantPopup)