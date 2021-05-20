# Created by matveyev at 10.05.2021

import numpy as np
import xrayutilities as xu
import matplotlib as mpl
import matplotlib.pyplot as plt
import p23lib
import h5py
import pylab as pl
from scipy import ndimage

SETTINGS = {'detector_gap_window_size': 7,
            'detector_gaps': [255, 515, 775, 1035, 1295]}

class Converter(object):

    def __init__(self, scan_data, mask, flat_field=None):

        self._original_data = scan_data
        self._mask = mask
        self._flat_filed = flat_field

    def _make_original_data_correction(self):

        for igap in (255, 515, 775, 1035, 1295):
            self._mask[:, igap:igap + 6] = False

        mask = mask[roi[1:]]
        mask += (ff < 0.3) + (ff > 2.5)
        mask += np.isnan(scan_data.sum(0))

        ### Interpolate dead pixels
        data = data.astype(float)
        weights = ndimage.uniform_filter(1. - mask, size=windowsize)
        # weights = ndimage.gaussian_filter(1.-mask, 1)
        for imnum in range(data.shape[0]):
            img = data[imnum]
            img /= ff
            img[mask] = 0
            img_f = ndimage.uniform_filter(img, size=windowsize)
            #     img_f = ndimage.gaussian_filter(img, 1)
            img[mask] = (img_f / weights)[mask]
            data[imnum] = img / monitor[imnum] * atten


class