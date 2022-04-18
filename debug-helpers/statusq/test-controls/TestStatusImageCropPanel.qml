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
            id: bannerPreview

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
        }
    }

    Settings {
        id: settings

        category: "TestStatusImageCropPanel"

        property alias interactive: interactiveCheckBox.checked
        property rect cropRect

        //Component.onCompleted: bannerPreview.setCropRect(cropRect)
    }
}
