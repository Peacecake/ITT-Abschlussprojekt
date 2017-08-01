# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from pylab import *
from numpy import *
from math import exp


class VectorTransform:
    def __init__(self):
        super().__init__()
        self.buffer = []
        self.buffer_size = 8
        self.weights = self.get_weights()

    def transform(self, vectors, x_size, y_size):
        self.DEST_W = x_size
        self.DEST_H = y_size
        vectors = self.get_ordered_vectors(vectors)
        sx1, sy1 = vectors[0]
        sx2, sy2 = vectors[1]
        sx3, sy3 = vectors[2]
        sx4, sy4 = vectors[3]
        l, m, t = self.get_factor_vector(sx1, sx2, sx3, sx4, sy1, sy2, sy3, sy4)
        unit_to_source = matrix([[l * sx1, m * sx2, t * sx3],
                                 [l * sy1, m * sy2, t * sy3],
                                 [l, m, t]])

        dx1, dy1 = 0, self.DEST_H
        dx2, dy2 = self.DEST_W, self.DEST_H
        dx3, dy3 = self.DEST_W, 0
        dx4, dy4 = 0, 0
        l, m, t = self.get_factor_vector(dx1, dx2, dx3, dx4, dy1, dy2, dy3, dy4)
        unit_to_destination = matrix([[l * dx1, m * dx2, t * dx3],
                                      [l * dy1, m * dy2, t * dy3],
                                      [l, m, t]])

        try:
            source_to_unit = inv(unit_to_source)
        except Exception:
            return 0, 0
        source_to_destination = unit_to_destination @ source_to_unit
        x, y, z = [float(w) for w in (source_to_destination @ matrix([[512], [384], [1]]))]
        x = x / z
        y = y / z

        # Calculate the weighted average of buffer
        self.buffer.append((x, y))
        self.buffer = self.buffer[-self.buffer_size:]
        x_sum = 0
        y_sum = 0
        wsum = 0
        for i in range(0, len(self.buffer)):
            a, b = self.buffer[i]
            weight = self.weights[i]
            x_sum = x_sum + (a * self.weights[i])
            y_sum = y_sum + (b * self.weights[i])
            wsum = wsum + weight

        return x_sum / wsum, y_sum / wsum

    def get_factor_vector(self, x1, x2, x3, x4, y1, y2, y3, y4):
        source_points_123 = matrix([[x1, x2, x3],
                                    [y1, y2, y3],
                                    [1, 1, 1]])
        source_point_4 = [[x4], [y4], [1]]

        try:
            scale_to_source = solve(source_points_123, source_point_4)
        except Exception:
            print("error scale_to_source solve")
            return 0, 0, 0

        return [float(x) for x in scale_to_source]

    # Coordinates first get ordered ascending by y value. From this follows that the first to entries have to be
    # the coordinates at the bottom and the third and fourth at the top. Depending on their x values they have to
    # be switched to represent the edges of the display.
    def get_ordered_vectors(self, vectors):
        # sorted_y is sorted by y value
        # Source: https://stackoverflow.com/questions/37111798/how-to-sort-a-list-of-x-y-coordinates
        sorted_y = sorted(vectors, key=lambda k: [k[1], k[0]])
        x1, y1 = sorted_y[0]
        x2, y2 = sorted_y[1]
        if x1 > x2:
            sorted_y[1] = (x1, y1)
            sorted_y[0] = (x2, y2)

        x1, y1 = sorted_y[2]
        x2, y2 = sorted_y[3]
        if x1 < x2:
            sorted_y[3] = x1, y1
            sorted_y[2] = x2, y2
        return sorted_y

    # Depending on buffer_size automatically fills a list containing weights for weighted average calculation.
    # The weights get calculated from a flattened exponential function.
    def get_weights(self):
        weights = []
        wsum = 0
        for i in range(0, self.buffer_size):
            weights.append(exp(i * 0.5))
            wsum += weights[i]

        for i in range(0, len(weights)):
            weights[i] = weights[i] / wsum

        return weights
