#!/usr/bin/env python3
"""
bash_blip: Modular real-time ASCII audio visualizer.
"""

import os
import sys
import argparse
from core import AudioEngine, get_default_monitor
from skins import SKINS
import random
import termios
import tty
import select
from colorama import init, Fore, Style
import time
import atexit


init(autoreset=True)

def key_pressed():
    """Return one key if pressed, else None (non-blocking)."""
    dr, dw, de = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1)
    return None

old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())
def restore_terminal():
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    sys.stdout.write("\033[?25h\033[2J\033[H")  # restore cursor and clear
    sys.stdout.flush()

atexit.register(restore_terminal)

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
    skins_list = [SKINS[name](bar_height, num_bands) for name in SKINS]
    current_idx = 0
    skin = skins_list[current_idx]
    sys.stdout.write("\033[?25l")  # Hide cursor
    sys.stdout.flush()
    try:
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

        while True:
            # check for keypress
            key = key_pressed()
            if key:
                if key.lower() == 's':
                    current_idx = (current_idx + 1) % len(skins_list)
                    skin = skins_list[current_idx]
                    sys.stdout.write(f"\033[2J\033[H[Switched skin → {skin.name}]\n")
                    sys.stdout.flush()
                elif key.lower() == 'q':
                    break  # optional quit shortcut


            engine.read_frame()
            raw = engine.read_frame()
            if raw is not None:
                norm_energies = engine.process(raw)
                screen = skin.render(norm_energies)
                sys.stdout.write("\033[H" + "\n".join(screen))
                sys.stdout.flush()

    except KeyboardInterrupt:
        pass
    finally:
        engine.stop()
        restore_terminal()



if __name__ == "__main__":
    main()