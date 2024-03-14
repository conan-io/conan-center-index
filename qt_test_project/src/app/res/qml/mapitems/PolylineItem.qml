// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
import QtQuick
import QtLocation

MapPolyline {
    line.color: "#330a0a"
    line.width: 2
    opacity: 0.75
    smooth: true
    autoFadeIn: false

    property string geojsonType: "Polyline"

    function setGeometry(anchorCoordinate){
        addCoordinate(anchorCoordinate)
    }

    function addGeometry(newCoordinate, changeLast){
        if (changeLast)
            replaceCoordinate(pathLength()-1, newCoordinate)
        else
            addCoordinate(newCoordinate)
        return false
    }

    function finishAddGeometry(){
        removeCoordinate(pathLength()-1)
    }
}
