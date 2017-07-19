# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from pylab import *
from numpy import *


class VectorTransform:
    def __init__(self, x_size, y_size):
        super().__init__()
        self.DEST_W = x_size
        self.DEST_H = y_size

    def transform(self, vectors):
        # Source: https://stackoverflow.com/questions/37111798/how-to-sort-a-list-of-x-y-coordinates
        ordered_vectors = sorted(vectors, key=lambda k: [k[1], k[0]])
        sx1, sy1 = vectors[1]
        sx2, sy2 = vectors[0]
        sx3, sy3 = vectors[3]
        sx4, sy4 = vectors[2]
        l, m, t = self.get_factor_vector(sx1, sx2, sx3, sx4, sy1, sy2, sy3, sy4)
        unit_to_source = matrix([[l * sx1, m * sx2, t * sx3],
                                 [l * sy1, m * sy2, t * sy3],
                                 [l, m, t]])

        dx1, dy1 = 0, 0
        dx2, dy2 = self.DEST_W, 0
        dx3, dy3 = self.DEST_W, self.DEST_H
        dx4, dy4 = 0, self.DEST_H
        l, m, t = self.get_factor_vector(dx1, dx2, dx3, dx4, dy1, dy2, dy3, dy4)
        unit_to_destination = matrix([[l * dx1, m * dx2, t * dx3],
                                      [l * dy1, m * dy2, t * dy3],
                                      [l, m, t]])

        source_to_unit = inv(unit_to_source)
        source_to_destination = unit_to_destination @ source_to_unit
        x, y, z = [float(w) for w in (source_to_destination @ matrix([[512], [384], [1]]))]
        return x / z, y / z

    def get_factor_vector(self, x1, x2, x3, x4, y1, y2, y3, y4):
        source_points_123 = matrix([[x1, x2, x3],
                                    [y1, y2, y3],
                                    [1, 1, 1]])
        source_point_4 = [[x4], [y4], [1]]

        try:
            scale_to_source = solve(source_points_123, source_point_4)
        except LinAlgError:
            print("error scale_to_source solve")
            return 0, 0, 0

        return [float(x) for x in scale_to_source]
