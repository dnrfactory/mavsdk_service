from PyQt5.QtCore import QUrl, QObject, pyqtSlot
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQuick import QQuickView

from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import Qt

import sys
import logging
import atexit

import mainController
import asyncThread
import socketServer

logger = logging.getLogger()


class WindowManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._windowList = list()
        self.cleanupFunc = None

    def add_window(self, window):
        for win in self._windowList:
            if win == window:
                return
        self._windowList.append(window)

    @pyqtSlot()
    def onMainWindowClosed(self):
        for win in self._windowList:
            win.close()

        if self.cleanupFunc:
            self.cleanupFunc()


def _handleQmlWarnings(warnings):
    for warning in warnings:
        print("QML Warning:", warning.toString())


def exit_handler():
    logger.debug('')


if __name__ == "__main__":
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)
    rootLogger.propagate = 0
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(thread)d][%(filename)s:%(funcName)s:%(lineno)d]'
                                  ' %(message)s')
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    rootLogger.addHandler(streamHandler)

    app = QApplication(sys.argv)

    # engine = QQmlApplicationEngine()
    # engine.warnings.connect(_handleQmlWarnings)

    mainController = mainController.MainController(app)

    # engine.load(QUrl.fromLocalFile("qml/Main.qml"))
    #
    # if not engine.rootObjects():
    #     sys.exit(-1)

    asyncThread.AsyncThread().getInstance().start()

    # wm = WindowManager(app)
    # wm.cleanupFunc = lambda: (
    #     mainController.cleanup(),
    #     asyncThread.AsyncThread().getInstance().putFinishMsg()
    # )

    # main_window = engine.rootObjects()[0]
    # main_window.closing.connect(wm.onMainWindowClosed)

    socketServer.SocketServer.getInstance().start_server()
    socketServer.SocketServer.getInstance().connect.connect(mainController.connect)
    socketServer.SocketServer.getInstance().setLeaderDrone.connect(mainController.setLeaderDrone)
    socketServer.SocketServer.getInstance().addFollowerDrone.connect(mainController.addFollowerDrone)
    socketServer.SocketServer.getInstance().removeFollowerDrone.connect(mainController.removeFollowerDrone)
    socketServer.SocketServer.getInstance().readyToFollow.connect(mainController.readyToFollow)
    socketServer.SocketServer.getInstance().followLeader.connect(mainController.followLeader)
    socketServer.SocketServer.getInstance().stopFollow.connect(mainController.stopFollow)
    socketServer.SocketServer.getInstance().setFollowFrequency.connect(mainController.setFollowFrequency)
    socketServer.SocketServer.getInstance().arm.connect(mainController.arm)
    socketServer.SocketServer.getInstance().startOffboardMode.connect(mainController.startOffboardMode)
    socketServer.SocketServer.getInstance().stopOffboardMode.connect(mainController.stopOffboardMode)
    socketServer.SocketServer.getInstance().setVelocityBody.connect(mainController.setVelocityBody)
    socketServer.SocketServer.getInstance().setVelocityNED.connect(mainController.setVelocityNED)
    socketServer.SocketServer.getInstance().setAttitude.connect(mainController.setAttitude)
    socketServer.SocketServer.getInstance().setPositionNED.connect(mainController.setPositionNED)
    socketServer.SocketServer.getInstance().closeServer.connect(mainController.closeServer)
    socketServer.SocketServer.getInstance().closeServer.connect(app.quit)

    atexit.register(exit_handler)

    sys.exit(app.exec_())
