from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal
import asyncio
import logging
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed, VelocityNedYaw, Attitude, PositionNedYaw,
                             PositionGlobalYaw)
from socketServer import SocketServer

logger = logging.getLogger()


class DroneProxy(QObject):
    statusTextChanged = pyqtSignal(str)
    isConnectedChanged = pyqtSignal(bool)
    isArmedChanged = pyqtSignal(bool)
    flightModeChanged = pyqtSignal(str)
    latitudeChanged = pyqtSignal(float)
    longitudeChanged = pyqtSignal(float)
    altitudeChanged = pyqtSignal(float)
    headingChanged = pyqtSignal(float)

    def __init__(self, port="50051", index=0, parent=None):
        super().__init__(parent)
        self._drone = None
        self._port = port
        self._index = index

        self._task_status_text = None
        self._task_armed = None
        self._task_flight_mode = None
        self._task_position = None
        self._task_heading = None

        self._statusText = ''
        self._isConnected = False
        self._isArmed = False
        self._flightMode = ''
        self._latitude = 0.0
        self._longitude = 0.0
        self._altitude = 0.0
        self._heading = 0.0

        """
        velocity_body
        """
        self._velocity_forward = 0
        self._velocity_right = 0
        self._velocity_down = 0
        self._yaw_angular_rate = 0
        """
        velocity_ned
        """
        self._velocity_north = 0
        self._velocity_east = 0
        self._velocity_down_ned = 0
        self._yaw_in_degrees = 0
        """
        attitude
        """
        self._roll_deg = 0
        self._pitch_deg = 0
        self._yaw_deg = 0
        self._thrust_value = 0
        """
        position_ned
        """
        self._position_ned_north_m = 0
        self._position_ned_east_m = 0
        self._position_ned_down_m = 0
        self._position_ned_yaw_deg = 0
        """
        position_global
        """
        self._position_global_latitude_m = 0
        self._position_global_longitude_m = 0
        self._position_global_altitude_m = 0
        self._position_global_yaw_deg = 0

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

    @pyqtProperty(float, notify=headingChanged)
    def heading(self):
        return self._heading

    @heading.setter
    def heading(self, val: float):
        self._heading = val
        self.headingChanged.emit(val)

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
        SocketServer.getInstance().send_message("connected", (self._index, True))

        logger.debug("Waiting for drone to have a global position estimate...")
        async for health in self._drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                logger.debug("-- Global position estimate OK")
                break

        self._task_status_text = asyncio.ensure_future(self._print_status_text())
        self._task_armed = asyncio.ensure_future(self._armed())
        self._task_flight_mode = asyncio.ensure_future(self._flight_mode())
        self._task_position = asyncio.ensure_future(self._position())
        self._task_heading = asyncio.ensure_future(self._heading_coroutine())

    async def _print_status_text(self):
        logger.debug('')
        try:
            async for status_text in self._drone.telemetry.status_text():
                # logger.debug(f'status text: {status_text.text}')
                self.statusText = status_text.text
                SocketServer.getInstance().send_message("statusText", (self._index, status_text.text))
        except asyncio.CancelledError:
            logger.debug("_print_status_text asyncio.CancelledError.")
            return

    async def _armed(self):
        logger.debug('')
        try:
            async for is_armed in self._drone.telemetry.armed():
                # logger.debug(f'is_armed: {is_armed}')
                self.isArmed = is_armed
                SocketServer.getInstance().send_message("armed", (self._index, is_armed))
        except asyncio.CancelledError:
            logger.debug("_armed asyncio.CancelledError.")
            return

    async def _flight_mode(self):
        logger.debug('')
        try:
            async for flight_mode in self._drone.telemetry.flight_mode():
                # logger.debug(f'flight_mode: {flight_mode}')
                self.flightMode = flight_mode.name
                SocketServer.getInstance().send_message("flightMode", (self._index, flight_mode.name))
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
                SocketServer.getInstance().send_message("position", (self._index,
                                                                     position.latitude_deg,
                                                                     position.longitude_deg,
                                                                     position.relative_altitude_m))
        except asyncio.CancelledError:
            logger.debug("_position asyncio.CancelledError.")
            return

    async def _heading_coroutine(self):
        try:
            async for heading in self._drone.telemetry.heading():
                # logger.debug(f'heading: {heading.heading_deg}')
                self.heading = heading.heading_deg
                SocketServer.getInstance().send_message("heading", (self._index, heading.heading_deg))
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
        if self._task_heading is not None:
            logger.debug("cancel _task_heading")
            self._task_heading.cancel()

    async def arm(self):
        await self._drone.action.arm()

    async def start_offboard_mode(self):
        try:
            await self._send_velocity_body()
            await self._send_velocity_ned()
            await self._send_attitude()
            await self._send_position_ned()
            await self._drone.offboard.start()
        except OffboardError as error:
            logger.debug(f"Starting offboard mode failed with error code: \
                  {error._result.result}")
            logger.debug("-- Disarming")
            await self._drone.action.disarm()
            return

    async def stop_offboard_mode(self):
        try:
            await self._drone.offboard.stop()
        except OffboardError as error:
            logger.debug(f"Stopping offboard mode failed with error code: \
                  {error._result.result}")

    async def set_velocity_body(self, forward, right, down, yaw):
        logger.debug(f"velocity_forward: {forward}")
        logger.debug(f"velocity_right: {right}")
        logger.debug(f"velocity_down: {down}")
        logger.debug(f"yaw_angular_rate: {yaw}")

        self._velocity_forward = forward
        self._velocity_right = right
        self._velocity_down = down
        self._yaw_angular_rate = yaw

        await self._send_velocity_body()

        logger.debug(".")

    async def set_velocity_ned(self, north, east, down, yaw):
        logger.debug(f"velocity_north: {north}")
        logger.debug(f"velocity_east: {east}")
        logger.debug(f"velocity_down_ned: {down}")
        logger.debug(f"yaw_in_degrees: {yaw}")

        self._velocity_north = north
        self._velocity_east = east
        self._velocity_down_ned = down
        self._yaw_in_degrees = yaw

        await self._send_velocity_ned()

        logger.debug(".")

    async def set_attitude(self, roll, pitch, yaw, thrust):
        logger.debug(f"roll_deg: {roll}")
        logger.debug(f"pitch_deg: {pitch}")
        logger.debug(f"yaw_deg: {yaw}")
        logger.debug(f"thrust_value: {thrust}")

        self._roll_deg = roll
        self._pitch_deg = pitch
        self._yaw_deg = yaw
        self._thrust_value = thrust

        await self._send_attitude()

        logger.debug(".")

    async def set_position_ned(self, north, east, down, yaw):
        logger.debug(f"position_ned_north: {north}")
        logger.debug(f"position_ned_east: {east}")
        logger.debug(f"position_ned_down: {down}")
        logger.debug(f"position_ned_yaw_deg: {yaw}")

        self._position_ned_north_m = north
        self._position_ned_east_m = east
        self._position_ned_down_m = down
        self._position_ned_yaw_deg = yaw

        await self._send_position_ned()

        logger.debug(".")

    async def set_position_global(self, lat, lon, alt, yaw):
        # logger.debug(f"position_global_latitude: {lat}")
        # logger.debug(f"position_global_longitude: {lon}")
        # logger.debug(f"position_global_altitude: {alt}")
        # logger.debug(f"position_global_yaw_deg: {yaw}")

        self._position_global_latitude_m = lat
        self._position_global_longitude_m = lon
        self._position_global_altitude_m = alt
        self._position_global_yaw_deg = yaw

        await self._send_position_global()

        # logger.debug(".")

    async def _send_velocity_body(self):
        await self._drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(self._velocity_forward,
                                 self._velocity_right,
                                 self._velocity_down,
                                 self._yaw_angular_rate))

    async def _send_velocity_ned(self):
        await self._drone.offboard.set_velocity_ned(
            VelocityNedYaw(self._velocity_north,
                           self._velocity_east,
                           self._velocity_down_ned,
                           self._yaw_in_degrees))

    async def _send_attitude(self):
        await self._drone.offboard.set_attitude(
            Attitude(self._roll_deg,
                     self._pitch_deg,
                     self._yaw_deg,
                     self._thrust_value))

    async def _send_position_ned(self):
        await self._drone.offboard.set_position_ned(
            PositionNedYaw(self._position_ned_north_m,
                           self._position_ned_east_m,
                           self._position_ned_down_m,
                           self._position_ned_yaw_deg))

    async def _send_position_global(self):
        await self._drone.offboard.set_position_global(
            PositionGlobalYaw(self._position_global_latitude_m,
                              self._position_global_longitude_m,
                              self._position_global_altitude_m,
                              self._position_global_yaw_deg,
                              altitude_type=PositionGlobalYaw.AltitudeType.AMSL))
