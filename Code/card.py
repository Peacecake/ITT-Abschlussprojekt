# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QFrame, QLineEdit, QTextEdit


class Card(QFrame):
    def __init__(self, parent, id, has_text_field=True):
        super(Card, self).__init__()
        self.setParent(parent)
        self.id = id
        self.DEFAULT_COLOR = "rgb(85, 170, 255)"
        self.DEFAULT_BORDER = "none"
        self.available_colors = [self.DEFAULT_COLOR, 'red', 'green', "yellow"]
        self.color_index = 0
        self.color = self.available_colors[self.color_index]
        self.border = self.DEFAULT_BORDER
        self.unfocued_border = "none"
        self.has_text_field = has_text_field
        self.is_focused = False
        self.setup_ui()

    def setup_ui(self):
        self.title_field = QLineEdit()
        self.content_field = QTextEdit()
        self.setup_default_card()
        if self.has_text_field is False:
            self.setup_title_only_card()
        self.update_stylesheet()
        self.setMouseTracking(True)

    def toggle_type(self):
        self.has_text_field = not self.has_text_field
        if self.has_text_field is not True:
            self.setup_title_only_card()
        else:
            self.setup_default_card()

    def setup_title_only_card(self):
        self.content_field.setParent(None)
        self.resize(281, 80)
        self.title_field.resize(230, 60)
        self.title_field.move(25, 10)
        self.set_title_font(25)

    def setup_default_card(self):
        self.setup_frame()
        self.setup_title()
        self.setup_content()
        self.set_title_font(12)

    def set_title_font(self, font_size):
        self.title_field.selectAll()
        font = self.title_field.font()
        font.setPointSize(font_size)
        self.title_field.setFont(font)

    def next_color(self):
        self.color_index = self.color_index + 1
        if len(self.available_colors) is self.color_index:
            self.color_index = 0
        self.set_background_color(self.available_colors[self.color_index])

    def previous_color(self):
        self.color_index = self.color_index - 1
        if self.color_index is -1:
            self.color_index = len(self.available_colors) - 1
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

    def focus(self):
        self.unfocued_border = self.border
        self.set_border("2px solid orange")
        self.title_field.setFocus()
        self.raise_()
        self.is_focused = True
        print("focus " + str(self.is_focused))

    def unfocus(self):
        self.set_border(self.unfocued_border)
        self.is_focused = False

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

    def collides(self, widget):
        x = self.pos().x()
        y = self.pos().y()
        width = self.size().width()
        height = self.size().height()
        return x < widget.pos().x() + widget.size().width() and x + width > widget.pos().x() and y < widget.pos().y() + widget.size().height() and y + height > widget.pos().y();

    def hits_window_frame(self, window_frame, new_x, new_y):
        if new_y <= 0 or new_y + self.size().height() >= window_frame.size().height() and new_x >= 0 or new_x + self.size().width() >= window_frame.size().width():
            return True
        else:
            return False
