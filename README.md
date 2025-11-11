# bashblip

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A real-time terminal audio visualizer for Linux CLI that renders system audio as dynamic ASCII with over 20 visualizations.

<p align="center">
  <img src="demo/demo_gradient.gif" width="32%" alt="tunnel skin">
  <!-- <img src="demo/fire.gif" width="32%" alt="fire skin">
  <img src="demo/quantumwave.gif" width="32%" alt="quantumwave skin">
  <br>
  <img src="demo/cymatic.gif" width="32%" alt="cymatic skin">
  <img src="demo/resonancesphere.gif" width="32%" alt="resonancesphere skin">
  <img src="demo/vortex.gif" width="32%" alt="vortex skin"> -->
</p>

## Features

- **Real-time system audio capture** via PulseAudio
- **Modular skins**: easily switch between visual styles with `s` key
- **Auto-fits terminal**: uses full width and height
- **Ultra-low latency**: no delay buildup, even after hours
- **Tunable via CLI**: adjust gain, frequency split, and headroom on the fly
- **Over 20 visualizers**

## Requirements

- Linux with PulseAudio (or PipeWire with PulseAudio compatibility)
- Python 3.7+
- `pulseaudio-utils` (for `parec`)
- `numpy`

Optional:
- `colorama` (for color skins)

## Installation

```bash
# Install system dependencies
sudo apt install pulseaudio-utils python3-numpy  # Debian/Ubuntu
# or
sudo dnf install pulseaudio-utils python3-numpy  # Fedora

# Install optional dependency for color support
pip3 install colorama

# Clone and run
git clone https://github.com/your-username/bashblip.git
cd bashblip
python3 bashblip.py
```

## Usage

```bash
# Default skin
python3 bashblip.py

# Use a specific skin
python3 bashblip.py --skin quantumwave

# Tune audio response
python3 bashblip.py --gain 3500 --split-freq 250 --headroom 2.0

# See all options
python3 bashblip.py --help
```

### Controls
- **`s`** - Cycle through all available skins
- **`q`** - Quit the application

### Key CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--skin` | Starting visualization style | `blocks` |
| `--gain` | Frequency balancing (higher = brighter highs) | `2500.0` |
| `--split-freq` | Bass/mid crossover frequency (Hz) | `300.0` |
| `--headroom` | Per-band clipping headroom (higher = less clipping) | `1.5` |

## Creating Your Own Skin

1. Create a new file in `skins/` (e.g., `fire.py`)
2. Subclass `BaseSkin` and implement `render()`
3. Register it in `skins/__init__.py`
4. Run with `--skin your_skin_name`

## License

MIT License. See [LICENSE](LICENSE).