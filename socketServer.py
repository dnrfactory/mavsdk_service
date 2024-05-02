from PyQt5.QtCore import QUrl, QObject, pyqtSlot, pyqtSignal
from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QHostAddress

import sys
import logging
import json

logger = logging.getLogger()


class SocketServer(QObject):
    instance = None
    connect = pyqtSignal(int, str, str)

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

    def send_message(self, msgType, value):
        data = {"type": msgType, "value": value}
        message = json.dumps(data) + '\n'
        for client in self.clients:
            client.write(message.encode())
            client.flush()