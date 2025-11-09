import subprocess
import numpy as np
import os
import fcntl

class AudioEngine:
    def __init__(
        self,
        num_bands,
        rate=22050,
        balance_gain_factor=2500.0,   # ← added
        split_freq=300.0,              # ← added
        headroom_factor=1.5            # ← added
    ):
        self.rate = rate
        self.num_bands = num_bands
        self.balance_gain_factor = balance_gain_factor  # ← store
        self.split_freq = split_freq                    # ← store
        self.headroom_factor = headroom_factor          # ← store
        self.chunk = min(2048, max(256, num_bands * 4))
        self.bands, self.freqs = self._create_hybrid_bands(split_freq)
        self.balance_gain = self._compute_balance_gain(balance_gain_factor)
        self.band_peaks = np.ones(num_bands) * 1000.0
        self.smoothed = np.zeros(num_bands)

    def _create_hybrid_bands(self, split_freq=300.0):
        freqs = np.fft.rfftfreq(self.chunk, 1.0 / self.rate)
        max_freq = self.rate / 2.0

        linear_bands = max(4, int(self.num_bands * 0.3))
        log_bands = self.num_bands - linear_bands

        linear_edges = np.linspace(20.0, split_freq, linear_bands + 1)
        if log_bands > 0:
            log_edges = np.logspace(
                np.log10(split_freq),
                np.log10(max_freq),
                log_bands + 1
            )
            all_edges = np.concatenate([linear_edges[:-1], log_edges])
        else:
            all_edges = linear_edges

        bands = []
        for i in range(self.num_bands):
            low = all_edges[i]
            high = all_edges[i + 1]
            indices = np.where((freqs >= low) & (freqs < high))[0]
            if len(indices) == 0:
                indices = bands[-1] if bands else [0]
            bands.append(indices)
        return bands, freqs

    def _compute_balance_gain(self, gain_factor):
        freq_centers = np.array([
            np.mean(self.freqs[band]) if len(self.freqs[band]) > 1 else self.freqs[band[0]]
            for band in self.bands
        ])
        return np.clip(gain_factor / np.sqrt(freq_centers), 1.0, 12.0)

    def start_stream(self, device):
        env = os.environ.copy()
        env["PULSE_LATENCY_MSEC"] = "10"
        self.proc = subprocess.Popen(
            [
                "parec",
                f"--rate={self.rate}",
                "--channels=1",
                "--format=s16le",
                f"--device={device}",
                "--latency-msec=10",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=env,
        )
        fd = self.proc.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        self.buffer = bytearray()

    def read_frame(self):
        try:
            while True:
                chunk = self.proc.stdout.read(4096)
                if chunk:
                    self.buffer.extend(chunk)
                else:
                    break
        except (OSError, TypeError):
            pass

        frame_bytes = self.chunk * 2
        if len(self.buffer) < frame_bytes:
            return None

        raw = self.buffer[:frame_bytes]
        del self.buffer[:frame_bytes]
        return raw

    def process(self, raw_frame):
        samples = np.frombuffer(raw_frame, dtype=np.int16).astype(np.float32)
        fft = np.abs(np.fft.rfft(samples))
        energies = np.array([np.mean(fft[band]) for band in self.bands])
        balanced = energies * self.balance_gain
        self.band_peaks = np.maximum(balanced, self.band_peaks * 0.995)
        norm = np.clip(
                balanced / (self.band_peaks * self.headroom_factor + 1e-8),  # ← use self.headroom_factor
                0.0, 1.0
            )
        self.smoothed = 0.3 * norm + 0.7 * self.smoothed
        return self.smoothed.copy()

    def stop(self):
        self.proc.terminate()
        self.proc.wait()