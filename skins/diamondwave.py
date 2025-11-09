from .base import BaseSkin

class DiamondWaveSkin(BaseSkin):
    name = "diamondwave"

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

        # diamond characters (outline -> filled)
        diamonds = [' ', '.', '*', 'o', 'O', '#']
        nd = len(diamonds)

        palette = None
        if self.has_color:
            palette = [self.Fore.CYAN, self.Fore.MAGENTA, self.Fore.YELLOW, self.Fore.GREEN, self.Fore.RED]

        screen = []
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0

        for y in range(h):
            row = []
            for x in range(w):
                # build a diamond lattice using manhattan-like metric rotated
                rx = (x - cx) / max(1.0, cx)
                ry = (y - cy) / max(1.0, cy)
                d = abs(rx) + abs(ry)

                # per-column band modulation
                band = x % n if n > 0 else 0
                e = norm_energies[band] if n > 0 else 0.0

                # wave ripple that depends on distance and average energy
                ripple = 0.5 + 0.5 * math.sin(d * 8.0 - avg * 10.0 + band * 0.3)

                intensity = max(0.0, min(1.0, ripple * (0.5 + e * 0.8)))
                idx = int(intensity * (nd - 1))
                ch = diamonds[idx]

                if palette:
                    color = palette[(idx + band) % len(palette)]
                    row.append(color + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen
