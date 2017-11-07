# Copyright (c) 2017 Ultimaker B.V.
# This plugin is released under the terms of Creative Commons 3.0 or higher.

from PyQt5.QtCore import Qt

from UM.Qt.ListModel import ListModel

class VariSliceLayersListModel(ListModel):
    LayerHeightRole = Qt.UserRole + 1
    LayerSlopeRole = Qt.UserRole + 2
    AbsoluteHeightRole = Qt.UserRole + 3
    TriangleCountRole = Qt.UserRole + 4

    def __init__(self, layer_data = None, parent = None):
        super().__init__(parent)

        self.addRoleName(self.LayerHeightRole, "layer_height")
        self.addRoleName(self.LayerSlopeRole, "layer_slope")
        self.addRoleName(self.AbsoluteHeightRole, "absolute_height")
        self.addRoleName(self.TriangleCountRole, "triangle_count")

        self._layers = []

        if layer_data:
            self.setLayerData(layer_data)

    def setLayerData(self, layer_data):
        self._layers = layer_data
        self._update()

    def _update(self):
        items = []

        if len(self._layers) == 0:
            return

        for index, layer in enumerate(self._layers):
            items.append({
                "layer_height": layer["layer_height"],
                "layer_slope": layer["layer_slope"],
                "absolute_height": layer["absolute_height"],
                "triangle_count": layer["triangle_count"],
                "layer_index": index
            })

        items.sort(key = lambda k: (k["layer_index"]))
        self.setItems(items)
