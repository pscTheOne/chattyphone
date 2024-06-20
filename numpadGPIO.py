import signal
import sys
import os
import time
from pprint import pprint
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

blue = 38   #3    # A
green = 32  #5   # B
orange = 26 #7  # C
grey = 22   # J
brown = 18  # K
red = 16    # L
yellow = 12 # M

events = []




def signal_handler(sig,Frame):
    GPIO.cleanup()
    sys.exit(0)

def key_pressed(key):
    print(key + " Pressed")

def key_released(key):
    print(key + " Released")

if __name__ == '__main__':
    GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
    GPIO.setup(blue, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(green, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(orange, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(grey, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(brown, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(red, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(yellow, GPIO.IN, pull_up_down=GPIO.PUD_UP)


    signal.signal(signal.SIGINT, signal_handler)

#We set the default keys for the different wires and some vars to count program cycles and if pins has been measured before since the last cycle.

    blue_key_measured = '5'
    blue_cycles = 0
    blue_key_was_down = False
    green_key_measured = '4'
    green_cycles = 0
    green_key_was_down = False
    orange_key_measured = '6'
    orange_cycles = 0
    orange_key_was_down = False
    grey_key_measured = 'B'
    grey_cycles = 0
    grey_key_was_down = False


"""
Pressing a key on the numpad causes 1-2 of of the color inputs to trigger, often more than once.
Setting a callback on a pin going low and then registring if there is a secondary pin pressed seems like a obvious tactic.
Problem is that sometimes the secondary pin is not low yet when the callback function runs.
Instead we test the secondary pin the first 10 cyles the program loops and assign the relevant key if we measure low on any of the secondary.
If none of the cycles measure anything we can safely assume it is the primary(?) key that has been pressed.
If it has been more than 2000 cycles it is properly a key_release event.
"""

#---------------------Blue--------------------------

        if (GPIO.input(blue)):
            if(blue_key_was_down):
                if(blue_cycles > 2000):
                    key_released(blue_key_measured)
                    blue_key_measured = '5'
                    blue_cycles = 0
                    blue_key_was_down = False
        else:
            blue_cycles = blue_cycles + 1
            if not (blue_key_was_down):
                if not GPIO.input(brown): blue_key_measured = '0'
                if not GPIO.input(red): blue_key_measured = '8'
                if not GPIO.input(yellow): blue_key_measured = '2'
                if(blue_cycles > 10):
                    key_pressed(blue_key_measured)
                    blue_key_was_down = True
#----------------------Green----------------------

        if (GPIO.input(green)):
            if(green_key_was_down):
                if(green_cycles > 2000): #
                    key_released(green_key_measured)
                    green_key_measured = '4'
                    green_cycles = 0
                    green_key_was_down = False
        else:
            green_cycles = green_cycles + 1
            if not (green_key_was_down):
                if not GPIO.input(brown): green_key_measured = '*'
                if not GPIO.input(red): green_key_measured = '7'
                if not GPIO.input(yellow): green_key_measured = '1'
                if(green_cycles > 10):
                    key_pressed(green_key_measured)
                    green_key_was_down = True

#----------------------Orange----------------------
        if (GPIO.input(orange)):
            if(orange_key_was_down):
                if(orange_cycles > 2000):
                    key_released(orange_key_measured)
                    orange_key_measured = '6'
                    orange_cycles = 0
                    orange_key_was_down = False
        else:
            orange_cycles = orange_cycles + 1
            if not (orange_key_was_down):
                if not GPIO.input(brown): orange_key_measured = '#'
                if not GPIO.input(red): orange_key_measured = '9'
                if not GPIO.input(yellow): orange_key_measured = '3'
                if(orange_cycles > 10):
                    key_pressed(orange_key_measured)
                    orange_key_was_down = True

#----------------------Grey----------------------
        if (GPIO.input(grey)):
            if(grey_key_was_down):
                if(grey_cycles > 2000):
                    key_released(grey_key_measured)
                    grey_key_measured = 'B'
                    grey_cycles = 0
                    grey_key_was_down = False
        else:
            grey_cycles = grey_cycles + 1
            if not (grey_key_was_down):
                if not GPIO.input(brown): grey_key_measured = 'D'
                if not GPIO.input(red): grey_key_measured = 'C'
                if not GPIO.input(yellow): grey_key_measured = 'A'
                if(grey_cycles > 10):
                    key_pressed(grey_key_measured)
                    grey_key_was_down = True
