import asyncio

from mavsdk.gimbal import ControlMode, GimbalMode, SendMode

from pkg.sys.drone import DroneController


class GimbalController:
    gimbal_id = None

    def __init__(self, drone: DroneController):
        self.gimbal = drone.drone.gimbal

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
        await self.set_roi_location(38.98665259811101, 117.3428250578938, 0)
        await asyncio.sleep(3)
        await self.set_angles(0, 0, 0)

    async def set_roi_location(self, latitude_deg, longitude_deg, altitude_m):
        await self.gimbal.set_roi_location(self.gimbal_id, latitude_deg, longitude_deg, altitude_m)

    async def set_angles(self, roll_deg, pitch_deg, yaw_deg):
        await self.gimbal.set_angles(self.gimbal_id, roll_deg, pitch_deg, yaw_deg, GimbalMode.YAW_FOLLOW, SendMode.ONCE)
