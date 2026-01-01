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

# Command overrides for handlers (used if <name>.py is missing)
# Default commands for read, write1 and write2 (chirpc invocations)
DEFAULT_COMMANDS = {
    "write1": [
        "chirpc",
        "-r",
        "QYT_KT-WP12",
        "--serial=/dev/ttyUSB0",
        "--mmap=/home/pi/Documents/RadioCode/version1.img",
        "--upload-mmap",
    ],
    "write2": [
        "chirpc",
        "-r",
        "QYT_KT-WP12",
        "--serial=/dev/ttyUSB0",
        "--mmap=/home/pi/Documents/RadioCode/version2.img",
        "--upload-mmap",
    ],
    "read": [
        "chirpc",
        "-r",
        "QYT_KT-WP12",
        "--serial=/dev/ttyUSB0",
        "--mmap=/home/pi/Documents/RadioCode/download.img",
        "--download-mmap",
    ],
}

# No external scripts or config: DEFAULT_COMMANDS are fixed and always used.
# Warn if chirpc is missing
if shutil.which('chirpc') is None:
    print("Warning: 'chirpc' not found in PATH; default commands may fail.")
# Validate mapping
for _k in ('read', 'write1', 'write2'):
    if _k not in DEFAULT_COMMANDS:
        print(f"Warning: no default command for {_k}")

# Dry-run mode: set via env var POCKET_DRY_RUN=1 or CLI flags --dry-run / -n
DRY_RUN = os.getenv("POCKET_DRY_RUN", "").lower() in ("1", "true", "yes")
if "--dry-run" in sys.argv:
    DRY_RUN = True
    try:
        sys.argv.remove("--dry-run")
    except ValueError:
        pass
if "-n" in sys.argv:
    DRY_RUN = True
    try:
        sys.argv.remove("-n")
    except ValueError:
        pass

import re

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


# Optionally run chirpc under a pseudo-tty to emulate interactive terminal
USE_PTY = os.getenv('POCKET_USE_PTY', '1').lower() in ('1', 'true', 'yes')

import pty
import select
import time
import types

def _run_cmd_pty(cmd, timeout=600):
    """Run cmd attached to a pseudo-tty and return a simple object with returncode and stdout attributes."""
    master, slave = pty.openpty()
    try:
        p = subprocess.Popen(cmd, stdin=slave, stdout=slave, stderr=slave)
    except Exception as e:
        os.close(master)
        os.close(slave)
        print(f"Error spawning command in pty: {e}")
        return None
    os.close(slave)
    output_chunks = []
    start = time.time()
    try:
        while True:
            r, _, _ = select.select([master], [], [], 0.1)
            if master in r:
                try:
                    data = os.read(master, 1024)
                except OSError:
                    break
                if not data:
                    break
                try:
                    output_chunks.append(data.decode('utf-8', errors='replace'))
                except Exception:
                    output_chunks.append(str(data))
            if p.poll() is not None:
                # read remaining
                while True:
                    try:
                        data = os.read(master, 1024)
                    except OSError:
                        break
                    if not data:
                        break
                    output_chunks.append(data.decode('utf-8', errors='replace'))
                break
            if time.time() - start > timeout:
                p.kill()
                print(f"Command timed out after {timeout}s")
                break
    finally:
        try:
            os.close(master)
        except Exception:
            pass
    out = ''.join(output_chunks)
    return types.SimpleNamespace(returncode=p.returncode, stdout=out, stderr='')


def _run_cmd(cmd):
    """Run the provided command list or print it in dry-run mode. Returns subprocess.CompletedProcess-like or None."""
    if DRY_RUN:
        print(f"DRY RUN: {' '.join(cmd)}")
        return None
    # Prefer a pty for chirpc if configured; it causes chirpc to behave like interactive CLI
    if USE_PTY and len(cmd) and os.path.basename(cmd[0]) == 'chirpc':
        return _run_cmd_pty(cmd)
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except Exception as e:
        print(f"Error running command: {e}")
        return None


