from .base import BaseSkin
from colorama import Fore, Style
class PrismSkin(BaseSkin):
    name = "prism"

    def __init__(self, bar_height, num_bands):
        super().__init__(bar_height, num_bands)
        self.has_color = True
        self.Fore = Fore
        self.Style = Style

    def render(self, norm_energies):
        import math

        w = self.num_bands
        h = self.bar_height
        if w <= 0 or h <= 0:
            return []

        # safe length check
        n = len(norm_energies) if hasattr(norm_energies, "__len__") else 0
        avg = (sum(norm_energies) / n) if n > 0 else 0.0

        phase = avg * math.pi * 2.0
        freq = 1.5 + avg * 5.0

        layers = " .,-~:;+=*#%@"
        nl = len(layers)

        colors = None
        if self.has_color:
            colors = [
                self.Fore.RED,
                self.Fore.MAGENTA,
                self.Fore.YELLOW,
                self.Fore.GREEN,
                self.Fore.CYAN,
                self.Fore.BLUE,
                self.Fore.WHITE,
            ]

        screen = []
        for y in range(h):
            row_chars = []
            # slanted offset to create diagonal prism effect
            slant = (y / max(1, h - 1)) * 2.0 - 1.0
            for x in range(w):
                # sample a band safely
                band = x % n if n > 0 else 0
                base = norm_energies[band] if n > 0 else 0.0

                # refractive shimmer: combine horizontal wave, vertical slant and per-band energy
                wave = (math.sin((x / max(1, w)) * freq * math.pi * 2.0 + phase * (0.5 + base)) + 1.0) / 2.0
                prism = (slant * 0.5 + (y / max(1, h - 1))) * 0.5
                intensity = max(0.0, min(1.0, base * 0.9 + wave * 0.55 + prism * 0.25))

                idx = int(intensity * (nl - 1))
                ch = layers[idx]

                if colors:
                    color = colors[(idx + x + y) % len(colors)]
                    row_chars.append(color + ch + self.Style.RESET_ALL)
                else:
                    row_chars.append(ch)
            screen.append(''.join(row_chars))
        return screen