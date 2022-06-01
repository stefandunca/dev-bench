import QtQuick 2.14

import "../../../status-desktop/ui/app/AppLayouts/Chat/panels/communities"
import "./TestBannerData"

Item {

    implicitWidth: 600
    implicitHeight: 800

    property bool logoLoaded: false
    property bool bannerLoaded: false

    CommunityOverviewSettingsPanel {
        anchors.fill: parent

        name: "Community Name"
        description: "Community description"
        logoImageData: logoLoaded ? FirstTestImageData.thumbnailData : ""
        bannerImageData: bannerLoaded ? FirstTestImageData.bannerData : ""
        color: "fuchsia"
        editable: true
        owned: true
        isCommunityHistoryArchiveSupportEnabled: true
        historyArchiveSupportToggle: true
        onHistoryArchiveSupportToggleChanged: console.debug(`@dd Community History Archive support was ${historyArchiveSupportToggle ? "Enabled" : "Disabled"}`)

        // Simulate user pressing "Edit Community"
        currentIndex: 1

        onEdited: {
            console.debug(`editCommunity(
                Utils.filterXSS(${item.name}),
                Utils.filterXSS(${item.description}),
                root.community.access,
                ${item.color.toString().toUpperCase()},
                ${JSON.stringify({imagePath: String(item.logoImagePath).replace("file://", ""), cropRect: item.logoCropRect})},
                ${JSON.stringify({imagePath: String(item.bannerPath).replace("file://", ""), cropRect: item.bannerCropRect})},
                ${historyArchiveSupportToggle},
                false
            )`)
            logoLoaded = logoLoaded || item.logoImagePath.toString().length > 0
            bannerLoaded = bannerLoaded || item.bannerPath.toString().length > 0
        }
    }
}
