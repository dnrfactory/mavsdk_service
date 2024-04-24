import QtQuick 2.5

Row {
    id: root

    property alias wKey: rectKey.width
    property alias wValue: rectValue.width
    property alias textKey: rectKeyText.text
    property alias textValue: rectValueText.text
    property bool wKeyDynamic: false

    Rectangle {
        id: rectKey
        width: wKeyDynamic ? textMetrics.tightBoundingRect.width + 20 : 120
        height: parent.height
        color: "darkgray"
        radius: 4
        Text {
            id: rectKeyText
            anchors.centerIn: parent
        }
        TextMetrics {
            id: textMetrics
            text: rectKeyText.text
        }
    }

    Rectangle {
        id: rectValue
        width: 200
        height: parent.height
        border.width: 1
        border.color: "black"

        Text {
            id: rectValueText
            anchors.centerIn: parent
        }
    }
}