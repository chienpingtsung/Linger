import asyncio

import torch

from pkg.utils.config import cfg
from pkg.utils.images import cv_to_pil


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
        self.box = None

    async def routing(self):
        for waypoint, perspectives in zip(self.waypoints, self.perspectives):
            self.drone.p.lat = waypoint[0]
            self.drone.p.lon = waypoint[1]
            self.drone.p.alt = waypoint[2]
            self.drone.p.yaw = 0
            async for p in self.drone.drone.telemetry.position():
                if perspectives:
                    if ((p.latitude_deg - waypoint[0]) ** 2 + (p.longitude_deg - waypoint[1]) ** 2 + (
                            p.absolute_altitude_m - waypoint[2]) ** 2) ** 0.5 < config.abs_dis:
                        roi = perspectives.pop()
                        self.drone.roi.lat = roi[0]
                        self.drone.roi.lon = roi[1]
                        self.drone.roi.alt = roi[2]
                        await asyncio.sleep(config.shoot_t)
                    continue
                break
        self.in_ctl = False

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

                self.box = rst['boxes'][torch.argmax(rst['scores'])].tolist()

                w, h = frame.size
                dcx = (self.box[0] + self.box[2]) / (2 * w) - 0.5
                dcy = 0.5 - (self.box[1] + self.box[3]) / (2 * h)
                bw = (self.box[2] - self.box[0]) / w
                bh = (self.box[3] - self.box[1]) / h
                darea = config.ep_area - bw * bh

                self.drone.v.f = 2 * dcy * config.max_trk_hor_speed
                self.drone.v.r = 2 * dcx * config.max_trk_hor_speed
                self.drone.v.d = darea * config.max_trk_ver_speed

    async def start_control(self):
        self.in_ctl = True

        await self.drone.start_offboard()
        routing = asyncio.create_task(self.routing())
        tracking = asyncio.create_task(self.tracking())

        while self.in_ctl:
            if self.in_tracking:
                await self.drone.set_velocity_body()
                await self.drone.set_pitch_and_yaw(-70, 0)
            else:
                await self.drone.set_position_global()
                await self.drone.set_roi_location()

        self.in_processing = False
        await routing
        await tracking
        await self.drone.stop_offboard()
