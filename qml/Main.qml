import QtQuick 2.15
import QtQuick.Controls 2.15
import "./component"

ApplicationWindow {
    id: root
    visible: true
    width: 1200
    height: 480
    title: "mavsdk_pyqt"

    property string ip: "172.17.0.2"//"localhost"

    Row {
        spacing: 10

        Column {
            spacing: 10

            ConnectionWidget {
                id: connectionWidget1
                ipInputText: root.ip
                portInputText: "14581"

                onConnectButtonClicked: {
                    mainController.connect(0, ipInputText, portInputText)
                }
            }
            DroneStatusWidget {
                drone: drone0
            }
        }
        Column {
            spacing: 10

            ConnectionWidget {
                id: connectionWidget2
                ipInputText: root.ip
                portInputText: "14582"

                onConnectButtonClicked: {
                    mainController.connect(1, ipInputText, portInputText)
                }
            }
            DroneStatusWidget {
                drone: drone1
            }
        }
        Column {
            spacing: 10

            ConnectionWidget {
                id: connectionWidget3
                ipInputText: root.ip
                portInputText: "14583"

                onConnectButtonClicked: {
                    mainController.connect(2, ipInputText, portInputText)
                }
            }
            DroneStatusWidget {
                drone: drone2
            }
        }
        Column {
            spacing: 10

            ConnectionWidget {
                id: connectionWidget4
                ipInputText: root.ip
                portInputText: "14584"

                onConnectButtonClicked: {
                    mainController.connect(3, ipInputText, portInputText)
                }
            }
            DroneStatusWidget {
                drone: drone3
            }
        }
    }
}