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
from connectionmanager import ConnectionManager
from card import Card


class IPlanPy(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.CONNECTIONS_FILE = "wii.motes"
        self.card_id = 0
        self.wiimote = None
        self.ir_callback_count = 0
        self.old_x_coord = 0
        self.old_y_coord = 0
        self.all_cards = []

        self.my_vector_transform = VectorTransform()
        self.classifier = GestureClassifier()
        self.connections = ConnectionManager()
        self.classifier.register_callback(self.handle_shake_gesture)

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
        self.setMouseTracking(True)
        self.ui.fr_save_and_load.setVisible(False)
        self.ui.btn_connect_wiimote.clicked.connect(self.toggle_wiimote_connection)
        self.ui.btn_scan_wiimotes.clicked.connect(self.scan_for_wiimotes)
        self.ui.btn_toggle_connection_frame.clicked.connect(self.toggle_connection_frame)
        self.ui.btn_toggle_save_and_load_frame.clicked.connect(self.toggle_save_and_load_frame)
        self.ui.btn_load_chart.clicked.connect(self.load_chart)
        self.ui.btn_save.clicked.connect(self.on_btn_save_chart)
        self.ui.btn_new_chart.clicked.connect(self.on_btn_new_chart)
        self.show()

    def on_btn_new_chart(self, event):
        self.remove_all_cards()
        self.connections.connections.clear()
        self.card_id = 0
        self.update()

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
            card_infos, conn_info = self.get_card_info_from_file(file_name.text())
            if card_infos is not None:
                self.card_id = 0
                self.remove_all_cards()
                self.connections.connections.clear()
                self.update()
                self.create_card_from_file(card_infos)
                self.create_conn_from_file(conn_info)
                self.toggle_save_and_load_frame(None)

    def create_card_from_file(self, card_infos):
        ids = []
        for info in card_infos:
            info = info.split(";")
            ids.append(int(info[0]))
            card = Card(self, int(info[0]), self.string_to_bool(info[5]))
            card.title_field.setText(info[1])
            card.content_field.setText(ast.literal_eval(info[2]))
            card.move_to(int(info[3]), int(info[4]))
            card.set_background_color(card.available_colors[int(info[6])])
            self.all_cards.append(card)
        self.card_id = max(ids) + 1

    def create_conn_from_file(self, conn_info):
        for info in conn_info:
            info = info.split(";")
            id1 = info[0]
            id2 = info[1]
            card1 = None
            card2 = None
            for card in self.all_cards:
                if str(card.id) == id1:
                    card1 = card
                if str(card.id) == id2:
                    card2 = card
            self.connections.connect((card1, card2))
        self.update()

    def string_to_bool(self, str):
        return str == "True"

    def get_card_info_from_file(self, file_name):
        try:
            conn_found = False
            card_info = []
            conn_info = []
            with open(file_name) as file:
                for line in file:
                    if line == "-\n":
                        conn_found = True
                        continue
                    if conn_found is False:
                        card_info.append(line)
                    else:
                        conn_info.append(line)
                return card_info, conn_info
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
            cid = card.id
            title = card.title_field.text()
            content = repr(card.content_field.toPlainText())
            x_pos = card.pos().x()
            y_pos = card.pos().y()
            card_type = str(card.has_text_field)
            color = card.color_index
            file.write(str(cid) + ";" + title + ";" + content + ";" + str(x_pos) +
                       ";" + str(y_pos) + ";" + card_type + ";" + color + ";\n")
        file.write("-\n")
        for conn in self.connections.connections:
            c1, c2 = conn
            file.write(str(c1.id) + ";" + str(c2.id) + ";\n")

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
                card = self.get_card_under_mouse()
                if button == "B":
                    mouse_press_event = QtGui.QMouseEvent(
                        QtCore.QEvent.MouseButtonPress,
                        self.mapFromGlobal(QtCore.QPoint(QtGui.QCursor.pos().x(), QtGui.QCursor.pos().y())),
                        QtCore.Qt.LeftButton,
                        QtCore.Qt.LeftButton,
                        QtCore.Qt.NoModifier)
                    QtCore.QCoreApplication.postEvent(self, mouse_press_event)
                if button == 'Up' and (card is not None):
                    card.next_color()
                if button == "Down" and (card is not None):
                    card.previous_color()
                if (button == "Left" or button == "Right") and (card is not None):
                    card.toggle_type()
                if button == "Minus":
                    self.connections.remove_last_connection()
                    self.update()
            else:
                if button == "B":
                    mouse_release_event = QtGui.QMouseEvent(
                        QtCore.QEvent.MouseButtonRelease,
                        self.mapFromGlobal(QtGui.QCursor.pos()),
                        QtCore.Qt.LeftButton,
                        QtCore.Qt.LeftButton,
                        QtCore.Qt.NoModifier
                    )
                    QtCore.QCoreApplication.postEvent(self, mouse_release_event)
                print("Button " + button + " is released")

    def on_wiimote_ir(self, event):
        if self.ir_callback_count % 3 == 0:
            # if len(event) > 4:
             #   signals = []
              #  for signal in event:
               #     if signal["size"] is 1 or signal["size"] is 2:
                #        signals.append(signal)
            # else:
            signals = event
            if len(signals) >= 4:
                print(signals)
                vectors = []
                for e in signals:
                    vectors.append((e["x"], e["y"]))
                x, y = self.my_vector_transform.transform(vectors, self.size().width(), self.size().height())
                QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(x, y)))
        self.ir_callback_count = self.ir_callback_count + 1

    def on_wiimote_accelerometer(self, event):
        self.classifier.add_accelerometer_data(event[0], event[1], event[2])

    def keyPressEvent(self, event):
        alt_modifier = (event.modifiers() & QtCore.Qt.AltModifier) != 0
        card = self.get_card_under_mouse()
        if card is not None:
            if (alt_modifier and event.key() == QtCore.Qt.Key_Up):
                card.next_color()
            if (alt_modifier and event.key() == QtCore.Qt.Key_Down):
                card.previous_color()
            if alt_modifier and (event.key() == QtCore.Qt.Key_Right):
                card.toggle_type()
            if alt_modifier and (event.key() == QtCore.Qt.Key_Left):
                card.toggle_type()
        if alt_modifier and (event.key() == QtCore.Qt.Key_Backspace):
            self.connections.remove_last_connection()
            self.update()

    def mousePressEvent(self, event):
        if self.ui.btn_toggle_connection_frame.underMouse() is True:
            self.toggle_connection_frame(event)
        elif self.ui.btn_toggle_save_and_load_frame.underMouse() is True:
            self.toggle_save_and_load_frame(event)
        elif self.ui.btn_new_chart.underMouse() is True:
            self.on_btn_new_chart(event)

        actual_card = self.get_card_under_mouse()
        if actual_card is not None:
            self.clicked_card_pos = actual_card.pos().x(), actual_card.pos().y()
            self.clicked_card_center = actual_card.center()
        self.__mousePressPos = None
        self.__mouseMovePos = None

        if event.button() == QtCore.Qt.LeftButton:
            for c in self.all_cards:
                c.unfocus()

            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()
            if self.ui.lbl_new_card.underMouse():
                self.make_new_card(event)

            card = self.get_card_under_mouse()
            if card is not None:
                card.focus()

    def mouseMoveEvent(self, event):
        if (self.wiimote is not None and self.wiimote.buttons["B"]) or (event.buttons() & QtCore.Qt.LeftButton):
            focused_card = self.get_focused_card()
            if focused_card is not None:
                self.handle_card_movement(event, focused_card)

        if event.buttons() == QtCore.Qt.LeftButton:
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.__mouseMovePos = globalPos

        self.old_y_coord = event.pos().y()
        self.old_x_coord = event.pos().x()

    # Returns the card under the mouse if there is one.
    def get_card_under_mouse(self):
        for c in self.all_cards:
            if c.underMouse() is True:
                return c
        return None

    # Returns the focused card if there is one focused.
    def get_focused_card(self):
        for c in self.all_cards:
            if c.is_focused is True:
                return c
        return None

    # Handles the card movement and collisions with the main window frame.
    def handle_card_movement(self, mouse_event, card):
        self.update()
        new_x = card.pos().x() + mouse_event.pos().x() - self.old_x_coord
        new_y = card.pos().y() + mouse_event.pos().y() - self.old_y_coord
        if not card.collides_with(self.ui.fr_control_container, new_x, new_y) and not card.hits_window_frame(self, new_x, new_y):
            card.move_to(new_x, new_y)
        else:
            # TODO: Doesnt work yet
            QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(self.old_x_coord, self.old_y_coord)))

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            self.check_release_position(event.pos().x(), event.pos().y())
            if moved.manhattanLength() > 3:
                event.ignore()
                return

    # Checks if the release position of the Drag and Drop requires a delete action or new connection.
    def check_release_position(self, posX, posY):
        self.check_for_delete(posX, posY)
        self.check_for_new_connection(posX, posY)

    # Builds a new card of the class Card.
    def make_new_card(self, event):
        card = Card(self, self.card_id)
        new_y = self.ui.fr_control_container.size().height() + 3
        card.move_to(event.pos().x(), new_y)
        self.all_cards.append(card)
        self.card_id = self.card_id + 1

    # Checks if card was released over the delete card button.
    def check_for_delete(self, posX, posY):
        card = self.get_card_under_mouse()
        if card is not None:
            x, y = card.center()
            # Cards center has to be over the delete button in order to delete it.
            if card.collides_with(self.ui.delete_card, x, y):
                self.connections.delete_all_card_connections(card)
                card.delete()
                self.all_cards.remove(card)
                self.update()

    # Checks if card was released over another card.
    def check_for_new_connection(self, posX, posY):
        current_card = self.get_card_under_mouse()
        if current_card is not None and len(self.all_cards) > 1:
            for c in self.all_cards:
                # Can collide with itself
                if c is current_card:
                    continue
                # Builds a new connection between the two collided cards.
                if current_card.collides(c):
                    self.connections.connect((current_card, c))
                    x, y = self.clicked_card_pos
                    current_card.move_to(x, y)
                    border = "1px solid black"
                    current_card.set_border(border)
                    c.set_border(border)
                    self.update()

    # Draw connections on every update
    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor(0, 0, 0))
        painter.setPen(pen)
        for conn in self.connections.connections:
            card1, card2 = conn
            x1, y1 = card1.center()
            x2, y2 = card2.center()
            painter.drawLine(x1, y1, x2, y2)
        painter.end()

    # Callback of gestureclassifier. Gets called when classifier detects "shake" gesture.
    # Deletes all connections from currently focued card.
    def handle_shake_gesture(self):
        for card in self.all_cards:
            if card.is_focused is True:
                self.connections.delete_all_card_connections(card)
                self.update()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    i_plan_py = IPlanPy()
    sys.exit(app.exec_())
