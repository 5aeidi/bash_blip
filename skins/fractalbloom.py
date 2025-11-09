from .base import BaseSkin
from colorama import Fore, Style
class FractalBloomSkin(BaseSkin):
    name = "fractalbloom"

    def __init__(self, bar_height, num_bands):
        super().__init__(bar_height, num_bands)
        self.has_color = True
        self.Fore = Fore
        self.Style = Style

    def render(self, norm_energies):
        import math

        w, h = self.num_bands, self.bar_height
        if w <= 0 or h <= 0:
            return []

        n = len(norm_energies) if hasattr(norm_energies, '__len__') else 0
        avg = (sum(norm_energies) / n) if n > 0 else 0.0

        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        phase = avg * math.pi * 5.0

        layers = " .`'-,^*+xX#%@"
        nl = len(layers)

        colors = None
        if self.has_color:
            colors = [self.Fore.MAGENTA, self.Fore.BLUE, self.Fore.CYAN, self.Fore.GREEN, self.Fore.WHITE]

        screen = []
        for y in range(h):
            row = []
            for x in range(w):
                dx, dy = (x - cx) / max(1, cx), (y - cy) / max(1, cy)
                r = math.sqrt(dx*dx + dy*dy)
                theta = math.atan2(dy, dx)

                # multi-harmonic flower pattern
                petal = math.sin(6 * theta + phase)
                ring = math.sin((r * 10.0) - phase * 2.0)
                bloom = (petal * ring + 1.0) / 2.0

                band = int(abs(math.sin(theta * 3)) * n) % n if n > 0 else 0
                e = norm_energies[band] if n > 0 else 0.0

                intensity = max(0.0, min(1.0, bloom * 0.8 + e * 1.2 - r * 0.2))
                idx = int(intensity * (nl - 1))
                ch = layers[idx]

                if colors:
                    color = colors[(idx + band + int(petal * 3)) % len(colors)]
                    row.append(color + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen