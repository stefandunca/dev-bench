import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property var controller: null

    enum ActivityType {
        Send,
        Receive,
        Buy,
        Swap,
        Bridge
    }

    enum ActivityStatus {
        Failed,
        Pending,
        Complete,
        Finalized
    }

    ColumnLayout {
        anchors.fill: parent

        ListView {
            id: listView

            Layout.fillWidth: true
            Layout.fillHeight: true

            Component.onCompleted: {
                if(controller.model.hasMore) {
                    controller.loadMoreItems();
                }
            }

            model: controller.model

            delegate: Item {
                width: parent ? parent.width : 0
                height: itemLayout.implicitHeight

                readonly property var entry: model.activityEntry

                ColumnLayout {
                    id: itemLayout
                    anchors.fill: parent
                    spacing: 5

                    RowLayout {
                        Label { text: entry.isMultiTransaction ? entry.fromAmount : entry.amount }
                        Label { text: "from"; Layout.leftMargin: 5; Layout.rightMargin: 5 }
                        Label { text: entry.sender; Layout.maximumWidth: 200; elide: Text.ElideMiddle }
                        Label { text: "to"; Layout.leftMargin: 5; Layout.rightMargin: 5 }
                        Label { text: entry.recipient; Layout.maximumWidth: 200; elide: Text.ElideMiddle }
                        Label { text: "got"; Layout.leftMargin: 5; Layout.rightMargin: 5; visible: entry.isMultiTransaction }
                        Label { text: entry.toAmount; Layout.leftMargin: 5; Layout.rightMargin: 5; visible: entry.isMultiTransaction }
                        RowLayout {}    // Spacer
                    }
                    RowLayout {
                        Label { text: entry.isMultiTransaction ? "MT" : entry.isPendingTransaction ? "PT" : " T" }
                        Label { text: `[${root.epochToDateStr(entry.timestamp)}] ` }
                        Label {
                            text: `{${
                                function() {
                                    switch (entry.status) {
                                        case ActivityView.ActivityStatus.Failed: return "Failed";
                                        case ActivityView.ActivityStatus.Pending: return "Pending";
                                        case ActivityView.ActivityStatus.Complete: return "Complete";
                                        case ActivityView.ActivityStatus.Finalized: return "Finalized";
                                    }
                                    return "-"
                                }()}}`
                            Layout.leftMargin: 5;
                        }
                        RowLayout {}    // Spacer
                    }
                }
            }

            onContentYChanged: checkIfFooterVisible()
            onHeightChanged: checkIfFooterVisible()
            onContentHeightChanged: checkIfFooterVisible()
            Connections {
                target: listView.footerItem
                function onHeightChanged() {
                    listView.checkIfFooterVisible()
                }
            }

            function checkIfFooterVisible() {
                if((contentY + height) > (contentHeight - footerItem.height) && controller.model.hasMore && !controller.loadingData) {
                    controller.loadMoreItems();
                }
            }

            footer: Column {
                id: loadingItems

                width: listView.width
                visible: controller.model.hasMore

                Repeater {
                    model: controller.model.hasMore ? 10 : 0

                    Text {
                        text: loadingItems.loadingPattern
                    }
                }

                property string loadingPattern: ""
                property int glanceOffset: 0
                Timer {
                    interval: 25; repeat: true; running: true

                    onTriggered: {
                        let offset = loadingItems.glanceOffset
                        let length = 100
                        let slashCount = 3;

                        let pattern = new Array(length).fill(' ');

                        for (let i = 0; i < slashCount; i++) {
                            let position = (offset + i) % length;
                            pattern[position] = '/';
                        }
                        pattern = '[' + pattern.join('') + ']';

                        loadingItems.loadingPattern = pattern;
                        loadingItems.glanceOffset = (offset + 1) % length;
                    }
                }
            }

            ScrollBar.vertical: ScrollBar {}
        }
    }

    function epochToDateStr(epochTimestamp) {
        var date = new Date(epochTimestamp * 1000);
        return date.toLocaleString(Qt.locale(), "dd-MM-yyyy hh:mm");
    }
}