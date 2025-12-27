# GoPro Highlight Extractor 🔧📹

A small utility (CLI + simple Tkinter GUI) to extract GoPro "highlight" clips from MP4 files that contain chapter markers. It uses `ffprobe` to read chapters and `ffmpeg` to trim clips, and supports both per-chapter extraction and fixed-length anchor clips around chapter starts.

---

## Features ✅

- Extract clips based on MP4 chapters produced by GoPro devices
- Two extraction modes:
  - `anchor`: fixed-length clip around chapter START (pre + post seconds)
  - `chapter`: use full chapter range, extended by pre/post
- Save clips with timestamp-based or numbered filenames
- Optional re-encode (frame-accurate) or fast copy (stream copy)
- Directory processing with optional progress callbacks (used by GUI)

---

## Prerequisites ⚙️

- Python 3.8+ (script itself only uses stdlib)
- System packages (must be installed on your OS):
  - `ffmpeg` and `ffprobe` (example on Debian/Ubuntu: `sudo apt install ffmpeg`)
- GUI requires a system Tk (usually provided with standard Python installation)

Optional (not required at runtime, present in `requirements.txt` as commented entries):
- `tqdm` — CLI progress bars
- `requests` — if you add network features later

---

## Installation 📥

1. Clone this repo or copy files into a project folder.
2. Ensure `ffmpeg`/`ffprobe` are installed and in your `PATH`.
3. (Optional) If you want optional Python packages, uncomment the entries in `requirements.txt` and run:

```bash
pip install -r requirements.txt
```

---

## Usage — Command Line 🔁

Basic CLI usage:

```bash
python gopro_highlight.py /path/to/video.mp4 --pre 1.0 --post 1.0
```

Process a directory (non-recursive):

```bash
python gopro_highlight.py /path/to/videos --outdir highlights
```

Flags summary:

- `--pre FLOAT` (default: `1.0`) — seconds before chapter start to include
- `--post FLOAT` (default: `1.0`) — seconds after chapter end to include
- `--outdir PATH` (default: `highlights`) — destination directory
- `--mode {chapter,anchor}` (default: `anchor`) — extraction mode
- `--reencode` — re-encode output (frame-accurate)
- `--name-with-ts` — name files with `HH-MM-SS.mmm` timestamps
- `--recursive` — descend subdirectories when input is a directory
- `--csv PATH` — write a CSV summary of created clips

Note: Using `--reencode` will re-encode video with H.264/AAC and is slower but frame-accurate.

---

## GUI — Tkinter Application 🪟

Run the GUI with:

```bash
python gopro_highlight_gui.py
```

The GUI lets you select a source folder, destination folder and options (pre/post, recursive, re-encode, name-with-timestamp). Progress and logs appear in the window.

---

## Implementation Notes 🧭

- The project intentionally avoids extra runtime Python dependencies — it interacts with video tools using subprocess calls to `ffprobe` and `ffmpeg`.
- `process_directory` accepts an optional `progress_callback` which can be either `callback(msg)` or `callback(msg, percent)` to update a UI progress bar.
- The GUI uses `root.after` to safely schedule UI updates from background threads.

---

## Troubleshooting & Tips ⚠️

- "ffmpeg not found" — install the `ffmpeg` package for your OS and ensure it is on the PATH.
- GUI progress not updating — confirm the callback you pass accepts `percent` (the GUI now passes `cb(msg, percent)` and the GUI callback signature is `cb(msg, percent=None)`).
- If clips seem truncated or misaligned when using stream copy (`-c copy`), try `--reencode` to make frame-accurate trims.

---

## Packaging into an executable (optional) 📦

Using `pyinstaller` (Linux/macOS/Windows):

```bash
pip install pyinstaller
pyinstaller --onefile gopro_highlight.py
# Or include GUI: pyinstaller --onefile gopro_highlight_gui.py
```

Windows-specific packaging (recommended for producing a double-clickable .exe):

1. Download a static ffmpeg build for Windows (e.g. https://www.gyan.dev/ffmpeg/builds/ or https://ffmpeg.org) and copy `ffmpeg.exe` and `ffprobe.exe` into a directory named `win-bins` inside the project root.
2. Install PyInstaller on the Windows machine: `pip install pyinstaller`.
3. Use the provided build script `build_windows.bat` from the project root (it runs the command below):

```bat
pyinstaller --noconsole --onefile --add-binary "win-bins\ffmpeg.exe;." --add-binary "win-bins\ffprobe.exe;." gopro_highlight_gui.py
```

- `--noconsole` hides the console for GUI builds; omit it for CLI builds.
- `--add-binary "SRC;DEST"` bundles the ffmpeg binaries into the executable's temporary runtime folder so the app can use them even if the target system doesn't have ffmpeg installed.

Note about bundled ffmpeg: The script has been updated to look for `ffmpeg`/`ffprobe` in PATH and in common bundled locations (PyInstaller's `_MEIPASS`, the exe directory, or script directory). If the binaries are bundled with the exe, no further steps are required — the exe will extract and use them at runtime.

If you prefer to keep ffmpeg external, instruct users to install ffmpeg on Windows and ensure it is on PATH (or place ffmpeg/ffprobe next to the exe).

---

## Examples 🧪

- Extract anchor clips (1s before + 1s after) from a single file:

```bash
python gopro_highlight.py ~/Videos/GL010750.MP4 --pre 1.0 --post 1.0 --outdir ~/clips
```

- Process a directory and write CSV summary:

```bash
python gopro_highlight.py /path/to/base --outdir ~/clips --recursive --csv summary.csv
```

---

## Contributing & Development 🤝

- Bug reports and PRs welcome. Small, focused PRs are easiest to review.
- If you add new runtime dependencies, update `requirements.txt` and document their purpose here.

---

## License

Include your preferred license here. (No license is specified in this repo by default.)

---

If you'd like, I can:

- Add usage screenshots for the GUI
- Add a simple unit-test or an automated smoke test for `process_directory`
- Convert the README into Chinese translation as well

Tell me which additions you'd like and I'll update the README accordingly.
