# Copyright (c) 2017 Ultimaker B.V.
# This plugin is released under the terms of Creative Commons 3.0 or higher.

import numpy

from UM.Logger import Logger
from UM.Scene import SceneNode

from VariSliceUtils import VariSliceUtils

class VariSliceAlgorithm:

    def __init__(self, selected_model):

        # list of allowed layer heights sorted with tallest on top
        # TODO: make dynamic
        self._layer_steps = [
            0.2,
            0.15,
            0.1,
            0.06
        ]

        self._selected_model = selected_model  # type: SceneNode
        self._triangles = []  # type: numpy.ndarray
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

    # Build the layers
    def buildLayers(self):
        self._selected_model.setCalculateBoundingBox(True)  # make sure the bounding box is calculated on the next line
        model_height = self._selected_model.getBoundingBox().height
        max_layers = int(model_height / self.minimumLayerHeight)

        # temporary lists that hold triangles of interest
        triangles_of_interest = []
        absolute_heights = []
        triangles_in_layers = []

        # keep track of current layer
        z_level = 0

        # loop over each potential layer
        for layer_index in range(0, max_layers):
            if layer_index != 0:
                z_level = absolute_heights[layer_index - 1]

            # loop over allowed layer heights to find intersecting triangles for consideration
            for layer_step in self._layer_steps:
                triangles_of_interest.clear()

                # loop over all triangles to find intersecting ones
                for i, triangle in enumerate(self._triangles):
                    if len(triangle) != 3:
                        Logger.log("e", "Could not parse triangles from selected model: length was not 3")
                        return

                    is_triangle_interesting = VariSliceUtils.isTriangleInRangeOfInterest(triangle, z_level, z_level + layer_step)

        return 0

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
        # verts[:, [1, 2]] = verts[:, [2, 1]]
        # verts[:, 1] *= -1

        # Convert vertices and indices into triangles (faces)
        indices = mesh_data.getIndices()
        if indices is not None:
            flat_verts = numpy.take(vertices, indices.flatten(), axis = 0)
        else:
            flat_verts = numpy.array(vertices)

        # Cache the triangle data
        self._triangles = flat_verts

    # calculates the minimum and maximum layer heights
    def _calculateMinAndMaxLayerHeights(self):
        self._maximum_layer_height = max(self._layer_steps)
        self._minimum_layer_height = min(self._layer_steps)
