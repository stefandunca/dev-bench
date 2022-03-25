import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Window 2.14

import shared.panels 1.0
import utils 1.0
import StatusQ.Core.Utils 0.1 as StatusQUtils

Item {
    implicitWidth: (replyText.implicitWidth < 400 ? replyText.implicitHeight : 400) * 1.2
    implicitHeight: replyText.implicitHeight * 1.2

    Component.onCompleted: replyText.font.family

    Rectangle {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.topMargin: -3
        anchors.right: parent.right
        anchors.rightMargin: 10
        anchors.bottom: parent.bottom
        clip: true
        color: "transparent"
        visible: true

        StyledText {
            id: replyText
            readonly property string message: '<p>take some emojis 😪😪😑☺️😉 😍?</p>'
            text: {
                console.debug(`@dd orig msg "${message}"`)

                const linkified = Utils.linkifyAndXSS(message)
                console.debug(`@dd linkified "${linkified}"`)
                const parsedEmoji = StatusQUtils.Emoji.parse(linkified)
                //const parsedEmoji = '<img class="emoji" draggable="false" alt="😪" src="file:///C:/Users/stefan/proj/status/status-desktop/ui/StatusQ/src/assets/twemoji/svg/1f62a.svg?svg" width="18" height="18" style="vertical-align: top"/>'
                console.debug(`@dd parsedEmoji "${parsedEmoji}"`)
                const finalText = Utils.getMessageWithStyle(parsedEmoji, false)
                //const finalText = Utils.getMessageWithStyle(parsedEmoji, false) // Ignore XSS;
                console.debug(`@dd finalText "${finalText}"`)
                return finalText
            }
            anchors.fill: parent
            elide: Text.ElideRight
            font.pixelSize: 13
            font.weight: Font.Normal
            textFormat: Text.RichText
            color: "black"
        }
    }
}
