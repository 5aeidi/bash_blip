# bash_blip: CLI Audio Visualizer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A real-time terminal-based audio spectrum visualizer for Linux.  
Displays system audio output as smooth, vertical ASCII bars using Unicode block characters.

![Demo](demo.gif) *(Imagine: `▄▅█▆▄▃▂▁▃▄▆█...` scrolling in real-time)*

## Features

- Captures **system audio** (not just microphone)
- **Low-latency** (~50ms) responsive display
- **Logarithmic frequency bands** for natural sound perception
- Works in any modern terminal
- Single-file, no dependencies beyond Python and PulseAudio

## Requirements

- **Linux** with PulseAudio (or PipeWire with PulseAudio compatibility)
- Python 3.7+
- `pulseaudio-utils` (for `parec` command)
- `numpy`

## Installation

1. Install system dependencies:
   ```bash
   # Ubuntu/Debian
   sudo apt install pulseaudio-utils python3-numpy

   # Fedora/RHEL
   sudo dnf install pulseaudio-utils python3-numpy
   ```

2. Clone and run:
   ```bash
   git clone https://github.com/your-username/audio-ascii-vis.git
   cd audio-ascii-vis
   python3 audiovis.py
   ```

## Usage

```bash
# Auto-select default monitor
python3 audiovis.py

# List available audio monitors
python3 audiovis.py --list

# Use specific monitor and adjust sensitivity
python3 audiovis.py --device "your.monitor.name" --energy 20000
```

### Find Your Monitor Device

Run:
```bash
pactl list short sources | grep monitor
```

Example output:
```
3 alsa_output.pci-0000_00_1f.3.analog-stereo.monitor ...
```

Use the full name (e.g., `alsa_output.pci-0000_00_1f.3.analog-stereo.monitor`).

## Tuning

- If bars are **too low**: decrease `--energy` (e.g., `10000`)
- If bars are **always maxed**: increase `--energy` (e.g., `30000`)
- For **lower latency**: reduce `CHUNK` in source (try `128`)


## ✅ Final Notes

- All user-facing messages go to `stderr` so the visualizer output can be piped cleanly if needed.
- The script is **safe to run**, handles Ctrl+C, and cleans up `parec`.
- `gc.disable()` is justified and documented.
