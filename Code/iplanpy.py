# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
import time
from PyQt5 import uic, QtWidgets, QtCore, QtGui
import wiimote


class IPlanPy(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.wiimote = None
        self.setMouseTracking(True)
        self.init_ui()

    def init_ui(self):
        self.ui = uic.loadUi("iplanpy.ui", self)
        self.ui.btn_connect_wiimote.clicked.connect(self.toggle_wiimote_connection)
        self.ui.btn_scan_wiimotes.clicked.connect(self.scan_for_wiimotes)
        self.ui.btn_toggle_connection_frame.clicked.connect(self.toggle_connection_frame)
        self.show()

    def toggle_connection_frame(self, event):
        self.ui.fr_connection.setVisible(not self.ui.fr_connection.isVisible())

    def scan_for_wiimotes(self, event):
        self.ui.btn_scan_wiimotes.setText("Scanning...")
        self.ui.list_available_wiimotes.clear()
        results = wiimote.find()
        for mote in results:
            address, name = mote
            self.ui.list_available_wiimotes.addItem(address)
        self.ui.btn_scan_wiimotes.setText("Scan")

    def toggle_wiimote_connection(self):
        if self.wiimote is not None:
            self.disconnect_wiimote()
            return
        self.connect_wiimote()

    def connect_wiimote(self):
        self.ui.btn_connect_wiimote.setText("Connecting...")
        current_item = self.ui.list_available_wiimotes.currentItem()
        if current_item is not None:
            address = current_item.text()
            if address is not "":
                try:
                    self.wiimote = wiimote.connect(address)
                except Exception:
                    QtWidgets.QMessageBox.critical(self, "Error", "Could not connect to " + address + "!")
                    self.ui.btn_connect_wiimote.setText("Connect")
                    return

                if self.wiimote is None:
                    self.ui.btn_connect_wiimote.setText("Connect")
                else:
                    self.ui.btn_connect_wiimote.setText("Disconnect")
                    self.ui.lbl_wiimote_address.setText("Connected to " + address)
                    self.wiimote.buttons.register_callback(self.on_wiimote_button)
                    self.wiimote.ir.register_callback(self.on_wiimote_ir)
                    self.wiimote.rumble()

    def disconnect_wiimote(self):
        self.wiimote.disconnect()
        self.wiimote = None
        self.ui.btn_connect_wiimote.setText("Connect")
        self.ui.lbl_wiimote_address.setText("Not connected")

    def on_wiimote_button(self, event):
        if len(event) is not 0:
            button, is_pressed = event[0]
            if is_pressed:
                print("Button " + button + " is pressed")
            else:
                print("Button " + button + " is released")

    def on_wiimote_ir(self, event):
        if len(event) is not 0:
            print(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            if self.ui.fr_card.underMouse() is True:
                self.ui.fr_card.setGeometry(event.pos().x(), event.pos().y(), self.ui.fr_card.size().width(), self.ui.fr_card.size().height())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    i_plan_py = IPlanPy()
    sys.exit(app.exec_())
