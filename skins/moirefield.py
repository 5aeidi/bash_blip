from .base import BaseSkin
import math

class MoireFieldSkin(BaseSkin):
    name = "moirefield"

    def __init__(self, bar_height, num_bands):
        super().__init__(bar_height, num_bands)
        try:
            from colorama import init, Fore, Style
            init(autoreset=True)
            self.has_color = True
            self.Fore = Fore
            self.Style = Style
        except ImportError:
            self.has_color = False
        self.phase = 0.0

    def render(self, norm_energies):
        w, h = self.num_bands, self.bar_height
        if w <= 0 or h <= 0:
            return []

        n = len(norm_energies) if hasattr(norm_energies, '__len__') else 0
        if n == 0:
            norm_energies = [0.5] * w
            n = w

        # Split spectrum: low = global scale, high = local noise
        low_avg = sum(norm_energies[:max(1, n // 4)]) / max(1, n // 4)
        high_avg = sum(norm_energies[-max(1, n // 4):]) / max(1, n // 4)

        self.phase += 0.03 + low_avg * 0.05

        chars = " .:-=+*#%@"
        colors = [self.Fore.GREEN, self.Fore.YELLOW, self.Fore.RED] if self.has_color else None

        screen = []
        for y in range(h):
            row = []
            for x in range(w):
                # Normalized coords
                u = x / max(1, w - 1)
                v = y / max(1, h - 1)

                # Base moiré: two rotating grids
                freq1 = 8.0 + low_avg * 12.0
                freq2 = 6.0 + low_avg * 10.0
                angle1 = self.phase
                angle2 = -self.phase + 0.3

                # Grid 1
                x1 = u * math.cos(angle1) - v * math.sin(angle1)
                y1 = u * math.sin(angle1) + v * math.cos(angle1)
                pattern1 = math.sin(x1 * freq1) * math.sin(y1 * freq1)

                # Grid 2
                x2 = u * math.cos(angle2) - v * math.sin(angle2)
                y2 = u * math.sin(angle2) + v * math.cos(angle2)
                pattern2 = math.sin(x2 * freq2) * math.sin(y2 * freq2)

                # Interference
                moire = (pattern1 + pattern2) / 2.0

                # Local perturbation from high frequencies
                band_idx = (x + y) % n
                noise = (norm_energies[band_idx] - 0.5) * 2.0
                moire += noise * high_avg * 0.5

                intensity = (moire + 1.0) / 2.0
                intensity = max(0.0, min(1.0, intensity))

                idx = int(intensity * (len(chars) - 1))
                ch = chars[idx]

                if colors:
                    color_idx = int(u * len(colors)) % len(colors)
                    row.append(colors[color_idx] + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen