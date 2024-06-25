# motion_sensor.py
import pigpio
import time

class MotionSensorCon:
    def __init__(self, pin):
        self.pi = pigpio.pi()
        self.pin = pin
        self.last_motion_time = time.time()
        self.setup_gpio()

    def setup_gpio(self):
        self.pi.set_mode(self.pin, pigpio.INPUT)

    def detect_motion(self):
        if self.pi.read(self.pin):
            self.last_motion_time = time.time()
            return True
        return False

    def get_last_motion_time(self):
        return self.last_motion_time
