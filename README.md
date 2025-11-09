# bashblip

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A real-time terminal audio visualizer for Linux that renders system audio as dynamic ASCII

<!-- <p align="center">
  <img src="demo/demo_blocks.gif" width="600" alt="blocks skin demo">
</p> -->

<p align="center">
  <img src="demo/demo_gradient.gif" width="600" alt="gradient skin demo">
</p>

## Features

- **Real-time system audio capture** via PulseAudio
- **Hybrid frequency bands**: linear spacing for bass (precise kick/bass separation), logarithmic for mids/treble
- **Per-band dynamic scaling** — no more bass domination or clipping
- **Modular skins**: easily switch between visual styles
- **Auto-fits terminal**: uses full width and height
- **Ultra-low latency**: no delay buildup, even after hours
- **Tunable via CLI**: adjust gain, frequency split, and headroom on the fly

## Built-in Skins

- `blocks` (default): Solid vertical bars using Unicode blocks (`█`)
- `dots`: Minimalist dot matrix showing only peak levels
- `gradient`: Color gradient bars (requires `colorama`)

## Requirements

- Linux with PulseAudio (or PipeWire with PulseAudio compatibility)
- Python 3.7+
- `pulseaudio-utils` (for `parec`)
- `numpy`

Optional:
- `colorama` (for `gradient` skin)

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
# Default: blocks skin
python3 bashblip.py

# Use a different skin
python3 bashblip.py --skin dots
python3 bashblip.py --skin gradient

# Tune audio response
python3 bashblip.py --gain 3500 --split-freq 250 --headroom 2.0

# See all options
python3 bashblip.py --help
```

### Key CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--skin` | Visualization style | `blocks` |
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