import QtQuick 2.15
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4

Rectangle {
    id: root
    width: 280
    height: 200
    color: 'lightgray'

    property real itemHeight: (root.height  - column.padding * 2 - column.spacing * 6) / 7
    property real keyItemWidth: 80
    property real valueItemWidth: root.width  - column.padding * 2 - keyItemWidth
    property var drone

    Column {
        id: column
        padding: 2
        spacing: 2

        KeyValueBox {
            height: itemHeight
            wKey: keyItemWidth
            wValue: valueItemWidth
            textKey: "Status"
            textValue: drone.statusText
        }
        KeyValueBox {
            height: itemHeight
            wKey: keyItemWidth
            wValue: valueItemWidth
            textKey: "Connection"
            textValue: drone.isConnected

            Connections {
                target: drone
                function onIsConnectedChanged(isConnected) {
                    console.log('onIsConnectedChanged ' + isConnected)
                }
            }
        }
        KeyValueBox {
            height: itemHeight
            wKey: keyItemWidth
            wValue: valueItemWidth
            textKey: "Arm"
            textValue: drone.isArmed
        }
        KeyValueBox {
            height: itemHeight
            wKey: keyItemWidth
            wValue: valueItemWidth
            textKey: "Flight Mode"
            textValue: drone.flightMode

            Connections {
                target: drone
                function onFlightModeChanged(flightMode) {
                    console.log('onFlightModeChanged ' + flightMode)
                }
            }
        }
        KeyValueBox {
            height: itemHeight
            wKey: keyItemWidth
            wValue: valueItemWidth
            textKey: "Latitude"
            //textValue: drone.latitude
        }
        KeyValueBox {
            height: itemHeight
            wKey: keyItemWidth
            wValue: valueItemWidth
            textKey: "Longitude"
            //textValue: drone.longitude
        }
        KeyValueBox {
            height: itemHeight
            wKey: keyItemWidth
            wValue: valueItemWidth
            textKey: "Altitude"
            //textValue: drone.altitude
        }
    }
}