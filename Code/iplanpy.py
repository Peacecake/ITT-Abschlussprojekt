# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
import os
import ast
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget
import wiimote
from vectortransform import VectorTransform
from gestureclassifier import GestureClassifier
from card import Card


class IPlanPy(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.CONNECTIONS_FILE = "wii.motes"
        self.wiimote = None
        self.my_vector_transform = VectorTransform()
        self.classifier = GestureClassifier()
        self.classifier.register_callback(self.handle_shake_gesture)
        self.setMouseTracking(True)
        self.all_cards = []
        self.bg_colors = ['background-color: rgb(85, 170, 255)', 'background-color: red', 'background-color: green']
        self.init_ui()
        self.load_available_charts()
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
        self.ui.fr_save_and_load.setVisible(False)
        self.ui.btn_connect_wiimote.clicked.connect(self.toggle_wiimote_connection)
        self.ui.btn_scan_wiimotes.clicked.connect(self.scan_for_wiimotes)
        self.ui.btn_toggle_connection_frame.clicked.connect(self.toggle_connection_frame)
        self.ui.btn_toggle_save_and_load_frame.clicked.connect(self.toggle_save_and_load_frame)
        self.ui.btn_load_chart.clicked.connect(self.load_chart)
        self.ui.btn_save.clicked.connect(self.on_btn_save_chart)

        self.ui.delete_card.setVisible(True)

        self.show()

    def toggle_connection_frame(self, event):
        value = not self.ui.fr_connection.isVisible()
        self.ui.fr_connection.setVisible(value)
        if value is True:
            self.ui.fr_connection.raise_()
            self.ui.fr_save_and_load.setVisible(not value)
        else:
            self.ui.fr_connection.lower()

    def toggle_save_and_load_frame(self, event):
        value = not self.ui.fr_save_and_load.isVisible()
        self.ui.fr_save_and_load.setVisible(value)
        if value is True:
            self.ui.fr_save_and_load.raise_()
            self.ui.fr_connection.setVisible(not value)
        else:
            self.ui.fr_save_and_load.lower()

    def load_chart(self, event):
        file_name = self.ui.list_chart_selection.currentItem()
        if file_name is not None:
            card_infos = self.get_card_info_from_file(file_name.text())
            if card_infos is not None:
                self.remove_all_cards()
                self.create_card_from_file(card_infos)
                self.toggle_save_and_load_frame(None)

    def create_card_from_file(self, card_infos):
        for info in card_infos:
            info = info.split(";")
            card = Card(self)
            card.title_field.setText(info[0])
            card.content_field.setText(ast.literal_eval(info[1]))
            card.setGeometry(int(info[2]), int(info[3]), card.size().width(), card.size().height())
            self.all_cards.append(card)

    def get_card_info_from_file(self, file_name):
        try:
            with open(file_name) as file:
                return file.readlines()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Warning", "Could not load chart!\nAdditional information:\n" + e)
            return None

    def remove_all_cards(self):
        for card in self.all_cards:
            card.delete()
        self.all_cards.clear()

    def on_btn_save_chart(self, event):
        file_name = self.ui.le_save_as.text()
        if file_name is not "":
            if os.path.isfile(file_name + ".chart") is True:
                res = QtWidgets.QMessageBox.question(self, "Warning", "Overwrite existing file?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
                if res == QtWidgets.QMessageBox.Yes:
                    self.save_chart(file_name)
                else:
                    return
            else:
                self.save_chart(file_name)
                QtWidgets.QMessageBox.information(self, "Success", "Chart saved!")
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Choose a name first!")

    def save_chart(self, file_name):
        self.ui.le_save_as.setText("")
        with open(file_name + ".chart", "w") as new_file:
            self.write_card_data(new_file)
        self.load_available_charts()

    def write_card_data(self, file):
        for card in self.all_cards:
            title = card.title_field.text()
            content = repr(card.content_field.toPlainText())
            x_pos = card.pos().x()
            y_pos = card.pos().y()
            file.write(title + ";" + content + ";" + str(x_pos) + ";" + str(y_pos) + ";\n")

    def load_available_charts(self):
        self.ui.list_chart_selection.clear()
        for file in os.listdir(os.getcwd()):
            if file.endswith(".chart"):
                self.ui.list_chart_selection.addItem(file)

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
            if self.ui.lbl_new_card.underMouse():
                self.make_new_card(event)
        # super(IPlanPy, self).mousePressEvent(event)
        # print("mousePressEvent" + str(self.__mousePressPos) + ' ' + str(self.__mouseMovePos))

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            card_under_mouse = self.get_card_under_mouse()
            if card_under_mouse is not None:
                card_under_mouse.setGeometry(event.pos().x(), event.pos().y(),
                                             card_under_mouse.size().width(), card_under_mouse.size().height())

        if event.buttons() == QtCore.Qt.LeftButton:
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.__mouseMovePos = globalPos

    def get_card_under_mouse(self):
        for c in self.all_cards:
            if c.underMouse() is True:
                return c
        return None

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
            self.lbl_new_card.setStyleSheet('background-color: blue')

    def make_new_card(self, event):
        card = Card(self)
        card.setGeometry(event.pos().x() - 10, event.pos().y() - 10, card.size().width(), card.size().height())
        self.all_cards.append(card)

    def register_if_deleted(self, posX, posY):
        delete_button_pos_x1 = self.delete_card.x()
        delete_button_pos_x2 = delete_button_pos_x1 + self.delete_card.width()
        delete_button_pos_y1 = self.delete_card.y()
        delete_button_pos_y2 = delete_button_pos_y1 + self.delete_card.height()
        if delete_button_pos_x2 >= posX >= delete_button_pos_x1 and delete_button_pos_y1 <= posY <= delete_button_pos_y2:
            card = self.get_card_under_mouse()
            card.delete()
            self.all_cards.remove(card)

    def handle_shake_gesture(self):
        print("shake detected")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    i_plan_py = IPlanPy()
    sys.exit(app.exec_())
