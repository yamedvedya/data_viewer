# ----------------------------------------------------------------------
# Author:        yury.matveev@desy.de
# ----------------------------------------------------------------------


"""
"""

import sys

from PyQt5 import QtWidgets

from src.main_window import DataViewer
from src.utils.option_parser import get_options

# ----------------------------------------------------------------------
def main():

    app = QtWidgets.QApplication(sys.argv)

    mainWindow = DataViewer(get_options(sys.argv))
    mainWindow.show()

    return app.exec_()


# ----------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())
