import json
import os
import pytest
from time import sleep
import numpy as np
from qtpy import QtWidgets
from mock import MagicMock

import AsapoWorker
from AsapoWorker.asapo_receiver import AsapoMetadataReceiver
from AsapoWorker.data_handler import serialize_ndarray
from unittest.mock import create_autospec

from src.main_window import DataViewer
from src.widgets.asapo_browser import ASAPOBrowser
from src.data_sources.asapo.asapo_data_set import ASAPODataSet
from optparse import OptionParser


@pytest.fixture
def message_data():
    return create_message_data((10, 5))


@pytest.fixture
def viewer(message_data):
    parser = OptionParser()

    parser.add_option("-d", "--dir", dest="dir",
                      help="start folder")

    parser.add_option("-f", "--file", dest="file",
                      help="open file after start")

    parser.add_option("--asapo", action='store_true', dest='asapo', help="include ASAPO scan")
    parser.add_option("--sardana", action='store_true', dest='sardana', help="include Sardana scan")
    parser.add_option("--beam", action='store_true', dest='beam', help="include Beamline view")
    parser.add_option("--def_file", dest="def_file", help="open file after start")
    parser.add_option("--def_stream", dest="def_stream", help="open file after start")
    (options, _) = parser.parse_args(['--asapo'])

    AsapoWorker.asapo_receiver.AsapoMetadataReceiver = MagicMock(return_value=True)
    ASAPOBrowser.set_settings = MagicMock(return_value=True)
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(['/home/karnem/workspace/data_viewer/main.py', '--asapo'])

    main = DataViewer(options)

    ASAPODataSet._setup_receiver = MagicMock(return_value=True)
    ASAPODataSet.receiver = create_autospec(AsapoWorker.asapo_receiver.SerialAsapoReceiver)
    ASAPODataSet.receiver.set_start_id = MagicMock(return_value=True)
    ASAPODataSet.meta_only = False
    ASAPODataSet._mode = 'file'
    ASAPODataSet.receiver.get_next = MagicMock(return_value=message_data)
    ASAPODataSet.receiver.get_current_size = MagicMock(return_value=10)

    yield main


def create_message_data(shape):
    data = serialize_ndarray(np.ones(shape)).getvalue()
    mdata = {'_id': 1,
             'size': 5392,
             'name': 'processed/tmp/20211015T_111706/mod_0_msg_0.h5',
             'timestamp': 1634289427969925572,
             'source': '192.168.1.27:20493',
             'buf_id': 0, 'dataset_substream': 0,
             'meta': {},
             'stream': '29',
             'data_source': 'test011_5_100_50'}
    return data, mdata


def test_load_stream(viewer, message_data):

    viewer.data_pool.open_stream("test007", "1", {})
    sleep(3)  # sleep for sometime to open stream

    assert len(viewer.data_pool._files_data) == 1
    assert 'test007/1' in viewer.data_pool._files_data
    assert viewer.data_pool._files_data['test007/1']._data_shape == [10, 10, 5]
    assert len(viewer.data_pool._files_data['test007/1']._additional_data['metadata']) == 1
    assert viewer.data_pool._files_data['test007/1']._additional_data['metadata'][0] == message_data[1]

    selection = viewer.data_pool.get_section("test007/1")
    assert len(selection) == 3
    assert selection[0]['range_limit'] == 3
    assert selection[1]['range_limit'] == 0


def test_add_file(viewer, message_data):

    viewer.data_pool.open_stream("test007", "1", {})
    sleep(3)  # sleep for sometime to open stream
    viewer.frame_view.add_file("test007/1", "second")
    assert viewer.frame_view.current_file() == "test007/1"
    assert viewer.data_pool.get_all_axes_limits() == [[0, 9], [0, 9], [0, 4]]

