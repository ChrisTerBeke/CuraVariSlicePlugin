# Copyright (c) 2017 Ultimaker B.V.
# This plugin is released under the terms of Creative Commons 3.0 or higher.

from PyQt5.QtCore import Qt

from UM.Qt.ListModel import ListModel

class VariSliceLayersListModel(ListModel):
    LayerHeightRole = Qt.UserRole + 1
    LayerSlopeRole = Qt.UserRole + 2
    AbsoluteHeightRole = Qt.UserRole + 3
    TriangleCountRole = Qt.UserRole + 4

    def __init__(self, layer_data = None):
        super().__init__()

        self.addRoleName(self.LayerHeightRole, "layer_height")
        self.addRoleName(self.LayerSlopeRole, "layer_slope")
        self.addRoleName(self.AbsoluteHeightRole, "absolute_height")
        self.addRoleName(self.TriangleCountRole, "triangle_count")

        self.setLayerData(layer_data)

    def setLayerData(self, layer_data):
        self.setItems(layer_data)
