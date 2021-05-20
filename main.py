# ----------------------------------------------------------------------
# Author:        yury.matveev@desy.de
# ----------------------------------------------------------------------


"""
"""

import sys
from optparse import OptionParser

from PyQt5 import QtWidgets

from src.main_window import DataViewer


# ----------------------------------------------------------------------
def main():
    parser = OptionParser()

    parser.add_option("-d", "--dir", dest="dir",
                      help="start folder")

    parser.add_option("-f", "--file", dest="file",
                      help="open file after start")

    (options, _) = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)

    mainWindow = DataViewer(options)
    mainWindow.show()

    return app.exec_()


# ----------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())
