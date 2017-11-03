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

    ListView {
        id: layerInfoList

        width: 200
        height: 200

        anchors {
            top: statusText.bottom
            verticalCenter: variSlice.verticalCenter
        }

        model: UM.ActiveTool.properties.getValue("LayerInfo")

        delegate: Text {
            text: layer_height
        }
    }
}
