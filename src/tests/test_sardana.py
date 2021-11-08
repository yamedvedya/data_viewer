import os

import h5py
import pytest

from time import sleep, time
import numpy as np
from PyQt5 import QtWidgets

from mock import MagicMock

from src.main_window import DataViewer
from src.utils.option_parser import get_options

TIMEOUT_FOR_FILE_OPEN = 500000

x_dim = 100
y_dim = 200
z_dim = 11


# ----------------------------------------------------------------------
def generate_fake_data():

    frame = np.zeros((y_dim, x_dim))
    for ind in range(y_dim):
        frame[ind] = np.sin(np.linspace(0, np.pi, x_dim))
    for ind in range(x_dim):
        frame[:, ind] *= np.sin(np.linspace(0, np.pi, y_dim))

    data_cube = np.zeros((z_dim, y_dim, x_dim))
    for ind, scale in enumerate(np.sin(np.linspace(0, np.pi, z_dim))):
        data_cube[ind] = frame*scale

    return data_cube


# ----------------------------------------------------------------------
def generate_fake_file():

    data = {'scan': {'data': {'lmbd' : None,
                             'point_nb': np.arange(11),
                             'omega': np.linspace(1, 2, 11)}
                    },
            'entry': {'instrument':{'detector': {'data': generate_fake_data()}}}
            }

    data_set = MagicMock()
    data_set.filename = 'test'
    data_set.__getitem__.side_effect = data.__getitem__
    data_set.__iter__.side_effect = data.__iter__

    return data_set


# ----------------------------------------------------------------------
@pytest.fixture(scope="function")
def change_test_dir(request):
    os.chdir(os.path.dirname(os.path.dirname(request.fspath.dirname)))
    yield
    os.chdir(request.config.invocation_dir)


# ----------------------------------------------------------------------
@pytest.fixture
def viewer():

    h5py.File = MagicMock(return_value=generate_fake_file())
    os.listdir = MagicMock(return_value=['test.nxs'])

    app = QtWidgets.QApplication([os.getcwd() + 'main.py', '--sardana'])
    if app is None:
        app = QtWidgets.QApplication([os.getcwd() + 'main.py', '--sardana'])

    main = DataViewer(get_options(['--sardana']))

    yield main


# ----------------------------------------------------------------------
def _load_file(viewer):

    viewer.data_pool.open_file("test007.nxs")
    start_time = time()
    while viewer.data_pool.open_file_in_progress and time() - start_time < TIMEOUT_FOR_FILE_OPEN:
        sleep(0.1)  # sleep for sometime to open stream

    assert not viewer.data_pool.open_file_in_progress


# ----------------------------------------------------------------------
def test_load_file(change_test_dir, viewer):

    _load_file(viewer)

    assert len(viewer.data_pool._files_data) == 1
