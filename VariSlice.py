# Copyright (c) 2017 Ultimaker B.V.
# This plugin is released under the terms of Creative Commons 3.0 or higher.

import threading

from PyQt5.QtCore import pyqtSlot, QVariant

from UM.Application import Application
from UM.Signal import Signal
from UM.Event import Event
from UM.Tool import Tool
from UM.Scene.Selection import Selection

from cura.Settings.ProfilesModel import ProfilesModel

from VariSliceAlgorithm import VariSliceAlgorithm
from VariSliceLayersListModel import VariSliceLayersListModel

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
        self._layer_info = []
        self._meta_data = None

        # stores the last algorithm instance
        self._algorithm_instance = None

        # expose properties to QML
        self.setExposedProperties("LayerInfo", "ModelHeight", "MaxLayers", "TotalTriangles", "LayerSteps", "Processing")

        # notify update when finished processing in thread
        self.finishedProcessing.connect(self._onProcessingFinished)

    finishedProcessing = Signal()

    def getProcessing(self):
        return self.__thread is not None

    @pyqtSlot(result = QVariant)
    def getLayerInfo(self):
        return QVariant(self._layer_info)

    def getMetaData(self):
        return self._meta_data

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

    def event(self, event):
        super().event(event)

        if (event.type == Event.MouseReleaseEvent or event.type == Event.ToolActivateEvent) and Selection.hasSelection():
            self._run(Selection.getSelectedObject(0))

    def _run(self, selected_model):
        self._selected_model = selected_model
        if self.__thread is None:
            self.__thread = threading.Thread(target = self._variSlice, daemon = True)
            self.__thread.start()

    def _onProcessingFinished(self, vari_slice_output):
        self._layer_info = VariSliceLayersListModel(vari_slice_output["layer_info"])
        self._meta_data = {
            "model_height": vari_slice_output["model_height"],
            "max_layers": vari_slice_output["max_layers"],
            "total_triangles": vari_slice_output["total_triangles"],
            "layer_steps": ", ".join(map(str, vari_slice_output["layer_steps"]))
        }
        self.propertyChanged.emit()

    def _variSlice(self):
        print("Starting VariSlice...")
        allowed_layer_heights = self._calculateAllowedLayerHeights()
        self._algorithm_instance = VariSliceAlgorithm(self._selected_model, allowed_layer_heights)
        output = self._algorithm_instance.buildLayers()
        print("Finished VariSlice")
        self.finishedProcessing.emit(output)
        self.__thread = None

    # get list of allowed layer heights from available quality profiles
    def _calculateAllowedLayerHeights(self):
        global_stack = Application.getInstance().getGlobalContainerStack()

        if not global_stack:
            return self._default_allowed_layer_heights

        available_layer_heights = []

        for quality_profile in ProfilesModel.getInstance().items:
            available_layer_heights.append(float(quality_profile["layer_height_without_unit"]))

        return sorted(available_layer_heights, key = float, reverse = True)
