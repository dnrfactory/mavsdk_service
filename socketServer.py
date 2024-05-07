from PyQt5.QtCore import QUrl, QObject, pyqtSlot, pyqtSignal
from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QHostAddress

import sys
import logging
import json

logger = logging.getLogger()


class SocketServer(QObject):
    instance = None
    connect = pyqtSignal(int, str, str)
    setLeaderDrone = pyqtSignal(int)
    addFollowerDrone = pyqtSignal(int, float, float)
    removeFollowerDrone = pyqtSignal(int)
    readyToFollow = pyqtSignal()
    followLeader = pyqtSignal()
    stopFollow = pyqtSignal()
    arm = pyqtSignal(int)
    startOffboardMode = pyqtSignal(int)
    stopOffboardMode = pyqtSignal(int)
    setVelocityBody = pyqtSignal(int, float, float, float, float)
    setVelocityNED = pyqtSignal(int, float, float, float, float)
    setAttitude = pyqtSignal(int, float, float, float, float)
    setPositionNED = pyqtSignal(int, float, float, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.server = QTcpServer(self)
        self.server.newConnection.connect(self._new_connection)
        self.clients = []

    @classmethod
    def getInstance(cls):
        if cls.instance is None:
            cls.instance = SocketServer()
        return cls.instance

    def start_server(self):
        if not self.server.listen(QHostAddress.Any, 12345):
            logger.debug("Unable to start the server:", self.server.errorString())
            self.close()

        logger.debug("Server started on port 12345")

    def _new_connection(self):
        client_socket = self.server.nextPendingConnection()
        client_socket.readyRead.connect(lambda: self.receive_message(client_socket))

        self.clients.append(client_socket)
        logger.debug("New connection")

    def receive_message(self, client_socket):
        message = client_socket.readAll().data().decode()
        data = json.loads(message)
        logger.debug(f"Received from client: {data}")

        func = data['func']
        args = data['args']

        if func == "connect":
            self.connect.emit(*args)
        elif func == "setLeaderDrone":
            self.setLeaderDrone.emit(*args)
        elif func == "addFollowerDrone":
            self.addFollowerDrone.emit(*args)
        elif func == "removeFollowerDrone":
            self.removeFollowerDrone.emit(*args)
        elif func == "readyToFollow":
            self.readyToFollow.emit(*args)
        elif func == "followLeader":
            self.followLeader.emit(*args)
        elif func == "stopFollow":
            self.stopFollow.emit(*args)
        elif func == "arm":
            self.arm.emit(*args)
        elif func == "startOffboardMode":
            self.startOffboardMode.emit(*args)
        elif func == "stopOffboardMode":
            self.stopOffboardMode.emit(*args)
        elif func == "setVelocityBody":
            self.setVelocityBody.emit(*args)
        elif func == "setVelocityNED":
            self.setVelocityNED.emit(*args)
        elif func == "setAttitude":
            self.setAttitude.emit(*args)
        elif func == "setPositionNED":
            self.setPositionNED.emit(*args)

    def send_message(self, msgType, value):
        data = {"type": msgType, "value": value}
        message = json.dumps(data) + '\n'
        for client in self.clients:
            client.write(message.encode())
            client.flush()