import QtQuick 2.15
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4

Rectangle {
    id: root
    width: 280
    height: 30
    color: 'lightgray'

    property alias ipInputText: ipInput.text
    property alias portInputText: portInput.text


    signal connectButtonClicked()

    Row {
        height: parent.height - 4
        anchors.centerIn: parent
        spacing: 4
        TextField {
            id: ipInput
            width: 120
            height: parent.height
            placeholderText: "IP"
            textColor: 'black'
            style: TextFieldStyle {
                background: Rectangle {
                    color: 'lightgray'
                    border.color: 'black'
                    border.width: 1
                }
            }
        }
        TextField {
            id: portInput
            width: 60
            height: parent.height
            placeholderText: "PORT"
            textColor: 'black'
            style: TextFieldStyle {
                background: Rectangle {
                    color: 'lightgray'
                    border.color: 'black'
                    border.width: 1
                }
            }
        }
        TextButton {
            id: connectBtn
            width: 80
            height: parent.height
            text:  'Connect'
            textSize: 14
            normalColor: 'lavender'
            radius: 4
            onBtnClicked: {
                console.log('%1 button clicked.'.arg(text))
                root.connectButtonClicked()
            }
        }
    }
}