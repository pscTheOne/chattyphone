# keypad_controller.py

import time
import signal
import sys
import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
import sounddevice as sd
import numpy as np

class KeypadController:
    def __init__(self, sleep_time=0.01, max_cycles=5, debounce_cycles=5):
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

        self.fs = 44100  # Sampling frequency
        self.tone_duration = 0.1  # Duration of the tone in seconds
        self.stream = None
        self.current_key = None
        self.tone_position = 0  # Position in the tone array

    def setup_pins(self):
        pins = [self.blue, self.green, self.orange, self.grey, self.brown, self.red, self.yellow]
        for pin in pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def signal_handler(self, sig, frame):
        GPIO.cleanup()
        sys.exit(0)

    def generate_dtmf_tone(self, key):
        dtmf_freqs = {
            '1': (697, 1209), '2': (697, 1336), '3': (697, 1477),
            '4': (770, 1209), '5': (770, 1336), '6': (770, 1477),
            '7': (852, 1209), '8': (852, 1336), '9': (852, 1477),
            '*': (941, 1209), '0': (941, 1336), '#': (941, 1477),
            'A': (697, 1633), 'B': (770, 1633), 'C': (852, 1633), 'D': (941, 1633)
        }

        if key not in dtmf_freqs:
            return None

        f1, f2 = dtmf_freqs[key]
        t = np.linspace(0, self.tone_duration, int(self.fs * self.tone_duration), endpoint=False)
        tone = 0.5 * (np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t))
        return tone

    def play_tone(self, key):
        tone = self.generate_dtmf_tone(key)
        if tone is not None:
            self.stream = sd.OutputStream(samplerate=self.fs, channels=1, callback=self.audio_callback)
            self.stream.start()
            self.tone = tone
            self.tone_position = 0

    def stop_tone(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            sd.stop()

    def audio_callback(self, outdata, frames, time, status):
        if status.output_underflow:
            print("Output underflow: increase buffer size or reduce CPU load")

        if self.tone is not None:
            chunk = self.tone[self.tone_position:self.tone_position + frames]
            outdata[:len(chunk)] = chunk.reshape(-1, 1)
            if len(chunk) < frames:
                outdata[len(chunk):] = 0
            self.tone_position = (self.tone_position + frames) % len(self.tone)
        else:
            outdata.fill(0)

    def key_pressed(self, key):
        print(key + " Pressed")
        self.play_tone(key)
        self.current_key = key

    def key_released(self, key):
        print(key + " Released")
        self.stop_tone()
        self.current_key = None

    def check_key(self, pin):
        key_info = self.keys[pin]
        if GPIO.input(pin):
            if key_info['key_was_down']:
                if key_info['cycles'] > self.max_cycles:
                    self.key_released(key_info['key_measured'])
                    key_info['cycles'] = 0
                    key_info['key_was_down'] = False
                    key_info['key_measured'] = key_info['default']

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
        time.sleep(2)
        while True:
            for pin in self.keys:
                self.keys[pin] = self.check_key(pin)
            time.sleep(self.sleep_time)  # Adjust sleep time as necessary

if __name__ == '__main__':
    controller = KeypadController()
    controller.run()
