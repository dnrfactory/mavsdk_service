from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant
import logging
import asyncio

from droneProxy import DroneProxy
from asyncThread import AsyncThread

logger = logging.getLogger()


class MainController(QObject):
    def __init__(self, qmlContext, parent=None):
        super().__init__(parent)
        self._qmlContext = qmlContext
        self._qmlContext.setContextProperty('mainController', self)

        self._drones = [DroneProxy(), DroneProxy(port="50052", index=1), DroneProxy(port="50053", index=2), DroneProxy(port="50054", index=3)]

        i = 0
        for drone in self._drones:
            self._qmlContext.setContextProperty(f'drone{i}', drone)
            i += 1

    @pyqtSlot(int, str, str)
    def connect(self, index, ip, port):
        logger.debug('')
        AsyncThread.getInstance().put((self._connect_async, (index, ip, port)))

    async def _connect_async(self, index, ip, port):
        logger.debug('')
        await self._drones[index].connect(f"udp://{ip}:{port}")
