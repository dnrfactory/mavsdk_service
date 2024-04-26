from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal
import asyncio
import logging
from mavsdk import System

logger = logging.getLogger()


class DroneProxy(QObject):
    statusTextChanged = pyqtSignal(str)
    isConnectedChanged = pyqtSignal(bool)
    isArmedChanged = pyqtSignal(bool)
    flightModeChanged = pyqtSignal(str)
    latitudeChanged = pyqtSignal(float)
    longitudeChanged = pyqtSignal(float)
    altitudeChanged = pyqtSignal(float)

    def __init__(self, port="50051", index=0, parent=None):
        super().__init__(parent)
        self._drone = None
        self._port = port
        self._index = index

        self._task_status_text = None
        self._task_armed = None
        self._task_flight_mode = None
        self._task_position = None

        self._statusText = ''
        self._isConnected = False
        self._isArmed = False
        self._flightMode = ''
        self._latitude = 0.0
        self._longitude = 0.0
        self._altitude = 0.0

    def __del__(self):
        logger.debug("")

    @property
    def index(self):
        return self._index

    @pyqtProperty(str, notify=statusTextChanged)
    def statusText(self):
        return self._statusText

    @statusText.setter
    def statusText(self, val: str):
        self._statusText = val
        self.statusTextChanged.emit(val)

    @pyqtProperty(bool, notify=isConnectedChanged)
    def isConnected(self):
        return self._isConnected

    @isConnected.setter
    def isConnected(self, val: bool):
        self._isConnected = val
        self.isConnectedChanged.emit(val)

    @pyqtProperty(bool, notify=isArmedChanged)
    def isArmed(self):
        return self._isArmed

    @isArmed.setter
    def isArmed(self, val: bool):
        self._isArmed = val
        self.isArmedChanged.emit(val)

    @pyqtProperty(str, notify=flightModeChanged)
    def flightMode(self):
        return self._flightMode

    @flightMode.setter
    def flightMode(self, val: str):
        self._flightMode = val
        self.flightModeChanged.emit(val)

    @pyqtProperty(float, notify=latitudeChanged)
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, val: float):
        self._latitude = val
        self.latitudeChanged.emit(val)

    @pyqtProperty(float, notify=longitudeChanged)
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, val: float):
        self._longitude = val
        self.longitudeChanged.emit(val)

    @pyqtProperty(float, notify=altitudeChanged)
    def altitude(self):
        return self._altitude

    @altitude.setter
    def altitude(self, val: float):
        self._altitude = val
        self.altitudeChanged.emit(val)

    def telemetry(self):
        return self._drone.telemetry

    def cleanup(self):
        logger.debug("cleanup")
        self._cancel_tasks()

        if self._drone:
            del self._drone
            self._drone = None

    async def connect(self, addr: str):
        if self._isConnected:
            logger.debug("Already connected.")
            return

        if self._drone is None:
            self._drone = System(port=self._port)

        logger.debug("Connecting to address:" + addr)
        try:
            await asyncio.wait_for(self._drone.connect(system_address=addr), timeout=3.0)
            logger.debug("Connected to drone successfully!")

        except asyncio.TimeoutError:
            logger.debug("Connection to drone timed out!")
            return

        self.isConnected = True

        logger.debug("Waiting for drone to have a global position estimate...")
        async for health in self._drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                logger.debug("-- Global position estimate OK")
                break

        self._task_status_text = asyncio.ensure_future(self._print_status_text())
        self._task_armed = asyncio.ensure_future(self._armed())
        self._task_flight_mode = asyncio.ensure_future(self._flight_mode())
        self._task_position = asyncio.ensure_future(self._position())

    async def _print_status_text(self):
        logger.debug('')
        try:
            async for status_text in self._drone.telemetry.status_text():
                # logger.debug(f'status text: {status_text.text}')
                self.statusText = status_text.text
        except asyncio.CancelledError:
            logger.debug("_print_status_text asyncio.CancelledError.")
            return

    async def _armed(self):
        logger.debug('')
        try:
            async for is_armed in self._drone.telemetry.armed():
                # logger.debug(f'is_armed: {is_armed}')
                self.isArmed = is_armed
        except asyncio.CancelledError:
            logger.debug("_armed asyncio.CancelledError.")
            return

    async def _flight_mode(self):
        logger.debug('')
        try:
            async for flight_mode in self._drone.telemetry.flight_mode():
                # logger.debug(f'flight_mode: {flight_mode}')
                self.flightMode = flight_mode.name
        except asyncio.CancelledError:
            logger.debug("_flight_mode asyncio.CancelledError.")
            return

    async def _position(self):
        try:
            async for position in self._drone.telemetry.position():
                # self.positionChanged(position.latitude_deg, position.longitude_deg, position.relative_altitude_m)
                self.latitude = position.latitude_deg
                self.longitude = position.longitude_deg
                self.altitude = position.relative_altitude_m
        except asyncio.CancelledError:
            logger.debug("_position asyncio.CancelledError.")
            return

    def _cancel_tasks(self):
        if self._task_status_text is not None:
            logger.debug("cancel status_text_task")
            self._task_status_text.cancel()
        if self._task_armed is not None:
            logger.debug("cancel _task_armed")
            self._task_armed.cancel()
        if self._task_flight_mode is not None:
            logger.debug("cancel _task_flight_mode")
            self._task_flight_mode.cancel()
        if self._task_position is not None:
            logger.debug("cancel _task_position")
            self._task_position.cancel()
