# pocket - Headless Chirp uploader for Raspberry Pi
![pocketpi programmer](https://github.com/cobungra/pocket/blob/main/assets/pocketpi2.png )

This is a simple device and softare to help reprogram ham radios in the field.
The device plugs into a Raspberry Pi Zero.

With Chirp installed and one of these python scripts, it can upload preloaded images from the SDcard to the radio, or download the current installed image to a file.



## Quick usage
- Create the desired radio image files using Chirp.
- Copy the images to the Pi's SDcard (e.g. into /home/pi/Documents/RadioCode/) using the naming conventions described below.
In the field:
- Run on the Pi (needs GPIO privileges and chirpc accessible in PATH):
- Use the buttons to upload or download images.

```bash
python3 pocket.py 
```


## Requires: 
- Raspberry Pi zero or other with the "pocket" GPIO daughterboard (see below)
- Chirp radio software installed (includes chirpc the CLI)
- Required cable from the Pi to the selected radio.
- Customize the code to suit your own radio. I tested with a QYT WP12 etc. (pocket.py: Lines 104,121) or (minimal.py: Lines 62,68,77). Edit the file to reflect your needs (ie name of radio). While logged into the pi, `chirpc --list-radios` provides the names.

pocket.py -Select from seven images to upload

minimal.py -Simple version for two images

## In Use:
Start the program on the Raspberry Pi. 
```bash
python3 pocket.py (or minimal.py)
```
This could autostart at boot using systemd. (see Docs)

pocket.py: Three buttons
- Button 1: Select one of seven led colours to choose a named image ( Green/Yellow/Blue/Red/Pink/Cyan/Purple)
- Button 2: Upload the named image (green.img / yellow.img .. etc)
- Button 3: Downloads the current image from the radio and saves on the Pi as download[n].img in increasing numbers


minimal.py: Three buttons:
- Button 1: Uploads the Chirp program version1.img to the radio
- Button 2: Uploads the Chirp program version2.img to the radio
- Button 3: Downloads the current image from the radio and saves on the Pi as download[n].img in increasing numbers

Stop = Shutdown: Hold Buton 3 button for two seconds and release. (Pi will shutdown)

Start at command line or as a systemctl service. 
To run headless I recommend start the program automaticaaly at boot.

---------------------------------------------------------------
Downloads
- `read` will save downloaded mmap files incrementally as `download1.img`, `download2.img`, ... in the same folder as the configured `--mmap` path to avoid overwriting existing files.

Error handling
- Some radios may return transient warnings like: "WARNING: Short reading 1 bytes from the 2 requested." In most cases uploads/downloads still finish successfully.

-------------------------------------------------------------------
## Parts list

PCB or suitable breadboard.

2   20 pin femaale headers

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


![PCB](https://github.com/cobungra/pocket/blob/main/assets/PCB_1.png)



VK3MBT
