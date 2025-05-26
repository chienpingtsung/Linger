import asyncio

from easydict import EasyDict
from mavsdk.gimbal import ControlMode, GimbalMode, SendMode

from pkg.sys.drone import DroneController


class GimbalController:
    gimbal_id = None

    def __init__(self, drone: DroneController):
        self.gimbal = drone.drone.gimbal

        self.roi = EasyDict({'latitude_deg': None, 'longitude_deg': None, 'altitude_m': None})
        self.ang = EasyDict({'roll_deg': None, 'pitch_deg': None, 'yaw_deg': None})

        print('[INFO] Searching gimbal...')
        async for gimbal_list in self.gimbal.gimbal_list():
            if gimbal_list.gimbals:
                self.gimbal_id = gimbal_list.gimbals[0]
                print(f'[INFO] Found gimbal {self.gimbal_id}')
                break

    async def take_control(self):
        print(f'[INFO] Take control of gimbal {self.gimbal_id}')
        await self.gimbal.take_control(self.gimbal_id, ControlMode.PRIMARY)

    async def release_control(self):
        print(f'[INFO] Release control of gimbal {self.gimbal_id}')
        await self.gimbal.release_control(self.gimbal_id)

    async def check_gimbal(self):
        print('[ACTION] Checking gimbal...')
        self.set_roi_location(38.98665259811101, 117.3428250578938, 0)
        await self.control_roi_location()
        await asyncio.sleep(3)
        self.set_angles(0, 0, 0)
        await self.control_angles()

    def set_roi_location(self, latitude_deg, longitude_deg, altitude_m):
        self.roi.latitude_deg = latitude_deg
        self.roi.longitude_deg = longitude_deg
        self.roi.altitude_m = altitude_m

    def set_angles(self, roll_deg, pitch_deg, yaw_deg):
        self.ang.roll_deg = roll_deg
        self.ang.pitch_deg = pitch_deg
        self.ang.yaw_deg = yaw_deg

    async def control_roi_location(self):
        await self.gimbal.set_roi_location(self.gimbal_id, **self.roi)

    async def control_angles(self):
        await self.gimbal.set_angles(gimbal_id=self.gimbal_id,
                                     gimbal_mode=GimbalMode.YAW_FOLLOW,
                                     SendMode=SendMode.ONCE,
                                     **self.ang)
