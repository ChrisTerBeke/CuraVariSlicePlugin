# Copyright (c) 2017 Ultimaker B.V.
# This plugin is released under the terms of Creative Commons 3.0 or higher.

import os.path

from PyQt5.QtCore import QUrl
from PyQt5.QtQml import QQmlComponent

from UM.Application import Application
from UM.Event import Event
from UM.Scene.Selection import Selection
from UM.PluginRegistry import PluginRegistry
from UM.Tool import Tool

from VariSliceAlgorithm import VariSliceAlgorithm

class VariSlice(Tool):

    def __init__(self):
        super().__init__()

        # the info window shows the regions that were created
        self.info_window = None

        # stores the VariSlice algorithm result for UI processing
        self._layer_info = []

    def event(self, event):
        super().event(event)

        if event.type == Event.MouseReleaseEvent and Selection.hasSelection():
            self._run(Selection.getSelectedObject(0))
            if not self.info_window:
                self.info_window = self._createInfoWindow()
            self.info_window.show()

    def _run(self, selected_model):
        algorithm_instance = VariSliceAlgorithm(selected_model)
        self._layer_info = algorithm_instance.buildLayers()

    def _createInfoWindow(self):
        qml_file = QUrl.fromLocalFile(os.path.join(PluginRegistry.getInstance().getPluginPath(self.getPluginId()), "VariSlice.qml"))
        component = QQmlComponent(Application.getInstance().getQmlEngine(), qml_file)
        qml_context = QQmlComponent(Application.getInstance().getQmlEngine().rootContext())
        return component.create(qml_context)
