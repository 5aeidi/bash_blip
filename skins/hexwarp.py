from .base import BaseSkin
from colorama import Fore, Style
class HexWarpSkin(BaseSkin):
    name = "hexwarp"

    def __init__(self, bar_height, num_bands):
        super().__init__(bar_height, num_bands)
        try:

            self.has_color = True
            self.Fore = Fore
            self.Style = Style
        except ImportError:
            self.has_color = False

    def render(self, norm_energies):
        import math

        w = self.num_bands
        h = self.bar_height
        if w <= 0 or h <= 0:
            return []

        n = len(norm_energies) if hasattr(norm_energies, "__len__") else 0
        avg = (sum(norm_energies) / n) if n > 0 else 0.0

        phase = avg * math.pi * 2.0
        freq = 1.8 + avg * 4.0

        layers = " .·oO0@#"
        nl = len(layers)

        colors = None
        if self.has_color:
            colors = [self.Fore.CYAN, self.Fore.GREEN, self.Fore.YELLOW, self.Fore.MAGENTA, self.Fore.RED]

        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0

        screen = []
        for y in range(h):
            row = []
            # stagger for "hex" look: every other row offsets the warp pattern
            row_offset = 0.5 if (y % 2) == 1 else 0.0
            for x in range(w):
                # compute a geometric warp field
                x_norm = (x + row_offset - cx) / max(1.0, cx)
                y_norm = (y - cy) / max(1.0, cy)
                r = math.hypot(x_norm, y_norm)

                # sample band safely (use x as band index)
                band = x % n if n > 0 else 0
                energy = norm_energies[band] if n > 0 else 0.0

                # warp combines radial ripples and diagonal shear for hex effect
                ripple = (math.sin(r * (freq * 3.0) - phase * (0.5 + energy)) + 1.0) / 2.0
                shear = (math.sin((x + y) * 0.3 + phase * 0.7) + 1.0) / 2.0

                intensity = max(0.0, min(1.0, energy * 0.85 + ripple * 0.6 + shear * 0.25 - r * 0.2))

                idx = int(intensity * (nl - 1))
                ch = layers[idx]

                if colors:
                    color = colors[(idx + band + y) % len(colors)]
                    row.append(color + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen