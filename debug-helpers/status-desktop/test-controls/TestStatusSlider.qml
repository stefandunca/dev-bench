import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Window 2.14
import QtQuick.Layouts 1.14

import shared.panels 1.0
import utils 1.0
import StatusQ.Core.Utils 0.1 as StatusQUtils
import StatusQ.Controls 0.1

Item {
    implicitWidth: mainLayout.implicitWidth
    implicitHeight: mainLayout.implicitHeight

    ColumnLayout {
        id: mainLayout

        anchors.fill: parent

        StatusSlider {
            id: testSlider

            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: 10

            enabled: true

            from: 1
            value: 10
            live: false

            to: 100

            Rectangle {
                border.width: 1
                border.color: "fuchsia"
                anchors.fill: parent
                color: "transparent"
                anchors.margins: -border.width
                z: parent.z - 1
            }
        }
    }
}
