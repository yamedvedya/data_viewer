# Created by matveyev at 19.01.2021,

from PyQt5 import QtCore

from src.devices_class import Node, DeviceNode, SerialDeviceNode, GroupNode

headers = ('Name', )

# ----------------------------------------------------------------------
class ASAPOModel(QtCore.QAbstractItemModel):

    root_index = QtCore.QModelIndex()
    drag_drop_signal = QtCore.pyqtSignal(str, QtCore.QModelIndex, int, QtCore.QModelIndex)

    # ----------------------------------------------------------------------
    def __init__(self, root=None):
        if root is None:
            root = Node(None, None, None)
        self.root = root
        self._last_num_column = 0
        self._drag_drop_storage = {}
        super(ASAPOModel, self).__init__()

    # ----------------------------------------------------------------------
    def clear(self):
        if len(self.root.children):
            self.beginRemoveRows(self.root_index, 0, len(self.root.children)-1)
            for row in range(len(self.root.children))[::-1]:
                self.root.remove_child(row)
            self.endRemoveRows()

    # ----------------------------------------------------------------------
    def rowCount(self, parent=None, *args, **kwargs):
        node = self.get_node(parent)
        return node.child_count

    # ----------------------------------------------------------------------
    def columnCount(self, parent=None, *args, **kwargs):
        return len(headers)

    # ----------------------------------------------------------------------
    def index(self, row, column, parent=None, *args, **kwargs):
        node = self.get_node(parent)
        return self.createIndex(row, column, node.child(row))

    # ----------------------------------------------------------------------
    def parent(self, index=None):
        node = self.get_node(index)
        if node.parent is None:
            return QtCore.QModelIndex()
        if node.parent == self.root:
            return QtCore.QModelIndex()
        return self.createIndex(node.parent.row, 0, node.parent)

    # ----------------------------------------------------------------------
    def data(self, index, role=QtCore.Qt.DisplayRole):
        node = self.get_node(index)
        return node.data(index.column(), role)

    # ----------------------------------------------------------------------
    def setData(self, index, value, role):
        node = self.get_node(index)
        if role in [QtCore.Qt.EditRole, QtCore.Qt.CheckStateRole]:
            if node.set_data(index.column(), value, role):
                self.dataChanged.emit(index, index)
                return True
        return False

    # ----------------------------------------------------------------------
    def flags(self, index):
        node = self.get_node(index)
        return node.flags(index.column())

    # ----------------------------------------------------------------------
    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if headers and 0 <= section < len(headers):
                return headers[section]
            return None
        return super(ASAPOModel, self).headerData(section, orientation, role)

    # ----------------------------------------------------------------------
    def get_node(self, index):
        if index and index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self.root

    # ----------------------------------------------------------------------
    def remove(self, index):
        node = self.get_node(index)
        self.beginRemoveRows(index.parent(), node.row, node.row)
        if not index.parent().isValid():
            parent_node = self.root
        else:
            parent_node = index.parent().internalPointer()

        parent_node.remove_child(node.row)
        self.endRemoveRows()

    # ----------------------------------------------------------------------
    def start_insert_row(self, insert_index, index=None, row=0):
        if index is not None:
            if index == insert_index:
                row = 0
            else:
                row = self.get_node(index).row
        row = max(0, row)
        self.beginInsertRows(insert_index, row, row)
        return self.get_node(insert_index), row

    # ----------------------------------------------------------------------
    def start_adding_row(self, num_elements, insert_index=0):
        self.beginInsertRows(self.root_index, insert_index, insert_index + num_elements-1)

    # ----------------------------------------------------------------------
    def finish_row_changes(self):
        self.endInsertRows()

    # ----------------------------------------------------------------------
    def filter_row(self, index, value_to_look):
        node = self.get_node(index)
        return node.filter_row(value_to_look)

    # ----------------------------------------------------------------------
    def save_columns_count(self):
        self._last_num_column = self.columnCount()

    # ----------------------------------------------------------------------
    def add_columns(self):
        num_columns = self.columnCount()

        if num_columns > self._last_num_column:
            self.beginInsertColumns(self.root_index, self._last_num_column, num_columns - 1)
            self.endInsertColumns()
        elif num_columns < self._last_num_column:
            self.beginRemoveRows(self.root_index, num_columns, self._last_num_column - 1)
            self.endRemoveColumns()

        self._last_num_column = num_columns


# ----------------------------------------------------------------------
class ProxyDeviceModel(QtCore.QSortFilterProxyModel):

    new_version = True

    # ----------------------------------------------------------------------
    def filterAcceptsRow(self, source_row, source_parent):

        if self.new_version:
            return super(ProxyDeviceModel, self).filterAcceptsRow(source_row, source_parent)
        else:
            match = False
            my_index = self.sourceModel().index(source_row, 0, source_parent)
            for row in range(self.sourceModel().rowCount(my_index)):
                match |= self.filterAcceptsRow(row, my_index)

            match |= super(ProxyDeviceModel, self).filterAcceptsRow(source_row, source_parent)

            return match

