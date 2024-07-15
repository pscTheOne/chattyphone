# controller.py
from keypad_controller import KeypadController
from motion_sensor import MotionSensor

class Controller:
    def __init__(self, motion_sensor_pin=37, keypad_sleep_time=0.01, keypad_max_cycles=20, keypad_debounce_cycles=10):
        self.motion_sensor = MotionSensor(motion_sensor_pin)
        self.keypad_controller = KeypadController(
            sleep_time=keypad_sleep_time,
            max_cycles=keypad_max_cycles,
            debounce_cycles=keypad_debounce_cycles
        )
        self.keypad_input = ""

    def detect_motion(self):
        return self.motion_sensor.detect_motion()

    def get_last_motion_time(self):
        return self.motion_sensor.get_last_motion_time()

    def run_keypad(self):
        self.keypad_controller.run()

    def keypad_key_pressed(self, key):
        self.keypad_input += key

    def keypad_key_released(self, key):
        pass  # Optional: handle key release if needed

    def reset_keypad_input(self):
        self.keypad_input = ""

    def get_keypad_input(self):
        return self.keypad_input
