# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
from PyQt5 import uic, QtWidgets, QtCore, QtGui
import wiimote
from vectortransform import VectorTransform
from gestureclassifier import GestureClassifier


class IPlanPy(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.wiimote = None
        self.my_vector_transform = VectorTransform(self.size().width(), self.size().height())
        self.classifier = GestureClassifier()
        self.classifier.register_observer(self)
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
                    self.wiimote.accelerometer.register_callback(self.on_wiimote_accelerometer)
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
        if len(event) is 4:
            vectors = []
            for e in event:
                vectors.append((e["x"], e["y"]))
            x, y = self.my_vector_transform.transform(vectors)
            QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(x, y)))

    def on_wiimote_accelerometer(self, event):
        self.classifier.add_accelerometer_data(event[0], event[1], event[2])

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            self.register_if_deleted(event.pos().x(), event.pos().y())
            if moved.manhattanLength() > 3:
                event.ignore()
                return

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_B:
            print("Key B")
        if event.key() == QtCore.Qt.Key_A:
            print("Key A")

        if event.type() == QtCore.QEvent.HoverMove:
            print('hover' + str(event))
            self.new_card.setStyleSheet('background-color: blue')

    def make_new_card(self):
        print("new card!")

    def register_if_deleted(self, posX, posY):
        delete_button_pos_x1 = self.delete_card.x()
        delete_button_pos_x2 = delete_button_pos_x1 + self.delete_card.width()
        delete_button_pos_y1 = self.delete_card.y()
        delete_button_pos_y2 = delete_button_pos_y1 + self.delete_card.height()
        print('pos' + str(posX), str(posY))
        print('buttonpos' + str(delete_button_pos_x1), str(delete_button_pos_x2), str(delete_button_pos_y1), str(delete_button_pos_y2))
        if(posX >= delete_button_pos_x1 and posX <= delete_button_pos_x2 and posY >= delete_button_pos_y1 and posY <= delete_button_pos_y2):
            print('DELETE!')

    def handle_shake_gesture(self):
        print("shake detected")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    i_plan_py = IPlanPy()
    sys.exit(app.exec_())
