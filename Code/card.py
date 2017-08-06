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
        self.available_colors = [self.DEFAULT_COLOR, '#c0392b', '#2ecc71', '#f1c40f', '#1abc9c']
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

    # Switches between default and only_title card types
    def toggle_type(self):
        self.has_text_field = not self.has_text_field
        if self.has_text_field is not True:
            self.setup_title_only_card()
        else:
            self.setup_default_card()

    # Sets card to card with only a title textbox
    def setup_title_only_card(self):
        self.content_field.setParent(None)
        self.resize(281, 80)
        self.title_field.resize(230, 60)
        self.title_field.move(25, 10)
        self.set_title_font(20)

    # Sets card to default card style
    def setup_default_card(self):
        self.setup_frame()
        self.setup_title()
        self.setup_content()
        self.set_title_font(12)

    # Sets font size of title textbox to passed size
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

    # Sets card background to passed color.
    def set_background_color(self, color):
        self.color = color
        self.update_stylesheet()

    # Sets border of card to passed border style
    def set_border(self, border):
        self.border = border
        self.update_stylesheet()

    def update_stylesheet(self):
        self.setStyleSheet("background-color: " + self.color +
                           "; border: " + self.border +
                           "; border-radius: 5px;")

    # Sets up size of card
    def setup_frame(self):
        self.resize(281, 181)
        self.setVisible(True)

    # Sets up title textbox
    def setup_title(self):
        self.title_field.resize(146, 29)
        self.title_field.move(67, 10)
        self.title_field.setParent(self)
        self.title_field.setStyleSheet('background-color: white')
        self.title_field.setVisible(True)

    # Sets up content textbox
    def setup_content(self):
        self.content_field.resize(261, 121)
        self.content_field.move(10, 50)
        self.content_field.setParent(self)
        self.content_field.setStyleSheet('background-color: white; font-size: 12px;')
        self.content_field.setVisible(True)

    # Source:
    # https://stackoverflow.com/questions/5899826/pyqt-how-to-remove-a-widget
    # Deletes card.
    def delete(self):
        self.setParent(None)

    # Gives card focus.
    def focus(self):
        self.unfocued_border = self.border
        self.set_border("2px solid #f39c12")
        self.title_field.setFocus()
        self.raise_()
        self.is_focused = True

    # Removes focus from card.
    def unfocus(self):
        self.set_border(self.unfocued_border)
        self.is_focused = False

    # Returns center of card.
    def center(self):
        x = self.pos().x() + (self.size().width() / 2)
        y = self.pos().y() + (self.size().height() / 2)
        return x, y

    # Moves card to passed coordinates.
    def move_to(self, x, y):
        self.setGeometry(x, y, self.size().width(), self.size().height())

    # Checks if given point collides with passed widget.
    def collides_with(self, widget, new_x, new_y):
        x1 = widget.pos().x()
        x2 = x1 + widget.size().width()
        y1 = widget.pos().y()
        y2 = y1 + widget.size().height()
        if x1 <= new_x <= x2 and y1 <= new_y <= y2:
            return True
        else:
            return False

    # Source:
    # https://stackoverflow.com/questions/23302698/java-check-if-two-rectangles-overlap-at-any-point
    # Checks if card collides with widget.
    def collides(self, widget):
        x = self.pos().x()
        y = self.pos().y()
        width = self.size().width()
        height = self.size().height()
        width_fits = x < widget.pos().x() + widget.size().width() and x + width > widget.pos().x()
        height_fits = y < widget.pos().y() + widget.size().height() and y + height > widget.pos().y()
        return width_fits and height_fits

    # Checks if given point collides with passed window frame.
    def hits_window_frame(self, window_frame, new_x, new_y):
        height_fits = new_y <= 0 or new_y + self.size().height() >= window_frame.size().height()
        width_fits = new_x >= 0 or new_x + self.size().width() >= window_frame.size().width()
        return height_fits and width_fits
