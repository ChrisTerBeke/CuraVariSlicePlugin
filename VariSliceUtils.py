# Copyright (c) 2017 Ultimaker B.V.
# This plugin is released under the terms of Creative Commons 3.0 or higher.

class VariSliceUtils:

    # Calculate if a given triangle has a vertex within an upper and lower bound
    @staticmethod
    def isTriangleInRangeOfInterest(triangle, lower_bound, upper_bound):
        max_z = max(triangle)
        min_z = min(triangle)

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
