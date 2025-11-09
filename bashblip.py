#!/usr/bin/env python3
"""
bash_blip: Modular real-time ASCII audio visualizer.
"""

import os
import sys
import argparse
from core import AudioEngine, get_default_monitor
from skins import SKINS

def main():
    parser = argparse.ArgumentParser(description="Modular ASCII audio visualizer.")
    parser.add_argument(
        "--skin",
        choices=list(SKINS.keys()),
        default="blocks",
        help="Visualization skin (default: blocks)"
    )

    # === NEW: Audio tuning parameters ===
    parser.add_argument(
        "--gain",
        type=float,
        default=2500.0,
        help="Frequency balancing gain. Higher = brighter highs (default: 2500)"
    )
    parser.add_argument(
        "--split-freq",
        type=float,
        default=300.0,
        help="Crossover frequency (Hz) between linear (bass) and log (mids/treble) bands (default: 300)"
    )
    parser.add_argument(
        "--headroom",
        type=float,
        default=1.5,
        help="Per-band headroom factor. Higher = less clipping (default: 1.5)"
    )

    args = parser.parse_args()

    # Terminal setup
    try:
        height = os.get_terminal_size().lines
        width = os.get_terminal_size().columns
    except OSError:
        height, width = 24, 80

    bar_height = max(4, height - 2)
    num_bands = max(8, width - 2)

    # Initialize
    try:
        device = get_default_monitor()
    except Exception:
        sys.exit(1)

    engine = AudioEngine(
        num_bands=num_bands,
        balance_gain_factor=args.gain,
        split_freq=args.split_freq,
        headroom_factor=args.headroom
    )
    engine.start_stream(device)
    skin = SKINS[args.skin](bar_height, num_bands)
    sys.stdout.write("\033[?25l")  # Hide cursor
    sys.stdout.flush()
    try:
        while True:
            engine.read_frame()
            raw = engine.read_frame()  # This returns one frame or None
            if raw is not None:
                norm_energies = engine.process(raw)
                screen = skin.render(norm_energies)
                sys.stdout.write("\033[2J\033[H" + "\n".join(screen))
                sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    finally:
        engine.stop()
        sys.stdout.write("\033[?25h\033[2J\033[H")  # Show cursor + clear
        sys.stdout.flush()

if __name__ == "__main__":
    main()