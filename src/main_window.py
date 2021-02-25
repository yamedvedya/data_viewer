# Created by matveyev at 15.02.2021

APP_NAME = "3D_Data_Viewer"

import os
import logging
import psutil

from PyQt5 import QtWidgets, QtCore
from src.gui.main_window_ui import Ui_MainWindow

from src.widgets.file_browser import FileBrowser
from src.widgets.files_inspector import FilesInspector
from src.widgets.rois_view import RoisView
from src.data_pool import DataPool
from src.utils.mask_selector import MaskSelector


class DataViewer(QtWidgets.QMainWindow):
    """
    """

    STATUS_TICK = 2000

    # ----------------------------------------------------------------------
    def __init__(self, options):
        """
        """
        super(DataViewer, self).__init__()
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)

        if options.folder is not None:
            self.folder = options.folder
        # elif last_folder is not None:
        #     self.folder = last_folder
        else:
            self.folder = os.getcwd()

        self.log = _init_logger()

        self._setup_menu()
        self.parameter_actions = []
        self.parameter_action_group = None

        self.data_pool = DataPool(self, self.log)

        self.setCentralWidget(None)

        self.setDockOptions(QtWidgets.QMainWindow.AnimatedDocks |
                            QtWidgets.QMainWindow.AllowNestedDocks |
                            QtWidgets.QMainWindow.AllowTabbedDocks)

        self.file_browser, self.file_browser_dock = self._add_dock(FileBrowser, "File Browser",
                                                                   QtCore.Qt.LeftDockWidgetArea, self)

        self.files_inspector, self.files_inspector_dock = self._add_dock(FilesInspector, "Files Inspector",
                                                                         QtCore.Qt.LeftDockWidgetArea,
                                                                         self, self.data_pool)

        self.rois_view, self.rois_view_dock = self._add_dock(RoisView, "ROIs View",
                                                             QtCore.Qt.LeftDockWidgetArea,
                                                             self, self.data_pool)

        # self.cube_view, self.cube_view_dock = self._add_dock(CubeView, "Cube iew",
        #                                                      QtCore.Qt.LeftDockWidgetArea,
        #                                                      self, self.data_pool)

        self.file_browser.file_selected.connect(self.data_pool.open_file)

        self.data_pool.new_file_added.connect(self.files_inspector.add_file)
        self.data_pool.new_file_added.connect(self.rois_view.add_file)

        self.data_pool.file_deleted.connect(self.rois_view.delete_file)

        self.data_pool.update_parameter_list.connect(self._setup_parameter_menu)

        self.data_pool.new_parameter_selected.connect(self.files_inspector.display_z_value)
        self.data_pool.new_parameter_selected.connect(self.rois_view.update_limits)

        self.data_pool.new_roi_range.connect(self.files_inspector.new_roi_range)
        self.data_pool.new_roi_range.connect(self.rois_view.new_roi_range)

        self._load_ui_settings()

        self._init_status_bar()

        self._status_timer = QtCore.QTimer(self)
        self._status_timer.timeout.connect(self._refresh_status_bar)
        self._status_timer.start(self.STATUS_TICK)

        self.data_pool.open_file('D://test//Bhat_B_2_02867.nxs')
        # self.data_pool.open_file()

    # ----------------------------------------------------------------------
    def add_roi(self, idx):
        self.files_inspector.add_roi(idx)

    # ----------------------------------------------------------------------
    def delete_roi(self, idx):
        self.files_inspector.delete_roi(idx)

    # ----------------------------------------------------------------------
    def _setup_parameter_menu(self):
        for action in self.parameter_actions:
            self.parameter_menu.removeAction(action)

        self.parameter_actions = []
        self.parameter_action_group = QtWidgets.QActionGroup(self)

        for parameter in self.data_pool.possible_display_parameters:
            action = QtWidgets.QAction(parameter, self)
            action.setCheckable(True)
            action.setChecked(parameter == self.data_pool.display_parameter)
            action.triggered.connect(lambda state, name=parameter: self.data_pool.set_new_display_parameter(name))
            self.parameter_action_group.addAction(action)
            self.parameter_menu.addAction(action)
            self.parameter_actions.append(action)

    # ----------------------------------------------------------------------
    def _setup_menu(self):
        self.parameter_menu = QtWidgets.QMenu('Display parameter', self)

        mask_setup = QtWidgets.QAction('Detector mask setup', self)
        mask_setup.triggered.connect(self._setup_mask)

        self._menu_view = QtWidgets.QMenu('Widgets', self)

        menu_exit = QtWidgets.QAction('Exit', self)
        menu_exit.triggered.connect(self._exit)

        self.menuBar().addMenu(self.parameter_menu)
        self.menuBar().addAction(mask_setup)
        self.menuBar().addMenu(self._menu_view)
        self.menuBar().addAction(menu_exit)

    # ----------------------------------------------------------------------
    def _setup_mask(self):
        MaskSelector(self, self.data_pool).exec_()

    # ----------------------------------------------------------------------
    def _add_dock(self, WidgetClass, label, location, *args, **kwargs):
        """
        """
        widget = WidgetClass(*args, **kwargs)

        dock = QtWidgets.QDockWidget(label)
        dock.setFocusPolicy(QtCore.Qt.StrongFocus)
        dock.setObjectName("{0}Dock".format("".join(label.split())))
        dock.setWidget(widget)

        self.addDockWidget(location, dock)
        self._menu_view.addAction(dock.toggleViewAction())

        return widget, dock

    # ----------------------------------------------------------------------
    def _exit(self):

        self.log.info("Closing the app...")
        self._save_ui_settings()
        QtWidgets.QApplication.quit()

    # ----------------------------------------------------------------------
    def closeEvent(self, event):
        """
        """
        self.log.info("Closing the app...")
        self._save_ui_settings()
        event.accept()

    # ----------------------------------------------------------------------
    def _save_ui_settings(self):
        """Save basic GUI settings.
        """
        settings = QtCore.QSettings(APP_NAME)

        self.file_browser.save_ui_settings(settings)
        self.rois_view.save_ui_settings(settings)
        self.files_inspector.save_ui_settings(settings)
        # self.cube_view.save_ui_settings(settings)

        settings.setValue("MainWindow/geometry", self.saveGeometry())
        settings.setValue("MainWindow/state", self.saveState())

        settings.setValue("StartFolder", self.folder)

    # ----------------------------------------------------------------------
    def _load_ui_settings(self):
        """Load basic GUI settings.
        """
        settings = QtCore.QSettings(APP_NAME)

        try:
            self.restoreGeometry(settings.value("MainWindow/geometry"))
        except:
            pass

        try:
            self.restoreState(settings.value("MainWindow/state"))
        except:
            pass

        self.file_browser.load_ui_settings(settings)
        self.rois_view.load_ui_settings(settings)
        self.files_inspector.load_ui_settings(settings)
        # self.cube_view.load_ui_settings(settings)

        # try:
        #     return settings.value("StartFolder")
        # except:
        #     return None

    # ----------------------------------------------------------------------
    def _init_status_bar(self):
        """
        """
        self._lbCursorPos = QtWidgets.QLabel("")

        processID = os.getpid()
        currentDir = os.getcwd()

        lbProcessID = QtWidgets.QLabel("PID {}".format(processID))
        lbProcessID.setStyleSheet("QLabel {color: #000066;}")
        lbCurrentDir = QtWidgets.QLabel("{}".format(currentDir))

            # resource usage
        process = psutil.Process(processID)
        mem = float(process.memory_info().rss) / (1024. * 1024.)
        cpu = process.cpu_percent()

        self._lb_resources_status = QtWidgets.QLabel("| {:.2f}MB | CPU {} % |".format(mem, cpu))

        self.statusBar().addPermanentWidget(self._lbCursorPos)
        self.statusBar().addPermanentWidget(lbProcessID)
        self.statusBar().addPermanentWidget(lbCurrentDir)
        self.statusBar().addPermanentWidget(self._lb_resources_status)

    # ----------------------------------------------------------------------
    def _refresh_status_bar(self):
        """
        """
        process = psutil.Process(os.getpid())
        mem = float(process.memory_info().rss) / (1024. * 1024.)
        cpu = psutil.cpu_percent()

        self._lb_resources_status.setText("| {:.2f}MB | CPU {} % |".format(mem,
                                                                           cpu))

# ----------------------------------------------------------------------
def _init_logger():
    main_log = logging.getLogger('3d_data_viewer')
    main_log.setLevel(10)

    format = logging.Formatter("%(asctime)s %(module)s %(lineno)-6d %(levelname)-6s %(message)s")

    fh = logging.FileHandler('./logs/main_log')
    fh.setFormatter(format)
    main_log.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(format)
    main_log.addHandler(ch)

    return main_log