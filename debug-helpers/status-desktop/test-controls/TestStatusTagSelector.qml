import QtQuick 2.14
import QtQuick.Layouts 1.14

import StatusQ.Components 0.1

Item {

    implicitWidth: mainLayout.implicitWidth
    implicitHeight: mainLayout.implicitHeight

    ColumnLayout {
        id: mainLayout

        StatusTagSelector {
           width: 650
           height: 44

           namesModel: ListModel {
               ListElement {
                   publicId: "0x0"
                   name: "Maria"
                   icon: ""
                   isIdenticon: false
                   onlineStatus: 3
               }
               ListElement {
                   publicId: "0x1"
                   name: "James"
                   icon: "https://pbs.twimg.com/profile_images/1369221718338895873/T_5fny6o_400x400.jpg"
                   isIdenticon: false
                   onlineStatus: 1
               }
               ListElement {
                   publicId: "0x2"
                   name: "Paul"
                   icon: ""
                   isIdenticon: false
                   onlineStatus: 2
               }
           }
           property ListModel contactsModel: ListModel {
               ListElement {
                   publicId: "0x0"
                   name: "Maria"
                   icon: ""
                   isIdenticon: false
                   onlineStatus: 3
               }
               ListElement {
                   publicId: "0x1"
                   name: "James"
                   icon: "https://pbs.twimg.com/profile_images/1369221718338895873/T_5fny6o_400x400.jpg"
                   isIdenticon: false
                   onlineStatus: 1
               }
               ListElement {
                   publicId: "0x2"
                   name: "Paul"
                   icon: ""
                   isIdenticon: false
                   onlineStatus: 2
               }
               ListElement {
                   publicId: "0x3"
                   name: "Mona"
                   icon: ""
                   isIdenticon: false
                   onlineStatus: 3
               }
               ListElement {
                   publicId: "0x4"
                   name: "John"
                   icon: "https://pbs.twimg.com/profile_images/1369221718338895873/T_5fny6o_400x400.jpg"
                   isIdenticon: false
                   onlineStatus: 1
               }
               ListElement {
                   publicId: "0x5"
                   name: "Alien"
                   icon: ""
                   isIdenticon: false
                   onlineStatus: 2
               }
           }
           listLabel: qsTr("Contacts")
           toLabelText: qsTr("To: ")
           warningText: qsTr("USER LIMIT REACHED")
           onTextChanged: sortModel(contactsModel)

        }
    }

}
