# VK3MBT Pocket Programmer. Not for commercial use.
# Version to select colour named images to upload
# Green, Yellow, Blue, Red, Pink,Cyan, Purple
# Button 1 - Select Colour
# Button 2 - Upload selected colour named image and the connected radio
# Button 3 - Download from Radio (will save to selected colour's radio folder)
# Long press Button 3 - Shutdown Pi

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

# Available colours: (name, rgb tuple, filename, radio model)
COLORS = [
    ("green",  (0, 1, 0), "green.img","QYT_KT-WP12"),
    ("yellow", (1, 0.3, 0), "yellow.img","QYT_KT-WP12"),
    ("blue",   (0, 0.1, 1), "blue.img","QYT_KT-WP12"),
    ("red",    (1, 0, 0), "red.img","QYT_KT-WP12"),
    ("pink",   (1, 0.1, 1), "pink.img","Baofeng_UV-5R"),
    ("cyan",   (0, 1, 1), "cyan.img","Baofeng_UV-5R"),
    ("purple", (0.3, 0, 1), "purple.img","Baofeng_UV-5R"),
]
SELECTED_INDEX = 0
selected_colour = COLORS[SELECTED_INDEX][0]

# Dry run support via POCKET_DRY_RUN (useful when developing off-device)
DRY_RUN = os.getenv("POCKET_DRY_RUN", "").lower() in ("1", "true", "yes")

# Set initial LED to match the selected colour
try:
    led.color = COLORS[SELECTED_INDEX][1]
except Exception:
    pass

SELECT_PIN = 13
WRITE_PIN = 19
READ_PIN = 26
LONG_PRESS_SEC = 2.0
# DOUBLE_PRESS_WINDOW = 0.6

_press_start = 0.0
# _last_press = 0.0

GPIO.setmode(GPIO.BCM)
GPIO.setup(SELECT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(WRITE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
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


def select():
    """Cycle the selected colour and update the LED."""
    global SELECTED_INDEX, selected_colour
    SELECTED_INDEX = (SELECTED_INDEX + 1) % len(COLORS)
    name, rgb, fname, radio = COLORS[SELECTED_INDEX]
    selected_colour = name
    directory =  radio
    print(f"Button 1 Select colour pressed. Selected: {name}")
    try:
        led.color = rgb
    except Exception:
        pass
    print("Waiting for button press...")

def write():
    """Upload the currently selected colour's image."""
    name, rgb, fname, radio = COLORS[SELECTED_INDEX]
    directory = radio 
    print(f"Button 2 pressed. Uploading {radio} {fname} (selected={name})")
    # indicate running
    try:
        led.color = (1, 0, 1)
    except Exception:
        pass
    cmd = ["chirpc", "-r", f"{radio}", "--serial=/dev/ttyUSB0", f"--mmap=/home/pi/Radios/{directory}/{fname}", "--upload-mmap"]
    if DRY_RUN:
        print("DRY RUN: " + " ".join(cmd))
    else:
        subprocess.run(cmd)
    # restore LED to selected colour
    try:
        led.color = COLORS[SELECTED_INDEX][1]
    except Exception:
        pass
    print("Waiting for button press...")
def read():
    print("Button 3 pressed. Downloading from Radio.")
    led.color = (0, 1, 1)
    # base_mmap = "/home/pi/Documents/RadioCode/download.img"
    name, rgb, fname, radio = COLORS[SELECTED_INDEX]
    base_mmap = f"/home/pi/Radios/{radio}/download.img"
    # base_mmap = f"/home/pi/Documents/{radio}"
    target_mmap = _next_incremental_filename(base_mmap)
    print(f"Saving download to {target_mmap}")
    cmd = ["chirpc", "-r", f"{radio}", "--serial=/dev/ttyUSB0", f"--mmap={target_mmap}", "--download-mmap"]
    if DRY_RUN:
        print("DRY RUN: " + " ".join(cmd))
    else:
        subprocess.run(cmd)
    # restore LED to the currently selected colour
    try:
        led.color = COLORS[SELECTED_INDEX][1]
    except Exception:
        pass
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
GPIO.add_event_detect(SELECT_PIN, GPIO.FALLING, callback=lambda x: select(), bouncetime=300)
GPIO.add_event_detect(WRITE_PIN, GPIO.FALLING, callback=lambda x: write(), bouncetime=300)
print(">>>> Pocket 1.3 is ready. <<<<")
print("Waiting for button press...")
try:
    pause()  # wait indefinitely until signal (callbacks will run)
except KeyboardInterrupt:
    print("Exiting on user interrupt...")
finally:
    GPIO.cleanup()
