import QtQuick 2.14
import QtQuick.Layouts 1.14
import QtQuick.Controls 2.14

import StatusQ.Controls 0.1

Item {
    implicitWidth: mainLayout.implicitWidth
    implicitHeight: mainLayout.implicitHeight

    ColumnLayout {
        id: mainLayout

        anchors.fill: parent

        Rectangle {
            id: testFence

            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: controlLayout.implicitWidth
            Layout.preferredHeight: controlLayout.implicitHeight

            property int testFenceWidth: 5

            border.width: testFenceWidth
            border.color: Qt.lighter("orange", 1.5)

            ColumnLayout {
                id: controlLayout

                anchors.fill: parent

                StatusBaseInput {
                    id: testControl

                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.margins: testFence.testFenceWidth

                    multiline: multilineCB.checked
                    clearable: clearableCB.checked
                    placeholderText: placeholderTextTI.text
                }
            }
        }
        RowLayout {
            Label {
                text: qsTr("Content")
            }
            Label {
                text: testControl.text
                Rectangle {
                    anchors.fill: parent
                    anchors.margins: -border.width
                    border.width: 2; border.color: Qt.darker("pink", 2)
                    z: parent.z - 1
                }
            }
        }
        GridLayout {
            id: propsLayout

            CheckBox {
                id: multilineCB
                text: qsTr("Multiline")
            }
            CheckBox {
                id: clearableCB
                text: qsTr("Clearable")
            }
            RowLayout {
                Label { text: qsTr("Placeholder Text") }
                TextInput {
                    id: placeholderTextTI
                    text: qsTr("Placeholder Text")
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: -border.width
                        border.width: 2; border.color: "Light Grey"
                        z: parent.z - 1
                    }
                }
            }
        }
    }
}
