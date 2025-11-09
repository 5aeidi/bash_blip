from .base import BaseSkin

class AuroraSkin(BaseSkin):
    name = "aurora"

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

        # safe length check for numpy arrays
        n = len(norm_energies) if hasattr(norm_energies, '__len__') else 0
        avg = (sum(norm_energies) / n) if n > 0 else 0.0
        phase = avg * math.pi * 2.0

        strips = [' ', '·', '░', '▒', '▓', '█']
        ns = len(strips)

        # color ramp for aurora (if available)
        palette = None
        if self.has_color:
            palette = [
                self.Fore.CYAN,
                self.Fore.MAGENTA,
                self.Fore.BLUE,
                self.Fore.GREEN,
                self.Fore.YELLOW,
            ]

        screen = []
        for y in range(h):
            row = []
            for x in range(w):
                # x-based wave plus band energy-driven jitter
                band = x % n if n > 0 else 0
                e = norm_energies[band] if n > 0 else 0.0

                # vertical position bias: center moves by a sinusoid that reacts to energy
                t = (x / max(1.0, w)) * 2.0 * math.pi * (1.0 + avg * 3.0) + phase
                wave = math.sin(t + y * 0.2)

                intensity = (wave + 1.0) / 2.0
                intensity = intensity * 0.6 + e * 0.4
                idx = int(intensity * (ns - 1))
                idx = max(0, min(ns - 1, idx))
                ch = strips[idx]

                if palette:
                    color = palette[(x + idx) % len(palette)]
                    row.append(color + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen
