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

from pocket.backups.pocket import _run_with_retries

led = RGBLED(17, 27, 22)

led.color = (1, 0, 0) # Red
sleep(1)
led.color = (0, 1, 0) # Green
sleep(2)
led.color = (0, 0, 1) # Blue
sleep(1)

WRITE1_PIN = 13
WRITE2_PIN = 19
READ_PIN = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(WRITE1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(WRITE2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(READ_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def _next_incremental_filename(path):
    """Return a new filename based on path, using incremental suffixes like name1.ext, name2.ext in the same directory.
    Example: /.../download.img -> /.../download1.img (or next available number).
    """
    d = os.path.dirname(path) or '.'
    base = os.path.basename(path)
    name, ext = os.path.splitext(base)
    # Ensure directory exists
    if not os.path.isdir(d):
        try:
            os.makedirs(d, exist_ok=True)
        except Exception as e:
            print(f"Could not create directory {d}: {e}")
            return path
    pat = re.compile(re.escape(name) + r"(\d+)" + re.escape(ext) + r"\Z")
    maxn = 0
    try:
        for f in os.listdir(d):
            m = pat.match(f)
            if m:
                try:
                    n = int(m.group(1))
                    if n > maxn:
                        maxn = n
                except ValueError:
                    pass
    except Exception as e:
        print(f"Error listing directory {d}: {e}")
        return path
    nextn = maxn + 1
    newname = f"{name}{nextn}{ext}"
    return os.path.join(d, newname)




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
        cmd = ("chirpc", "-r", "QYT_KT-WP12", "--serial=/dev/ttyUSB0", "--mmap=/home/pi/Documents/RadioCode/download.img", "--download-mmap")
        cmd2 = list(cmd)
        if name == 'read':
                for i, a in enumerate(cmd2):
                    if a.startswith('--mmap='):
                        orig = a.split('=', 1)[1]
                        newpath = _next_incremental_filename(orig)
                        cmd2[i] = f'--mmap={newpath}'
                        print(f"Saving download to {newpath}")
                        break
                    elif a == '--mmap' and i + 1 < len(cmd2):
                        orig = cmd2[i + 1]
                        newpath = _next_incremental_filename(orig)
                        cmd2[i + 1] = newpath
                        print(f"Saving download to {newpath}")
                        break
        else:
                cmd2 = cmd

        print(f"Running default command for {os.name}: {' '.join(cmd2)}")
        # proc = _run_with_retries(cmd2, os.name)
        # else:
        # print(f"No default command for {os.name}; nothing to do")
        #finally:
        # restore LED to green if possible
        try:
            led.color = (0, 1, 0)
        except Exception:
            pass


        # subprocess.run(["chirpc", "-r", "QYT_KT-WP12", "--serial=/dev/ttyUSB0", "--mmap=/home/pi/Documents/RadioCode/download.img", "--download-mmap"])
        led.color = (0, 1, 0)
        print("Waiting for button press...")
# Main loop to wait for button presses

GPIO.add_event_detect(READ_PIN, GPIO.FALLING, callback=lambda x: read(), bouncetime=300)
GPIO.add_event_detect(WRITE1_PIN, GPIO.FALLING, callback=lambda x: write1(), bouncetime=300)
GPIO.add_event_detect(WRITE2_PIN, GPIO.FALLING, callback=lambda x: (), bouncetime=300)
print(">>>> Pocket is ready. <<<<")
print("Waiting for button press...")
try:
    pause()  # wait indefinitely until signal (callbacks will run)
except KeyboardInterrupt:
    print("Exiting on user interrupt...")
finally:
    GPIO.cleanup()


