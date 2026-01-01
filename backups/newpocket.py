from gpiozero import RGBLED
from signal import pause
from time import sleep
import RPi.GPIO as GPIO
import os
import sys
import subprocess
import threading
import shutil
from datetime import datetime

led = RGBLED(17, 27, 22)

led.color = (1, 0, 0) # Red
sleep(1)
led.color = (0, 1, 0) # Green


WRITE1_PIN = 13
WRITE2_PIN = 19
READ_PIN = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(WRITE1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(WRITE2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(READ_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def write1():
        print("Button 1 pressed. Running write1.py")
        led.color = (1, 1, 0)
        subprocess.run(["chirpc", "-r", "QYT_KT-WP12", "--serial=/dev/ttyUSB0", "--mmap=/home/pi/Documents/RadioCode/version1.img", "--upload-mmap"])
        led.color = (0, 1, 0) 
        print("Waiting for button press...")       
def write2():
        print("Button 2 pressed. Running write2.py")
        led.color = (1, 0, 1)
        subprocess.run(["chirpc", "-r", "QYT_KT-WP12", "--serial=/dev/ttyUSB0", "--mmap=/home/pi/Documents/RadioCode/version2.img", "--upload-mmap"])
        led.color = (0, 1, 0)
        print("Waiting for button press...")
def read():
        print("Button 3 pressed. Running read.py")
        led.color = (0, 1, 1)
        subprocess.run(["chirpc", "-r", "QYT_KT-WP12", "--serial=/dev/ttyUSB0", "--mmap=/home/pi/Documents/RadioCode/download.img", "--download-mmap"])
        led.color = (0, 1, 0)
        print("Waiting for button press...")
# Main loop to wait for button presses

GPIO.add_event_detect(READ_PIN, GPIO.FALLING, callback=lambda x: read(), bouncetime=300)
GPIO.add_event_detect(WRITE1_PIN, GPIO.FALLING, callback=lambda x: write1(), bouncetime=300)
GPIO.add_event_detect(WRITE2_PIN, GPIO.FALLING, callback=lambda x: write2(), bouncetime=300)
print(">>>> Pocket is ready. <<<<")
print("Waiting for button press...")
try:
    pause()  # wait indefinitely until signal (callbacks will run)
except KeyboardInterrupt:
    print("Exiting on user interrupt...")
finally:
    GPIO.cleanup()


