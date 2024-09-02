from easydict import EasyDict
from mavsdk import System
from mavsdk.offboard import VelocityBodyYawspeed, OffboardError, PositionGlobalYaw
from mavsdk.telemetry import LandedState

from lib.util.config import config


class Drone:
    def __init__(self):
        self.drone = System()

        self.offboard = False
        self.v = EasyDict({'f': 0, 'r': 0, 'd': 0, 'y': 0})
        self.p = EasyDict({'lat': None, 'lon': None, 'alt': None, 'yaw': None, 'type': 1})

    async def connect(self):
        print('ℹ️ Connecting the drone.')
        await self.drone.connect(config.system_address)
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                print('✅ Connected the drone.')
                break

    async def check_position(self):
        print('ℹ️ Checking global position and home position.')
        async for health in self.drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                print('✅ Global position and home position are ok.')
                break

    async def takeoff(self):
        await self.drone.action.set_takeoff_altitude(config.altitude)
        print(f'ℹ️ Takeoff altitude is set to {config.altitude}m.')

        await self.drone.action.arm()
        print('✅ Armed.')

        print('ℹ️ Taking off.')
        await self.drone.action.takeoff()
        async for state in self.drone.telemetry.landed_state():
            if state is LandedState.IN_AIR:
                print('✅ Drone has token off.')
                break

    async def return_to_launch(self):
        await self.drone.action.set_return_to_launch_altitude(config.altitude)
        print(f'ℹ️ Return to launch altitude is set to {config.altitude}m.')

        print('ℹ️ Returning to launch.')
        await self.drone.action.return_to_launch()
        async for state in self.drone.telemetry.landed_state():
            if state is LandedState.ON_GROUND:
                print('✅ Returned.')
                break

        await self.drone.action.disarm()
        print('✅ Disarmed.')

    def reset_v(self):
        self.v.f = 0
        self.v.r = 0
        self.v.d = 0
        self.v.y = 0

    async def set_velocity_body(self):
        await self.drone.offboard.set_velocity_body(VelocityBodyYawspeed(**self.v))

    async def set_position_global(self):
        await self.drone.offboard.set_position_global(PositionGlobalYaw(**self.p))

    async def start_offboard(self):
        if await self.drone.offboard.is_active():
            return

        self.reset_v()
        await self.set_velocity_body()

        try:
            print('⚠️ Starting offboard.')
            await self.drone.offboard.start()
            print('✅ Offboard Started.')
        except OffboardError as error:
            print(f'❌ Start offboard failed with error: {error}.')

    async def stop_offboard(self):
        if not await self.drone.offboard.is_active():
            return

        self.reset_v()
        await self.set_velocity_body()

        try:
            print('ℹ️ Stopping offboad.')
            await self.drone.offboard.stop()
            print('✅ Offboard stopped.')
        except OffboardError as error:
            print(f'❌ Stop offboard failed with error: {error}.')
