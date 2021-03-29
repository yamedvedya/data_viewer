# Created by matveyev at 15.02.2021

WIDGET_NAME = 'DataBrowser'

file_formats = ["*.nxs"]

FILE_REFRESH_PERIOD = 1

import threading
import os
import time

try:
    from watchdog.observers import Observer
    from watchdog.events import PatternMatchingEventHandler
except:
    pass

from PyQt5 import QtWidgets, QtCore, QtGui
from src.gui.file_browser_ui import Ui_FileBrowser

from src.utils.utils import FileFilter


# ----------------------------------------------------------------------
def _scan_folder(folder):
    return set([f_name for f_name in os.listdir(folder) if f_name.endswith('.nxs')])

# ----------------------------------------------------------------------
class FileBrowser(QtWidgets.QWidget):
    """
    """

    file_selected = QtCore.pyqtSignal(str)

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """
        """
        super(FileBrowser, self).__init__()
        self._ui = Ui_FileBrowser()
        self._ui.setupUi(self)

        self._parent = parent

        self.file_browser = QtWidgets.QFileSystemModel()
        self.file_browser.setRootPath("")
        self.file_browser.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.NoDot | QtCore.QDir.Files)
        self.file_browser.setNameFilters(file_formats)
        self.file_browser.setNameFilterDisables(False)

        self.file_filter = FileFilter()
        try:
            self.file_filter.setRecursiveFilteringEnabled(True)
        except AttributeError:
            self.file_filter.new_version = False
        self.file_filter.setSourceModel(self.file_browser)

        self._ui.tr_file_browser.setModel(self.file_filter)
        self._ui.tr_file_browser.hideColumn(2)
        self._ui.tr_file_browser.hideColumn(1)

        self._ui.tr_file_browser.header().setSortIndicatorShown(True)
        self._ui.tr_file_browser.setSortingEnabled(True)
        self._ui.tr_file_browser.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)

        try:
            self._my_event_handler = PatternMatchingEventHandler(file_formats, "", False, True)
            self._my_event_handler.on_any_event = self._on_created

            self._my_observer = None
        except:
            self._ui.chk_monitor.setEnabled(False)

        self._file_watch_dog = threading.Thread(target=self._file_watch_dog)
        self._stop_file_watch = False
        self._monitor_folder = None
        self._file_watch_dog.start()

        self._ui.tr_file_browser.doubleClicked.connect(self._open_folder)
        self._ui.le_filter.editingFinished.connect(self._apply_filter)
        self._ui.chk_monitor.clicked.connect(lambda state: self._toggle_watch_dog(state))

        self._ui.cmd_reload.clicked.connect(self._reload)

    # ----------------------------------------------------------------------
    def stop_threads(self):
        self._stop_file_watch = True

    # ----------------------------------------------------------------------
    def _file_watch_dog(self):
        _last_file_list = []
        while not self._stop_file_watch:
            if self._monitor_folder is not None:
                if not _last_file_list:
                    _last_file_list = _scan_folder(self._monitor_folder)
                else:
                    new_files = _scan_folder(self._monitor_folder)
                    new_names = list(new_files - _last_file_list)
                    for name in new_names:
                        self.file_selected.emit(os.path.join(self._monitor_folder, name))
            else:
                _last_file_list = []
            time.sleep(FILE_REFRESH_PERIOD)

    # ----------------------------------------------------------------------
    def _reload(self):
        current_folder = self.file_filter.mapToSource(self._ui.tr_file_browser.rootIndex())
        parent = self.file_filter.mapToSource(self.file_filter.parent(self._ui.tr_file_browser.rootIndex()))
        self.file_browser.setRootPath(self.file_browser.filePath(parent))
        self.file_browser.setRootPath(self.file_browser.filePath(current_folder))

    # ----------------------------------------------------------------------
    def _open_folder(self):

        selected_index = self._ui.tr_file_browser.selectionModel().currentIndex()
        file_index = self.file_filter.mapToSource(selected_index)
        if self.file_browser.isDir(file_index):
            name = str(self.file_browser.filePath(file_index))
            if name.endswith('..'):
                parent = self.file_filter.parent(self.file_filter.parent(selected_index))
                if self.file_filter.parent(parent) == QtCore.QModelIndex():
                    self._ui.tr_file_browser.setRootIndex(QtCore.QModelIndex())
                    self.file_browser.setRootPath("")
                else:
                    self._ui.tr_file_browser.setRootIndex(parent)
                    self.file_browser.setRootPath(self.file_browser.filePath(self.file_filter.mapToSource(parent)))
            else:
                self._ui.tr_file_browser.setRootIndex(selected_index)
                self.file_browser.setRootPath(name)
        else:
            file_name = str(self.file_browser.filePath(file_index))
            if ".nxs" in file_name:
                self.file_selected.emit(file_name)

    # ----------------------------------------------------------------------
    def _apply_filter(self):

        text = str(self._ui.le_filter.text())
        self.file_filter.setFilterRegExp(text)
        self.file_filter.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.file_filter.setDynamicSortFilter(True)

        if text != '':
            self._ui.tr_file_browser.expandAll()
        else:
            self._ui.tr_file_browser.collapseAll()

    # ----------------------------------------------------------------------
    def current_folder(self):
        return self.file_browser.filePath(self.file_filter.mapToSource(self._ui.tr_file_browser.rootIndex()))

    # ----------------------------------------------------------------------
    def _change_observer_folder(self):
        if self._ui.chk_monitor.isChecked():
            if self._my_observer is not None:
                self._my_observer.stop()
                self._my_observer.join()

            folder = self.file_browser.filePath(self.file_filter.mapToSource(self._ui.tr_file_browser.rootIndex()))

            if folder != '':
                self._my_observer = Observer()
                self._my_observer.schedule(self._my_event_handler, folder, recursive=True)
                self._my_observer.start()
                self._monitor_folder = folder
            else:
                self._monitor_folder = None

    # ----------------------------------------------------------------------
    def _toggle_watch_dog(self, state):
        if state:
            self._change_observer_folder()
        else:
            if self._my_observer is not None:
                self._my_observer.stop()
                self._my_observer.join()
                self._my_observer = None
                self._monitor_folder = None

    # ----------------------------------------------------------------------
    def _on_created(self, event):

        if ".nxs" in event.src_path:
            self.file_selected.emit(event.src_path)

    # ----------------------------------------------------------------------
    def load_ui_settings(self, settings):
        try:
            self.restoreGeometry(settings.value("{}/geometry".format(WIDGET_NAME)))
        except Exception as err:
            self._parent.log.error("{} : cannot restore geometry: {}".format(WIDGET_NAME, err))

    # ----------------------------------------------------------------------
    def save_ui_settings(self, settings):
        settings.setValue("{}/geometry".format(WIDGET_NAME), self.saveGeometry())
