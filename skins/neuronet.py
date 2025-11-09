from .base import BaseSkin
from colorama import Fore, Style
class NeuroNetSkin(BaseSkin):
    name = "neuronet"

    def __init__(self, bar_height, num_bands):
        super().__init__(bar_height, num_bands)
        self.has_color = True
        self.Fore = Fore
        self.Style = Style

    def render(self, norm_energies):
        import math, random

        w, h = self.num_bands, self.bar_height
        if w <= 0 or h <= 0:
            return []

        n = len(norm_energies) if hasattr(norm_energies, '__len__') else 0
        avg = (sum(norm_energies) / n) if n > 0 else 0.0

        phase = avg * math.pi * 8.0
        layers = " .`'~-^:+*xX#%@"
        nl = len(layers)

        colors = None
        if self.has_color:
            colors = [
                self.Fore.BLUE,
                self.Fore.CYAN,
                self.Fore.GREEN,
                self.Fore.MAGENTA,
                self.Fore.YELLOW,
            ]

        screen = []
        for y in range(h):
            row = []
            for x in range(w):
                # normalized coordinates
                nx, ny = x / max(1, w), y / max(1, h)
                e = norm_energies[int(nx * n) % n] if n > 0 else 0.0

                # multi-layer interference pattern
                layer1 = math.sin((nx * 6 + phase) * (1.2 + e))
                layer2 = math.cos((ny * 8 - phase * 0.8) * (1.3 + e * 0.5))
                layer3 = math.sin((nx + ny + phase * 0.3) * 10.0)
                net = (layer1 * layer2 * layer3 + 1.0) / 2.0

                depth = (math.sin(ny * 3 + phase * 0.5) + 1.0) / 2.0
                intensity = max(0.0, min(1.0, net * 0.8 + e * 1.0 + depth * 0.3))
                idx = int(intensity * (nl - 1))
                ch = layers[idx]

                if colors:
                    color = colors[(idx + int(x * 0.3) + int(y * 0.2)) % len(colors)]
                    row.append(color + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen