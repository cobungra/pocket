# pocket - Headless Chirp uploader for Raspberry Pi
![pocketpi programmer](https://github.com/cobungra/pocket/blob/main/assets/pocketpi2.png )

This is a simple device and software to help reprogram ham radios in the field.
The device plugs onto a Raspberry Pi Zero.

With Chirp installed and one of these python scripts, it can upload preloaded images from the SDcard to the radio, or download the current installed image to a file.



## Quick usage
The image files will be saved into /home/pi/{radioname} where {radioname} is the chirpc name for your radio (chirpc --list-radios)
- First run, connect to the radio, select a colour and Download (Button 3).  This will create the working folder for that radio.
- Create the desired radio image files using Chirp.
- Copy the images to the Pi's SDcard relevant directory (e.g. into /home/pi/Radios/Baofeng_UV-5R) using the naming conventions described below.


In the field:
- Run on the Pi (needs GPIO privileges and chirpc accessible in PATH):
- Use the buttons to upload or download images.

cd to where you have put the python file (e.g /home/pi/python)
```bash
cd /home/pi/python
python3 pocket.py 
```


## Requires: 
- Raspberry Pi zero or other with the "pocket" GPIO daughterboard (see below)
- Chirp radio software installed (includes chirpc the CLI)
- Required cable from the Pi to the selected radio.
- Customize the code to suit your own radio. I tested with a UV-5R & QYT WP12. (pocket.py: Lines 26-32) or (minimal.py: Lines 62,68,74,77). Edit the file to reflect your needs (ie name of radio). While logged into the pi, `chirpc --list-radios` provides the names.

pocket.py -Select from seven images to upload

minimal.py -Simple version for two images

## In Use:
Start the program on the Raspberry Pi. 
```bash
python3 pocket.py (or minimal.py)
```
To run headless I recommend starting the program automatically at boot using systemd. (see docs/autostart for an example)

pocket.py: Three buttons
- Button 1: Select one of seven led colours to choose a named image ( Green/Yellow/Blue/Red/Pink/Cyan/Purple)
- Button 2: Upload the named image (green.img / yellow.img .. etc)
- Button 3: Downloads the current image from the radio and saves on the Pi as download[n].img in increasing numbers in the folder configured in `--mmap` path to avoid overwriting existing files.


minimal.py: Three buttons:
- Button 1: Uploads the Chirp program version1.img to the radio
- Button 2: Uploads the Chirp program version2.img to the radio
- Button 3: Downloads the current image from the radio and saves on the Pi as download[n].img in increasing numbers in the folder configured in `--mmap` path to avoid overwriting existing files.

Stop = Shutdown: Hold Button 3 for two seconds and release. (Pi will shutdown)


## Development / Build timestamp 🔧
- The repo includes a small helper that updates the `Pocket ready` line in `pocket.py` with a build timestamp in **YYMMDDHHMM** format (for example, `2601101503`).
- To update the timestamp manually: run:

```bash
python3 scripts/update_build_ts.py pocket.py
```

- A pre-commit hook is supplied to run the updater automatically before commits. Install the hooks once from the repo root:

```bash
./scripts/install-hooks.sh
```

(When the script updates the file it will also `git add` the changed file so the timestamp is included in the commit.)

---------------------------------------------------------------

Error handling
- Some radios may return transient warnings like: "WARNING: Short reading 1 bytes from the 2 requested." In most cases uploads/downloads still finish successfully.

-------------------------------------------------------------------
## Parts list

PCB or suitable breadboard.

2   20 pin female headers

3   Tactile buttons

1   RGB led - common cathode

3   300R resistors


## Construction:

- Straightforward, use a common cathode RGB led.
- Perhaps put the pi in a plastic box with exposed pins, but in any case ensure that the board canot short or foul the pi's circuitry!
- I take no reponsibility for unintended consequences of this project.
- The code is minimal and works for me. Improve it as you see fit.


## PCB

- GPIO 13 > Switch 1 > Gnd
- GPIO 19 > Switch 2 > Gnd
- GPIO 26 > Switch 3 > Gnd
- GPIO 17 > 330R > LED R
- GPIO 27 > 330R > LED G
- GPIO 22 > 330R > LED B
- Gnd     >      > LED Cathode


![PCB](https://github.com/cobungra/pocket/blob/main/assets/pcb004.png)



VK3MBT
