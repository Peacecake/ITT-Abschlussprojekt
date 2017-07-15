# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
from PyQt5 import uic, QtWidgets, QtCore, QtGui
import wiimote


class IPlanPy(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.wiimote = None
        self.init_ui()

    def init_ui(self):
        self.ui = uic.loadUi("iplanpy.ui", self)
        self.ui.btn_connect_wiimote.clicked.connect(self.toggle_wiimote_connection)
        self.show()

    def toggle_wiimote_connection(self):
        if self.wiimote is not None:
            self.disconnect_wiimote()
            return
        else:
            self.ui.lbl_wiimote_address.setText("Connecting...")
            results = wiimote.find()
            if len(results) > 0:
                addr, name = results[0]
                self.wiimote = wiimote.connect(addr, name)
                if self.wiimote is None:
                    self.ui.btn_connect_wiimote.setText("Connect")
                else:
                    self.ui.btn_connect_wiimote.setText("Disconnect")
                    self.ui.lbl_wiimote_address.setText("Connected to " + addr)
            else:
                self.ui.btn_connect_wiimote.setText("Connect")

    def disconnect_wiimote(self):
        self.wiimote.disconnect()
        self.wiimote = None
        self.ui.btn_connect_wiimote.setText("Connect")
        self.ui.lbl_wiimote_address.setText("Not connected")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    i_plan_py = IPlanPy()
    sys.exit(app.exec_())
