// Copyright (c) 2017 Ultimaker B.V.
// This plugin is released under the terms of Creative Commons 3.0 or higher.

import UM 1.1 as UM
import QtQuick 2.2

UM.Dialog {
    id: base

    width: 200
    height: 200
    minimumWidth: 200
    minimumHeight: 200

    Text {
        anchors {
            top: base.top
            verticalCenter: base.verticalCenter
        }
        text: "VariSlice!"
    }
}
