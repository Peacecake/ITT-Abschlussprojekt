# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QFrame, QLineEdit, QTextEdit


class Card(QFrame):
    def __init__(self, parent):
        super(Card, self).__init__()
        self.setParent(parent)
        self.title_field = QLineEdit()
        self.content_field = QTextEdit()
        self.setup_frame()
        self.setup_title()
        self.setup_content()
        self.setMouseTracking(True)

    def setup_frame(self):
        self.setStyleSheet('background-color: rgb(85, 170, 255)')
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

    def move_to(self, x, y):
        self.setGeometry(x, y, self.size().width(), self.size().height())
