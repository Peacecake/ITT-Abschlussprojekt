# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QFrame, QLineEdit, QTextEdit


class Card(QFrame):
    def __init__(self, parent):
        super(Card, self).__init__()
        self.setParent(parent)
        self.DEFAULT_COLOR = "rgb(85, 170, 255)"
        self.DEFAULT_BORDER = "none"
        self.available_colors = [self.DEFAULT_COLOR, 'red', 'green', "yellow"]
        self.color_index = 0
        self.color = self.available_colors[self.color_index]
        self.border = self.DEFAULT_BORDER
        self.title_field = QLineEdit()
        self.content_field = QTextEdit()
        self.setup_frame()
        self.setup_title()
        self.setup_content()
        self.update_stylesheet()
        self.setMouseTracking(True)

    def next_color(self):
        self.color_index = self.color_index + 1
        if len(self.available_colors) is self.color_index:
            self.color_index = 0
        self.set_background_color(self.available_colors[self.color_index])

    def set_background_color(self, color):
        self.color = color
        self.update_stylesheet()

    def set_border(self, border):
        self.border = border
        self.update_stylesheet()

    def update_stylesheet(self):
        self.setStyleSheet("background-color: " + self.color + "; border: " + self.border + ";")

    def setup_frame(self):
        self.resize(281, 181)
        self.setVisible(True)

    def setup_title(self):
        self.title_field.resize(131, 29)
        self.title_field.move(72, 10)
        self.title_field.setParent(self)
        self.title_field.setStyleSheet('background-color: white')
        self.title_field.setVisible(True)

    def setup_content(self):
        self.content_field.resize(261, 121)
        self.content_field.move(10, 50)
        self.content_field.setParent(self)
        self.content_field.setStyleSheet('background-color: white')
        self.content_field.setVisible(True)

    def delete(self):
        self.setParent(None)
        # Todo: remove connections

    def center(self):
        x = self.pos().x() + (self.size().width() / 2)
        y = self.pos().y() + (self.size().height() / 2)
        return x, y

    def move_to(self, x, y):
        self.setGeometry(x, y, self.size().width(), self.size().height())

    def collides_with(self, widget, new_x, new_y):
        x1 = widget.pos().x()
        x2 = x1 + widget.size().width()
        y1 = widget.pos().y()
        y2 = y1 + widget.size().height()
        if x1 <= new_x <= x2 and y1 <= new_y <= y2:
            return True
        else:
            return False

    def hits_window_frame(self, window_frame, new_x, new_y):
        if new_y <= 0 or new_y + self.size().height() >= window_frame.size().height() and new_x >= 0 or new_x + self.size().width() >= window_frame.size().width():
            return True
        else:
            return False
