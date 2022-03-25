import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14

import Qt.labs.folderlistmodel 2.3

Item {
    implicitWidth: mainLayout.implicitWidth
    implicitHeight: mainLayout.implicitHeight

    property string testFolder: "."
    property string initialTest: ""

    FolderListModel {
        id: filesModel
        folder: testFolder
        nameFilters: ["*.qml"]
        showDirs: false
    }

    ColumnLayout {
        id: mainLayout
        anchors.fill: parent

        ComboBox {
            id: testFileCB

            Layout.fillWidth: true
            Layout.maximumWidth: 400
            Layout.alignment: Qt.AlignHCenter

            model: filesModel
            textRole: "fileName"
            valueRole: "filePath"

            onCountChanged: {
                currentIndex = -1
                const foundIdx = find(initialTest)
                currentIndex = foundIdx > -1 ? foundIdx : 0
            }
        }

        Shortcut {
            sequence: "ctrl+r"
            onActivated: {
                loadPopup.active = false
                loadPopup.active = true
            }
        }

        Loader {
            id: loadPopup

            Layout.fillWidth: true
            Layout.fillHeight: true

            source: testFileCB.currentValue ? "file:///" + testFileCB.currentValue : ""
            active: true
        }
    }
}
