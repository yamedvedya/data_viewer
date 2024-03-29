# Created by matveyev at 10.11.2021

import time
import traceback

import h5py
import sys

from PyQt5 import QtCore

if 'asapo_consumer' in sys.modules:
    from petra_viewer.data_sources.asapo.asapo_data_set import ASAPODataSet

from petra_viewer.data_sources.beamview.beamview_data_set import BeamLineView
from petra_viewer.data_sources.reciprocal.reciprocal_data_set import ReciprocalScan
from petra_viewer.data_sources.p23scan.p23scan_data_set import P23ScanDataSet
from petra_viewer.data_sources.p1mscan.p1mscan_data_set import P1MScanDataSet
from petra_viewer.data_sources.p11scan.p11scan_data_set import P11ScanDataSet
from petra_viewer.data_sources.test_datasets.test_datasets import Peak1, Peak2, HeavyPeak, \
    ASAPO2DPeak, ASAPO3DPeak, ASAPO4DPeak, BeamView


# ----------------------------------------------------------------------
class Opener(QtCore.QThread):
    """
    separate QThread, that reads new file
    """

    exception = QtCore.pyqtSignal(str, str, str)
    done = QtCore.pyqtSignal()

    # ----------------------------------------------------------------------
    def __init__(self, data_pool, mode, params):
        super(Opener, self).__init__()

        self.data_pool = data_pool
        self.mode = mode
        self.params = params

    # ----------------------------------------------------------------------
    def run(self):
        try:
            if self.mode == 'p23scan':
                finished = False
                while not finished:
                    try:
                        new_file = P23ScanDataSet(self.data_pool, self.params['file_name'])
                        self.data_pool.add_new_entry(self.params['entry_name'], new_file)
                        finished = True

                    except OSError as err:
                        if 'Resource temporarily unavailable' in str(err.args):
                            time.sleep(0.5)
                            print('Waiting for file {}'.format(self.params['file_name']))
                        else:
                            self.exception.emit('Cannot open file',
                                                'Cannot open {}'.format(self.params['file_name']),
                                                self._make_err_msg(err))
                            finished = True

            elif self.mode == 'p11scan':
                new_file = P11ScanDataSet(self.data_pool, self.params['file_name'])
                self.data_pool.add_new_entry(self.params['entry_name'], new_file)

            elif self.mode == 'p1mscan':
                new_file = P1MScanDataSet(self.data_pool, self.params['file_name'])
                self.data_pool.add_new_entry(self.params['entry_name'], new_file)

            elif self.mode == 'stream':
                new_file = ASAPODataSet(self.params['detector_name'], self.params['stream_name'], self.data_pool)
                self.data_pool.add_new_entry(self.params['entry_name'], new_file)

            elif self.mode == 'reciprocal':
                with h5py.File(self.params['file_name'], 'r') as f:
                    new_file = ReciprocalScan(self.data_pool, self.params['file_name'], f)
                    self.data_pool.add_new_entry(self.params['entry_name'], new_file)

            elif self.mode == 'beamline':
                new_file = BeamLineView(self.data_pool, self.params['file_name'])
                self.data_pool.add_new_entry(self.params['entry_name'], new_file)

            elif self.mode == 'test':
                if self.params['test_name'] == 'Peak1':
                    new_file = Peak1(self.data_pool)
                elif self.params['test_name'] == 'Peak2':
                    new_file = Peak2(self.data_pool)
                elif self.params['test_name'] == 'HeavyPeak':
                    new_file = HeavyPeak(self.data_pool)
                elif self.params['test_name'] == 'ASAPO2DPeak':
                    new_file = ASAPO2DPeak(self.data_pool)
                elif self.params['test_name'] == 'ASAPO3DPeak':
                    new_file = ASAPO3DPeak(self.data_pool)
                elif self.params['test_name'] == 'ASAPO4DPeak':
                    new_file = ASAPO4DPeak(self.data_pool)
                elif self.params['test_name'] == 'BeamView':
                    new_file = BeamView(self.data_pool)
                else:
                    raise RuntimeError('Unknown test')

                self.data_pool.add_new_entry(self.params['entry_name'], new_file)

        except Exception as err:
            self.exception.emit(f'Cannot open {self.mode}',
                                f'Cannot open {self.params["entry_name"]}',
                                self._make_err_msg(err)+traceback.format_exc())

        self.done.emit()

    # ----------------------------------------------------------------------
    def _make_err_msg(self, err):
        """

        :param err:
        :return:
        """
        error_msg = f'{err.__class__.__module__}.{err.__class__.__name__}: {err}'
        error_cause = err.__cause__
        while error_cause is not None:
            error_msg += f'\n\nCaused by {error_cause.__class__.__module__}.{error_cause.__class__.__name__}: {error_cause}'
            error_cause = error_cause.__cause__

        return error_msg