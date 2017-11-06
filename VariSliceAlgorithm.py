# Copyright (c) 2017 Ultimaker B.V.
# This plugin is released under the terms of Creative Commons 3.0 or higher.

import numpy

from UM.Logger import Logger
from UM.Scene import SceneNode

from VariSliceUtils import VariSliceUtils

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

        absolute_heights = []
        layer_output = []
        triangle_slopes = numpy.array([])

        # keep track of current layer
        z_level = 0

        # calculate the slope of each triangle (as we need them anyways)
        for index, triangle in numpy.ndenumerate(self._triangles):
            triangle_slope = VariSliceUtils.findSlope(triangle)
            triangle_slopes = numpy.append(triangle_slopes, triangle_slope)

        # loop over each potential layer
        for layer_index in range(0, max_layers):
            if layer_index != 0:
                z_level = round(absolute_heights[layer_index - 1], 2)

            # we cache the triangles so we have a smaller set to check next layer step (making it faster)
            triangles_cache = []
            triangles_of_interest = []

            # loop over allowed layer heights to find intersecting triangles for consideration
            for layer_step in self._layer_steps:

                # if no cached triangles from previous layer step, use all triangles
                if len(triangles_cache) == 0:
                    triangles_cache = self._triangles

                triangles_of_interest = numpy.where(triangles_cache[:, :, 2] >= z_level)

                # cache the triangles for potential next iteration of layer steps
                triangles_cache = triangles_of_interest

                # create the layer when it is small enough or we're on the thinnest layer allowed
                # if VariSliceUtils.isValidLayerHeight(layer_slope, layer_step, 0.1) or layer_step == min(self._layer_steps):
                #     absolute_heights.append(z_level + layer_step)
                #     layer_output.append({
                #         "layer_height": str(layer_step),
                #         "absolute_height": str(round(z_level + layer_step, 2)),
                #         "layer_slope": str(round(layer_slope, 2)),
                #         "triangle_count": str(len(triangles_of_interest))
                #     })
                #     break

            # break when we're out of triangles (top of model)
            if len(triangles_of_interest) == 0:
                break

        # return all output data
        return {
            "layer_info": layer_output,
            "model_height": str(model_height),
            "max_layers": str(max_layers),
            "total_triangles": str(len(self._triangles)),
            "layer_steps": self._layer_steps
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

        Logger.log("d", vertices)

        # convert to multi-dimensional array of triangles of vertices
        self._triangles = numpy.reshape(vertices, [-1, 3, 3])

        return self._triangles

    # Appends a triangle to cached triangles
    def _appendTriangle(self, triangle):
        if self._triangles is None:
            self._triangles = numpy.array([triangle])
        else:
            self._triangles = numpy.append(self._triangles, [triangle], axis = 1)

    # calculates the minimum and maximum layer heights
    def _calculateMinAndMaxLayerHeights(self):
        self._maximum_layer_height = max(self._layer_steps)
        self._minimum_layer_height = min(self._layer_steps)
