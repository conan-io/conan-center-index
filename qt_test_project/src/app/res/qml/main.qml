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
        source: "" //"/home/spiderkeys/qt_videos/bad.mp4"
        videoOutput: videoOutput

        Component.onCompleted: {
console.log("z")
        }

        onPlaybackRateChanged: {
            console.log( "playback rate: " + playbackRate )
        }

        onSourceChanged: function(source) {
            if( source === "" )
            {
                console.log("A")
            }
            else
            {
                console.log("B")
                mediaPlayer.pause()
            }
        }

        onMediaStatusChanged: {
            if( mediaStatus == MediaPlayer.EndOfMedia )
            {
                console.log("C")
            }
            console.log("D")
        }

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
}
