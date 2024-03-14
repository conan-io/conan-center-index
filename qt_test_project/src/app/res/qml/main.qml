// Copyright (C) 2019 Julian Sherollari <jdotsh@gmail.com>
// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Dialogs
import QtQuick.Controls
import QtCore
import QtMultimedia

ApplicationWindow {
    id: win
    visible: true
    width: 512
    height: 512
    title: qsTr("Test mediaplayer: ")

   MediaPlayer {
        id: mediaplayer
        source: "https://download.samplelib.com/mp4/sample-5s.mp4"
        videoOutput: videoOutput
        audioOutput: AudioOutput {}

        onErrorOccurred: {
            console.log("E")
            console.log( mediaPlayer.errorString );
        }
    }

    VideoOutput {
        id: videoOutput
        anchors.fill: parent
    }

    MouseArea {
        anchors.fill: parent
        onPressed: { mediaplayer.play(); console.log( "click" ) }
    }

    Rectangle {
        color: "green"
        width: 50
        height: 50
    }

    Image {
        source: "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/PNG_Test.png/477px-PNG_Test.png"
        width: 100
        height: 100
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.rightMargin: 5
        anchors.bottomMargin: 5
    }
}
