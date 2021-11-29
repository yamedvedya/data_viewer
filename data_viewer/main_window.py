# Created by matveyev at 15.02.2021
import shutil

APP_NAME = "3D_Data_Viewer"

import os
import logging
import psutil
import configparser
from pathlib import Path

from PyQt5 import QtWidgets, QtCore
from data_viewer.gui.main_window_ui import Ui_MainWindow

from data_viewer.widgets.file_browser import FileBrowser
try:
    from data_viewer.widgets.asapo_browser import ASAPOBrowser
    from data_viewer.widgets.json_viewer import JsonView
    from data_viewer.data_sources.asapo.asapo_data_set import apply_settings_asapo
    has_asapo = True
except:
    has_asapo = False

from data_viewer.data_sources.sardana.sardana_data_set import apply_settings_sardana

from data_viewer.widgets.cube_view import CubeView
from data_viewer.widgets.tests_browser import TestsBrowser

from data_viewer.widgets.frame_view import FrameView
from data_viewer.widgets.rois_view import RoisView
from data_viewer.data_pool import DataPool
from data_viewer.widgets.settings import ProgramSetup
from data_viewer.widgets.aboutdialog import AboutDialog
from data_viewer.convertor.convert import Converter

from data_viewer.utils.utils import check_settings


logger = logging.getLogger(APP_NAME)


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

        self.configuration = {}

        self.parameter_actions = []
        self.parameter_action_group = None

        self.data_pool = DataPool(self)
        self.converter = Converter(self.data_pool)

        self.setCentralWidget(None)

        self.setDockOptions(QtWidgets.QMainWindow.AnimatedDocks |
                            QtWidgets.QMainWindow.AllowNestedDocks |
                            QtWidgets.QMainWindow.AllowTabbedDocks)

        self.settings = self.get_settings(options)

        self._menu_view = QtWidgets.QMenu('Widgets', self)

        self.frame_view, self.frame_view_dock = self._add_dock(FrameView, "Frame View",
                                                               QtCore.Qt.LeftDockWidgetArea,
                                                               self, self.data_pool, self.settings)

        try:
            self.configuration['cube_view'] = 'cube' in self.settings['WIDGETS']['visualization']
        except:
            self.configuration['cube_view'] = True

        if self.configuration['cube_view']:
            try:
                self.cube_view, self.cube_view_dock = self._add_dock(CubeView, "Cube view",
                                                                     QtCore.Qt.LeftDockWidgetArea,
                                                                     self, self.data_pool)

                self.cube_view_dock.visibilityChanged.connect(self.cube_view.visibility_changed)
            except:
                self.configuration['cube_view'] = False

        try:
            self.configuration['roi'] = 'roi' in self.settings['WIDGETS']['visualization']
        except:
            self.configuration['roi'] = True

        if self.configuration['roi']:
            self.rois_view, self.rois_view_dock = self._add_dock(RoisView, "ROIs View",
                                                                 QtCore.Qt.LeftDockWidgetArea,
                                                                 self, self.data_pool)

        try:
            self.configuration['sardana'] = 'sardana' in self.settings['WIDGETS']['file_types']
        except:
            self.configuration['sardana'] = True

        if self.configuration['sardana']:
            self.file_browser, self.file_browser_dock = self._add_dock(FileBrowser, "Sardana Browser",
                                                                       QtCore.Qt.LeftDockWidgetArea, self, 'sardana')
            self.file_browser.file_selected.connect(self.data_pool.open_file)

        try:
            self.configuration['asapo'] = 'asapo' in self.settings['WIDGETS']['file_types']
        except:
            self.configuration['asapo'] = True

        self.metadata_browser = None

        if has_asapo and self.configuration['asapo']:
            self.asapo_browser, self.asapo_browser_dock = self._add_dock(ASAPOBrowser, "ASAPO View",
                                                                         QtCore.Qt.LeftDockWidgetArea, self)
            self.asapo_browser.stream_selected.connect(self.data_pool.open_stream)
            self.asapo_browser.stream_updated.connect(self.data_pool.update_stream)
            self.metadata_browser, self.metadata_browser_dock = self._add_dock(JsonView, "Metadata View",
                                                                               QtCore.Qt.LeftDockWidgetArea,
                                                                               self, self.data_pool)
            self.frame_view.section_updated.connect(self.metadata_browser.update_meta)
            self.data_pool.file_updated.connect(self.frame_view.update_file)

        try:
            self.configuration['beamline'] = 'beamline' in self.settings['WIDGETS']['file_types']
        except:
            self.configuration['beamline'] = True

        if self.configuration['beamline']:
            self.file_browser, self.file_browser_dock = self._add_dock(FileBrowser, "Beamline Browser",
                                                                       QtCore.Qt.LeftDockWidgetArea, self, 'beam')
            self.file_browser.file_selected.connect(self.data_pool.open_file)

        try:
            self.configuration['tests'] = 'tests' in self.settings['WIDGETS']['file_types']
        except:
            self.configuration['tests'] = True

        if self.configuration['tests']:
            self.tests_browser, self.tests_browser_dock = self._add_dock(TestsBrowser, "Test Browser",
                                                                       QtCore.Qt.LeftDockWidgetArea, self)
            self.tests_browser.test_selected.connect(self.data_pool.open_test)
            if self.metadata_browser is None:
                self.metadata_browser, self.metadata_browser_dock = self._add_dock(JsonView, "Metadata View",
                                                                                   QtCore.Qt.LeftDockWidgetArea,
                                                                                   self, self.data_pool)
                self.frame_view.section_updated.connect(self.metadata_browser.update_meta)

        self.data_pool.new_file_added.connect(self.frame_view.add_file)
        self.data_pool.close_file.connect(self.frame_view.file_closed_by_pool)
        self.data_pool.data_updated.connect(self.frame_view.data_updated)

        if self.configuration['cube_view']:
            self.frame_view.main_file_changed.connect(self.cube_view.main_file_changed)
            self.frame_view.roi_moved.connect(self.cube_view.roi_changed)
            self.frame_view.clear_view.connect(self.cube_view.clear_view)
            self.frame_view.new_axes.connect(self.cube_view.display_file)
            self.data_pool.data_updated.connect(self.cube_view.data_updated)

        if self.configuration['roi']:
            self.frame_view.main_file_changed.connect(self.rois_view.main_file_changed)
            self.frame_view.roi_moved.connect(self.rois_view.roi_changed)
            self.frame_view.new_units.connect(self.rois_view.units_changed)
            self.frame_view.clear_view.connect(self.rois_view.main_file_changed)

            self.data_pool.data_updated.connect(self.rois_view.update_plots)
            self.data_pool.new_file_added.connect(self.rois_view.add_file)
            self.data_pool.file_deleted.connect(self.rois_view.delete_file)

            self.rois_view.update_roi.connect(self.frame_view.roi_changed)

            if self.configuration['cube_view']:
                self.rois_view.update_roi.connect(self.cube_view.roi_changed)

        self._load_ui_settings()
        self.apply_settings()

        self._setup_menu()

        if self.configuration['sardana']:
            action = self.additions_menu.addAction("Fetch ROI from MacroServer...")
            action.triggered.connect(self.rois_view.fetch_rois)

        self._init_status_bar()

        self._status_timer = QtCore.QTimer(self)
        self._status_timer.timeout.connect(self._refresh_status_bar)
        self._status_timer.start(self.STATUS_TICK)

    # ----------------------------------------------------------------------
    def set_settings(self, settings):

        self.settings = settings
        self.apply_settings()

    # ----------------------------------------------------------------------
    def get_settings(self, options):

        settings = configparser.ConfigParser()

        home = os.path.join(str(Path.home()), '.petra_viewer')
        file_name = str(options.profile)
        if not file_name.endswith('.ini'):
            file_name += '.ini'

        if not os.path.exists(os.path.join(home, file_name)):
            _finished = False
            while not _finished:
                file = QtWidgets.QFileDialog.getOpenFileName(self, 'Cannot find settings file, please locate it',
                                                             str(Path.home()), 'INI settings (*.ini)')
                if file[0]:
                    settings.read(file[0])
                    _finished = check_settings(settings)
                else:
                    break
            if _finished:
                return settings
        else:
            settings.read(os.path.join(home, file_name))
            if check_settings(settings):
                return settings

        if not os.path.exists(home):
            os.mkdir(home)

        if not os.path.exists(os.path.join(home, file_name)):
            shutil.copy(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'default_settings.ini'),
                        os.path.join(home, 'default.ini'))

        settings.read(os.path.join(home, 'default.ini'))

        if not check_settings(settings):
            shutil.copy(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'default_settings.ini'),
                        os.path.join(home, 'default.ini'))
            settings.read(os.path.join(home, 'default.ini'))

        return settings

    # -----------------------------------------------------------------
    def save_settings(self, file_name):
        if not os.path.exists(os.path.dirname(file_name)):
            os.mkdir(os.path.dirname(file_name))

        with open(file_name, 'w') as configfile:
            self.settings.write(configfile)

    # ----------------------------------------------------------------------
    def apply_settings(self):

        if 'DATA_POOL' in self.settings:
            self.data_pool.set_settings(self.settings['DATA_POOL'])

        if 'FRAME_VIEW' in self.settings:
            self.frame_view.set_settings(self.settings['FRAME_VIEW'])

        if 'ROIS_VIEW' in self.settings and self.configuration['roi']:
            self.rois_view.set_settings(self.settings['ROIS_VIEW'])

        if 'CUBE_VIEW' in self.settings and self.configuration['cube_view']:
            self.cube_view.set_settings(self.settings['CUBE_VIEW'])

        if 'SARDANA' in self.settings and self.configuration['sardana']:
            apply_settings_sardana(self.settings['SARDANA'])

        if 'ASAPO' in self.settings and self.configuration['asapo']:
            apply_settings_asapo(self.settings['ASAPO'])

        self.data_pool.apply_settings()

        self.save_settings(os.path.join(os.path.join(str(Path.home()), '.petra_viewer'), 'default.ini'))

    # ----------------------------------------------------------------------
    def get_current_file(self):
        return self.frame_view.current_file()

    # ----------------------------------------------------------------------
    def get_current_folder(self):
        if self.configuration['sardana'] or self.configuration['beamline']:
            return self.file_browser.current_folder()
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
        if self.configuration['sardana']:
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

        menu_settings = QtWidgets.QAction('Program settings', self)
        menu_settings.triggered.connect(self._show_settings)
        self.menuBar().addAction(menu_settings)

        self.menuBar().addSeparator()

        self.additions_menu = QtWidgets.QMenu('Additional features', self)
        self.menuBar().addMenu(self.additions_menu)

        about_action = QtWidgets.QAction('About', self)
        about_action.triggered.connect(lambda: AboutDialog(self).exec_())

        menu_exit = QtWidgets.QAction('Exit', self)
        menu_exit.triggered.connect(self._exit)

        self.menuBar().addMenu(self._menu_view)
        self.menuBar().addAction(about_action)
        self.menuBar().addAction(menu_exit)

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

        logger.error("Error: {}, {}, {} ".format(text, informative_text, detailed_text))

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
        logger.info("Closing the app...")
        if self.configuration['sardana']:
            self.file_browser.safe_close()
        self.save_settings(os.path.join(os.path.join(str(Path.home()), '.petra_viewer'), 'default.ini'))
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

        if self.configuration['sardana']:
            self.file_browser.save_ui_settings(settings)

        if self.configuration['asapo']:
            self.asapo_browser.save_ui_settings(settings)

        self.rois_view.save_ui_settings(settings)
        self.frame_view.save_ui_settings(settings)

        settings.setValue("MainWindow/geometry", self.saveGeometry())
        settings.setValue("MainWindow/state", self.saveState())

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

        if self.configuration['sardana']:
            self.file_browser.load_ui_settings(settings)

        if self.configuration['asapo']:
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

        self._lb_resources_status.setText("| {:.2f}MB | CPU {} % |".format(mem, cpu))
