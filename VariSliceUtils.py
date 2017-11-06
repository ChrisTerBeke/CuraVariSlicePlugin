# Copyright (c) 2017 Ultimaker B.V.
# This plugin is released under the terms of Creative Commons 3.0 or higher.

import math

import numpy

from UM.Math.Vector import Vector

class VariSliceUtils:

    # Calculates if a given triangle has a vertex within an upper and lower bound
    @staticmethod
    def isTriangleInRangeOfInterest(triangle, lower_bound, upper_bound):
        max_x, max_y, max_z = triangle.max(axis = 0)
        min_x, min_y, min_z = triangle.min(axis = 0)

        if max_z > lower_bound > min_z:
            # top if triangle is in RoI
            return True
        elif min_z < upper_bound < max_z:
            # bottom of triangle is in RoI
            return True
        elif min_z < lower_bound and max_z > upper_bound:
            # triangle spans above and below RoI
            return True
        elif max_z < upper_bound and min_z > lower_bound:
            # triangle is completely within RoI
            return True

        return False

    @staticmethod
    def findSlope(triangle):

        print("triangle", triangle)

        slope = max(numpy.angle(triangle))

        # a = Vector(triangle[0][0], triangle[0][1], triangle[0][2])
        # b = Vector(triangle[1][0], triangle[1][1], triangle[1][2])
        # c = Vector(triangle[2][0], triangle[2][1], triangle[2][2])
        #
        # ab = b - a
        # ac = c - a
        # normal = ab.cross(ac)
        # slope = Vector(0.0, 0.0, 1.0).angleToVector(normal)
        #
        # if slope > math.pi / 2:
        #     # limit between -45 and +45 degrees
        #     slope = int(math.pi - slope)

        return slope

    # Finds the minimum slope in an ndarray of triangle vertices
    @staticmethod
    def findMinimumSlope(triangles):
        min_slope = 999

        for triangle in triangles:
            slope = VariSliceUtils.findSlope(triangle)

            if slope < min_slope:
                min_slope = slope

        return min_slope

    # Checks if layer height is valid for slope
    @staticmethod
    def isValidLayerHeight(layer_slope, layer_step, treshold):
        slope_tan = math.tan(layer_slope)
        if slope_tan > 0 and layer_step / slope_tan <= treshold:
            return True
        return False
