# Created by matveyev at 23.02.2021

from PyQt5 import QtCore, QtGui

device_view_role = QtCore.Qt.UserRole + 1

# ----------------------------------------------------------------------
class Node(object):

    def __init__(self, parent, info=None, parent_info=None, row=-1):

        self.parent = parent

        self.children = []
        self.headers = []

        if info is not None:
            if isinstance(info, dict):
                self.info = info
            else:
                self.info = deepcopy(info.attrib)
                for child in info:
                    if child.tag not in ['group', 'serial_device', 'single_device']:
                        self.info[child.tag] = child.text
        else:
            self.info = {}

        if self.parent is not None:
            self.parent_info = parent.info
        else:
            self.parent_info = {}

        if parent_info is not None:
            self.parent_info = parent_info
            self.part_of_serial_device = True

        all_attribs = list(self.info.keys()) + list(self.parent_info.keys())
        for name in headers.device_headers:
            if name in all_attribs:
                self.headers.append(name)

        for name in all_attribs:
            if name not in self.headers:
                self.headers.append(name)
            if name not in headers.possible_headers:
                headers.possible_headers.append(name)

        if self.parent is not None:
            self.parent.add_child(self, row)

    # ----------------------------------------------------------------------
    def _refill_headers(self):
        self.headers = []
        all_headers = []
        for child in self.children:
            all_headers += child.headers

        all_headers = list(set(all_headers))

        for name in headers.device_headers:
            if name in all_headers:
                self.headers.append(name)

        for name in all_headers:
            if name not in self.headers:
                self.headers.append(name)

    # ----------------------------------------------------------------------
    def add_child(self, child, row=-1):
        if row == -1:
            self.children.append(child)
        else:
            self.children.insert(row, child)
        child.parent = self
        self._refill_headers()

    # ----------------------------------------------------------------------
    def remove_child(self, row):
        del self.children[row]
        self._refill_headers()

    # ----------------------------------------------------------------------
    @property
    def row(self):
        if self.parent is None:
            return 0
        return self.parent.children.index(self)

    # ----------------------------------------------------------------------
    @property
    def child_item_count(self):
        return len(self.headers)

    # ----------------------------------------------------------------------
    @property
    def child_count(self):
        return len(self.children)

    # ----------------------------------------------------------------------
    def child(self, row):
        try:
            return self.children[row]
        except IndexError:
            return None

    # ----------------------------------------------------------------------
    def data(self, column, role):

        if role >= device_view_role:
            role -= device_view_role
            key = self.parent.headers[column].lower()
        else:
            key = headers.online_headers[column].lower()

        if role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
            if key in self.info:
                return self.info[key]
            elif self.part_of_serial_device:
                if key in self.parent_info:
                    return self.parent_info[key]
            elif key == 'device':
                return self.class_name()
            else:
                return ''

        elif role == QtCore.Qt.FontRole:
            my_font = QtGui.QFont()
            if self.check_status() != QtCore.Qt.Unchecked:
                my_font.setBold(True)
            else:
                my_font.setItalic(True)
            return my_font

        elif role == QtCore.Qt.ForegroundRole:
            if not self.check_status() != QtCore.Qt.Unchecked:
                return QtGui.QColor(QtCore.Qt.gray)
            else:
                return QtCore.QVariant()

        elif role == QtCore.Qt.CheckStateRole:
            if column == check_column:
                return self.check_status()
            else:
                return QtCore.QVariant()

    # ----------------------------------------------------------------------
    def flags(self, column):

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    # ----------------------------------------------------------------------
    def class_name(self):
        return ''

    # ----------------------------------------------------------------------
    def class_type(self):
        return ''

    # ----------------------------------------------------------------------
    def get_my_path(self):
        return self.parent.get_my_path() + '/' + self.data(headers.device_headers.index('name'), QtCore.Qt.DisplayRole)

    # ----------------------------------------------------------------------
    def filter_row(self, search_value):
        for value in self.info.values():
            if search_value in value:
                return True
        if self.part_of_serial_device:
            for value in self.parent_info.values():
                if search_value in value:
                    return True
        return False




# ----------------------------------------------------------------------
class FrameNode(Node):

    # ----------------------------------------------------------------------
    def class_type(self):
        return 'single_device'

    # ----------------------------------------------------------------------
    def export_devices(self, dev_list):
        if self.is_activated():
            dev_list.append(self)


# ----------------------------------------------------------------------
class ScanNode(Node):

    # ----------------------------------------------------------------------
    def class_name(self):
        return 'Group'

    # ----------------------------------------------------------------------
    def class_type(self):
        return 'group'

    # ----------------------------------------------------------------------
    def check_status(self):

        if not self.is_activated():
            return QtCore.Qt.Unchecked
        else:
            all_active = True
            for device in self.children:
                all_active *= device.is_all_active()
            if all_active:
                return QtCore.Qt.Checked
            else:
                return QtCore.Qt.PartiallyChecked

    # ----------------------------------------------------------------------
    def export_devices(self, dev_list):
        for children in self.children:
            children.export_devices(dev_list)

    # ----------------------------------------------------------------------
    def accept_add(self):
        return True
