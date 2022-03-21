import DebugStatus 0.1

DebugWindow {
    title: qsTr("Debug StatusQ")

    testFolder: `${Qt.resolvedUrl(".")}/test-controls/`
    initialTest: "TestStatusInput"
}