def _run_with_retries(cmd, name, retries=2, retry_delay=2):
    """Run cmd, retrying on short-read warnings or non-zero exit codes.
    Returns the final subprocess.CompletedProcess or None.
    """
    for attempt in range(1, retries + 2):
        proc = _run_cmd(cmd)
        if DRY_RUN:
            return None
        if proc is None:
            print(f"{name}: command failed to run (proc is None)")
            if attempt <= retries:
                print(f"Retrying ({attempt}/{retries}) in {retry_delay}s...")
                sleep(retry_delay)
                continue
            return None
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        combined = (stdout + "\n" + stderr).strip()

        # Detect success anywhere in output first — accept immediately.
        # Consider 'Upload successful', 'Download successful', and cloning messages as success.
        success_match = re.search(r"Upload successful|Download successful|Cloning to radio|Cloning from radio", combined, re.I)
        short_match = re.search(r"Short reading \d+ bytes", combined, re.I)

        if success_match:
            if short_match:
                print(f"Warning from command but reported success: {short_match.group(0)}")
            return proc

        # If we see a short-read warning without a success message, retry (applies to both read and write).
        if short_match:
            print(f"Detected short-read warning without success: {short_match.group(0)}")
            if attempt <= retries:
                print(f"Retrying ({attempt}/{retries}) in {retry_delay}s...")
                sleep(retry_delay)
                continue
            return proc

        # If non-zero return code, retry
        if proc.returncode != 0:
            print(f"Command returned rc={proc.returncode}")
            if attempt <= retries:
                print(f"Retrying ({attempt}/{retries}) in {retry_delay}s...")
                sleep(retry_delay)
                continue

        return proc
    return proc

def _worker(name, color_running=(1, 1, 0)):
    ts = datetime.now().isoformat()
    print(f"[{ts}] Button triggered: {name}")
    try:
        # indicate running
        try:
            led.color = color_running
        except Exception:
            pass

        cmd = DEFAULT_COMMANDS.get(name)
        if cmd:
            # For read, make the --mmap target incremental to avoid overwrites
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

            print(f"Running default command for {name}: {' '.join(cmd2)}")
            proc = _run_with_retries(cmd2, name)
            if DRY_RUN:
                print(f"Dry-run enabled: command not executed")
            else:
                if proc is None:
                    print(f"{name}: command failed to run or produced no output")
                else:
                    print(f"{name} finished (rc={proc.returncode})\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}")
        else:
            print(f"No default command for {name}; nothing to do")
    finally:
        # restore LED to green if possible
        try:
            led.color = (0, 1, 0)
        except Exception:
            pass

def write1():
    threading.Thread(target=_worker, args=("write1", (1, 0.5, 0)), daemon=True).start()

def write2():
    threading.Thread(target=_worker, args=("write2", (1, 0, 1)), daemon=True).start()

def read():
    threading.Thread(target=_worker, args=("read", (0, 1, 1)), daemon=True).start()



# Main loop to wait for button presses
def _on_read(channel):
    read()

def _on_write1(channel):
    write1()

def _on_write2(channel):
    write2()

GPIO.add_event_detect(READ_PIN, GPIO.FALLING, callback=_on_read, bouncetime=300)
GPIO.add_event_detect(WRITE1_PIN, GPIO.FALLING, callback=_on_write1, bouncetime=300)
GPIO.add_event_detect(WRITE2_PIN, GPIO.FALLING, callback=_on_write2, bouncetime=300)

print("Waiting for button press...")
try:
    pause()  # wait indefinitely until signal (callbacks will run)
except KeyboardInterrupt:
    print("Exiting on user interrupt...")
finally:
    GPIO.cleanup()









#led.color = (1, 1, 0) # Yellow (Red + Green)
#sleep(1)

#led.color = (0, 0, 0) # Off

# Using color names (requires colorzero)
#from colorzero import Color
#led.color = Color('cyan') # (0, 1, 1)
#sleep(1)

# Pulse (fade in/out)
#led.pulse()
#pause() # Keeps the script alive


