import io
import numpy as np
import hdf5plugin
import h5py
import zlib
from skimage.io import imread


def get_image(data, metadata):
    if 'liveimage' in metadata["name"]:
        image = zlib.decompress(data)
        if metadata['meta']['frame_depth'] == 24:
            image = np.frombuffer(image, dtype=np.uint32).copy()
        else:
            image = np.frombuffer(image, dtype=np.uint16).copy()

        image = np.reshape(image, (metadata['meta']['frame_height'],
                                   metadata['meta']['frame_width']))
        return image

    typ = metadata["name"].rpartition(".")[-1]
    if typ == "tif":
        buf = io.BytesIO(data)
        image = imread(buf)
    elif typ == "numpy":
        shape = metadata["meta"]["shape"]
        dtype = metadata["meta"]["dtype"]
        image = np.frombuffer(data, dtype=dtype).reshape(shape)
    elif typ == "nxs":
        buf = io.BytesIO(data)
        h5file = h5py.File(buf)
        image = get_default_data(h5file)
    elif typ == "txt":
        delimiter = metadata["meta"].get("delimiter", ' ')
        image = np.loadtxt(io.BytesIO(data), delimiter=delimiter)
    elif typ == "h5":
        buf = io.BytesIO(data)
        h5file = h5py.File(buf, 'r')
        image = h5file["ndarray"][()]
    else:
        raise ValueError("Unknown extension: " + typ)
    return image


def serialize_ndarray(array):
    """
    Serialize ndarray into compressed h5 in-memory file

    :param array: numpy.ndarray to be serialized
    :return buf: BytesIO with compressed h5 file
    """
    buf = io.BytesIO()
    with h5py.File(buf, 'w') as f:
        f.create_dataset("ndarray", data=array,
                         **hdf5plugin.Blosc(cname="lz4"))
    return buf


def get_default_data(group):
    default_name = group.attrs.get("default", None)
    if default_name:
        return get_default_data(group[default_name])
    signal_name = group.attrs.get("signal", "data")
    signal = group[signal_name]
    if signal.ndim == 1:
        axis_name = group.attrs.get("axes", "axis")[0]
        axis = group[axis_name]
        return np.vstack((axis, signal)).T
    else:
        return np.asarray(signal)


def get_filename_parts(metadata):
    name = metadata["name"]
    base, sep, index_and_ext = name.rpartition("-")
    index, ext = index_and_ext.split(".")
    return base, int(index), ext
