import QtQuick 2.14

Item {

    implicitWidth: 600
    implicitHeight: 800

    Loader {
        id: panelLoader
        source: "../../../status-desktop/ui/app/AppLayouts/Chat/panels/communities/CommunityEditSettingsPanel.qml"

        active: true
        visible: true
        anchors.fill: parent
    }
}
