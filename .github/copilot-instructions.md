# Copilot / AI Agent Instructions for "pocket"

Purpose: Help an AI agent be immediately productive in this small Raspberry Pi headless app that maps hardware buttons to `chirpc` commands.

## Quick start (how to run)
- On Pi (needs GPIO privileges and `chirpc` in PATH):
  - POCKET_DRY_RUN=1 python3 pocket.py
  - python3 pocket.py --dry-run
- `boot_led.py` contains an example `ExecStart` comment for a systemd startup script.

## Big-picture architecture
- This is a headless, portable programmer: three physical buttons map to three actions: `read`, `write1`, `write2`.
- There are two main implementation flavors in-repo:
  - `pocket.py` — minimal runtime: direct `subprocess.run(...)` on button press (keeps runtime simple for field use).
  - `backups/pocket.py` — canonical, more robust implementation: uses `DEFAULT_COMMANDS`, runs `chirpc` under a pseudo-tty (`POCKET_USE_PTY`), implements incremental download filenames and _retry_ logic (`_run_with_retries`). Use this file as the reference for behavior/edge cases.
- `newpocket.py` contains experimental changes but is incomplete/buggy (missing imports and incorrect variables) — do not assume it is canonical.

## Key files to reference
- `pocket.py` — small, simple runtime used in README examples
- `backups/pocket.py` — reference implementation with:
  - `DEFAULT_COMMANDS` map for `read|write1|write2`
  - `_run_cmd_pty`, `_run_cmd`, `_run_with_retries`
  - `_next_incremental_filename` for avoiding overwrites on downloads
- `README.md` — usage and behavior notes (dry-run, incremental download behavior)
- `boot_led.py` — startup service example and LED patterns

## Project-specific conventions & patterns (do not invent alternatives)
- No external config or runtime overrides: default commands are defined in code (see `DEFAULT_COMMANDS` in `backups/pocket.py`). If you need to change behavior, edit those constants or refactor carefully (keep defaults in-code to preserve the headless design).
- Dry-run support: enabled via environment variable `POCKET_DRY_RUN=1` or CLI flags `--dry-run` / `-n`. Dry-run prints commands instead of executing them — use this for safe testing without hardware.
- Incremental download behavior: downloads are saved with numeric suffixes (`download1.img`, `download2.img`, ...). See `_next_incremental_filename` in `backups/pocket.py` and the `read` handler logic.
- Success and retry heuristics are output-driven: the code looks for phrases such as `Upload successful|Download successful|Cloning to radio|Cloning from radio` and treats short-read warnings (e.g., `Short reading N bytes`) specially by retrying.
- Pseudo-tty behaviour: the robust implementation prefers a pseudo-tty when running `chirpc` (controlled by `POCKET_USE_PTY`). This makes `chirpc` behave like the interactive CLI which is important for reliable parsing of progress messages.

## Integration points & external dependencies
- External CLI: `chirpc` must be present in PATH. `backups/pocket.py` explicitly warns if `chirpc` isn't found (see `shutil.which('chirpc')`).
- Serial device: default uses `/dev/ttyUSB0` in the default commands — ensure the device path matches your hardware.
- Hardware libraries: `RPi.GPIO` and `gpiozero` are used; runtime expected on Raspberry Pi. Local development may need to avoid importing these or run on PI/have mocks.

## Debugging tips / developer workflows
- To verify default commands without hardware: run with `POCKET_DRY_RUN=1` (or `--dry-run`) to see the exact `chirpc` arguments printed.
- If `chirpc` behavior seems wrong, inspect `_run_cmd_pty` output in `backups/pocket.py` — stdout is captured and printed on completion.
- The script prints clear warnings on missing `DEFAULT_COMMANDS` or missing `chirpc` — monitor startup logs on the device.
- For changes that affect runtime behavior, prefer editing `backups/pocket.py` first and then carefully sync minimal behavior into `pocket.py` if you need to keep the simple runtime.

---

If any of the above is unclear or you'd like me to expand examples (e.g., exact systemd unit snippets, or a small local-test shim to avoid `RPi.GPIO` imports), tell me which part to expand and I will iterate. ✅
