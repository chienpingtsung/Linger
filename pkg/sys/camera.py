from threading import Thread

import cv2

from lib.util.config import config


class Camera:
    def __init__(self):
        self.capture = cv2.VideoCapture(config.cam_src)
        self.status = None
        self.frame = None

        self.update_thread = Thread(target=self.update, daemon=True)
        self.update_thread.start()

    def update(self):
        while True:
            if self.capture.isOpened():
                self.status, self.frame = self.capture.read()

    def get_frame(self):
        return self.frame

    def __del__(self):
        self.capture.release()
