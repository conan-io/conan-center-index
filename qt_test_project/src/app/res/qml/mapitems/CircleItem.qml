// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
import QtQuick
import QtLocation

MapCircle {
    color: "#da5546"
    border.color: "#330a0a"
    border.width: 2
    smooth: true
    opacity: 0.75
    autoFadeIn: false

    property string geojsonType: "Point"

    function setGeometry(anchorCoordinate) {
        center = anchorCoordinate
    }

    function addGeometry(newCoordinate, changeLast){
        radius = center.distanceTo(newCoordinate)
        return true
    }

    function finishAddGeometry(){
    }
}
