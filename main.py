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

    parser.add_option("--asapo", action='store_true', dest='asapo', help="include ASAPO scan")
    parser.add_option("--sardana", action='store_true', dest='sardana', help="include Sardana scan")
    parser.add_option("--beam", action='store_true', dest='beam', help="include Beamline view")

    (options, _) = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)

    mainWindow = DataViewer(options)
    mainWindow.show()

    return app.exec_()


# ----------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())
