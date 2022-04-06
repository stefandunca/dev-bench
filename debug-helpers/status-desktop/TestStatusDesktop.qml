import QtQml 2.14
import QtQuick.Window 2.14

import DebugStatus 0.1

Window {
    title: qsTr("Debug Status Desktop")

    x: 300
    y: 100
    width: debugView.implicitWidth
    height: debugView.implicitHeight

    visible: true

    DebugView {
        id: debugView
        anchors.fill: parent

        testFolder: `${Qt.resolvedUrl(".")}/test-controls/`
        initialTest: "TestCommunityEditSettingsPanel.qml"
    }
}
