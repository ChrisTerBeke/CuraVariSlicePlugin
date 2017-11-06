// Copyright (c) 2017 Ultimaker B.V.
// This plugin is released under the terms of Creative Commons 3.0 or higher.

import UM 1.1 as UM
import QtQuick 2.2

Item {
    id: variSlice

    width: 200
    height: 200

    Text {
        id: statusText

        anchors {
            top: variSlice.top
        }

        text: UM.ActiveTool.properties.getValue("Processing") ? "Processing..." : "Analysis complete"
    }

    Text {
        id: maxLayersText

        anchors {
            top: statusText.bottom
        }

        text: "Layers: " + layerInfoList.count + " (down from " + UM.ActiveTool.properties.getValue("MaxLayers") + ")"
    }

    Text {
        id: modelHeightText

        anchors {
            top: maxLayersText.bottom
        }

        text: "Model height: " + UM.ActiveTool.properties.getValue("ModelHeight")
    }

    Text {
        id: totalTrianglesText

        anchors {
            top: modelHeightText.bottom
        }

        text: "Triangles parsed: " + UM.ActiveTool.properties.getValue("TotalTriangles")
    }

    Text {
        id: layerStepsText

        anchors {
            top: totalTrianglesText.bottom
        }

        text: "Layer steps used: " + UM.ActiveTool.properties.getValue("LayerSteps")
    }

    ListView {
        id: layerInfoList

        width: 200
        height: 200

        anchors {
            top: layerStepsText.bottom
        }

        model: UM.ActiveTool.properties.getValue("LayerInfo")

        delegate: Text {
            text: index + ": " + layer_height
        }
    }
}
