import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14

import shared.panels 1.0
import "./TestBannerData"

Item {
    id: root

    implicitWidth: mainLayout.implicitWidth
    implicitHeight: mainLayout.implicitHeight

    ColumnLayout {
        id: mainLayout
        RowLayout {
            id: controlsLayout

            Label {
                text: "Left size"
            }

            Slider {
                from: 100
                to: 500
                value: emptyTestControl.Layout.preferredWidth
                onMoved: emptyTestControl.Layout.preferredWidth = value
            }
            CheckBox {
                id: roundedCheckBox
                text: "Rounded"
                checked: false
            }
            Label {
                text: "Radius"
            }

//            Slider {
//                id: devSlider
//                from: 0
//                to: 200
//                value: emptyTestControl.radius
//                onMoved: emptyTestControl.radius = value
//            }
        }

        RowLayout {
            EditCroppedImagePanel {
                id: emptyTestControl

                Layout.preferredWidth: 160
                Layout.preferredHeight: Layout.preferredWidth

                imageFileDialogTitle: qsTr("Choose an image for profile picture")
                title: qsTr("Profile picture")
                acceptButtonText: qsTr("Make this my profile picture")

                aspectRatio: 1
                roundedImage: roundedCheckBox.checked

                NoImageUploadedPanel {
                    anchors.centerIn: parent

                    visible: true
                }
            }

            EditCroppedImagePanel {
                id: dataImageTestControl

                Layout.preferredWidth: emptyTestControl.Layout.preferredWidth
                Layout.preferredHeight: emptyTestControl.Layout.preferredHeight

                imageFileDialogTitle: qsTr("Choose an image for profile picture")
                title: qsTr("Profile picture")
                acceptButtonText: qsTr("Make this my profile picture")

                aspectRatio: 1
                roundedImage: roundedCheckBox.checked
                //radius: emptyTestControl.radius

                dataImage: FirstTestImageData.deaTestImageData
            }
            EditCroppedImagePanel {
                id: selectedImageTestControl

                Layout.preferredWidth: emptyTestControl.Layout.preferredWidth
                Layout.preferredHeight: emptyTestControl.Layout.preferredHeight

                imageFileDialogTitle: qsTr("Choose an image for profile picture")
                title: qsTr("Profile picture")
                acceptButtonText: qsTr("Make this my profile picture")

                aspectRatio: 1
                roundedImage: roundedCheckBox.checked
                //radius: emptyTestControl.radius

                source: "/Users/stefan/proj/status/debug-helpers/status-desktop/test-controls/TestBannerPanel/portrait.jpg"
            }
        }
    }
}
