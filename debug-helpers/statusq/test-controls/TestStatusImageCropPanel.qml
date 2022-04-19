import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14

import Qt.labs.settings 1.0

import StatusQ.Core.Theme 0.1
import StatusQ.Components 0.1

Item {
    implicitWidth: 400
    implicitHeight: 300

    ColumnLayout {
        id: mainLayout

        anchors.fill: parent

        StatusImageCropPanel {
            id: testControl

            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignHCenter

            interactive: settings.interactive
            wallColor: Theme.palette.statusAppLayout.backgroundColor
            wallTransparency: 1

            source: `${Qt.resolvedUrl(".")}../../../StatusQ/sandbox/demoapp/data/logo-test-image.png`

            Component.onDestruction: settings.cropRect = cropRect
        }
        RowLayout {
            CheckBox {
                id: interactiveCheckBox
                text: "Interactive"
                checked: false
            }
            Text { text: aspectRatioControl.from }
            Slider {
                id: aspectRatioControl
                from: 0.5
                to: 5
                value: testControl.aspectRatio
                live: false
                onMoved: testControl.aspectRatio = valueAt(visualPosition)
            }
            Text { text: aspectRatioControl.to }
        }
    }

    Settings {
        id: settings

        category: "TestStatusImageCropPanel"

        property alias interactive: interactiveCheckBox.checked
        property rect cropRect

        Component.onCompleted: testControl.setCropRect(cropRect)
    }
}
