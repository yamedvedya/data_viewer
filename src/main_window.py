# Created by matveyev at 15.02.2021

APP_NAME = "3D_Data_Viewer"

import os
import logging
import psutil
import configparser
import re

from PyQt5 import QtWidgets, QtCore
from src.gui.main_window_ui import Ui_MainWindow

from src.widgets.file_browser import FileBrowser
try:
    from src.widgets.asapo_browser import ASAPOBrowser
    has_asapo = True
except:
    has_asapo = False

from src.widgets.frame_view import FrameView
from src.widgets.rois_view import RoisView
from src.data_pool import DataPool
from src.widgets.image_setup import ImageSetup
from src.widgets.settings import ProgramSetup
from src.widgets.aboutdialog import AboutDialog

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

        self.frame_view, self.frame_view_dock = self._add_dock(FrameView, "Frame View",
                                                               QtCore.Qt.LeftDockWidgetArea,
                                                               self, self.data_pool)

        self.rois_view, self.rois_view_dock = self._add_dock(RoisView, "ROIs View",
                                                             QtCore.Qt.LeftDockWidgetArea,
                                                             self, self.data_pool)

        if has_asapo:
            self.asapo_browser, self.asapo_browser_dock = self._add_dock(ASAPOBrowser, "ASAPO View",
                                                                         QtCore.Qt.LeftDockWidgetArea, self)

        # self.cube_view, self.cube_view_dock = self._add_dock(CubeView, "Cube iew",
        #                                                      QtCore.Qt.LeftDockWidgetArea,
        #                                                      self, self.data_pool)

        self.file_browser.file_selected.connect(self.data_pool.open_file)
        if has_asapo:
            self.asapo_browser.stream_selected.connect(self.data_pool.open_stream)

        self.data_pool.new_file_added.connect(self.frame_view.add_file)
        self.data_pool.new_file_added.connect(self.rois_view.add_file)

        self.data_pool.file_deleted.connect(self.rois_view.delete_file)

        self.data_pool.close_file.connect(self.frame_view.file_closed_by_pool)

        self.data_pool.new_roi_range.connect(self.frame_view.new_roi_range)
        self.data_pool.new_roi_range.connect(self.rois_view.new_roi_range)

        self.data_pool.data_updated.connect(self.frame_view.update_image)
        self.data_pool.data_updated.connect(self.rois_view.update_plots)

        self._load_ui_settings()
        self.apply_settings()

        self._init_status_bar()

        self._test_run = True
        self._status_timer = QtCore.QTimer(self)
        self._status_timer.timeout.connect(self._refresh_status_bar)
        self._status_timer.start(self.STATUS_TICK)

    # ----------------------------------------------------------------------
    def apply_settings(self, settings=None):
        if settings is None:
            settings = configparser.ConfigParser()
            settings.read('./settings.ini')

        if 'FILE_BROWSER' in settings:
            self.file_browser.set_settings(settings['FILE_BROWSER'])
        if 'ASAPO' in settings and has_asapo:
            self.asapo_browser.set_settings(settings['ASAPO'])
        if 'FRAME_VIEW' in settings:
            self.frame_view.set_settings(settings['FRAME_VIEW'])
        if 'ROIS_VIEW' in settings:
            self.rois_view.set_settings(settings['ROIS_VIEW'])
        if 'DATA_POOL' in settings:
            self.data_pool.set_settings(settings['DATA_POOL'])

    # ----------------------------------------------------------------------
    def get_current_folder(self):
        return self.file_browser.current_folder()

    # ----------------------------------------------------------------------
    def add_roi(self, idx):
        self.frame_view.add_roi(idx)

    # ----------------------------------------------------------------------
    def delete_roi(self, idx):
        self.frame_view.delete_roi(idx)

    # ----------------------------------------------------------------------
    def _batch_process(self, mode):
        if mode == 'files':
            file_names, _ = QtWidgets.QFileDialog.getOpenFileNames(self, 'Select files',
                                                                   self.file_browser.current_folder(),
                                                                   'NEXUS files (*.nxs)')
        else:
            dir_name = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory',
                                                                  self.file_browser.current_folder())

            file_names = [name for name in os.listdir(dir_name) if name.endswith('.nxs')]

        save_dir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Save to', self.file_browser.current_folder())
        if save_dir:
            self.data_pool.batch_process_rois(file_names, save_dir, '.txt')

    # ----------------------------------------------------------------------
    def _new_space(self, space):
        self.data_pool.set_space(space)
        pass # TODO

    # ----------------------------------------------------------------------
    def _show_settings(self):
        ProgramSetup(self).exec_()

    # ----------------------------------------------------------------------
    def _setup_menu(self):
        self._menu_view = QtWidgets.QMenu('Widgets', self)

        space_menu = QtWidgets.QMenu('Displayed space', self)
        space_group = QtWidgets.QActionGroup(self)
        action = space_menu.addAction('Real')
        action.setCheckable(True)
        action.setChecked(True)
        action.triggered.connect(lambda: self._new_space('real'))
        space_group.addAction(action)
        action = space_menu.addAction('Reciprocal')
        action.setCheckable(True)
        action.triggered.connect(lambda: self._new_space('reciprocal'))
        space_group.addAction(action)

        image_setup = QtWidgets.QAction('Image setup', self)
        image_setup.triggered.connect(self._setup_image)

        menu_settings = QtWidgets.QAction('Program settings', self)
        menu_settings.triggered.connect(self._show_settings)

        about_action = QtWidgets.QAction('About', self)
        about_action.triggered.connect(lambda: AboutDialog(self).exec_())

        menu_exit = QtWidgets.QAction('Exit', self)
        menu_exit.triggered.connect(self._exit)

        batch_menu = QtWidgets.QMenu('Batch process', self)

        action = batch_menu.addAction("Process files...")
        action.triggered.connect(lambda checked, x='files': self._batch_process(x))

        action = batch_menu.addAction("Process folder...")
        action.triggered.connect(lambda checked, x='folder': self._batch_process(x))

        self.menuBar().addMenu(batch_menu)

        self.menuBar().addSeparator()

        self.menuBar().addAction(image_setup)
        self.menuBar().addAction(menu_settings)

        self.menuBar().addSeparator()

        self.menuBar().addMenu(self._menu_view)
        self.menuBar().addAction(about_action)
        self.menuBar().addAction(menu_exit)

    # ----------------------------------------------------------------------
    def _setup_image(self):
        ImageSetup(self, self.data_pool).exec_()

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
    def report_error(self, text, informative_text='', detailed_text=''):

        self.log.error("Error: {}, {}, {} ".format(text, informative_text, detailed_text))

        self.msg = QtWidgets.QMessageBox()
        self.msg.setModal(False)
        self.msg.setIcon(QtWidgets.QMessageBox.Critical)
        self.msg.setText(text)
        self.msg.setInformativeText(informative_text)
        if detailed_text != '':
            self.msg.setDetailedText(detailed_text)
        self.msg.setWindowTitle("Error")
        self.msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.msg.show()

    # ----------------------------------------------------------------------
    def _exit(self):

        self.log.info("Closing the app...")
        self.file_browser.safe_close()
        self._save_ui_settings()
        QtWidgets.QApplication.quit()

    # ----------------------------------------------------------------------
    def closeEvent(self, event):
        """
        """
        self.log.info("Closing the app...")
        self.file_browser.safe_close()
        self._save_ui_settings()
        event.accept()

    # ----------------------------------------------------------------------
    def _save_ui_settings(self):
        """Save basic GUI settings.
        """
        settings = QtCore.QSettings(APP_NAME)

        self.file_browser.save_ui_settings(settings)
        self.rois_view.save_ui_settings(settings)
        self.frame_view.save_ui_settings(settings)
        if has_asapo:
            self.asapo_browser.save_ui_settings(settings)        # self.cube_view.save_ui_settings(settings)

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
        self.frame_view.load_ui_settings(settings)
        if has_asapo:
            self.asapo_browser.load_ui_settings(settings)        # self.cube_view.load_ui_settings(settings)

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
        if self._test_run:
            # self.data_pool.open_file('./test/Bhat_B_1V_02665.nxs')
            self.data_pool.open_file('./test/Bhat_B_2_02867.nxs')
            self._test_run =False

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

    if not os.path.exists('./logs'):
        os.mkdir('./logs')

    fh = logging.FileHandler('./logs/main_log')
    fh.setFormatter(format)
    main_log.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(format)
    main_log.addHandler(ch)

    return main_log