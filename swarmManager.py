import asyncio
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed, VelocityNedYaw, Attitude, PositionNedYaw, PositionGlobalYaw)
from droneProxy import DroneProxy
from haversine import inverse_haversine, Unit
import math
import logging

logger = logging.getLogger()


class SwarmManager:
    instance = None

    def __init__(self):
        self._leader = None
        self._followers = list()
        self._task_follow = None
        self._followFrequency = 1.0

    @classmethod
    def getInstance(cls):
        if cls.instance is None:
            cls.instance = SwarmManager()
        return cls.instance

    @property
    def followFrequency(self):
        return self._followFrequency

    @followFrequency.setter
    def followFrequency(self, val):
        self._followFrequency = val

    def setLeader(self, leader: DroneProxy):
        logger.debug('')
        self._leader = leader

    def addFollower(self, drone: DroneProxy, distance: float, angle: float):
        logger.debug('')
        for follower in self._followers:
            if follower['drone'] == drone:
                return

        self._followers.append({'drone': drone, 'distance': distance, 'angle': angle})

        logger.debug(f'followers {self._followers}')

    def removeFollower(self, drone: DroneProxy):
        logger.debug('')
        for follower in self._followers:
            if follower['drone'] == drone:
                self._followers.remove(follower)
                break

        logger.debug(f'followers {self._followers}')

    async def readyToFollow(self):
        logger.debug('')
        if self._leader is None:
            logger.debug("ready_to_follow leader is None.")
            return

        if not self._followers:
            logger.debug("ready_to_follow followers are Empty.")
            return

        for follower in self._followers:
            drone = follower['drone']
            await drone.arm()
            await asyncio.sleep(0.1)
            await drone.start_offboard_mode()

    async def follow(self):
        lat = self._leader.latitude
        lon = self._leader.longitude
        alt = self._leader.altitude_absolute
        yaw = self._leader.heading

        # logger.debug(f'lat:{lat}, lon:{lon}, alt:{alt}, yaw:{yaw}')

        try:
            for follower in self._followers:
                follower_lat, follower_lon = self._calculateFollowerPosition(lat, lon, yaw,
                                                                               follower['distance'],
                                                                               follower['angle'])
                # logger.debug(f'follower lat:{follower_lat}, lon:{follower_lon}')
                await follower['drone'].set_position_global(follower_lat, follower_lon, alt, yaw)
            await asyncio.sleep(1/self._followFrequency)
        except OffboardError as e:
            logger.debug("OffboardError:", e)
            return

    async def goToPositionOfLeader(self):
        logger.debug('')
        if not self._checkSwarmCondition():
            return

        await self.follow()

    async def followLeader(self):
        while True:
            await self.follow()

    async def runTaskFollow(self):
        if not self._checkSwarmCondition():
            return

        if self._task_follow is None:
            self._task_follow = asyncio.ensure_future(self.followLeader())

    def stopFollow(self):
        if self._task_follow:
            self._task_follow.cancel()

        self._task_follow = None

    def _checkSwarmCondition(self):
        if self._leader is None:
            logger.debug("check_swarm_condition leader is None.")
            return False

        if not self._followers:
            logger.debug("check_swarm_condition followers are Empty.")
            return False

        return True

    @staticmethod
    def _calculateFollowerPosition(leader_latitude, leader_longitude, leader_heading, distance, relative_angle):
        # 리더 드론의 헤딩 각도를 라디안으로 변환
        leader_heading_rad = math.radians(leader_heading)

        # 상대적 각도를 라디안으로 변환
        relative_angle_rad = math.radians(relative_angle)

        # 팔로워 드론의 절대적인 각도 계산
        absolute_angle_rad = leader_heading_rad + relative_angle_rad

        # logger.debug(f"leader_heading: {leader_heading}")
        # logger.debug(f"relative_angle: {relative_angle}")
        # logger.debug(f"leader_heading_rad: {leader_heading_rad}")
        # logger.debug(f"relative_angle_rad: {relative_angle_rad}")
        # logger.debug(f"absolute_angle_rad: {absolute_angle_rad}")

        leader_pos = (leader_latitude, leader_longitude)
        follower_pos = inverse_haversine(leader_pos, distance, absolute_angle_rad, unit=Unit.METERS)

        # 팔로워 드론의 위치 계산
        follower_latitude = follower_pos[0]
        follower_longitude = follower_pos[1]

        return follower_latitude, follower_longitude

