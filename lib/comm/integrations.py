import asyncio

import torch

from lib.util.config import config
from lib.util.images import cv_to_pil


class IntegrationCommander:
    def __init__(self, drone, camera, model, waypoints, perspectives):
        self.drone = drone
        self.camera = camera
        self.model = model
        self.waypoints = waypoints
        self.perspectives = perspectives

        self.in_ctl = False
        self.in_tracking = False
        self.in_processing = False

        self.text = config.text

    async def routing(self):
        pass

    async def tracking(self):
        self.in_processing = True
        while self.in_processing:
            frame = self.camera.get_frame()
            if frame is not None:
                frame = cv_to_pil(frame)
                rst = self.model(frame, self.text)[0]

                if len(rst['scores']) == 0:
                    self.in_tracking = False
                    self.drone.reset_v()
                    continue
                self.in_tracking = True

                box = rst['boxes'][torch.argmax(rst['scores'])].tolist()

                w, h = frame.size
                dcx = (box[0] + box[2]) / (2 * w) - 0.5
                dcy = 0.5 - (box[1] + box[3]) / (2 * h)
                bw = (box[2] - box[0]) / w
                bh = (box[3] - box[1]) / h
                darea = config.ep_area - bw * bh

                self.drone.v.f = 2 * dcy * config.max_trk_hor_speed
                self.drone.v.r = 2 * dcx * config.max_trk_hor_speed
                self.drone.v.d = darea * config.max_trk_ver_speed

    async def start_control(self):
        self.in_ctl = True

        await self.drone.start_offboard()
        tracking = asyncio.create_task(self.tracking())

        while self.in_ctl:
            if self.tracking:
                await self.drone.set_velocity_body()
            else:
                await self.drone.set_position_global()
                await self.drone.set_roi_location()

        self.in_processing = False
        await tracking
        await self.drone.stop_offboard()
