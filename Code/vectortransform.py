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
        sx1, sy1 = vectors[0]
        sx2, sy2 = vectors[1]
        sx3, sy3 = vectors[2]
        sx4, sy4 = vectors[3]

        # Step 1
        source_points_123 = matrix([[sx1, sx2, sx3],
                                    [sy1, sy2, sy3],
                                    [1, 1, 1]])
        source_point_4 = [[sx4], [sy4], [1]]

        try:
            scale_to_source = solve(source_points_123, source_point_4)
        except Exception:
            print("error scale_to_source solve")
            return 0, 0

        l, m, t = [float(x) for x in scale_to_source]

        # Step 2
        unit_to_source = matrix([[l * sx1, m * sx2, t * sx3],
                                 [l * sy1, m * sy2, t * sy3],
                                 [l, m, t]])

        # Step 3
        dx1, dy1 = 0, 0
        dx2, dy2 = self.DEST_W, 0
        dx3, dy3 = self.DEST_W, self.DEST_H
        dx4, dy4 = 0, self.DEST_H
        dest_points_123 = matrix([[dx1, dx2, dx3],
                                  [dy1, dy2, dy3],
                                  [1, 1, 1]])
        dest_point_4 = matrix([[dx4], [dy4], [1]])
        scale_to_dest = solve(dest_points_123, dest_point_4)
        l, m, t = [float(x) for x in scale_to_dest]
        unit_to_dest = matrix([[l * dx1, m * dx2, t * dx3],
                               [l * dy1, m * dy2, t * dy3],
                               [l, m, t]])

        # Step 4
        source_to_unit = inv(unit_to_source)

        # Step 5
        source_to_dest = unit_to_dest @ source_to_unit

        # Step 6
        x, y, z = [float(w) for w in (source_to_dest @ matrix([[512], [384], [1]]))]

        # Step 7
        x = x / z
        y = y / z

        return x, y
