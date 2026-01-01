# pocket

This folder contains the `pocket.py` button-driven runner for controlling chirp (radio read/write) via GPIO buttons on a Raspberry Pi.

Quick usage
- Run on the Pi (needs GPIO privileges and chirpc accessible in PATH):

```bash
cd ~/Documents/Code/python/pocket
# set dry-run via env var or CLI flag
POCKET_DRY_RUN=1 python3 pocket.py
# or
python3 pocket.py --dry-run
```

Behavior
- This device is a headless, portable programmer and does not support external config or script overrides.
- The three default commands for `read`, `write1`, and `write2` are defined directly in `pocket.py` in the `DEFAULT_COMMANDS` map.
- Edit `pocket.py` to change those commands; this keeps the runtime simple and robust for field use.

Dry-run mode
- Use `POCKET_DRY_RUN=1` or `python3 pocket.py --dry-run` (or `-n`) to print the commands that would be run without executing them. This is useful for field verification.

Downloads
- `read` will save downloaded mmap files incrementally as `download1.img`, `download2.img`, ... in the same folder as the configured `--mmap` path to avoid overwriting existing files.

Error handling
- Some radios may return transient warnings like: "WARNING: Short reading 1 bytes from the 2 requested." In many cases uploads/downloads still finish successfully.
- For uploads pocket will retry on warnings/non-zero return codes and will accept reported success when present.
- For downloads (the `read` action) pocket treats progress lines like "Cloning from radio" as success. Short-read warnings without any success text will trigger retries (short-read messages are uncommon for downloads).

Safety
- `pocket.py` will warn on startup if `chirpc` is not in PATH.

