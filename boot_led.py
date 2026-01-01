# from gpiozero import LED
# from time import sleep

# # ExecStart=/usr/bin/python3 /home/pi/python/pocket/boot_led.py


# led = LED(17)

# # Small delay to ensure system is stable
# sleep(2)

# led.on()

# Basic colors (Common Cathode: 1=On, 0=Off)
from gpiozero import RGBLED
from signal import pause
from time import sleep

led = RGBLED(2, 3, 4)

led.color = (1, 0, 0) # Red
sleep(1)
led.color = (0, 1, 0) # Green
sleep(1)
led.color = (0, 0, 1) # Blue
sleep(1)

led.color = (1, 1, 0) # Yellow (Red + Green)
sleep(1)

led.color = (0, 0, 0) # Off

# Using color names (requires colorzero)
from colorzero import Color
led.color = Color('cyan') # (0, 1, 1)
sleep(1)

# Pulse (fade in/out)
led.pulse()
pause() # Keeps the script alive
