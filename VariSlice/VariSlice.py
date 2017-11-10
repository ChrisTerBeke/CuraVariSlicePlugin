# Copyright (c) 2017 Ultimaker B.V.
# This plugin is released under the terms of Creative Commons 3.0 or higher.

import threading

from UM.Application import Application
from UM.Event import Event
from UM.Scene.Selection import Selection
from UM.Signal import Signal
from UM.Tool import Tool

from cura.Settings.ProfilesModel import ProfilesModel

from VariSlice.VariSliceAlgorithm import VariSliceAlgorithm
from VariSlice.VariSliceLayersListModel import VariSliceLayersListModel

class VariSlice(Tool):

    def __init__(self):
        super().__init__()

        # use separate thread for VariSlice algorithm otherwise we lock up the UI
        self.__thread = None

        # the selected model to pass between threads
        self._selected_model = None

        # the allowed layer heights steps to try in the algorithm
        self._default_allowed_layer_heights = [
            0.2,
            0.15,
            0.1
        ]

        # stores the VariSlice result for UI processing
        self._layer_info = VariSliceLayersListModel()
        self._meta_data = None

        # stores the last algorithm instance
        self._algorithm_instance = None

        # notify update when finished processing in thread
        self.finishedProcessing.connect(self._onProcessingFinished)

        # expose needed QML properties
        self.setExposedProperties("LayerInfo", "ModelHeight", "MaxLayers", "TotalTriangles", "LayerSteps", "Finished", "PercentageImproved")

    finishedProcessing = Signal()

    def getFinished(self):
        return self.__thread is None

    def getLayerInfo(self):
        return self._layer_info

    def getModelHeight(self):
        if not self._meta_data:
            return ""
        return self._meta_data["model_height"]

    def getMaxLayers(self):
        if not self._meta_data:
            return ""
        return self._meta_data["max_layers"]

    def getTotalTriangles(self):
        if not self._meta_data:
            return ""
        return self._meta_data["total_triangles"]

    def getLayerSteps(self):
        if not self._meta_data:
            return ""
        return self._meta_data["layer_steps"]

    def getPercentageImproved(self):
        if not self._meta_data:
            return ""
        return self._meta_data["percentage_improved"]

    def event(self, event):
        super().event(event)

        if (event.type == Event.MouseReleaseEvent or event.type == Event.ToolActivateEvent) and Selection.hasSelection():
            if not Selection.getSelectedObject(0).hasChildren():
                self._run(Selection.getSelectedObject(0))

    def _run(self, selected_model):
        self._layer_info = None
        self._selected_model = selected_model
        if self.__thread is None:
            self.__thread = threading.Thread(target = self._variSlice, daemon = True)
            self.__thread.start()
        self.propertyChanged.emit()

    def _onProcessingFinished(self, vari_slice_output):
        self._layer_info = VariSliceLayersListModel(vari_slice_output["layer_info"])
        self._meta_data = {
            "model_height": vari_slice_output["model_height"],
            "max_layers": vari_slice_output["max_layers"],
            "total_triangles": vari_slice_output["total_triangles"],
            "percentage_improved": vari_slice_output["percentage_improved"],
            "layer_steps": ", ".join(map(str, vari_slice_output["layer_steps"]))
        }

        # Set the settings value so the data is passed to CuraEngine
        for stack in Application.getInstance().getExtruderManager().getActiveGlobalAndExtruderStacks():
            stack.setProperty("layer_height_use_variable", "value", True)
            stack.setProperty("layer_height_variable_heights", "value", vari_slice_output["variable_layer_heights_field"])

        self.__thread = None
        self.propertyChanged.emit()

    def _variSlice(self):
        print("Starting VariSlice...")
        allowed_layer_heights = self._calculateAllowedLayerHeights()
        self._algorithm_instance = VariSliceAlgorithm(self._selected_model, allowed_layer_heights)
        output = self._algorithm_instance.buildLayers()
        print("Finished VariSlice")
        self.finishedProcessing.emit(output)

    # get list of allowed layer heights from available quality profiles
    def _calculateAllowedLayerHeights(self):
        global_stack = Application.getInstance().getGlobalContainerStack()

        if not global_stack:
            return self._default_allowed_layer_heights

        available_layer_heights = []

        for quality_profile in ProfilesModel.getInstance().items:
            available_layer_heights.append(float(quality_profile["layer_height_without_unit"]))

        return sorted(available_layer_heights, key = float, reverse = True)
