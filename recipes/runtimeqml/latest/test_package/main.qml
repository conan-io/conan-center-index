import QtQuick

Window {
    visible: true
    width: 640
    height: 480
    title: "Runtime Qml Test"
    Rectangle {
        anchors.fill: parent
        Component.onCompleted: () => {
            console.log("Successfully Loaded");
            Qt.quit();
        }
    }
}