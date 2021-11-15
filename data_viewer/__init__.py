import sys
import os
import logging
import traceback
import time

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

from PyQt5 import QtWidgets

# Add path to icon_rc filecp set
sys.path.append(f"{os.path.dirname(__file__)}/gui")

from data_viewer.main_window import DataViewer
from data_viewer.utils.option_parser import get_options
from .version import __version__


def excepthook(exc_type, exc_value, traceback_obj):
    """
    Global function to catch unhandled exceptions. This function will result in an error dialog which displays the
    error information.

    :param exc_type: exception type
    :param exc_value: exception value
    :param traceback_obj: traceback object
    :return:
    """
    separator = '-' * 80
    log_path = f"{os.path.expanduser('~')}/data_viewer_error.log"
    time_string = time.strftime("%Y-%m-%d, %H:%M:%S")
    tb_info_file = StringIO()
    traceback.print_tb(traceback_obj, None, tb_info_file)
    tb_info_file.seek(0)
    tb_info = tb_info_file.read()
    errmsg = '%s: \n%s' % (str(exc_type), str(exc_value))
    sections = [separator, time_string, separator, errmsg, separator, tb_info]
    msg = '\n'.join(sections)
    try:
        f = open(log_path, "a")
        f.write(msg)
        f.close()
    except IOError:
        pass

    msg_box = QtWidgets.QMessageBox()
    msg_box.setModal(False)
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)
    msg_box.setText(msg)
    msg_box.setInformativeText(msg)
    msg_box.setWindowTitle("Error")
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.show()


def setup_logger(args):
    log_level = "DEBUG"
    format = (
        "%(asctime)s %(filename)s:%(lineno)d "
        "%(levelname)-8s %(message)s")

    filename = f"{os.path.expanduser('~')}/data_viewer.log"
    print(f"Logs to file: {filename}")
    logging.basicConfig(level=log_level, format=format, filename=filename)
    logging.info("Log level set to %s", log_level)


def main():
    args = get_options(sys.argv)
    setup_logger(args)

    app = QtWidgets.QApplication([])
    sys.excepthook = excepthook

    mainWindow = DataViewer(args)
    mainWindow.show()

    app.exec_()
    del app


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    main()
