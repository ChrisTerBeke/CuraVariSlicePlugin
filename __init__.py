# Copyright (c) 2017 Ultimaker B.V.
# This plugin is released under the terms of Creative Commons 3.0 or higher.

import VariSlice

def getMetaData():
    return {
        "tool": {
            "name": "VariSlice",
            "description": "Generate quality regions based on mesh properties.",
            "icon": "varislice_icon.svg",
            "tool_panel": "VariSlice.qml"
        }
    }

def register(app):
    return {
        "tool": VariSlice.VariSlice()
    }
