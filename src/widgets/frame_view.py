# Created by matveyev at 15.02.2021

WIDGET_NAME = 'FrameView'

import logging
import configparser
from distutils.util import strtobool

from PyQt5 import QtWidgets, QtCore, QtGui, QtPrintSupport

from src.main_window import APP_NAME
from src.utils.fake_image_item import FakeImageItem
from src.widgets.abstract_widget import AbstractWidget
from src.widgets.view_2d import ViewPyQt, ViewSilx
from src.gui.frame_view_ui import Ui_FrameView

logger = logging.getLogger(APP_NAME)


# ----------------------------------------------------------------------
class FrameView(AbstractWidget):
    """
    """
    section_updated = QtCore.pyqtSignal()
    new_file_selected = QtCore.pyqtSignal()

    update_roi = QtCore.pyqtSignal(int)

    # ----------------------------------------------------------------------
    def __init__(self, parent, data_pool):
        """
        """
        super(FrameView, self).__init__(parent)
        self._ui = Ui_FrameView()
        self._ui.setupUi(self)

        self.hist = self._ui.hist
        self.hist.setBackground('w')

        self._ui.cut_selectors.new_cut.connect(self.update_image)
        self._ui.cut_selectors.new_axis.connect(self._update_axes)

        settings = configparser.ConfigParser()
        settings.read('./settings.ini')

        try:
            self.backend = settings['FRAME_VIEW']['backend']
        except:
            self.backend = 'pyqt'

        if self.backend == 'pyqt':
            self._main_view = ViewPyQt(self, 'main', data_pool)
            self._second_view = ViewPyQt(self, 'second', data_pool)

            self._fake_image_item = FakeImageItem(data_pool, self._main_view.plot_2d)

            self.hist.item.setImageItem(self._fake_image_item)

            self.level_mode = 'lin'

            self._ui.chk_auto_levels.clicked.connect(self._toggle_auto_levels)
            self._ui.bg_lev_mode.buttonClicked.connect(self._change_level_mode)
            self.hist.scene().sigMouseClicked.connect(self._hist_mouse_clicked)
            self.hist.item.sigLevelChangeFinished.connect(lambda: self._toggle_auto_levels(False))
            self.hist.item.sigLookupTableChanged.connect(self._new_lookup_table)

            self._main_view.update_roi.connect(lambda roi_id: self.update_roi.emit(roi_id))
            self._main_view.update_roi.connect(lambda roi_id: self._second_view.roi_changed(roi_id))

            self._second_view.update_roi.connect(lambda roi_id: self.update_roi.emit(roi_id))
            self._second_view.update_roi.connect(lambda roi_id: self.second_view.roi_changed(roi_id))

            self._setup_actions()

        else:
            self._main_view = ViewSilx(self, 'main', data_pool)
            self._second_view = ViewSilx(self, 'second', data_pool)

            self._ui.fr_hist.setVisible(False)

        self._second_view.hide()

        self._ui.view_layout.addWidget(self._main_view, 0)
        self._ui.view_layout.addWidget(self._second_view, 0)

        self._status_bar = QtWidgets.QStatusBar(self)
        self._ui.v_layout.addWidget(self._status_bar, 0)

        self._shape_label = QtWidgets.QLabel("")
        self._status_bar.addPermanentWidget(self._shape_label)

        self._coordinate_label = QtWidgets.QLabel("")
        self._status_bar.addPermanentWidget(self._coordinate_label)

        self.current_frames = [0, 0]
        self.level_mode = 'lin'
        self.max_frame = 0

        self._ui.cut_selectors.layout().setSpacing(0)
        self._ui.cut_selectors.layout().setContentsMargins(0, 0, 0, 0)

        self.data_pool = data_pool

    # ----------------------------------------------------------------------
    def _block_hist_signal(self, state):
        if state:
            self.hist.scene().sigMouseClicked.disconnect()
            self.hist.item.sigLevelChangeFinished.disconnect()
            self.hist.item.sigLookupTableChanged.disconnect()
        else:
            self.hist.scene().sigMouseClicked.connect(self._hist_mouse_clicked)
            self.hist.item.sigLevelChangeFinished.connect(lambda: self._toggle_auto_levels(False))
            self.hist.item.sigLookupTableChanged.connect(self._new_lookup_table)

    # ----------------------------------------------------------------------
    def set_settings(self, settings):

        if self.backend == 'pyqt':
            for action in ['axes', 'axes_titles', 'grid', 'cross', 'aspect']:
                try:
                    getattr(self, f'action_{action}').setChecked(strtobool(settings[f'display_{action}']))
                except Exception as err:
                    self._parent.log.error("{} : cannot apply settings: {}".format(WIDGET_NAME, err), exc_info=True)

    # ----------------------------------------------------------------------
    def add_file(self, file_name, move_from='second'):

        logger.debug(f"Add file {file_name}, view: {move_from}")
        if move_from == 'second':
            self._main_view.add_file(file_name)
            self.data_pool.protect_file(file_name, False)
        else:
            self._second_view.add_file(file_name)
            self.data_pool.protect_file(file_name, True)

        self.new_main_file()

    # ----------------------------------------------------------------------
    def roi_changed(self, roi_ind):

        self._main_view.roi_changed(roi_ind)
        self._second_view.roi_changed(roi_ind)

    # ----------------------------------------------------------------------
    def add_roi(self, idx):

        self._main_view.add_roi(idx)
        self._second_view.add_roi(idx)

    # ----------------------------------------------------------------------
    def file_closed_by_pool(self, file_name):

        self._main_view.file_closed_by_pool(file_name)
        self._second_view.file_closed_by_pool(file_name)

    # ----------------------------------------------------------------------
    def new_coordinate(self, source,x_name, x_value, y_name, y_value, pos):

        self._coordinate_label.setText(f'{x_name}: {x_value}, {y_name}: {y_value}')

        if source == 'main':
            self._second_view.move_marker(pos)
        else:
            self._main_view.move_marker(pos)

    # ----------------------------------------------------------------------
    def new_view_box(self, source, view_box):

        if source == 'main':
            self._second_view.new_view_box(view_box)
        else:
            self._main_view.new_view_box(view_box)

    # ----------------------------------------------------------------------
    def delete_roi(self, idx):

        self._main_view.delete_roi(idx)
        self._second_view.delete_roi(idx)

    # ----------------------------------------------------------------------
    def _update_axes(self, axes_labels):

        self._main_view.new_axes(axes_labels)
        self._second_view.new_axes(axes_labels)

    # ----------------------------------------------------------------------
    def _new_lookup_table(self):

        self._second_view.new_lookup_table()

    # ----------------------------------------------------------------------
    def get_levels(self):
        return self._fake_image_item.levels

    # ----------------------------------------------------------------------
    def _change_chk_auto_levels_state(self, state):
        self._ui.chk_auto_levels.blockSignals(True)
        self._ui.chk_auto_levels.setChecked(state)
        self._ui.chk_auto_levels.blockSignals(False)

    # ----------------------------------------------------------------------
    def _toggle_auto_levels(self, state):

        if state:
            self._block_hist_signal(True)
            self._fake_image_item.setAutoLevels()
            l_min, l_max = self._fake_image_item.levels
            self.hist.item.setLevels(l_min, l_max)
            self._block_hist_signal(False)

            self.update_image()
        else:
            self._change_chk_auto_levels_state(False)

        self._second_view.new_levels()

    # ----------------------------------------------------------------------
    def _change_level_mode(self, button):

        if button == self._ui.rb_lin_levels:
            self.level_mode = 'lin'
        elif button == self._ui.rb_sqrt_levels:
            self._level_mode = 'sqrt'
        else:
            self.level_mode = 'log'

        self._fake_image_item.setMode(self.level_mode)

        self._toggle_auto_levels(True)
        self._change_chk_auto_levels_state(True)

    # ----------------------------------------------------------------------
    def _hist_mouse_clicked(self, event):

        if event.double():
            if self._main_view.current_file is not None:
                self._toggle_auto_levels(True)
                self._change_chk_auto_levels_state(True)

    # ----------------------------------------------------------------------
    def get_current_axes(self):

        selection = self._ui.cut_selectors.get_current_selection()

        return {'x': [ind for ind, sect in enumerate(selection) if sect['axis'] == 'X'][0],
                'y': [ind for ind, sect in enumerate(selection) if sect['axis'] == 'Y'][0]}

    # ----------------------------------------------------------------------
    def data_updated(self):
        if self._main_view.current_file is not None:
            self._toggle_auto_levels(True)
            self._change_chk_auto_levels_state(True)
            self._fake_image_item.sigImageChanged.emit()

    # ----------------------------------------------------------------------
    def update_image(self):

        selection = self._ui.cut_selectors.get_current_selection()
        logger.debug(f"Saving selection {selection} for file {self._main_view.current_file}")
        self.data_pool.save_section(self._main_view.current_file, selection)

        logger.debug(f"Update image with sel {selection}")

        if self.backend == 'pyqt':
            self._block_hist_signal(True)

        self._main_view.update_image()
        self._second_view.update_image()

        if self.backend == 'pyqt':
            self._block_hist_signal(False)

        self.section_updated.emit()

    # ----------------------------------------------------------------------
    def _setup_limits(self):
        """
        Set ranges for all selectors
        """
        if self._main_view.current_file is None:
            return

        limits = self.data_pool.get_file_axis_limits(self._main_view.current_file)
        self._ui.cut_selectors.set_limits(limits)

        self._shape_label.setText(f"Data shape: {limits}")

    # ----------------------------------------------------------------------
    def get_value_for_frame(self, axis, frame):
        return self.data_pool.get_value_for_frame(self._main_view.current_file, axis, frame)

    # ----------------------------------------------------------------------
    def get_max_frame_along_axis(self, axis):
        return self.data_pool.get_max_frame_along_axis(self._main_view.current_file, axis)

    # ----------------------------------------------------------------------
    def get_frame_for_value(self, axis, value):
        return self.data_pool.get_frame_for_value(self._main_view.current_file, axis, value)

    # ----------------------------------------------------------------------
    def current_file(self):
        return self._main_view.current_file

    # ----------------------------------------------------------------------
    def update_file(self, file_key):
        """
        Update widget parameters to reflect changes in the data shape _refresh_selectors of given stream.
        """
        if self._main_view.current_file == file_key and file_key is not None:
            self._setup_limits()

            sections = self.data_pool.get_section(self._main_view.current_file)
            axes_names = self.data_pool.get_file_axes(self._main_view.current_file)
            logger.debug(f"Setup frame_view selectors with section: {sections}")
            self._ui.cut_selectors.set_section(sections)

            axes_labels = [name for s, name in zip(sections, axes_names) if s['axis'] == 'X']
            axes_labels += [name for s, name in zip(sections, axes_names) if s['axis'] == 'Y']
            self._update_axes(axes_labels)
            self.update_image()

    # ----------------------------------------------------------------------
    def new_main_file(self):
        """
        Update widget in case if main file was changed
        """
        self._ui.cut_selectors.refresh_selectors(self.data_pool.get_file_axes(self._main_view.current_file))
        if self.backend == 'pyqt':
            self._fake_image_item.setNewFile(self._main_view.current_file)
            self._change_chk_auto_levels_state(True)
        self.update_file(self._main_view.current_file)
        self.new_file_selected.emit()

    # ----------------------------------------------------------------------
    def _setup_actions(self):

        toolbar = QtWidgets.QToolBar("Main toolbar", self)

        label = QtWidgets.QLabel("Level and colors: ", self)
        toolbar.addWidget(label)

        action_levels = toolbar.addAction(QtGui.QIcon(QtGui.QPixmap(":/icon/colormap.png")), "Grid")
        action_levels.setCheckable(True)
        action_levels.setChecked(True)
        action_levels.toggled.connect(lambda flag: self._ui.fr_hist.setVisible(flag))

        toolbar.addSeparator()

        label = QtWidgets.QLabel("Lock aspect: ", self)
        toolbar.addWidget(label)

        self.action_aspect = toolbar.addAction(QtGui.QIcon(QtGui.QPixmap(":/icon/aspect.png")), "Aspect ratio")
        self.action_aspect.setCheckable(True)
        self.action_aspect.toggled.connect(lambda flag, setting='aspect': self._apply_setting(setting, flag))

        toolbar.addSeparator()

        label = QtWidgets.QLabel("Axes and grid: ", self)
        toolbar.addWidget(label)

        self.action_axes = toolbar.addAction(QtGui.QIcon(QtGui.QPixmap(":/icon/axes.png")), "Axes")
        self.action_axes.setCheckable(True)
        self.action_axes.toggled.connect(lambda flag, setting='axes': self._apply_setting(setting, flag))

        self.action_axes_titles = toolbar.addAction(QtGui.QIcon(QtGui.QPixmap(":/icon/titles.png")), "Titles")
        self.action_axes_titles.setCheckable(True)
        self.action_axes_titles.toggled.connect(lambda flag, setting='titles': self._apply_setting(setting, flag))

        self.action_grid = toolbar.addAction(QtGui.QIcon(QtGui.QPixmap(":/icon/grid.png")), "Grid")
        self.action_grid.setCheckable(True)
        self.action_grid.toggled.connect(lambda flag, setting='grid': self._apply_setting(setting, flag))

        self.action_cross = toolbar.addAction(QtGui.QIcon(QtGui.QPixmap(":/icon/crosshair.png")), "Crosshair")
        self.action_cross.setCheckable(True)
        self.action_cross.toggled.connect(lambda flag, setting='cross': self._apply_setting(setting, flag))

        toolbar.addSeparator()

        label = QtWidgets.QLabel("Export image: ", self)
        toolbar.addWidget(label)

        print_action = toolbar.addAction(QtGui.QIcon(QtGui.QPixmap(":/icon/print.png")), "Print")
        print_action.triggered.connect(self._print)

        action = toolbar.addAction(QtGui.QIcon(QtGui.QPixmap(":/icon/copy.png")), "Copy to Clipboard")
        action.triggered.connect(self._copy_to_clipboard)

        action = toolbar.addAction(QtGui.QIcon(QtGui.QPixmap(":/icon/save.png")), "Save")
        action.triggered.connect(self._save)

        toolbar.addSeparator()

        self._ui.v_layout.insertWidget(0, toolbar, 0)

    # ----------------------------------------------------------------------
    def _apply_setting(self, setting, state):
        self._main_view.apply_setting(setting, state)
        self._second_view.apply_setting(setting, state)

    # ----------------------------------------------------------------------
    def _save(self):
        default_name = self._parent.current_folder() + '/roi_{}'.format(self.data_pool.get_roi_index(self.my_id))
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save as', default_name,
                                                             'Windows Bitmap (*.bmp);; Joint Photographic Experts Group (*jpg);; Portable Network Graphics (*.png);; Portable Pixmap (*ppm); X11 Bitmap (*xbm);; X11 Pixmap (*xpm)')
        if file_name:
            pix = QtGui.QPixmap(self._ui.view_layout.size())
            self._ui.view_widget.render(pix)
            pix.save(file_name)

    # ----------------------------------------------------------------------
    def _copy_to_clipboard(self):
        QtWidgets.qApp.clipboard().setPixmap(self._ui.view_widget.grab())

    # ----------------------------------------------------------------------
    def _print(self):
        dialog = QtPrintSupport.QPrintPreviewDialog()
        dialog.paintRequested.connect(self.handlePaintRequest)
        dialog.exec_()

    # ----------------------------------------------------------------------
    def handlePaintRequest(self, printer):
        self._ui.view_widget.render(QtGui.QPainter(printer))

