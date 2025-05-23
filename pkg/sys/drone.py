from easydict import EasyDict
from mavsdk import System
from mavsdk.offboard import VelocityBodyYawspeed, PositionGlobalYaw
from mavsdk.telemetry import LandedState

from pkg.utils.config import cfg


class DroneController:
    def __init__(self):
        self.drone = System()

        self.v = EasyDict({'forward_m_s': 0, 'right_m_s': 0, 'down_m_s': 0, 'yawspeed_deg_s': 0})
        self.p = EasyDict({'lat_deg': None, 'lon_deg': None, 'alt_m': None, 'yaw_deg': None, 'altitude_type': 1})

    async def connect(self, address: str = 'udp://:14540'):
        print(f'[INFO] Connecting to drone at {address}...')
        await self.drone.connect(address)
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                print(f'[INFO] Connected to drone at {address}')
                break

    async def check_localization(self):
        print('[INFO] Localizing...')
        async for health in self.drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                print('[INFO] Global position and home position OK')
                break

    async def check_battery(self):
        battery = await self.drone.telemetry.battery()
        if battery.remaining_percent < cfg.min_bat_life:
            raise RuntimeError(f'[ERROR] Battery too low for flight: {battery.remaining_percent}%')

    async def takeoff(self):
        await self.check_battery()
        await self.drone.action.set_takeoff_altitude(cfg.takeoff_altitude)
        print(f'[INFO] Takeoff altitude set to: {cfg.takeoff_altitude}m')
        await self.drone.action.arm()
        print('[ACTION] Armed')

        print('[ACTION] Taking off...')
        await self.drone.action.takeoff()
        async for state in self.drone.telemetry.landed_state():
            if state is LandedState.IN_AIR:
                break

    async def return_to_launch(self):
        await self.drone.action.set_return_to_launch_altitude(cfg.takeoff_altitude)
        print(f'[INFO] Return to launch altitude set to: {cfg.takeoff_altitude}m')

        print('[ACTION] Returning to launch...')
        await self.drone.action.return_to_launch()
        async for state in self.drone.telemetry.landed_state():
            if state is LandedState.ON_GROUND:
                break

        await self.drone.action.disarm()
        print('[ACTION] Disarmed')

    def set_velocity_body(self, f, r, d, y):
        self.v.forward_m_s = f
        self.v.right_m_s = r
        self.v.down_m_s = d
        self.v.yawspeed_deg_s = y

    def set_position_global(self, lat, lon, alt, yaw):
        self.p.lat_deg = lat
        self.p.lon_deg = lon
        self.p.alt_m = alt
        self.p.yaw_deg = yaw

    async def control_velocity_body(self):
        await self.drone.offboard.set_velocity_body(VelocityBodyYawspeed(**self.v))

    async def control_position_global(self):
        await self.drone.offboard.set_position_global(PositionGlobalYaw(**self.p))

    async def start_offboard(self):
        if await self.drone.offboard.is_active():
            return

        self.set_velocity_body(0, 0, 0, 0)
        await self.control_velocity_body()

        await self.drone.offboard.start()
        print('[ACTION] Offboard started')

    async def stop_offboard(self):
        if not await self.drone.offboard.is_active():
            return

        self.set_velocity_body(0, 0, 0, 0)
        await self.control_velocity_body()

        await self.drone.offboard.stop()
        print('[ACTION] Offboard stopped')
