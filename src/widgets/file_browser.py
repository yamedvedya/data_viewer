# Created by matveyev at 15.02.2021

import os

try:
    from watchdog.observers import Observer
    from watchdog.events import PatternMatchingEventHandler
except:
    pass

try:
    import PyTango
except:
    pass

from PyQt5 import QtWidgets, QtCore

from src.widgets.abstract_widget import AbstractWidget
from src.gui.file_browser_ui import Ui_FileBrowser

from src.utils.utils import FileFilter, read_mask_file, read_ff_file
from src.data_sources.sardana.sardana_data_set import SETTINGS

WIDGET_NAME = 'DataBrowser'

file_formats = ["*.nxs", "*.h5"]

FILE_REFRESH_PERIOD = 1


# ----------------------------------------------------------------------
def _scan_folder(folder):
    return set([f_name for f_name in os.listdir(folder) if f_name.endswith('.nxs')])


# ----------------------------------------------------------------------
class FileBrowser(AbstractWidget):
    """
    """

    file_selected = QtCore.pyqtSignal(str)

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """
        """
        super(FileBrowser, self).__init__(parent)
        self._ui = Ui_FileBrowser()
        self._ui.setupUi(self)

        self.file_browser = QtWidgets.QFileSystemModel()
        self.file_browser.setRootPath("")
        self.file_browser.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.NoDot | QtCore.QDir.Files)
        self.file_browser.setNameFilters(file_formats)
        self.file_browser.setNameFilterDisables(False)

        self._eid = None
        self._door_server = None

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

        self._ui.tr_file_browser.doubleClicked.connect(self._open_folder)
        self._ui.le_filter.textEdited.connect(self._apply_filter)
        self._ui.chk_monitor.clicked.connect(self._toggle_watch_dog)
        self._ui.chk_door.clicked.connect(self._toggle_watch_door)

        self._ui.cmd_reload.clicked.connect(self._reload)

    # ----------------------------------------------------------------------
    def _reload(self):
        current_folder = self.file_filter.mapToSource(self._ui.tr_file_browser.rootIndex())
        parent = self.file_filter.mapToSource(self.file_filter.parent(self._ui.tr_file_browser.rootIndex()))
        self.file_browser.setRootPath(self.file_browser.filePath(parent))
        self.file_browser.setRootPath(self.file_browser.filePath(current_folder))

    # ----------------------------------------------------------------------
    def set_settings(self, settings):
        try:
            if 'door_address' in settings:
                if self._eid is not None:
                    self._toggle_watch_door(False)
                    _need_to_reset = True
                else:
                    _need_to_reset = False
                try:
                    self._door_server = PyTango.DeviceProxy(settings['door_address'])
                    if _need_to_reset:
                        self._toggle_watch_door(True)
                except:
                    self._parent.report_error('Cannot connect to {}'.format(settings['door_address']))

            if 'default_mask' in settings:
                SETTINGS['enable_mask'] = True
                SETTINGS['mask'] = read_mask_file(settings['default_mask'])
                SETTINGS['mask_file'] = settings['default_mask']

            if 'default_ff' in settings:
                SETTINGS['enable_ff'] = True
                SETTINGS['ff'] = read_ff_file(settings['default_ff'])
                SETTINGS['ff_file'] = settings['default_ff']
                if 'min_ff' in settings:
                    SETTINGS['ff_min'] = settings['min_ff']
                if 'max_ff' in settings:
                    SETTINGS['ff_max'] = settings['max_ff']

        except Exception as err:
            self._parent.log.error("{} : cannot apply settings: {}".format(WIDGET_NAME, err), exc_info=True)

    # ----------------------------------------------------------------------
    def safe_close(self):
        if self._eid is not None:
            self._door_server.unsubscribe_event(self._eid)

    # ----------------------------------------------------------------------
    def _toggle_watch_door(self, state):
        if state:
            if self._door_server is not None:
                self._eid = self._door_server.subscribe_event('Info', PyTango.EventType.CHANGE_EVENT, self.new_info)
        else:
            if self._eid is not None:
                self._door_server.unsubscribe_event(self._eid)
                self._eid = None

    # ----------------------------------------------------------------------
    def new_info(self, event):
        if not event.err:
            if event.attr_value.value is not None:
                info = str(event.attr_value.value[0])
                if info.startswith("Operation saved in") and info.endswith('(nxs)'):
                    self.file_selected.emit(info.strip("Operation saved in").strip('(nxs)').strip())

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
            self.file_selected.emit(file_name)

    # ----------------------------------------------------------------------
    def _apply_filter(self, text):

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
        for type in file_formats:
            if type in event.src_path:
                self.file_selected.emit(event.src_path)
