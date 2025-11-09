from .base import BaseSkin
from colorama import Fore, Style
class SpiralSkin(BaseSkin):
    name = "spiral"

    def render(self, norm_energies):
        import math

        w = self.num_bands
        h = self.bar_height
        if w <= 0 or h <= 0:
            return []

        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        maxr = math.hypot(cx, cy) or 1.0

        # avoid using 'if norm_energies' (numpy arrays are ambiguous)
        n = len(norm_energies) if hasattr(norm_energies, '__len__') else 0
        avg = (sum(norm_energies) / n) if n > 0 else 0.0
        phase = avg * math.pi * 2.0 * 1.5

        chars = " .:-=+*#%@"
        nchar = len(chars)

        screen = []
        for row in range(h):
            line = []
            for col in range(w):
                dx = col - cx
                dy = row - cy
                r = math.hypot(dx, dy)
                theta = math.atan2(dy, dx)

                # spiral mapping: angle + radius*scale moves along spiral; phase shifts with energy
                val = theta + (r / maxr) * (math.pi * 2.5) + phase
                frac = (val / (2 * math.pi)) % 1.0

                # band energy mapped per column (if bands < columns wrap)
                band_idx = col % n if n > 0 else 0
                energy = norm_energies[band_idx] if n > 0 else 0.0

                # bias index by energy so brighter bands produce denser center
                idx = int(frac * nchar + energy * (nchar // 2))
                idx = max(0, min(nchar - 1, idx))

                # fade out outermost ring slightly unless energy is high
                fade = r / maxr
                if fade > 0.95 and energy < 0.1:
                    ch = ' '
                else:
                    ch = chars[idx]
                line.append(ch)
            screen.append(''.join(line))
        return screen
