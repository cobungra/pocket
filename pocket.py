from gpiozero import RGBLED
from signal import pause
from time import sleep
import time
import RPi.GPIO as GPIO
import os
import subprocess
import re

led = RGBLED(17, 27, 22)

led.color = (1, 0, 0) # Red
sleep(1)
led.color = (0, 1, 0) # Green


WRITE1_PIN = 13
WRITE2_PIN = 19
READ_PIN = 26
LONG_PRESS_SEC = 2.0
# DOUBLE_PRESS_WINDOW = 0.6 # not used

_press_start = 0.0
# _last_press = 0.0

GPIO.setmode(GPIO.BCM)
GPIO.setup(WRITE1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(WRITE2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(READ_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def _next_incremental_filename(path):
    """Return next available numbered filename alongside path (download1.img, download2.img, ...)."""
    d = os.path.dirname(path) or '.'
    base = os.path.basename(path)
    name, ext = os.path.splitext(base)
    if not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    pat = re.compile(re.escape(name) + r"(\d+)" + re.escape(ext) + r"\Z")
    maxn = 0
    for f in os.listdir(d):
        m = pat.match(f)
        if m:
            try:
                n = int(m.group(1))
                if n > maxn:
                    maxn = n
            except ValueError:
                pass
    nextn = maxn + 1
    return os.path.join(d, f"{name}{nextn}{ext}")


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
        base_mmap = "/home/pi/Documents/RadioCode/download.img"
        target_mmap = _next_incremental_filename(base_mmap)
        print(f"Saving download to {target_mmap}")
        subprocess.run(["chirpc", "-r", "QYT_KT-WP12", "--serial=/dev/ttyUSB0", f"--mmap={target_mmap}", "--download-mmap"])
        led.color = (0, 1, 0)
        print("Waiting for button press...")

def shutdown_pi():
        print("Long press detected: shutting down")
        led.color = (1, 0, 0)
        subprocess.run(["sudo", "shutdown", "-h", "now"])

def _on_read_edge(channel):
        """Handle both edges for read button to detect long press."""
        global _press_start
        now = time.time()
        if GPIO.input(channel) == GPIO.LOW:
            _press_start = now
            return
        duration = now - _press_start
        if duration >= LONG_PRESS_SEC:
            shutdown_pi()
            return
        read()
# Main loop to wait for button presses

GPIO.add_event_detect(READ_PIN, GPIO.BOTH, callback=_on_read_edge, bouncetime=50)
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
