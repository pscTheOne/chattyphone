# motion_sensor.py
import RPi.GPIO as GPIO
import time

class MotionSensor:
    def __init__(self, pin):
        self.pin = pin
        self.last_motion_time = time.time()
        self.setup_gpio()

    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)

    def detect_motion(self):
        if GPIO.input(self.pin):
            self.last_motion_time = time.time()
            return True
        return False

    def get_last_motion_time(self):
        return self.last_motion_time

    def cleanup(self):
        GPIO.cleanup()

# Example usage
if __name__ == "__main__":
    sensor = MotionSensor(pin=17)
    try:
        while True:
            if sensor.detect_motion():
                print("Motion detected!")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated")
    finally:
        sensor.cleanup()