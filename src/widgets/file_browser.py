# Created by matveyev at 15.02.2021

WIDGET_NAME = 'DataBrowser'

file_formats = ["*.nxs"]

try:
    from watchdog.observers import Observer
    from watchdog.events import PatternMatchingEventHandler
except:
    pass

from PyQt5 import QtWidgets, QtCore, QtGui
from src.gui.file_browser_ui import Ui_FileBrowser

from src.utils.utils import FileFilter

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

        try:
            self._my_event_handler = PatternMatchingEventHandler(file_formats, "", False, True)
            self._my_event_handler.on_created = self._on_created

            self._my_observer = None
        except:
            self._ui.chk_monitor.setEnabled(False)

        self._ui.tr_file_browser.setModel(self.file_filter)
        self._ui.tr_file_browser.hideColumn(2)
        self._ui.tr_file_browser.hideColumn(1)

        self._ui.tr_file_browser.doubleClicked.connect(self._open_folder)
        self._ui.le_filter.editingFinished.connect(self._apply_filter)
        self._ui.chk_monitor.clicked.connect(lambda state: self._toggle_watch_dog(state))

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
                else:
                    self._ui.tr_file_browser.setRootIndex(parent)
            else:
                self._ui.tr_file_browser.setRootIndex(selected_index)
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

    # ----------------------------------------------------------------------
    def _toggle_watch_dog(self, state):
        if state:
            self._change_observer_folder()
        else:
            if self._my_observer is not None:
                self._my_observer.stop()
                self._my_observer.join()
                self._my_observer = None

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