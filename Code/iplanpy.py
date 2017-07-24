# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
import os
import ast
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPainter, QColor, QPen
import wiimote
from vectortransform import VectorTransform
from gestureclassifier import GestureClassifier
from card import Card


class IPlanPy(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.CONNECTIONS_FILE = "wii.motes"
        self.main_windows = self
        self.wiimote = None
        self.old_x_coord = 0
        self.old_y_coord = 0
        self.my_vector_transform = VectorTransform()
        self.classifier = GestureClassifier()
        self.classifier.register_callback(self.handle_shake_gesture)
        self.setMouseTracking(True)
        self.all_cards = []
        self.all_lines = []
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
            QMessageBox.warning(self, "Warning", "Could not load chart!\nAdditional information:\n" + e)
            return None

    def remove_all_cards(self):
        for card in self.all_cards:
            card.delete()
        self.all_cards.clear()

    def on_btn_save_chart(self, event):
        file_name = self.ui.le_save_as.text()
        if file_name is not "":
            if os.path.isfile(file_name + ".chart") is True:
                msg = "Overwrite existing file?"
                res = QMessageBox.question(self, "Warning", msg, QMessageBox.Yes, QMessageBox.No)
                if res == QMessageBox.Yes:
                    self.save_chart(file_name)
                else:
                    return
            else:
                self.save_chart(file_name)
                QMessageBox.information(self, "Success", "Chart saved!")
        else:
            QMessageBox.warning(self, "Warning", "Choose a name first!")

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
                    QMessageBox.critical(self, "Error", "Could not connect to " + address + "!")
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
                if button == "A":
                    self.on_wiimote_button_press()
                print("Button " + button + " is pressed")
                if button == 'A' and self.ui.lbl_new_card.underMouse():
                    print('New Card with Wii')
                    # Doesnt work because: QObject::setParent: Cannot set parent, new parent is in a different thread

                    # card = Card(self)
                    # new_y = self.ui.fr_control_container.size().height()
                    # card.setGeometry(0, new_y, card.size().width(), card.size().height())
                    # self.all_cards.append(card)
                if button == 'B' and (self.get_card_under_mouse() is not None):
                    self.get_card_under_mouse().next_color()
                    # print('Color changed with Wii')
                    # print(str(self.get_card_under_mouse()))
                    # self.changeColor(self.get_card_under_mouse())
            else:
                print("Button " + button + " is released")

    def on_wiimote_button_press(self):
        card = Card(self.main_windows)
        new_y = self.ui.fr_control_container.size().height()
        card.move_to(QtGui.QCursor.pos().x(), new_y)
        self.all_cards.append(card)
        print(self)

    def on_wiimote_ir(self, event):
        if len(event) is 4:
            vectors = []
            for e in event:
                vectors.append((e["x"], e["y"]))
            x, y = self.my_vector_transform.transform(vectors, self.size().width(), self.size().height())
            QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(x, y)))

    def on_wiimote_accelerometer(self, event):
        self.classifier.add_accelerometer_data(event[0], event[1], event[2])

    def changeColor(self, curr_card):
        style = str(curr_card.styleSheet())
        print(style)
        if 'rgb(85, 170, 255)' in style:
            curr_card.setStyleSheet(self.bg_colors[1])
        elif 'red' in style:
            curr_card.setStyleSheet(self.bg_colors[2])
        else:
            curr_card.setStyleSheet(self.bg_colors[0])

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            '''
            curr_card = self.get_card_under_mouse()
            style = str(curr_card.styleSheet())
            print(style)
            if 'rgb(85, 170, 255)' in style:
                curr_card.setStyleSheet(self.bg_colors[1])
            elif 'red' in style:
                curr_card.setStyleSheet(self.bg_colors[2])
            else:
                curr_card.setStyleSheet(self.bg_colors[0])
        '''
            self.get_card_under_mouse().next_color()
            # self.changeColor(self.get_card_under_mouse())

        self.__mousePressPos = None
        self.__mouseMovePos = None

        if event == "A" or event.button() == QtCore.Qt.LeftButton:
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
                self.handle_card_movement(event, card_under_mouse)

        if event.buttons() == QtCore.Qt.LeftButton:
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.__mouseMovePos = globalPos

        self.old_y_coord = event.pos().y()
        self.old_x_coord = event.pos().x()

    def get_card_under_mouse(self):
        for c in self.all_cards:
            if c.underMouse() is True:
                return c
        return None

    def handle_card_movement(self, mouse_event, card):
        new_x = card.pos().x() + mouse_event.pos().x() - self.old_x_coord
        new_y = card.pos().y() + mouse_event.pos().y() - self.old_y_coord
        if not card.collides_with(self.ui.fr_control_container, new_x, new_y) and not card.hits_window_frame(self, new_x, new_y):
            card.move_to(new_x, new_y)
        else:
            # Doesnt work yet
            QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(self.old_x_coord, self.old_y_coord)))

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            self.check_release_pos(event.pos().x(), event.pos().y())
            if moved.manhattanLength() > 3:
                event.ignore()
                return

    def check_release_pos(self, posX, posY):
        self.register_if_deleted(posX, posY)
        self.register_if_drawline(posX, posY)

    def make_new_card(self, event):
        card = Card(self)
        new_y = self.ui.fr_control_container.size().height() + 3
        card.move_to(event.pos().x(), new_y)
        self.all_cards.append(card)

    def register_if_deleted(self, posX, posY):
        delete_button_pos_x1 = self.delete_card.x()
        delete_button_pos_x2 = delete_button_pos_x1 + self.delete_card.width()
        delete_button_pos_y1 = self.delete_card.y()
        delete_button_pos_y2 = delete_button_pos_y1 + self.delete_card.height()
        if delete_button_pos_x2 >= posX >= delete_button_pos_x1 and delete_button_pos_y1 <= posY <= delete_button_pos_y2:
            card = self.get_card_under_mouse()
            try:
                card.delete()
                self.all_cards.remove(card)
            except:
                print('That did not work!')

    def register_if_drawline(self, posX, posY):
        print('register drawline')
        current_card = self.get_card_under_mouse()
        if current_card is not None:
            for i in range(len(self.all_cards)):
                '''
                card_w = self.all_cards[i].width()
                card_h = self.all_cards[i].height()
                card_pos_x1 = self.all_cards[i].x()
                card_pos_x2 = card_pos_x1 + card_w
                card_pos_y1 = self.all_cards[i].y()
                card_pos_y2 = card_pos_y1 + card_h
                if(posX >= card_pos_x1 and posX <= card_pos_x2 and posY >= card_pos_y1 and posY <= card_pos_y2):
                '''
                if current_card.collides_with(self.all_cards[i], current_card.pos().x(), current_card.pos().y()):
                    new_line = current_card.center(), self.all_cards[i].center()
                    print(str(new_line))
                    self.all_lines.append(new_line)
                    border = "1px solid black"
                    current_card.set_border(border)
                    self.all_cards[i].set_border(border)
                    self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor(0, 0, 0))
        painter.setPen(pen)
        for i in range(len(self.all_lines)):
            start, target = self.all_lines[i]
            x1, y1 = start
            x2, y2 = target
            print(str(start) + '' + str(target))
            painter.drawLine(x1, y1, x2, y2)
        painter.end()

    def handle_shake_gesture(self):
        print("shake detected")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    i_plan_py = IPlanPy()
    sys.exit(app.exec_())
