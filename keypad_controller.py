# keypad_controller.py

import time
import signal
import sys
import os
import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library

class KeypadController:
    def __init__(self, sleep_time=0.01, max_cycles=20, debounce_cycles=10):
        self.sleep_time = sleep_time
        self.max_cycles = max_cycles
        self.debounce_cycles = debounce_cycles

        self.blue = 38
        self.green = 32
        self.orange = 26
        self.grey = 22
        self.brown = 18
        self.red = 16
        self.yellow = 12

        self.keys = {
            self.blue: {'key_measured': '5', 'cycles': 0, 'key_was_down': False, 'default': '5', 'secondary': {self.brown: '0', self.red: '8', self.yellow: '2'}},
            self.green: {'key_measured': '4', 'cycles': 0, 'key_was_down': False, 'default': '4', 'secondary': {self.brown: '*', self.red: '7', self.yellow: '1'}},
            self.orange: {'key_measured': '6', 'cycles': 0, 'key_was_down': False, 'default': '6', 'secondary': {self.brown: '#', self.red: '9', self.yellow: '3'}},
            self.grey: {'key_measured': 'B', 'cycles': 0, 'key_was_down': False, 'default': 'B', 'secondary': {self.brown: 'D', self.red: 'C', self.yellow: 'A'}}
        }

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

    def check_key(self, pin):
        key_info = self.keys[pin]
        if GPIO.input(pin):
            if key_info['key_was_down']:
                if key_info['cycles'] > self.max_cycles:
                    self.key_released(key_info['key_measured'])
                    key_info['cycles'] = 0
                    key_info['key_was_down'] = False
        else:
            key_info['cycles'] += 1
            if not key_info['key_was_down']:
                for test_pin, test_key in key_info['secondary'].items():
                    if not GPIO.input(test_pin):
                        key_info['key_measured'] = test_key
                if key_info['cycles'] > self.debounce_cycles:
                    self.key_pressed(key_info['key_measured'])
                    key_info['key_was_down'] = True
        return key_info

    def run(self):
        while True:
            for pin in self.keys:
                self.keys[pin] = self.check_key(pin)
            time.sleep(self.sleep_time)  # Adjust sleep time as necessary

if __name__ == '__main__':
    controller = KeypadController()
    controller.run()
