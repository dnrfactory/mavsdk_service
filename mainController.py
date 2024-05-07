from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant
import logging
import asyncio

from droneProxy import DroneProxy
from asyncThread import AsyncThread
from swarmManager import SwarmManager

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

    def cleanup(self):
        for drone in self._drones:
            drone.cleanup()

    @pyqtSlot(int, str, str)
    def connect(self, index, ip, port):
        logger.debug(f'index:{index}, ip:{ip}, port:{port}')
        AsyncThread.getInstance().put((self._connect_async, (index, ip, port)))

    async def _connect_async(self, index, ip, port):
        logger.debug('')
        await self._drones[index].connect(f"udp://{ip}:{port}")

    @pyqtSlot(int)
    def setLeaderDrone(self, index):
        logger.debug('')
        SwarmManager.getInstance().setLeader(self._drones[index])

    @pyqtSlot(int, float, float)
    def addFollowerDrone(self, index, distance, angle):
        logger.debug('')
        SwarmManager.getInstance().addFollower(self._drones[index], distance, angle)

    @pyqtSlot(int)
    def removeFollowerDrone(self, index):
        logger.debug('')
        SwarmManager.getInstance().removeFollower(self._drones[index])

    @pyqtSlot()
    def readyToFollow(self):
        logger.debug('')
        AsyncThread.getInstance().put((SwarmManager.getInstance().readyToFollow, ()))

    @pyqtSlot()
    def followLeader(self):
        logger.debug('')
        AsyncThread.getInstance().put((SwarmManager.getInstance().runTaskFollow, ()))

    @pyqtSlot()
    def stopFollow(self):
        logger.debug('')
        SwarmManager.getInstance().stopFollow()

    @pyqtSlot(int)
    def arm(self, index):
        logger.debug('')
        AsyncThread.getInstance().put((self._drones[index].arm, ()))

    @pyqtSlot(int)
    def startOffboardMode(self, index):
        logger.debug('')
        AsyncThread.getInstance().put((self._drones[index].start_offboard_mode, ()))

    @pyqtSlot(int)
    def stopOffboardMode(self, index):
        logger.debug('')
        AsyncThread.getInstance().put((self._drones[index].stop_offboard_mode, ()))
