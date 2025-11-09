#!/usr/bin/env python3
"""
bash_blip: Real-time ASCII audio visualizer with balanced frequency response.

Features:
- Auto-detects PulseAudio monitor
- Per-band dynamic scaling (no bass clipping)
- Frequency balancing for clear mids/treble
- Fills terminal height/width
- Ultra-low latency, no delay buildup
- Clean, silent operation
"""

import subprocess
import numpy as np
import sys
import gc
import os
import fcntl

gc.disable()

# === Configuration ===
CHUNK = 256          # Lower = less latency
RATE = 22050         # Sample rate (covers up to ~11 kHz)

# Terminal size detection
try:
    TERMINAL_HEIGHT = os.get_terminal_size().lines
    TERMINAL_WIDTH = os.get_terminal_size().columns
except OSError:
    TERMINAL_HEIGHT = 24
    TERMINAL_WIDTH = 80

BAR_HEIGHT = max(4, TERMINAL_HEIGHT - 2)
NUM_BANDS = min(64, max(16, TERMINAL_WIDTH))

# Precompute frequency bands
freqs = np.fft.rfftfreq(CHUNK, 1.0 / RATE)
min_f, max_f = 20.0, RATE / 2.0
log_bins = np.logspace(np.log10(min_f), np.log10(max_f), NUM_BANDS + 1)
bands = [
    np.where((freqs >= log_bins[i]) & (freqs < log_bins[i + 1]))[0]
    for i in range(NUM_BANDS)
]
bands = [b if len(b) > 0 else [0] for b in bands]


def get_default_monitor():
    """Get the default PulseAudio monitor source."""
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
    # Get monitor device
    try:
        device = get_default_monitor()
    except Exception:
        sys.exit(1)

    # Launch parec with low-latency settings
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

    # Make stdout non-blocking
    fd = parec.stdout.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    audio_buffer = bytearray()
    smoothed = np.zeros(NUM_BANDS)
    band_peaks = np.ones(NUM_BANDS) * 1000.0  # per-band peak tracker

    # Precompute frequency centers for balancing
    freq_centers = np.array([
        np.mean(freqs[band]) if len(band) > 1 else freqs[band[0]]
        for band in bands
    ])
    balance_gain = np.clip(2500.0 / np.sqrt(freq_centers), 1.0, 12.0)

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

                # Apply frequency balancing
                balanced_energies = energies * balance_gain

                # Update per-band peaks (slow decay)
                band_peaks = np.maximum(balanced_energies, band_peaks * 0.995)

                # Normalize each band independently with headroom
                norm_energies = np.clip(
                    balanced_energies / (band_peaks * 1.5 + 1e-8),
                    0.0, 1.0
                )

                # Smooth for visual stability
                smoothed = 0.3 * norm_energies + 0.7 * smoothed
                processed = True

            # Render only if processed or forced by silence decay
            if processed:
                # Build screen
                screen = []
                for row in range(BAR_HEIGHT):
                    line = ''.join(
                        "█" if row >= (BAR_HEIGHT - int(h * BAR_HEIGHT)) else " "
                        for h in smoothed
                    )
                    screen.append(line)
                sys.stdout.write("\033[2J\033[H" + "\n".join(screen))
                sys.stdout.flush()

            # Minimal yield to avoid 100% CPU (optional)
            # time.sleep(0.001)

    except KeyboardInterrupt:
        pass
    finally:
        parec.terminate()
        parec.wait()
        sys.stdout.write("\033[2J\033[H")


if __name__ == "__main__":
    main()