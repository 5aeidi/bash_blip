#!/usr/bin/env python3
"""
bash_blip: Real-time ASCII audio visualizer using parec.

"""

import subprocess
import numpy as np
import sys
import gc
import os
import fcntl
import time

gc.disable()

# Config
CHUNK = 256             # Small = low latency
RATE = 22050
NUM_BANDS = 48
BAR_HEIGHT = 8
MAX_ENERGY = 18000.0

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
    """Get default monitor name from PulseAudio."""
    try:
        sink = subprocess.check_output(
            ["pactl", "get-default-sink"], text=True
        ).strip()
        return sink + ".monitor"
    except Exception:
        # Fallback: pick first monitor
        try:
            sources = subprocess.check_output(
                ["pactl", "list", "short", "sources"], text=True
            )
            for line in sources.splitlines():
                if ".monitor" in line:
                    return line.split()[1]
        except Exception:
            pass
    raise RuntimeError("No monitor found")

def main():
    # Get monitor
    try:
        device = get_default_monitor()
    except Exception:
        sys.exit(1)

    # Start parec with ultra-low latency
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

    try:
        while True:
            # Read available data (non-blocking)
            try:
                chunk = parec.stdout.read(4096)
                if chunk:
                    audio_buffer.extend(chunk)
            except (OSError, TypeError):
                pass  # no data available

            # Process as many frames as possible
            frame_bytes = CHUNK * 2
            processed = False
            while len(audio_buffer) >= frame_bytes:
                raw_frame = audio_buffer[:frame_bytes]
                del audio_buffer[:frame_bytes]

                samples = np.frombuffer(raw_frame, dtype=np.int16).astype(np.float32)
                fft = np.abs(np.fft.rfft(samples))
                energies = np.array([np.mean(fft[band]) for band in bands])
                smoothed = 0.25 * energies + 0.75 * smoothed

                # Render
                # heights = np.clip(smoothed / MAX_ENERGY, 0.0, 1.0) * BAR_HEIGHT
                # heights = heights.astype(int)
                HEADROOM_SCALE = 80000.0  # ↑ increase for more headroom

                norm_energies = np.clip(smoothed / HEADROOM_SCALE, 0.0, 1.0)
                heights = (norm_energies * BAR_HEIGHT).astype(int)
                screen = []
                for row in range(BAR_HEIGHT):
                    line = ''.join("█" if row >= (BAR_HEIGHT - h) else " " for h in heights)
                    screen.append(line)
                
                sys.stdout.write("\033[2J\033[H" + "\n".join(screen))
                sys.stdout.flush()
                processed = True

            # If no audio processed, decay smoothly
            if not processed:
                smoothed *= 0.92  # gentle decay on silence
                # Re-render to show decay
                heights = np.clip(smoothed / MAX_ENERGY, 0.0, 1.0) * BAR_HEIGHT
                heights = heights.astype(int)
                screen = [
                    ''.join("█" if row >= (BAR_HEIGHT - h) else " " for h in heights)
                    for row in range(BAR_HEIGHT)
                ]
                sys.stdout.write("\033[2J\033[H" + "\n".join(screen))
                sys.stdout.flush()

            time.sleep(0.016)  # ~60 FPS

    except KeyboardInterrupt:
        pass
    finally:
        parec.terminate()
        parec.wait()
        sys.stdout.write("\033[2J\033[H")

if __name__ == "__main__":
    main()