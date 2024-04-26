from PyQt5.QtCore import QUrl, QObject, pyqtSlot
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQuick import QQuickView
# from PyQt5.QtQuick import QQuickWindow

from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import Qt

import sys
import logging
import time
from functools import partial

import mainController
import asyncThread

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

    engine = QQmlApplicationEngine()
    engine.warnings.connect(_handleQmlWarnings)

    mainController = mainController.MainController(engine.rootContext(), app)

    engine.load(QUrl.fromLocalFile("qml/Main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)

    asyncThread.AsyncThread().getInstance().start()

    wm = WindowManager(app)
    wm.cleanupFunc = lambda: (
        mainController.cleanup(),
        asyncThread.AsyncThread().getInstance().putFinishMsg()
    )

    main_window = engine.rootObjects()[0]
    main_window.closing.connect(wm.onMainWindowClosed)

    sys.exit(app.exec_())
