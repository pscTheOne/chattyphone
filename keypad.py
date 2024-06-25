# keypad_controller.py

import time
from keypad import DTMFKeypad
import signal
import sys
import os
import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library

class KeypadController:
    def __init__(self):
        self.blue = 38
        self.green = 32
        self.orange = 26
        self.grey = 22
        self.brown = 18
        self.red = 16
        self.yellow = 12

        self.blue_key_measured = '5'
        self.blue_cycles = 0
        self.blue_key_was_down = False

        self.green_key_measured = '4'
        self.green_cycles = 0
        self.green_key_was_down = False

        self.orange_key_measured = '6'
        self.orange_cycles = 0
        self.orange_key_was_down = False

        self.grey_key_measured = 'B'
        self.grey_cycles = 0
        self.grey_key_was_down = False

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        self.setup_pins()

        signal.signal(signal.SIGINT, self.signal_handler)

    def setup_pins(self):
        pins = [self.blue, self.green, self.orange, self.grey, self.brown, self.red, self.yellow]
        for pin in pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def signal_handler(self, sig, frame):
        GPIO.cleanup()
        sys.exit(0)

    def key_pressed(self, key):
        print(key + " Pressed")

    def key_released(self, key):
        print(key + " Released")

    def check_key(self, pin, key_measured, key_was_down, cycles, keys_map):
        if GPIO.input(pin):
            if key_was_down:
                if cycles > 2000:
                    self.key_released(key_measured)
                    return keys_map['default'], 0, False
        else:
            cycles += 1
            if not key_was_down:
                for test_pin, test_key in keys_map['secondary'].items():
                    if not GPIO.input(test_pin):
                        key_measured = test_key
                if cycles > 10:
                    self.key_pressed(key_measured)
                    key_was_down = True
        return key_measured, cycles, key_was_down

    def run(self):
        while True:
            self.blue_key_measured, self.blue_cycles, self.blue_key_was_down = self.check_key(
                self.blue, self.blue_key_measured, self.blue_key_was_down, self.blue_cycles,
                {'default': '5', 'secondary': {self.brown: '0', self.red: '8', self.yellow: '2'}}
            )
            self.green_key_measured, self.green_cycles, self.green_key_was_down = self.check_key(
                self.green, self.green_key_measured, self.green_key_was_down, self.green_cycles,
                {'default': '4', 'secondary': {self.brown: '*', self.red: '7', self.yellow: '1'}}
            )
            self.orange_key_measured, self.orange_cycles, self.orange_key_was_down = self.check_key(
                self.orange, self.orange_key_measured, self.orange_key_was_down, self.orange_cycles,
                {'default': '6', 'secondary': {self.brown: '#', self.red: '9', self.yellow: '3'}}
            )
            self.grey_key_measured, self.grey_cycles, self.grey_key_was_down = self.check_key(
                self.grey, self.grey_key_measured, self.grey_key_was_down, self.grey_cycles,
                {'default': 'B', 'secondary': {self.brown: 'D', self.red: 'C', self.yellow: 'A'}}
            )
            time.sleep(0.01)  # Adjust sleep time as necessary

if __name__ == '__main__':
    controller = KeypadController()
    controller.run()
