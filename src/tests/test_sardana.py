import os

import h5py
import pytest

from time import sleep, time
import numpy as np
from PyQt5 import QtWidgets

from mock import MagicMock

from src.main_window import DataViewer
from src.utils.option_parser import get_options
from src.data_sources.sardana.sardana_data_set import SETTINGS

TIMEOUT_FOR_FILE_OPEN = 500000

x_dim = 100
y_dim = 200
z_dim = 11


# ----------------------------------------------------------------------
def generate_fake_data():

    frame = np.zeros((y_dim, x_dim))
    for ind in range(y_dim):
        frame[ind] = np.cos(np.linspace(0, 2*np.pi, x_dim))
    for ind in range(x_dim):
        frame[:, ind] *= np.cos(np.linspace(0, 2*np.pi, y_dim))

    data_cube = np.zeros((z_dim, y_dim, x_dim))
    for ind, scale in enumerate(np.cos(np.linspace(0, 2*np.pi, z_dim))):
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
    assert 'test007' in viewer.data_pool._files_data
    assert viewer.data_pool._files_data['test007']._data_shape == (z_dim, y_dim, x_dim)
    assert viewer.data_pool._files_data['test007']._scan_length == z_dim
    assert 'point_nb' in viewer.data_pool._files_data['test007']._additional_data['scanned_values'] and \
           'omega' in viewer.data_pool._files_data['test007']._additional_data['scanned_values']
    assert np.all(viewer.data_pool._files_data['test007']._additional_data['point_nb'] == np.arange(11))
    assert np.all(viewer.data_pool._files_data['test007']._additional_data['omega'] == np.linspace(1, 2, 11))
    assert viewer.data_pool._files_data['test007']._detector_folder == 'test/lmbd'
    assert viewer.data_pool._files_data['test007']._detector == 'lmbd'


# ----------------------------------------------------------------------
def test_2d_functionality(change_test_dir, viewer):

    _load_file(viewer)

    section = viewer.data_pool.get_section('test007')
    for axis, axis_lim in enumerate([z_dim, y_dim, x_dim]):
        assert section[axis]['max'] == axis_lim
        assert section[axis]['range_limit'] == axis_lim

    for axis, axis_lim in enumerate([z_dim, y_dim, x_dim]):
        assert viewer.data_pool.get_max_frame_along_axis('test007', axis) == axis_lim - 1

    omega = np.linspace(1, 2, 11)
    assert np.all(viewer.data_pool.get_additional_data('test007', 'omega') == omega)

    SETTINGS['displayed_param'] = 'omega'
    assert viewer.data_pool.get_frame_for_value('test007', 0, omega[2]) == 2
    assert viewer.data_pool.get_value_for_frame('test007', 0, 2) == ('omega', omega[2])

    fake_data_cube = generate_fake_data()
    old_max = [section[axis]['max'] for axis in range(3)]

    for section_axis, do_rotate, axes_set in zip([0, 0, 1, 2],
                                                 [True, False, False, True],
                                                 [['', 'Y', 'X'], ['', 'X', 'Y'], ['X', '', 'Y'], ['Y', 'X', '']]):
        for ind, axis in enumerate(axes_set):
            section[ind]['axis'] = axis

        viewer.data_pool.save_section('test007', section)
        cut_data = np.sum(fake_data_cube.take(indices=[0], axis=section_axis), axis=section_axis)
        if do_rotate:
            cut_data = np.transpose(cut_data)
        assert np.all(np.isclose(viewer.data_pool.get_2d_picture('test007'), cut_data))

        section[section_axis]['integration'] = True
        section[section_axis]['max'] = 5
        viewer.data_pool.save_section('test007', section)

        cut_data = np.sum(fake_data_cube.take(indices=range(0, 5), axis=section_axis), axis=section_axis)
        if do_rotate:
            cut_data = np.transpose(cut_data)
        assert np.all(np.isclose(viewer.data_pool.get_2d_picture('test007'), cut_data))

        for axis in range(3):
            section[axis]['max'] = 5
        viewer.data_pool.save_section('test007', section)

        cut_data = np.sum(fake_data_cube[:5, :5, :5], axis=section_axis)
        if do_rotate:
            cut_data = np.transpose(cut_data)

        assert np.all(np.isclose(viewer.data_pool.get_2d_picture('test007'), cut_data))

        for ind, lim in enumerate(old_max):
            section[ind]['max'] = lim
        section[section_axis]['integration'] = False

        viewer.data_pool.save_section('test007', section)

# # ----------------------------------------------------------------------
# def test_roi_functionality(change_test_dir, viewer):
#
#     _load_file(viewer)
#
#     ind, roi_key = viewer.data_pool.add_new_roi()




