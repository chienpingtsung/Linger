import asyncio
import json

import cv2

from pkg.algorithm.groundingdino import GroundingDINO
from pkg.commander.retrieve import RetrieveCommander
from pkg.sys.camera import CameraController
from pkg.sys.drone import DroneController
from pkg.sys.gimbal import GimbalController
from pkg.utils.config import cfg
from pkg.utils.image import cv_to_pil, draw_box_mask, pil_to_cv


class Main:
    def __init__(self):
        self.drone = DroneController()
        self.gimbal = GimbalController(self.drone)
        self.camera = CameraController(cfg.camera_src)
        self.model = GroundingDINO()

        with open('waypoints.json', 'r', encoding='utf-8') as f:
            self.waypoints = json.load(f)

        self.commander = RetrieveCommander(self.drone, self.gimbal, self.camera, self.model, self.waypoints)

        self.window = False

    def window_thread(self):
        self.window = True
        while self.window:
            frame = self.camera.get_frame()
            if frame is not None:
                if self.commander.box is not None:
                    frame = cv_to_pil(frame)
                    frame = draw_box_mask(frame, self.commander.box)
                    frame = pil_to_cv(frame)
                cv2.imshow('Linger', frame)
            if cv2.waitKey(0) & 0xFF == ord('0'):
                self.window = False
        cv2.destroyAllWindows()

    async def report_battery(self):
        async for b in self.drone.drone.telemetry.battery():
            print(b.remaining_percent)
            await asyncio.sleep(1)

    async def __call__(self):
        await self.drone.connect()
        rep_bat = asyncio.create_task(self.report_battery())

        try:
            await self.drone.takeoff()
            await self.commander.start_control()
        except Exception as e:
            print(e)
        finally:
            await self.drone.return_to_launch()


if __name__ == '__main__':
    cfg.load('config/default.yaml')
    main = Main()
    asyncio.run(main())
