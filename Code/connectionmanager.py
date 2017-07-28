# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-


class ConnectionManager:
    def __init__(self):
        super(ConnectionManager, self).__init__()
        self.connections = []
        self.restoreable_connections = []

    def connect(self, new_connection):
        self.connections.append(new_connection)

    def delete_connection(self, cards):
        for conn in self.connections:
            c1 = self.get_centers(conn)
            c2 = self.get_centers(cards)
            if sorted(c1) == sorted(c2):
                self.connections.remove(conn)

    def delete_all_card_connections(self, card):
        new_connections = []
        for conn in self.connections:
            c1, c2 = conn
            if c1 is not card and c2 is not card:
                new_connections.append((c1, c2))
        self.connections = new_connections

    def remove_last_connection(self):
        if len(self.connections) > 0:
            deleteable_connection = self.connections[-1]
            if deleteable_connection is not None:
                self.restoreable_connections.append(deleteable_connection)
                self.connections.remove(deleteable_connection)
        # self.connections = self.connections[:-1]

    def restore_connection(self):
        if len(self.restoreable_connections) > 0:
            restoreable = self.restoreable_connections[-1]
            if restoreable is not None:
                self.connections.append(restoreable)
                self.restoreable_connections.remove(restoreable)

    def get_centers(self, connection):
        c1, c2 = connection
        return c1.center(), c2.center()