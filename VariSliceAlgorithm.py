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

        # keep track of current layer
        z_level = 0

        # loop over each potential layer
        for layer_index in range(0, max_layers):
            if layer_index != 0:
                z_level = absolute_heights[layer_index - 1]

            # we cache the triangles so we have a smaller set to check next layer step (making it faster)
            triangles_cache = []
            triangles_of_interest = []

            # loop over allowed layer heights to find intersecting triangles for consideration
            for layer_step in self._layer_steps:

                triangles_of_interest = triangles_cache

                if len(triangles_cache) == 0:
                    # loop over all triangles to find intersecting ones
                    for triangle in numpy.array(self._triangles):
                        if len(triangle) != 3:
                            Logger.log("e", "Could not parse triangles from selected model: length was not 3")
                            return

                        if VariSliceUtils.isTriangleInRangeOfInterest(triangle, z_level, z_level + layer_step):
                            triangles_of_interest.append(triangle)

                # cache the triangles for potential next iteration of layer steps
                triangles_cache = triangles_of_interest

                # get the minimum slope for interesting triangles
                layer_slope = VariSliceUtils.findMinimumSlope(triangles_of_interest)

                # create the layer when it is small enough or we're on the thinnest layer allowed
                if VariSliceUtils.isValidLayerHeight(layer_slope, layer_step, 0.1) or layer_step == min(self._layer_steps):
                    absolute_heights.append(z_level + layer_step)
                    layer_output.append({
                        "layer_height": layer_step,
                        "absolute_height": z_level + layer_step,
                        "layer_slope": layer_slope,
                        "triangle_count": len(triangles_of_interest)
                    })
                    break

            # break when we're out of triangles (top of model)
            if len(triangles_of_interest) == 0:
                break

        return layer_output

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

        # Convert vertices and indices into triangles (faces)
        if mesh_data.hasIndices():
            for face in mesh_data.getIndices():
                v1 = vertices[face[0]]
                v2 = vertices[face[1]]
                v3 = vertices[face[2]]
                self._appendTriangle([v1, v2, v3])
        else:
            for index in range(0, len(vertices) - 1, 3):
                v1 = vertices[index]
                v2 = vertices[index + 1]
                v3 = vertices[index + 2]
                self._appendTriangle([v1, v2, v3])

        return self._triangles

    # Appends a triangle to cached triangles
    def _appendTriangle(self, triangle):
        if self._triangles is None:
            self._triangles = [triangle]
        else:
            self._triangles.append(triangle)

    # calculates the minimum and maximum layer heights
    def _calculateMinAndMaxLayerHeights(self):
        self._maximum_layer_height = max(self._layer_steps)
        self._minimum_layer_height = min(self._layer_steps)
