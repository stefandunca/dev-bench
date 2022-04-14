import QtQuick 2.14
import QtQuick.Layouts 1.14

import utils 1.0
import shared 1.0
import shared.popups 1.0
import shared.stores 1.0
import shared.controls.chat 1.0

import StatusQ.Core 0.1
import StatusQ.Core.Theme 0.1
import StatusQ.Components 0.1
import StatusQ.Controls 0.1
import StatusQ.Popups 0.1

Item {
    id: popup

    implicitWidth: 400
    implicitHeight: 300

    property string userPublicKey: "0x332db32a32d3bd2a32d32da3bd123d2"
    property string userDisplayName: "Test Display Name"
    property string userIcon: ""
    property bool isUserIconIdenticon: true
    property bool isCurrentUser: true
    property var profileStore: ({
        "icon": "",
        "isIdenticon": true
    })

    ProfileHeader {
        id: firstTestControl
        x: 0
        y: 0

        displayName: popup.userDisplayName
        pubkey: popup.userPublicKey
        icon: popup.isCurrentUser ? popup.profileStore.icon : popup.userIcon
        //isIdenticon: popup.isCurrentUser ? popup.profileStore.isIdenticon : popup.isUserIconIdenticon

        displayNameVisible: false
        pubkeyVisible: false

        //emojiSize: Qt.size(20,20)
        //imageWidth: 80
        //imageHeight: 80
        //supersampling: false

        imageOverlay: Item {
            visible: popup.isCurrentUser

            StatusFlatRoundButton {
                width: 24
                height: 24

                anchors {
                    right: parent.right
                    bottom: parent.bottom
                    rightMargin: -8
                }

                type: StatusFlatRoundButton.Type.Secondary
                icon.name: "pencil"
                icon.color: Theme.palette.directColor1
                icon.width: 12.5
                icon.height: 12.5

                onClicked: Global.openChangeProfilePicPopup()
            }
        }
    }

    ProfileHeader {
        // ProfileHeader implementation is broken
        //x: firstTestControl.width + 10
        x: 120.7
        y: 0.4

        displayName: popup.userDisplayName
        pubkey: popup.userPublicKey
        icon: popup.isCurrentUser ? popup.profileStore.icon : popup.userIcon
        //isIdenticon: popup.isCurrentUser ? popup.profileStore.isIdenticon : popup.isUserIconIdenticon

        displayNameVisible: false
        pubkeyVisible: false

        //emojiSize: Qt.size(20,20)
        //imageWidth: 80
        //imageHeight: 80

        imageOverlay: Item {
            visible: popup.isCurrentUser

            StatusFlatRoundButton {
                width: 24
                height: 24

                anchors {
                    right: parent.right
                    bottom: parent.bottom
                    rightMargin: -8
                }

                type: StatusFlatRoundButton.Type.Secondary
                icon.name: "pencil"
                icon.color: Theme.palette.directColor1
                icon.width: 12.5
                icon.height: 12.5

                onClicked: Global.openChangeProfilePicPopup()
            }
        }
    }
}
