"""
Audio ASCII Visualizer

Real-time terminal spectrum visualizer for system audio on Linux.
Uses PulseAudio's monitor sources and renders frequency bands as vertical
ASCII bars using Unicode block characters.

Author: [Your Name]
License: MIT
"""

import subprocess
import numpy as np
import sys
import gc
import argparse
import time

# Disable garbage collection for real-time performance
gc.disable()

# Configuration constants
CHUNK: int = 256          # Audio samples per frame (lower = less latency)
RATE: int = 22050         # Sample rate (Hz)
NUM_BANDS: int = 32       # Number of frequency bands (columns)
BLOCKS: str = "▁▂▃▄▅▆▇█"  # Unicode block characters for levels
MAX_LEVEL: int = len(BLOCKS) - 1
DEFAULT_MAX_ENERGY: float = 15000.0  # Tune based on system volume


def get_frequency_bands(chunk_size: int, rate: int, num_bands: int):
    """Precompute log-spaced frequency band indices for FFT output."""
    freqs = np.fft.rfftfreq(chunk_size, 1.0 / rate)
    min_freq, max_freq = 20.0, rate / 2.0
    log_bins = np.logspace(np.log10(min_freq), np.log10(max_freq), num_bands + 1)
    bands = []
    for i in range(num_bands):
        indices = np.where((freqs >= log_bins[i]) & (freqs < log_bins[i + 1]))[0]
        bands.append(indices if len(indices) > 0 else np.array([0]))
    return bands


def list_monitor_sources():
    """List available PulseAudio monitor sources."""
    try:
        result = subprocess.run(
            ["pactl", "list", "short", "sources"],
            capture_output=True, text=True, check=True
        )
        monitors = [
            line.split()[1] for line in result.stdout.splitlines()
            if ".monitor" in line
        ]
        return monitors
    except (subprocess.CallingProcessError, FileNotFoundError):
        return []


def main():
    parser = argparse.ArgumentParser(description="Real-time ASCII audio visualizer for Linux.")
    parser.add_argument(
        "--device",
        help="PulseAudio monitor source (e.g., alsa_output.pci-0000_00_1f.3.analog-stereo.monitor)"
    )
    parser.add_argument(
        "--energy",
        type=float,
        default=DEFAULT_MAX_ENERGY,
        help=f"Energy scaling factor (default: {DEFAULT_MAX_ENERGY})"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available monitor sources and exit"
    )
    args = parser.parse_args()

    if args.list:
        monitors = list_monitor_sources()
        if monitors:
            print("Available monitor sources:")
            for m in monitors:
                print(f"  {m}")
        else:
            print("No monitor sources found. Ensure PulseAudio is running.")
        return

    # Auto-detect device if not provided
    device = args.device
    if not device:
        monitors = list_monitor_sources()
        if not monitors:
            print("Error: No PulseAudio monitor sources found. Run with --list to debug.", file=sys.stderr)
            sys.exit(1)
        device = monitors[0]
        print(f"Auto-selected monitor: {device}", file=sys.stderr)

    # Precompute frequency bands
    bands = get_frequency_bands(CHUNK, RATE, NUM_BANDS)

    # Start PulseAudio recorder
    parec_cmd = [
        "parec",
        f"--rate={RATE}",
        "--channels=1",
        "--format=s16le",
        f"--device={device}"
    ]
    try:
        parec = subprocess.Popen(
            parec_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        print("Error: 'parec' not found. Install PulseAudio utils (e.g., pulseaudio-utils).", file=sys.stderr)
        sys.exit(1)

    audio_buffer = bytearray()
    smoothed = np.zeros(NUM_BANDS)
    print("Starting visualizer... Press Ctrl+C to exit.", file=sys.stderr)

    try:
        while True:
            # Read in larger chunks to avoid blocking
            new_data = parec.stdout.read(4096)
            if not new_data:
                break
            audio_buffer.extend(new_data)

            # Process all available frames
            frame_bytes = CHUNK * 2  # s16le = 2 bytes/sample
            while len(audio_buffer) >= frame_bytes:
                raw_frame = audio_buffer[:frame_bytes]
                del audio_buffer[:frame_bytes]

                # Compute spectrum
                samples = np.frombuffer(raw_frame, dtype=np.int16).astype(np.float32)
                fft = np.abs(np.fft.rfft(samples))
                energies = np.array([np.mean(fft[band]) for band in bands])
                smoothed = 0.25 * energies + 0.75 * smoothed

                # Render line
                line = ''.join(
                    BLOCKS[int(min(e / args.energy, 1.0) * MAX_LEVEL)]
                    for e in smoothed
                )
                sys.stdout.write('\r' + line)
                sys.stdout.flush()

                # Throttle to ~80 FPS to prevent terminal overload
                time.sleep(0.0125)

    except KeyboardInterrupt:
        pass
    finally:
        parec.terminate()
        parec.wait()
        sys.stdout.write('\nBye!\n')


if __name__ == "__main__":
    main()