from .base import BaseSkin
from colorama import Fore, Style
import math

class HarmonicFlowSkin(BaseSkin):
    name = "harmonicflow"

    def __init__(self, bar_height, num_bands):
        super().__init__(bar_height, num_bands)
        try:

            self.has_color = True
            self.Fore = Fore
            self.Style = Style
        except ImportError:
            self.has_color = False
        self.time = 0.0

    def render(self, norm_energies):
        w = self.num_bands
        h = self.bar_height
        if w <= 0 or h <= 0:
            return []

        n = len(norm_energies) if hasattr(norm_energies, '__len__') else 0
        if n == 0:
            norm_energies = [0.0] * w
            n = w

        avg_energy = sum(norm_energies) / n
        self.time += 0.05 + avg_energy * 0.1

        # Smooth waveform using sine interpolation
        def smooth_sample(x):
            if n <= 1:
                return norm_energies[0] if n == 1 else 0.0
            t = x * (n - 1) / max(1, w - 1)
            i = int(t)
            frac = t - i
            a = norm_energies[max(0, min(i, n - 1))]
            b = norm_energies[max(0, min(i + 1, n - 1))]
            return a + (b - a) * frac

        # Flowing wave character set
        flow_chars = " ~≈≋∿﹏"

        screen = []
        for y in range(h):
            row = []
            for x in range(w):
                # Sample smooth energy
                energy = smooth_sample(x)

                # Simulate wave displacement
                displacement = math.sin(x * 0.1 + self.time) * 0.3 + \
                               math.sin(x * 0.05 + self.time * 0.7) * 0.2
                y_wave = (y / h) + displacement * energy * 0.8

                # Only draw if near wave center
                wave_center = energy * 0.8
                dist = abs(y_wave - wave_center)
                if dist > 0.15:
                    ch = " "
                else:
                    intensity = 1.0 - (dist / 0.15)
                    idx = int(intensity * (len(flow_chars) - 1))
                    ch = flow_chars[idx]

                if self.has_color and ch != " ":
                    # Color flows from blue → white → red with energy
                    if energy < 0.3:
                        color = self.Fore.BLUE
                    elif energy < 0.6:
                        color = self.Fore.CYAN
                    elif energy < 0.85:
                        color = self.Fore.YELLOW
                    else:
                        color = self.Fore.RED
                    ch = color + ch + self.Style.RESET_ALL

                row.append(ch)
            screen.append(''.join(row))

        return screen