#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Author:        sebastian.piec@mail.desy.de
# Last modified: 2017, November 7
# ----------------------------------------------------------------------

"""Basic info dialog
"""

from datetime import datetime
import os

from PyQt5 import QtWidgets

from petra_viewer.gui.about_dialog_ui import Ui_AboutDialog
from petra_viewer.release import Release


# ----------------------------------------------------------------------
class AboutDialog(QtWidgets.QDialog):
    """
    """
    SOURCE_DIR = "./petra_viewer"
    DATETIME = "%Y-%m-%d %H:%M:%S"

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent)

        self._ui = Ui_AboutDialog()
        self._ui.setupUi(self)

        release = Release()

        self._ui.lb_version.setText(f"Version: {release.version_long}")
        self._ui.lb_authors.setText(f"Authors:\n{release.author_lines}")



