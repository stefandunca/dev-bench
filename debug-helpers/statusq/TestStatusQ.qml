import DebugStatus 0.1

import QtQuick 2.14
import QtQuick.Window 2.14

Window {
    x: 100
    y: 100
    width: 640
    height: 480

    visible: true

    title: qsTr("Hello World")

    DebugView {
        testFolder: `${Qt.resolvedUrl(".")}/test-controls/`
        initialTest: "TestStatusImageCropPanel.qml"
    }
}
