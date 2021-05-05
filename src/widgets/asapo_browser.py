# Created by matveyev at 14.04.2021
import numpy as np

WIDGET_NAME = 'ASAPO Browser'

import asapo_consumer

from PyQt5 import QtCore

from src.widgets.abstract_widget import AbstractWidget

from src.asapo_browser.asapo_table_model import ASAPOModel, ProxyModel
from src.asapo_browser.asapo_entries_class import StreamNode, DetectorNode
from src.asapo_browser.asapo_table_headers import headers
from AsapoWorker.asapo_receiver import AsapoMetadataReceiver


from src.gui.asapo_browser_ui import Ui_ASAPOBrowser


# ----------------------------------------------------------------------
class ASAPOBrowser(AbstractWidget):
    """
    """

    stream_selected = QtCore.pyqtSignal(str, str) # detector, stream

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """
        """
        super(ASAPOBrowser, self).__init__(parent)
        self._ui = Ui_ASAPOBrowser()
        self._ui.setupUi(self)

        self.asapo_model = ASAPOModel()
        self.asapo_model.save_columns_count() # reserved for further

        self.asapo_proxy = ProxyModel()
        self.asapo_proxy.setSourceModel(self.asapo_model)
        try:
            self.asapo_proxy.setRecursiveFilteringEnabled(True)
            self.asapo_proxy.new_version = True
        except AttributeError:
            self.asapo_proxy.new_version = False
        self.asapo_proxy.setFilterKeyColumn(-1)

        self.asapo_proxy.setDynamicSortFilter(True)

        self._ui.tr_asapo_browser.setModel(self.asapo_proxy)
        self._ui.tr_asapo_browser.header().setSortIndicatorShown(True)
        self._ui.tr_asapo_browser.setSortingEnabled(True)
        self._ui.tr_asapo_browser.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)
        self._ui.tr_asapo_browser.doubleClicked.connect(self.display_stream)

        self._ui.le_filter.textEdited.connect(self._apply_filter)

        self._ui.chk_refresh.clicked.connect(self._toggle_refresh)
        self._ui.chk_auto_add.clicked.connect(self._add_open)

        self._ui.sb_sec.editingFinished.connect(self._new_period)

        self._ui.chk_time_filter.clicked.connect(self._time_filter)
        self._ui.dte_from.editingFinished.connect(self._new_time_range)
        self._ui.dte_to.editingFinished.connect(self._new_time_range)

        self.host = ''
        self.beamtime = ''
        self.token = ''
        self._max_depth = 100

        self._auto_open = False

        self._refresh_timer = QtCore.QTimer(self)
        self._refresh_timer.timeout.connect(self.refresh_view)

    # ---------------------------------------------------------------------
    def _toggle_refresh(self, state):
        self._ui.sb_sec.setEnabled(state)
        if state:
            self._refresh_timer.start(int(self._ui.sb_sec.value())*1000)
        else:
            self._refresh_timer.stop()

    # ---------------------------------------------------------------------
    def _add_open(self, state):
        self._auto_open = state

    # ---------------------------------------------------------------------
    def _new_period(self, value):
        if self._refresh_timer.isActive():
            self._refresh_timer.stop()
            self._refresh_timer.start(int(value) * 1000)

    # ---------------------------------------------------------------------
    def _new_time_range(self):
        self.asapo_proxy.filter_from = self._ui.dte_from.dateTime().toSecsSinceEpoch()
        self.asapo_proxy.filter_to = self._ui.dte_to.dateTime().toSecsSinceEpoch()
        self.asapo_proxy.invalidate()

    # ----------------------------------------------------------------------
    def _time_filter(self, state):
        self.asapo_proxy.filter_time = state
        self._ui.dte_from.setEnabled(state)
        self._ui.dte_to.setEnabled(state)
        self._get_time_range()
        self.asapo_proxy.invalidate()

    # ----------------------------------------------------------------------
    def set_settings(self, settings):
        try:
            self.host = settings['host']
            self.beamtime = settings['beamtime']
            self.token = settings['token']
            self._max_depth = int(settings['max_streams'])
            self.reset_detectors([detector.strip() for detector in settings['detectors'].split(';')])
            self.refresh_view(auto_open=False)
        except Exception as err:
            self._parent.log.error("{} : cannot apply settings: {}".format(WIDGET_NAME, err))

    # ----------------------------------------------------------------------
    def reset_detectors(self, new_detector_list):

        current_detectors = [child.my_name() for child in self.asapo_model.root.all_child()]

        _detectors_to_remove = list(set(current_detectors) - set(new_detector_list))

        for detector in _detectors_to_remove:
            ind = current_detectors.index(detector)
            self.asapo_model.remove(self.asapo_model.index(ind, 0))

        _detectors_to_add = list(set(new_detector_list) - set(current_detectors))
        for detector in _detectors_to_add:
            ind = new_detector_list.index(detector)
            self.asapo_model.start_adding_detector(ind)
            DetectorNode(self.asapo_model.root, ind, {'name': detector})
            self.asapo_model.finish_row_changes()

        pass

    # ----------------------------------------------------------------------
    def refresh_view(self, auto_open=True):
        for detector_ind, detector in enumerate([child.my_name() for child in self.asapo_model.root.all_child()]):
            detector_index = self.asapo_model.index(detector_ind, 0)
            detector_node = self.asapo_model.get_node(detector_index)
            model_streams_names = [child.my_name() for child in detector_node.all_child()]

            meta_data_receiver = AsapoMetadataReceiver(asapo_consumer.create_consumer(self.host, "", False,
                                                                                      self.beamtime, detector,
                                                                                      self.token, 1000))
            asapo_streams = meta_data_receiver.get_stream_list()[-self._max_depth:]
            possible_name_fields = headers['Name']
            asapo_streams_names = []
            asapo_streams_indexes = []
            for ind, stream in enumerate(asapo_streams):
                for name in possible_name_fields:
                    if name in stream:
                        asapo_streams_names.append(stream[name])
                        asapo_streams_indexes.append(ind)

            _streams_to_delete = list(set(model_streams_names) - set(asapo_streams_names))
            for stream in _streams_to_delete:
                ind = model_streams_names.index(stream)
                self.asapo_model.remove(self.asapo_model.index(ind, 0, detector_index))

            _streams_to_add = list(set(asapo_streams_names) - set(model_streams_names))
            _streams_to_add.sort()
            for stream in _streams_to_add:
                ind = asapo_streams_names.index(stream)
                self.asapo_model.start_insert_row(detector_index, ind)
                StreamNode(detector_node, ind, asapo_streams[asapo_streams_indexes[ind]])
                self.asapo_model.finish_row_changes()
                if auto_open and self._auto_open:
                    self.stream_selected.emit(detector_node.my_name(), stream)

        self._get_time_range()

    # ----------------------------------------------------------------------
    def _get_time_range(self):
        min_time = 9223372036854775807
        max_time = -9223372036854775808
        for detector in self.asapo_model.root.all_child():
            for stream in detector.all_child():
                min_time = np.min([min_time, stream.time_stamp])
                max_time = np.max([max_time, stream.time_stamp])

        time = QtCore.QDateTime()
        if not self.asapo_proxy.filter_time:
            self._ui.dte_from.setDateTime(time.fromSecsSinceEpoch(min_time))
            self.asapo_proxy.filter_from = min_time

            self._ui.dte_to.setDateTime(time.fromSecsSinceEpoch(max_time))
            self.asapo_proxy.filter_to = max_time

    # ----------------------------------------------------------------------
    def _apply_filter(self, text):

        self.asapo_proxy.setFilterRegExp(text)
        self.asapo_proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        if text != '':
            self._ui.tr_asapo_browser.expandAll()
        else:
            self._ui.tr_asapo_browser.collapseAll()

    # ----------------------------------------------------------------------
    def display_stream(self, index):
        selected_node = self.asapo_model.get_node(self.asapo_proxy.mapToSource(index))
        if isinstance(selected_node, StreamNode):
            self.stream_selected.emit(selected_node.parent.my_name(), selected_node.my_name())

