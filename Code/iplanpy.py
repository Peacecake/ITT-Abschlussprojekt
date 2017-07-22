# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QLineEdit, QPlainTextEdit
import wiimote
from vectortransform import VectorTransform
from gestureclassifier import GestureClassifier


class IPlanPy(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.CONNECTIONS_FILE = "wii.motes"
        self.wiimote = None
        self.my_vector_transform = VectorTransform()
        self.classifier = GestureClassifier()
        self.classifier.register_callback(self.handle_shake_gesture)
        self.setMouseTracking(True)
        self.bg_colors = ['background-color: rgb(85, 170, 255)', 'background-color: red', 'background-color: green']
        self.init_ui()
        self.display_known_wiimotes()

    def display_known_wiimotes(self):
        content = self.get_all_known_connections()
        for address in content:
            self.ui.list_available_wiimotes.addItem(address)
        if len(content) > 0:
            self.ui.list_available_wiimotes.setCurrentRow(0)

    def save_connection_address(self, address):
        content = self.get_all_known_connections()
        if address not in content:
            with open(self.CONNECTIONS_FILE, "a") as f:
                f.write("\n" + address)
                f.close()

    def get_all_known_connections(self):
        with open(self.CONNECTIONS_FILE) as f:
            content = f.readlines()
            f.close()
        return [x.strip() for x in content]

    def init_ui(self):
        self.ui = uic.loadUi("iplanpy.ui", self)
        self.ui.btn_connect_wiimote.clicked.connect(self.toggle_wiimote_connection)
        self.ui.btn_scan_wiimotes.clicked.connect(self.scan_for_wiimotes)
        self.ui.btn_toggle_connection_frame.clicked.connect(self.toggle_connection_frame)

        self.ui.new_card.clicked.connect(self.make_new_card)
        self.ui.delete_card.setVisible(True)

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
        if len(results) > 0:
            self.ui.list_available_wiimotes.setCurrentRow(0)
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
                    self.ui.fr_connection.setVisible(False)
                    self.save_connection_address(address)

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
            x, y = self.my_vector_transform.transform(vectors, self.size().width(), self.size().height())
            QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(x, y)))

    def on_wiimote_accelerometer(self, event):
        self.classifier.add_accelerometer_data(event[0], event[1], event[2])

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            pos = QtGui.QCursor.pos()
            widget_at = QApplication.widgetAt(pos)
            style = str(widget_at.styleSheet())
            print(style)
            if 'rgb(85, 170, 255)' in style:
                self.fr_card.setStyleSheet(self.bg_colors[1])
            elif 'red' in style:
                self.fr_card.setStyleSheet(self.bg_colors[2])
            else:
                self.fr_card.setStyleSheet(self.bg_colors[0])
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()
        # super(IPlanPy, self).mousePressEvent(event)
        # print("mousePressEvent" + str(self.__mousePressPos) + ' ' + str(self.__mouseMovePos))

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            if self.ui.fr_card.underMouse() is True:
                self.ui.fr_card.setGeometry(event.pos().x(), event.pos().y(),
                                            self.ui.fr_card.size().width(), self.ui.fr_card.size().height())
            else:
                widget_at = QApplication.widgetAt(QtGui.QCursor.pos())
                if widget_at.underMouse() is True:
                    widget_at.setGeometry(event.pos().x(), event.pos().y(),
                                          widget_at.size().width(), widget_at.size().height())

        if event.buttons() == QtCore.Qt.LeftButton:
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.__mouseMovePos = globalPos

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
        self.new_frame = QFrame(self)
        self.new_frame.setStyleSheet('background-color: rgb(85, 170, 255)')
        self.new_frame.resize(281, 181)
        self.new_frame.setVisible(True)

        self.new_title = QLineEdit(self)
        self.new_title.resize(131, 29)
        self.new_title.move(72, 10)
        self.new_title.setParent(self.new_frame)
        self.new_title.setStyleSheet('background-color: white')
        self.new_title.setVisible(True)

        self.new_text_edit = QPlainTextEdit(self)
        self.new_text_edit.resize(261, 121)
        self.new_text_edit.move(10, 50)
        self.new_text_edit.setParent(self.new_frame)
        self.new_text_edit.setStyleSheet('background-color: white')
        self.new_text_edit.setVisible(True)

        self.new_frame.setMouseTracking(True)

        self.show()

    def register_if_deleted(self, posX, posY):
        delete_button_pos_x1 = self.delete_card.x()
        delete_button_pos_x2 = delete_button_pos_x1 + self.delete_card.width()
        delete_button_pos_y1 = self.delete_card.y()
        delete_button_pos_y2 = delete_button_pos_y1 + self.delete_card.height()
        if(posX >= delete_button_pos_x1 and posX <= delete_button_pos_x2 and posY >= delete_button_pos_y1 and posY <= delete_button_pos_y2):
            pos = QtGui.QCursor.pos()
            widget_at = QApplication.widgetAt(pos)
            widget_at.setParent(None)

    def handle_shake_gesture(self):
        print("shake detected")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    i_plan_py = IPlanPy()
    sys.exit(app.exec_())
