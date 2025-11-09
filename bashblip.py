#!/usr/bin/env python3
"""
bash_blip: Real-time ASCII audio visualizer with professional-grade frequency separation.

Features:
- Hybrid linear (bass) + log (mids/treble) band spacing
- Per-band independent scaling (no bass domination)
- Frequency balancing for balanced spectrum
- Auto-fits terminal width and height
- Ultra-low latency with no accumulating delay
- Silent, flicker-free output
"""

import subprocess
import numpy as np
import sys
import gc
import os
import fcntl

gc.disable()

# === Configuration ===
RATE = 22050  # Sample rate (covers up to ~11 kHz)

# Terminal size detection
try:
    TERMINAL_HEIGHT = os.get_terminal_size().lines
    TERMINAL_WIDTH = os.get_terminal_size().columns
except OSError:
    TERMINAL_HEIGHT = 24
    TERMINAL_WIDTH = 80

BAR_HEIGHT = max(4, TERMINAL_HEIGHT - 2)
NUM_BANDS = max(8, TERMINAL_WIDTH - 2)  # Use nearly full width

# Adjust CHUNK based on band count for frequency resolution
CHUNK = min(2048, max(256, NUM_BANDS * 4))


def create_hybrid_bands(chunk_size, rate, num_bands, split_freq=300.0):
    """Create frequency bands with linear spacing below split_freq, log above."""
    freqs = np.fft.rfftfreq(chunk_size, 1.0 / rate)
    max_freq = rate / 2.0

    # Allocate ~30% of bands to linear (bass) region
    linear_bands = max(4, int(num_bands * 0.3))
    log_bands = num_bands - linear_bands

    # Linear spacing from 20 Hz to split_freq
    linear_edges = np.linspace(20.0, split_freq, linear_bands + 1)
    
    # Log spacing from split_freq to Nyquist
    if log_bands > 0:
        log_edges = np.logspace(
            np.log10(split_freq),
            np.log10(max_freq),
            log_bands + 1
        )
        # Combine, avoiding duplicate at split_freq
        all_edges = np.concatenate([linear_edges[:-1], log_edges])
    else:
        all_edges = linear_edges

    # Build band index lists
    bands = []
    for i in range(num_bands):
        low = all_edges[i]
        high = all_edges[i + 1]
        indices = np.where((freqs >= low) & (freqs < high))[0]
        if len(indices) == 0:
            # Fallback: use previous band or first bin
            indices = bands[-1] if bands else [0]
        bands.append(indices)
    return bands, freqs


def get_default_monitor():
    """Auto-detect PulseAudio monitor source."""
    try:
        sink = subprocess.check_output(["pactl", "get-default-sink"], text=True).strip()
        if sink:
            return sink + ".monitor"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        sources = subprocess.check_output(["pactl", "list", "short", "sources"], text=True)
        for line in sources.splitlines():
            if ".monitor" in line:
                return line.split()[1]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    raise RuntimeError("No monitor")


def main():
    # Setup frequency bands
    bands, freqs = create_hybrid_bands(CHUNK, RATE, NUM_BANDS, split_freq=300.0)

    # Frequency balancing: boost highs
    freq_centers = np.array([
        np.mean(freqs[band]) if len(band) > 1 else freqs[band[0]]
        for band in bands
    ])
    balance_gain = np.clip(2500.0 / np.sqrt(freq_centers), 1.0, 12.0)

    # Get monitor
    try:
        device = get_default_monitor()
    except Exception:
        sys.exit(1)

    # Launch low-latency parec
    env = os.environ.copy()
    env["PULSE_LATENCY_MSEC"] = "10"

    parec = subprocess.Popen(
        [
            "parec",
            f"--rate={RATE}",
            "--channels=1",
            "--format=s16le",
            f"--device={device}",
            "--latency-msec=10",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env=env,
    )

    # Non-blocking read
    fd = parec.stdout.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    audio_buffer = bytearray()
    smoothed = np.zeros(NUM_BANDS)
    band_peaks = np.ones(NUM_BANDS) * 1000.0  # per-band peak tracker

    try:
        while True:
            # Read all available data
            try:
                while True:
                    chunk = parec.stdout.read(4096)
                    if chunk:
                        audio_buffer.extend(chunk)
                    else:
                        break
            except (OSError, TypeError):
                pass

            frame_bytes = CHUNK * 2
            processed = False

            # Process all available frames
            while len(audio_buffer) >= frame_bytes:
                raw_frame = audio_buffer[:frame_bytes]
                del audio_buffer[:frame_bytes]

                samples = np.frombuffer(raw_frame, dtype=np.int16).astype(np.float32)
                fft = np.abs(np.fft.rfft(samples))
                energies = np.array([np.mean(fft[band]) for band in bands])

                # Apply balancing
                balanced_energies = energies * balance_gain

                # Update per-band peaks
                band_peaks = np.maximum(balanced_energies, band_peaks * 0.995)

                # Normalize per band with headroom
                norm_energies = np.clip(
                    balanced_energies / (band_peaks * 1.5 + 1e-8),
                    0.0, 1.0
                )

                smoothed = 0.3 * norm_energies + 0.7 * smoothed
                processed = True

            # Render only when audio processed
            if processed:
                screen = []
                for row in range(BAR_HEIGHT):
                    line = ''.join(
                        "█" if row >= (BAR_HEIGHT - int(h * BAR_HEIGHT)) else " "
                        for h in smoothed
                    )
                    screen.append(line)
                sys.stdout.write("\033[2J\033[H" + "\n".join(screen))
                sys.stdout.flush()

    except KeyboardInterrupt:
        pass
    finally:
        parec.terminate()
        parec.wait()
        sys.stdout.write("\033[2J\033[H")


if __name__ == "__main__":
    main()