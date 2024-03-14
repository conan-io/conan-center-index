// Copyright (C) 2019 Julian Sherollari <jdotsh@gmail.com>
// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Dialogs
import QtQuick.Controls
import QtPositioning
import QtLocation
import QtCore
import Qt.GeoJson
import "mapitems"

ApplicationWindow {
    id: win
    visible: true
    width: 512
    height: 512
    menuBar: mainMenu
    title: qsTr("GeoJSON Viewer: ") + view.map.center +
           " zoom " + view.map.zoomLevel.toFixed(3)
           + " min " + view.map.minimumZoomLevel +
           " max " + view.map.maximumZoomLevel

    FileDialog {
        visible: false
        id: fileDialog
        title: "Choose a GeoJSON file"
        fileMode: FileDialog.OpenFile
        currentFolder: dataPath
        nameFilters: ["GeoJSON files (*.geojson *.json)"]
        onAccepted: {
            view.clearAllItems()
            geoJsoner.load(fileDialog.selectedFile)
        }
    }

    FileDialog {
        visible: false
        id: fileWriteDialog
        title: "Write your geometry to a file"
        fileMode: FileDialog.SaveFile
        currentFolder: StandardPaths.writableLocation(StandardPaths.TempLocation)
        nameFilters: ["GeoJSON files (*.geojson *.json)"]
        //! [Write File]
        onAccepted: {
            geoJsoner.dumpGeoJSON(geoJsoner.toVariant(miv), fileWriteDialog.selectedFile);
        }
        //! [Write File]
    }

    FileDialog {
        visible: false
        id: debugWriteDialog
        title: "Write Qvariant debug view"
        fileMode: FileDialog.SaveFile
        currentFolder: StandardPaths.writableLocation(StandardPaths.TempLocation)
        nameFilters: ["GeoJSON files (*.geojson *.json)"]
        onAccepted: {
            geoJsoner.writeDebug(geoJsoner.toVariant(miv), debugWriteDialog.selectedFile);
        }
    }

    MenuBar {
        id: mainMenu

        Menu {
            title: "&File"
            id : geoJsonMenu
            MenuItem {
                text: "&Open"
                onTriggered: {
                    fileDialog.open()
                }
            }
            MenuItem {
                text: "&Export"
                onTriggered: {
                    fileWriteDialog.open()
                }
            }
            MenuItem {
                text: "&Clear"
                onTriggered: {
                    view.clearAllItems()
                }
            }
            MenuItem {
                text: "E&xit"
                onTriggered: Qt.quit()
            }
        }
        Menu {
            title: "&Debug"
            id : debugMenu
            MenuItem {
                text: "Print debug data to &file"
                onTriggered: {
                    debugWriteDialog.open()
                }
            }
            MenuItem {
                text: "&Print debug data"
                onTriggered: {
                    geoJsoner.print(miv)
                }
            }
        }
    }

    GeoJsoner {
        id: geoJsoner
    }

    Shortcut {
        enabled: view.map.zoomLevel < view.map.maximumZoomLevel
        sequence: StandardKey.ZoomIn
        onActivated: view.map.zoomLevel = Math.round(view.map.zoomLevel + 1)
    }
    Shortcut {
        enabled: view.map.zoomLevel > view.map.minimumZoomLevel
        sequence: StandardKey.ZoomOut
        onActivated: view.map.zoomLevel = Math.round(view.map.zoomLevel - 1)
    }

    //! [MapView Creation]
    MapView {
        id: view
        anchors.fill: parent
        map.plugin: Plugin { name: "osm" }
        map.zoomLevel: 4
    //! [MapView Creation]

        property variant unfinishedItem: undefined

        signal showMainMenu(variant coordinate)

        //! [add item]
        function addGeoItem(item)
        {
            var co = Qt.createComponent('mapitems/'+item+'.qml')
            if (co.status === Component.Ready) {
                unfinishedItem = co.createObject(map)
                unfinishedItem.setGeometry(tapHandler.lastCoordinate)
                unfinishedItem.addGeometry(hoverHandler.currentCoordinate, false)
                view.map.addMapItem(unfinishedItem)
            } else {
                console.log(item + " is not supported right now, please call us later.")
            }
        }
        //! [add item]

        //! [finish item]
        function finishGeoItem()
        {
            unfinishedItem.finishAddGeometry()
            geoJsoner.addItem(unfinishedItem)
            map.removeMapItem(unfinishedItem)
            unfinishedItem = undefined
        }
        //! [finish item]

        //! [clearAllItems]
        function clearAllItems()
        {
            geoJsoner.clear();
        }
        //! [clearAllItems]

        //! [MapItemView]
        MapItemView {
            id: miv
            parent: view.map
            //! [MapItemView]
            //! [MapItemView Model]
            model: geoJsoner.model
            //! [MapItemView Model]
            //! [MapItemView Delegate]
            delegate: GeoJsonDelegate {
            }
            //! [MapItemView Delegate]
        }
        Menu {
            id: mapPopupMenu

            property variant coordinate

            MenuItem {
                text: qsTr("Rectangle")
                onTriggered: view.addGeoItem("RectangleItem")
            }
            MenuItem {
                text: qsTr("Circle")
                onTriggered: view.addGeoItem("CircleItem")
            }
            MenuItem {
                text: qsTr("Polyline")
                onTriggered: view.addGeoItem("PolylineItem")
            }
            MenuItem {
                text: qsTr("Polygon")
                onTriggered: view.addGeoItem("PolygonItem")
            }
            MenuItem {
                text: qsTr("Clear all")
                onTriggered: view.clearAllItems()
            }

            function show(coordinate) {
                mapPopupMenu.coordinate = coordinate
                mapPopupMenu.popup()
            }
        }

        //! [Hoverhandler Map]
        HoverHandler {
            id: hoverHandler
            property variant currentCoordinate
            grabPermissions: PointerHandler.CanTakeOverFromItems | PointerHandler.CanTakeOverFromHandlersOfDifferentType

            onPointChanged: {
                currentCoordinate = view.map.toCoordinate(hoverHandler.point.position)
                if (view.unfinishedItem !== undefined)
                    view.unfinishedItem.addGeometry(view.map.toCoordinate(hoverHandler.point.position), true)
            }
        }
        //! [Hoverhandler Map]

        TapHandler {
            id: tapHandler
            property variant lastCoordinate
            acceptedButtons: Qt.LeftButton | Qt.RightButton

            //! [Taphandler Map]
            onSingleTapped: (eventPoint, button) => {
                lastCoordinate = view.map.toCoordinate(tapHandler.point.position)
                if (button === Qt.RightButton) {
                    if (view.unfinishedItem !== undefined) {
                        view.finishGeoItem()
                    } else
                        mapPopupMenu.show(lastCoordinate)
                } else if (button === Qt.LeftButton) {
                    if (view.unfinishedItem !== undefined) {
                        if (view.unfinishedItem.addGeometry(view.map.toCoordinate(tapHandler.point.position), false)) {
                            view.finishGeoItem()
                        }
                    }
                }
            }
            //! [Taphandler Map]
        }
        TapHandler {
            acceptedButtons: Qt.LeftButton | Qt.RightButton
            onDoubleTapped: (eventPoint, button) => {
                var preZoomPoint = view.map.toCoordinate(eventPoint.position);
                if (button === Qt.LeftButton)
                    view.map.zoomLevel = Math.floor(view.map.zoomLevel + 1)
                else
                    view.map.zoomLevel = Math.floor(view.map.zoomLevel - 1)
                var postZoomPoint = view.map.toCoordinate(eventPoint.position);
                var dx = postZoomPoint.latitude - preZoomPoint.latitude;
                var dy = postZoomPoint.longitude - preZoomPoint.longitude;
                view.map.center = QtPositioning.coordinate(view.map.center.latitude - dx,
                                                           view.map.center.longitude - dy);
            }
        }
    }
}
