import QtQuick 2.15
//import QtQuick.Controls 1.4
//import QtQuick.Controls.Styles 1.4

Rectangle {
    id: root

    property alias text: btnText.text
    property alias textSize: btnText.font.pixelSize
    property alias textColor: btnText.color
    property color normalColor: "transparent"
    property color pressedColor: Qt.darker(normalColor, 1.5)

    signal btnClicked()

    Text {
        id: btnText
        anchors.fill: parent
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
    }

    MouseArea {
        id: btnMouseArea
        anchors.fill: parent
        onClicked: root.btnClicked()
    }

    states: [
        State {
            name: "normal"
            when: !btnMouseArea.containsPress
            PropertyChanges { target: root; color: root.normalColor }
        },
        State {
            name: "pressed"
            when: btnMouseArea.containsPress
            PropertyChanges { target: root; color: root.pressedColor }
        }
    ]
}