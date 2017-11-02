# Copyright (c) 2017 Ultimaker B.V.
# This plugin is released under the terms of Creative Commons 3.0 or higher.

import os.path

from PyQt5.QtCore import QUrl
from PyQt5.QtQml import QQmlComponent

from UM.Application import Application
from UM.PluginRegistry import PluginRegistry
from UM.Tool import Tool

class VariSlice(Tool):

    def __init__(self):
        super().__init__()

        # the info window shows the regions that were created
        self._info_window = None

    def _regionsCreated(self):
        if not self._info_window:
            self._info_window = self._createInfoWindow()
        self._info_window.show()

    def _createInfoWindow(self):
        qml_file = QUrl.fromLocalFile(os.path.join(PluginRegistry.getInstance().getPluginPath(self.getPluginId()), "VariSlice.qml"))
        component = QQmlComponent(Application.getInstance().getQmlEngine(), qml_file)
        qml_context = QQmlComponent(Application.getInstance().getQmlEngine().rootContext())
        return component.create(qml_context)
