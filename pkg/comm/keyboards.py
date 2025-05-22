from pynput import keyboard

from lib.util.config import config


class KeyboardCommander:
    def __init__(self, drone):
        self.drone = drone

        self.in_ctl = False

    def on_press(self, key):
        try:
            key = key.char
        except AttributeError:
            pass

        if key == 'w':
            self.drone.v.f = config.kb_ctl_ls
        if key == 's':
            self.drone.v.f = -config.kb_ctl_ls
        if key == 'd':
            self.drone.v.r = config.kb_ctl_ls
        if key == 'a':
            self.drone.v.r = -config.kb_ctl_ls
        if key == 'f':
            self.drone.v.d = config.kb_ctl_ls
        if key == 'r':
            self.drone.v.d = -config.kb_ctl_ls
        if key == 'e':
            self.drone.v.y = config.kb_ctl_ys
        if key == 'q':
            self.drone.v.y = -config.kb_ctl_ys

    def on_release(self, key):
        try:
            key = key.char
        except AttributeError:
            pass

        if key == 'w':
            self.drone.v.f = 0
        if key == 's':
            self.drone.v.f = 0
        if key == 'd':
            self.drone.v.r = 0
        if key == 'a':
            self.drone.v.r = 0
        if key == 'f':
            self.drone.v.d = 0
        if key == 'r':
            self.drone.v.d = 0
        if key == 'e':
            self.drone.v.y = 0
        if key == 'q':
            self.drone.v.y = 0

        if key == keyboard.Key.esc:
            self.in_ctl = False

    async def start_control(self):
        self.in_ctl = True
        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)

        await self.drone.start_offboard()
        listener.start()

        while self.in_ctl:
            await self.drone.set_velocity_body()

        listener.stop()
        await self.drone.stop_offboard()
