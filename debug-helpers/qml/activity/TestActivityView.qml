import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml.Models 2.15

import "views" 1.0

Item {
    id: root

    width: 640
    height: 480

    property int itemsCount: 50

    ActivityView {
        id: activityView

        anchors.fill: parent

        controller: activityController
    }

    QtObject {
        id: activityController

        property var model: dummyModel
        property bool loadingData: false

        function loadMoreItems() {
            console.debug(`@dd loadMoreItems - Current count: ${dummyModel.count}}`)
            loadingData = true
            loadTimer.restart()
        }
    }

    Timer {
        id: loadTimer

        interval: 1000
        running: false
        repeat: false

        onTriggered: {
            root.loadMoreItems()
            activityController.loadingData = false
        }
    }

    function loadMoreItems() {
        if(dummyModel.count <= root.itemsCount) {
            if(dummyModel.count < root.itemsCount) {
                for (var i = 0; i < 10; i++) {
                    dummyModel.append({"activityEntry": testEntry1})
                }
                // Simulate might have more
                dummyModel.hasMore = dummyModel.count <= root.itemsCount
            } else {
                dummyModel.hasMore = false
            }
        }
    }

    QtObject {
        id: testEntry1

        property var amount: "10.0"
        property var sender: "Alice"
        property var recipient: "Bob"
        property var timestamp: 1623922393
        property var status: 2 //corresponding to ActivityView.ActivityStatus.Complete
        property var isPendingTransaction: false
        property var isMultiTransaction: false
        property var fromAmount: 0.0
        property var toAmount: 0.0
    }

    // Create a dummy model
    ListModel {
        id: dummyModel

        property bool hasMore: true
    }
}
