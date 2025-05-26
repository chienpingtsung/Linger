from threading import Thread

import cv2


class CameraController:
    def __init__(self, source):
        self.capture = cv2.VideoCapture(source)

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
