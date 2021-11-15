import numpy as np

from data_viewer.tests.test_sardana import _load_file, z_dim, y_dim, x_dim, generate_fake_data, viewer, change_test_dir
from data_viewer.data_sources.sardana.sardana_data_set import SETTINGS


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

def test_roi_functionality(change_test_dir, viewer):

    _load_file(viewer)

    ind, roi_key, dims = viewer.data_pool.add_new_roi()

    assert viewer.data_pool.get_roi_key(ind) == roi_key
    assert viewer.data_pool.get_roi_index(roi_key) == ind

