# Copyright (c) 2017 Ultimaker B.V.
# This plugin is released under the terms of Creative Commons 3.0 or higher.

import numpy

from UM.Scene import SceneNode

class VariSliceAlgorithm:

    def __init__(self, selected_model, allowed_layer_heights):

        # list of allowed layer heights sorted with tallest on top
        self._layer_steps = allowed_layer_heights

        self._selected_model = selected_model  # type: SceneNode
        self._triangles = None
        self._maximum_layer_height = None
        self._minimum_layer_height = None

        self._calculateModelTriangles()

    @property
    def maximumLayerHeight(self):
        self._calculateMinAndMaxLayerHeights()
        return self._maximum_layer_height

    @property
    def minimumLayerHeight(self):
        self._calculateMinAndMaxLayerHeights()
        return self._minimum_layer_height

    @property
    def triangles(self):
        return self._triangles

    # Update the list of allowed layer height steps
    def setAllowedLayerHeights(self, layer_heights):
        self._layer_steps = layer_heights

    # Build the layers
    def buildLayers(self):
        self._selected_model.setCalculateBoundingBox(True)  # make sure the bounding box is calculated on the next line

        model_height = self._selected_model.getBoundingBox().height
        max_layers = int(model_height / self.minimumLayerHeight)
        triangle_slopes = self._calculateTriangleSlopes()
        layer_heights = []
        absolute_heights = []
        layer_output = []
        triangles_of_interest = []

        # calculate the minimum and maximum z value per triangle
        z_levels = self._triangles[::, ::, 2]
        min_z = z_levels.min(axis=1)
        max_z = z_levels.max(axis=1)

        # keep track of current layer
        z_level = 0

        # loop over all potential layers
        for layer_index in range(0, max_layers):
            if layer_index != 0:
                z_level = absolute_heights[layer_index - 1]

            # check the bounds for each layer height, starting with the largest layer height
            for layer_step in self._layer_steps:
                lower_bound = z_level
                upper_bound = z_level + layer_step

                # check if the smallest z value in a triangle is within or completely below bounds
                min_bounds = numpy.where(((min_z >= lower_bound) & (min_z <= upper_bound)) | ((min_z < lower_bound) & (min_z < upper_bound)))

                # check if the largest z value in a triangle is within or completely above bounds
                max_bounds = numpy.where(((max_z <= upper_bound) & (max_z >= lower_bound)) | ((max_z > upper_bound) & (max_z > lower_bound)))

                # union bounds to find triangles that are interesting for this layer range
                triangles_of_interest = numpy.intersect1d(min_bounds[0], max_bounds[0])

                # if no triangles are found stop checking
                if len(triangles_of_interest) == 0:
                    break

                # find the slopes for the interesting triangles
                slopes = numpy.array(triangle_slopes)[triangles_of_interest]

                # calculate the treshold of the steepest triangle
                minimum_slope = min(slopes)
                slope_tan = numpy.tan(minimum_slope)

                # if it is below the treshold we create the layer for this layer step height
                if slope_tan == 0 or layer_step / slope_tan <= 0.1 or layer_step == min(self._layer_steps):
                    layer_heights.append(layer_step)
                    absolute_heights.append(z_level + layer_step)
                    layer_output.append({
                        "layer_height": str(layer_step),
                        "absolute_height": str(round(z_level, 2)),
                        "layer_slope": str(round(minimum_slope, 2)),
                        "triangle_count": str(len(triangles_of_interest))
                    })
                    break

            if len(triangles_of_interest) == 0:
                break

        # get smallest used layer height
        min_layer_height = min(layer_heights)
        max_layers_otherwise = int(model_height / min_layer_height)
        layer_count_improvement = (max_layers_otherwise - len(layer_heights)) / max_layers_otherwise * 100

        # return all output data
        return {
            "layer_info": layer_output,
            "model_height": str(model_height),
            "max_layers": str(max_layers_otherwise),
            "total_triangles": str(len(self._triangles)),
            "percentage_improved": str(int(layer_count_improvement)),
            "layer_steps": numpy.unique(layer_heights)
        }

    # Calculates triangles for selected model from vertices and indices
    def _calculateModelTriangles(self):

        # Ignore when group
        if self._selected_model.hasChildren():
            return

        mesh_data = self._selected_model.getMeshData()
        rot_scale = self._selected_model.getWorldTransformation().getTransposed().getData()[0:3, 0:3]
        translate = self._selected_model.getWorldTransformation().getData()[:3, 3]

        # This effectively performs a limited form of MeshData.getTransformed that ignores normals.
        vertices = mesh_data.getVertices()
        vertices = vertices.dot(rot_scale)
        vertices += translate

        # Convert from Y up axes to Z up axes. Equals a 90 degree rotation.
        vertices[:, [1, 2]] = vertices[:, [2, 1]]
        vertices[:, 1] *= -1

        # convert to multi-dimensional array of triangles of vertices
        self._triangles = numpy.reshape(vertices, [-1, 3, 3])

        return self._triangles

    # calculate the z direction slopes of all triangles
    def _calculateTriangleSlopes(self):
        slopes = []

        for triangle in self._triangles:
            n = numpy.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
            normal = n / numpy.linalg.norm(n)
            z_angle = numpy.arccos(abs(normal[2]))
            slopes.append(z_angle)

        return slopes

    # calculates the minimum and maximum layer heights
    def _calculateMinAndMaxLayerHeights(self):
        self._maximum_layer_height = max(self._layer_steps)
        self._minimum_layer_height = min(self._layer_steps)
