import DebugStatus 0.1

DebugWindow {
    title: qsTr("Debug Status Desktop")

    testFolder: `${Qt.resolvedUrl(".")}/test-controls/`
    initialTest: "TestStyledText"
}
