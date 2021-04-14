# Created by matveyev at 14.04.2021

import asapo_consumer

from src.widgets.abstract_widget import AbstractWidget

from src.online_table_model import OnlineModel, DeviceModel, ProxyDeviceModel
from src.devices_class import DeviceNode, GroupNode, SerialDeviceNode, ConfigurationNode, check_column

from src.gui.asapo_browser_ui import Ui_ASAPOBrowser


# ----------------------------------------------------------------------
class ASAPOBrowser(AbstractWidget):
    """
    """

    # TEMP:
    host = 'hasep23swt01:8400'
    beamtime = 'asapo_test'
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJjMWY2OG0ydWlkZDE3dWxmaDN1ZyIsInN1YiI6ImJ0X2FzYXBvX3Rlc3QiLCJFeHRyYUNsYWltcyI6eyJBY2Nlc3NUeXBlcyI6WyJyZWFkIl19fQ.zo7ZDfY2sf4o9RYuXpxNR9kHLG594xr-SE5yLoyDC2Q"
    detector = 'lambda'

    # ----------------------------------------------------------------------
    def __init__(self, options):
        """
        """
        super(ASAPOBrowser, self).__init__()
        self._ui = Ui_ASAPOBrowser()
        self._ui.setupUi(self)

        self.asapo_model = OnlineModel()
        self.asapo_model.save_columns_count() # reserved for further

        self.asapo_proxy = ProxyDeviceModel()
        self.asapo_proxy.setSourceModel(self.online_model)
        try:
            self.asapo_proxy.setRecursiveFilteringEnabled(True)
            self.asapo_proxy.new_version = True
        except AttributeError:
            self.asapo_proxy.new_version = False
        self.asapo_proxy.setFilterKeyColumn(-1)

        self._ui.tr_asapo_browser.setModel(self.asapo_proxy)

        self._ui.tr_asapo_browser.doubleClicked.connect(self.display_device)

        self.refresh_view()

    # ----------------------------------------------------------------------
    def refresh_view(self):
        consumer = asapo_consumer.create_consumer(self.ana_device.ASAPO_Host, "", False,
                                                  self.ana_device.attr_Beamtime_read, self.ana_device.ASAPO_Detector,
                                                  self.ana_device.ASAPO_Host, self.ana_device.ASAPO_Timeout)

    # ----------------------------------------------------------------------
    def display_device(self):
        pass

