import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Window 2.14

import shared.panels 1.0
import AppLayouts.Profile.popups 1.0
import "../dummies/local_account_sensitive_settings.nim.js" as LocalAccountSensitiveSettings

Item {
    anchors.fill: parent

    property var localAccountSensitiveSettings: LocalAccountSensitiveSettings


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
            // text: Utils.getMessageWithStyle(Utils.linkifyAndXSS(StatusQUtils.Emoji.parse(message)), false)
            //text: '<style type="text/css">img, a, del, code, blockquote { margin: 0; padding: 0; }code {font-family: Roboto Mono;font-weight: 400;font-size: 14;padding: 2px 4px;border-radius: 4px;background-color: #eef2f5;color: #000000;white-space: pre;}p {line-height: 22px;}a {color: #4360df;}a.mention {color: #0da4c9;background-color: #1a07bce9;text-decoration: none;padding: 0px 2px;}del {text-decoration: line-through;}table.blockquote td {padding-left: 10px;color: #939ba1;}table.blockquote td.quoteline {background-color: #939ba1;height: 100%;padding-left: 0;}.emoji {vertical-align: bottom;}span.isEdited {color: #939ba1;margin-left: 5px}</style><p>Text here <img alt="😪" src width="18" height="18" /><img alt="😪" src width="18" height="18" /><img alt="😑" src width="18" height="18" /><img alt="🤔" src width="18" height="18" /><img alt="☺️" src width="18" height="18" /><img alt="😉" src width="18" height="18" /> <img alt="😍" src width="18" height="18" /></p>'
            text: {
                return `<html>`+
                `<head>`+
                    `<style type="text/css">`+
                    `a {`+
                        `color: black;`+
                        `text-decoration: none;`+
                    `}`+
                    `</style>`+
                `</head>`+
                `<body>`+
                    '<style type="text/css">img, a, del, code, blockquote { margin: 0; padding: 0; }code {font-family: Roboto Mono;font-weight: 400;font-size: 14;padding: 2px 4px;border-radius: 4px;background-color: #eef2f5;color: #000000;white-space: pre;}p {line-height: 22px;}a {color: #4360df;}a.mention {color: #0da4c9;background-color: #1a07bce9;text-decoration: none;padding: 0px 2px;}del {text-decoration: line-through;}table.blockquote td {padding-left: 10px;color: #939ba1;}table.blockquote td.quoteline {background-color: #939ba1;height: 100%;padding-left: 0;}.emoji {vertical-align: bottom;}span.isEdited {color: #939ba1;margin-left: 5px}</style><p>Text here <img alt="😪" src width="18" height="18" /><img alt="😪" src width="18" height="18" /><img alt="😑" src width="18" height="18" /><img alt="🤔" src width="18" height="18" /><img alt="☺️" src width="18" height="18" /><img alt="😉" src width="18" height="18" /> <img alt="😍" src width="18" height="18" /></p>'+
                `</body>`+
            `</html>`;
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
