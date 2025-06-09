import asyncio

import torch

from pkg.sys.camera import CameraController
from pkg.sys.drone import DroneController
from pkg.sys.gimbal import GimbalController
from pkg.utils.config import cfg
from pkg.utils.image import cv_to_pil


class RetrieveCommander:
    def __init__(self,
                 drone: DroneController,
                 gimbal: GimbalController,
                 camera: CameraController,
                 model, waypoints):
        self.drone = drone
        self.gimbal = gimbal
        self.camera = camera
        self.model = model
        self.waypoints = waypoints

        self.text = cfg.text
        self.box = None

        self.in_ctl = False
        self.in_processing = False
        self.in_tracking = False

    async def routing(self):
        for gps, rois in self.waypoints:
            self.drone.set_position_global(*gps)
            async for p in self.drone.drone.telemetry.position():
                if rois:
                    if ((p.latitude_deg - gps[0]) ** 2 +
                        (p.longitude_deg - gps[1]) ** 2 +
                        (p.absolute_altitude_m - gps[2]) ** 2) ** 0.5 < cfg.arr_dis:
                        roi = rois.pop()
                        self.gimbal.set_roi_location(*roi)
                        await asyncio.sleep(cfg.shoot_t)
                    continue
                break
        self.in_ctl = False

    async def tracking(self):
        self.in_processing = True
        while self.in_processing:
            frame = self.camera.get_frame()
            if frame is not None:
                frame = cv_to_pil(frame)
                oputs = self.model(frame, self.text)[0]

                if len(oputs['scores']) == 0:
                    self.in_tracking = False
                    continue
                self.in_tracking = True

                self.box = oputs['boxes'][torch.argmax(oputs['scores'])].tolist()

                w, h = frame.size
                dcx = (self.box[0] + self.box[2]) / (2 * w) - 0.5
                dcy = 0.5 - (self.box[1] + self.box[3]) / (2 * h)
                bw = (self.box[2] - self.box[0]) / w
                bh = (self.box[3] - self.box[1]) / h
                darea = cfg.expt_area - bw * bh

                self.drone.set_velocity_body(2 * dcy * cfg.max_trk_hor_speed,
                                             2 * dcx * cfg.max_trk_hor_speed,
                                             darea * cfg.max_trk_ver_speed, 0)

    async def start_control(self):
        self.in_ctl = True

        await self.drone.start_offboard()
        await self.gimbal.take_control()
        routing = asyncio.create_task(self.routing())
        tracking = asyncio.create_task(self.tracking())

        while self.in_ctl:
            if not self.in_tracking:
                await self.drone.control_position_global()
                await self.gimbal.control_roi_location()
            else:
                await self.drone.control_velocity_body()
                await self.gimbal.set_angles(0, -70, 0)
                await self.gimbal.control_angles()

        self.in_processing = False
        await routing
        await tracking
        await self.drone.stop_offboard()
        await self.gimbal.release_control()
