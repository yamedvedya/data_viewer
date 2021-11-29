# Created by matveyev at 15.02.2021

import os

from PyQt5 import QtWidgets, QtCore

from data_viewer.widgets.abstract_widget import AbstractWidget
from data_viewer.gui.folder_browser_ui import Ui_FolderBrowser

from data_viewer.utils.utils import FileFilter

WIDGET_NAME = 'FolderBrowser'

file_formats = ["*.dat"]


# ----------------------------------------------------------------------
class FolderBrowser(AbstractWidget):
    """
    """

    file_selected = QtCore.pyqtSignal(str, str)

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """
        """
        super(FolderBrowser, self).__init__(parent)
        self._ui = Ui_FolderBrowser()
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

        self._ui.tr_file_browser.doubleClicked.connect(self._open_folder)
        self._ui.le_filter.textEdited.connect(self._apply_filter)

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
            self.file_selected.emit(file_name, 'beam')

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
