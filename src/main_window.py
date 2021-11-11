# Created by matveyev at 15.02.2021

APP_NAME = "3D_Data_Viewer"

import os
import logging
import psutil
import configparser

from PyQt5 import QtWidgets, QtCore
from src.gui.main_window_ui import Ui_MainWindow

from src.widgets.file_browser import FileBrowser
try:
    from src.widgets.asapo_browser import ASAPOBrowser
    from src.widgets.json_viewer import JsonView
    has_asapo = True
except:
    has_asapo = False
from src.widgets.folder_browser import FolderBrowser
from src.widgets.cube_view import CubeView
from src.widgets.tests_browser import TestsBrowser

from src.widgets.frame_view import FrameView
from src.widgets.rois_view import RoisView
from src.data_pool import DataPool
from src.widgets.image_setup import ImageSetup
from src.widgets.settings import ProgramSetup
from src.widgets.aboutdialog import AboutDialog
from src.convertor.convert import Converter


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

        if options.dir is not None:
            self.folder = options.dir
        else:
            self.folder = os.getcwd()

        self.log = _init_logger()

        self.parameter_actions = []
        self.parameter_action_group = None

        self.data_pool = DataPool(self)
        self.converter = Converter(self.data_pool)

        self.setCentralWidget(None)

        self.setDockOptions(QtWidgets.QMainWindow.AnimatedDocks |
                            QtWidgets.QMainWindow.AllowNestedDocks |
                            QtWidgets.QMainWindow.AllowTabbedDocks)

        self._menu_view = QtWidgets.QMenu('Widgets', self)

        self.frame_view, self.frame_view_dock = self._add_dock(FrameView, "Frame View",
                                                               QtCore.Qt.LeftDockWidgetArea,
                                                               self, self.data_pool)

        self.cube_view, self.cube_view_dock = self._add_dock(CubeView, "Cube view",
                                                             QtCore.Qt.LeftDockWidgetArea,
                                                             self, self.data_pool)

        self.rois_view, self.rois_view_dock = self._add_dock(RoisView, "ROIs View",
                                                             QtCore.Qt.LeftDockWidgetArea,
                                                             self, self.data_pool)

        if options.sardana:
            self.file_browser, self.file_browser_dock = self._add_dock(FileBrowser, "File Browser",
                                                                       QtCore.Qt.LeftDockWidgetArea, self)
            self.file_browser.file_selected.connect(self.data_pool.open_file)
            self.has_sardana = True
        else:
            self.has_sardana = False

        if has_asapo and options.asapo:
            self.asapo_browser, self.asapo_browser_dock = self._add_dock(ASAPOBrowser, "ASAPO View",
                                                                         QtCore.Qt.LeftDockWidgetArea, self)
            self.asapo_browser.stream_selected.connect(self.data_pool.open_stream)
            self.asapo_browser.stream_updated.connect(self.data_pool.update_stream)
            self.metadata_browser, self.metadata_browser_dock = self._add_dock(JsonView, "Metadata View",
                                                                               QtCore.Qt.LeftDockWidgetArea,
                                                                               self, self.data_pool)
            self.frame_view.section_updated.connect(self.metadata_browser.update_meta)
            self.data_pool.file_updated.connect(self.frame_view.update_file)
            self.has_asapo = True
        else:
            self.has_asapo = False

        if options.beam:
            self.folder_browser, self.folder_browser_dock = self._add_dock(FolderBrowser, "Folder Browser",
                                                                           QtCore.Qt.LeftDockWidgetArea, self)
            self.folder_browser.file_selected.connect(self.data_pool.open_file)
            self.has_beam_view = True
        else:
            self.has_beam_view = False

        if options.tests:
            self.tests_browser, self.tests_browser_dock = self._add_dock(TestsBrowser, "Test Browser",
                                                                       QtCore.Qt.LeftDockWidgetArea, self)
            self.tests_browser.test_selected.connect(self.data_pool.open_test)
            self.has_tests = True
        else:
            self.has_tests = False

        self.frame_view.new_file_selected.connect(self.cube_view.new_file)

        self.frame_view.update_roi.connect(self.rois_view.roi_changed)

        self.rois_view.update_roi.connect(self.frame_view.roi_changed)

        self.data_pool.new_file_added.connect(self.frame_view.add_file)
        self.data_pool.new_file_added.connect(self.rois_view.add_file)

        self.data_pool.file_deleted.connect(self.rois_view.delete_file)

        self.data_pool.close_file.connect(self.frame_view.file_closed_by_pool)

        self.data_pool.roi_changed.connect(self.frame_view.roi_changed)
        self.data_pool.roi_changed.connect(self.rois_view.roi_changed)

        self.data_pool.data_updated.connect(self.frame_view.update_image)
        self.data_pool.data_updated.connect(self.rois_view.update_plots)

        self._load_ui_settings()
        self.apply_settings()

        self._setup_menu()

        self._init_status_bar()

        self._status_timer = QtCore.QTimer(self)
        self._status_timer.timeout.connect(self._refresh_status_bar)
        self._status_timer.start(self.STATUS_TICK)

        if options.def_file is not None:
            self.data_pool.open_file(options.def_file)

        if options.def_stream is not None:
            self.data_pool.open_file(options.def_stream)

    # ----------------------------------------------------------------------
    def apply_settings(self, settings=None):
        if settings is None:
            settings = configparser.ConfigParser()
            settings.read('./settings.ini')

        if 'FILE_BROWSER' in settings and self.has_sardana:
            self.file_browser.set_settings(settings['FILE_BROWSER'])
        if 'ASAPO' in settings and self.has_asapo:
            self.asapo_browser.set_settings(settings['ASAPO'])
        if 'FRAME_VIEW' in settings:
            self.frame_view.set_settings(settings['FRAME_VIEW'])
        if 'ROIS_VIEW' in settings:
            self.rois_view.set_settings(settings['ROIS_VIEW'])
        if 'CUBE_VIEW' in settings:
            self.cube_view.set_settings(settings['CUBE_VIEW'])
        if 'DATA_POOL' in settings:
            self.data_pool.set_settings(settings['DATA_POOL'])

    # ----------------------------------------------------------------------
    def get_current_file(self):
        return self.frame_view.current_file()

    # ----------------------------------------------------------------------
    def get_current_folder(self):
        if self.has_sardana:
            return self.file_browser.current_folder()
        elif self.has_beam_view:
            return self.folder_browser.current_folder()
        else:
            return os.getcwd()

    # ----------------------------------------------------------------------
    def add_roi(self, idx):
        self.frame_view.add_roi(idx)
        self.cube_view.fill_roi()

    # ----------------------------------------------------------------------
    def delete_roi(self, idx):
        self.frame_view.delete_roi(idx)
        self.cube_view.fill_roi()

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
    def _convert(self):
        self.converter.show(self.frame_view.current_file())

    # ----------------------------------------------------------------------
    def _show_settings(self):
        ProgramSetup(self).exec_()

    # ----------------------------------------------------------------------
    def _setup_menu(self):
        if self.has_sardana:
            batch_menu = QtWidgets.QMenu('Batch process', self)

            action = batch_menu.addAction("Process files...")
            action.triggered.connect(lambda checked, x='files': self._batch_process(x))

            action = batch_menu.addAction("Process folder...")
            action.triggered.connect(lambda checked, x='folder': self._batch_process(x))

            space_menu = QtWidgets.QMenu('Space', self)
            action = space_menu.addAction('Convert current file')
            action.triggered.connect(self._convert)

            self.menuBar().addMenu(batch_menu)
            self.menuBar().addMenu(space_menu)
            self.menuBar().addSeparator()

        image_setup = QtWidgets.QAction('Image setup', self)
        image_setup.triggered.connect(self._setup_image)

        menu_settings = QtWidgets.QAction('Program settings', self)
        menu_settings.triggered.connect(self._show_settings)

        self.menuBar().addAction(image_setup)
        self.menuBar().addAction(menu_settings)

        self.menuBar().addSeparator()

        about_action = QtWidgets.QAction('About', self)
        about_action.triggered.connect(lambda: AboutDialog(self).exec_())

        menu_exit = QtWidgets.QAction('Exit', self)
        menu_exit.triggered.connect(self._exit)

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
    def _close_me(self):
        self.log.info("Closing the app...")
        if self.has_sardana:
            self.file_browser.safe_close()
        self._save_ui_settings()

    # ----------------------------------------------------------------------
    def _exit(self):
        self._close_me()
        QtWidgets.QApplication.quit()

    # ----------------------------------------------------------------------
    def closeEvent(self, event):
        """
        """
        self._close_me()
        event.accept()

    # ----------------------------------------------------------------------
    def _save_ui_settings(self):
        """Save basic GUI settings.
        """
        settings = QtCore.QSettings(APP_NAME)

        if self.has_sardana:
            self.file_browser.save_ui_settings(settings)

        if self.has_asapo:
            self.asapo_browser.save_ui_settings(settings)

        self.rois_view.save_ui_settings(settings)
        self.frame_view.save_ui_settings(settings)


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

        if self.has_sardana:
            self.file_browser.load_ui_settings(settings)

        if self.has_asapo:
            self.asapo_browser.load_ui_settings(settings)

        self.rois_view.load_ui_settings(settings)
        self.frame_view.load_ui_settings(settings)

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
    main_log = logging.getLogger(APP_NAME)
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