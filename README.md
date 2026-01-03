# pocket
![pocketpi programmer](https://github.com/cobungra/pocket/blob/main/assets/pocketpi.jpg  )
![PCB](https://github.com/cobungra/pocket/blob/main/assets/PCB_1.png)

This folder contains the `pocket.py` button-driven runner for controlling chirp (radio read/write) via GPIO buttons on a Raspberry Pi.

Quick usage
- Run on the Pi (needs GPIO privileges and chirpc accessible in PATH):

```bash
cd ~/Documents/Code/python/pocket
python3 pocket.py 
```

Behavior
- This device is a headless, portable programmer. 

Requires: 
- Raspberry Pi zero or other with the "pocket" GPIO daughterboard (see below)
- Chirp radio software installed (includes chirpc the CLI)
- Required cable from the Pi to the selected radio.
- Customize the code to suit your own radio. I tested with a QYT WP12 etc. (Lines 56,62,71)

In Use:
Three buttons:
- Write1: Uploads the Chirp program version1.img to the radio
- Write2: Uploads the Chirp program version2.img to the radio
- Read: Downloads the current image from the radio and saves on the Pi as download[n].img in increasing numbers

There is an RGB led: 
- Green: Ready
- Red: Stopped / shutdown
- Colours for Write1, Write2 and Read (Yellow, Purple, Cyan)

Start at command line or as a systemctl service.

Stop = Shutdown: Hold Read button for two seconds and release. (Pi will shutdown)


- The three default commands for `read`, `write1`, and `write2` are defined directly in `pocket.py` 
- Edit `pocket.py` to change those commands; this keeps the runtime simple and robust for field use.

---------------------------------------------------------------

The colours.py version supports writing of 7 images:
- This software treats button1 as select: Green/Yellow/Blue/Red/Pink/Cyan/Purple
- Select a colour and the relevant image green.img / yellow.img .. etc 
- Press button 2 to write this file t0 the radio.
- Button 3 is download as usual


Downloads
- `read` will save downloaded mmap files incrementally as `download1.img`, `download2.img`, ... in the same folder as the configured `--mmap` path to avoid overwriting existing files.

Error handling
- Some radios may return transient warnings like: "WARNING: Short reading 1 bytes from the 2 requested." In most cases uploads/downloads still finish successfully.
- For uploads pocket will retry on warnings/non-zero return codes and will accept reported success when present.
- For downloads (the `read` action) pocket treats progress lines like "Cloning from radio" as success. Short-read warnings without any success text will trigger retries (short-read messages are uncommon for downloads).

Safety
- `pocket.py` will warn on startup if `chirpc` is not in PATH.
-------------------------------------------------------------------
Construction:

- Straightforward, use a common cathode RGB led.
- Perhaps put the pi in a plastic box with exposed pins, but in any case ensure that the board canot short or foul the pi's circuitry!
- I take no reponsibility for unintended consequences of this project.
- The code is minimal and works for me. Improve it as you see fit.

I do not authorize commercial use of the board design or code.
