import asyncio
from pathlib import Path

import cv2
import pandas

from pkg.comm.integrations import IntegrationCommander
from pkg.comp.cam import Camera
from pkg.comp.drones import Drone
from pkg.models.groundingdino import GroundingDINO
from pkg.utils.config import cfg
from pkg.utils.images import cv_to_pil, add_box_mask, pil_to_cv


class Main:
    def __init__(self):
        self.drone = Drone()
        self.camera = Camera()
        self.model = GroundingDINO()

        self.waypoints = pandas.read_csv(cfg.waypoints, header=None).to_numpy()
        self.perspectives = [
            pandas.read_csv(Path(cfg.perspectives).joinpath(f'{i}.csv'), header=None).to_numpy().tolist() for i in
            range(len(self.waypoints))]

        self.commander = IntegrationCommander(self.drone, self.camera, self.model, self.waypoints, self.perspectives)

        self.window = False

    def window_thread(self):
        self.window = True
        while self.window:
            frame = self.camera.get_frame()
            if frame is not None:
                if self.commander.box is not None:
                    frame = cv_to_pil(frame)
                    frame = add_box_mask(frame, self.commander.box)
                    frame = pil_to_cv(frame)
                cv2.imshow('Mission-Center', frame)
            if cv2.waitKey(0) & 0xFF == ord('0'):
                self.window = False
        cv2.destroyAllWindows()

    async def moni_battery(self):
        async for b in self.drone.drone.telemetry.battery():
            print(b.remaining_percent)
            await asyncio.sleep(1)

    async def __call__(self):
        await self.drone.connect()

        try:
            await self.drone.takeoff()
            await self.commander.start_control()
        except Exception as e:
            print(e)
        finally:
            await self.drone.return_to_launch()


if __name__ == '__main__':
    cfg.load('configurations/base.yaml')
    main = Main()
    asyncio.run(main())
