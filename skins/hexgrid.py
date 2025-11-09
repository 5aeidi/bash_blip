from .base import BaseSkin

class HexGridSkin(BaseSkin):
    name = "hexgrid"

    def __init__(self, bar_height, num_bands):
        super().__init__(bar_height, num_bands)
        try:
            from colorama import init, Fore, Style
            init(autoreset=True)
            self.has_color = True
            self.Fore = Fore
            self.Style = Style
        except Exception:
            self.has_color = False

    def render(self, norm_energies):
        import math

        w = self.num_bands
        h = self.bar_height
        if w <= 0 or h <= 0:
            return []

        n = len(norm_energies) if hasattr(norm_energies, '__len__') else 0
        avg = (sum(norm_energies) / n) if n > 0 else 0.0

        # characters approximating hex cells (alternating rows shifted)
        cells = [' ', '·', '○', '●', '◆', '■']
        nc = len(cells)

        palette = None
        if self.has_color:
            palette = [self.Fore.CYAN, self.Fore.MAGENTA, self.Fore.YELLOW, self.Fore.GREEN, self.Fore.RED]

        # spacing factors to make 'hex' look good in monospace
        x_scale = 1.0
        y_scale = 0.5

        screen = []
        for row in range(h):
            line = []
            for col in range(w):
                # axial-like coordinates: shift every other row
                sx = col + (0.5 if row % 2 == 0 else 0.0)
                sy = row * (1.0 / y_scale)

                # distance from a moving center that reacts to avg energy
                cx = (w - 1) / 2.0 + math.sin(avg * 2.0 * math.pi) * (w * 0.05)
                cy = (h - 1) / 2.0

                dx = (sx - cx) * x_scale
                dy = (sy - cy) * y_scale
                r = math.hypot(dx, dy)

                # sample a band to modulate the cell (wrap if needed)
                band = col % n if n > 0 else 0
                e = norm_energies[band] if n > 0 else 0.0

                # rhythmic ring effect plus per-band pulse
                ring = 0.5 + 0.5 * math.sin(r * 1.5 - avg * 6.0 + col * 0.1)
                intensity = max(0.0, min(1.0, ring * (0.6 + e * 0.8)))

                idx = int(intensity * (nc - 1))
                ch = cells[idx]

                if palette:
                    color = palette[(idx + band) % len(palette)]
                    line.append(color + ch + self.Style.RESET_ALL)
                else:
                    line.append(ch)
            screen.append(''.join(line))
        return screen
