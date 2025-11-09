from .base import BaseSkin

class PulseMatrixSkin(BaseSkin):
    name = "pulsematrix"

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

        w, h = self.num_bands, self.bar_height
        if w <= 0 or h <= 0:
            return []

        n = len(norm_energies) if hasattr(norm_energies, '__len__') else 0
        avg = (sum(norm_energies) / n) if n > 0 else 0.0

        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        phase = avg * math.pi * 6.0
        layers = " `'.,-~:+*=#%@"
        nl = len(layers)

        colors = None
        if self.has_color:
            colors = [self.Fore.CYAN, self.Fore.GREEN, self.Fore.MAGENTA, self.Fore.YELLOW, self.Fore.WHITE]

        screen = []
        for y in range(h):
            row = []
            for x in range(w):
                dx, dy = (x - cx) / max(1, cx), (y - cy) / max(1, cy)
                r = math.hypot(dx, dy)
                angle = math.atan2(dy, dx)

                # radial pulse and grid overlay
                pulse = (math.sin(10.0 * r - phase * 2.0) + 1.0) / 2.0
                grid = (math.sin((x + phase * 2.0) * 0.7) * math.cos((y - phase) * 0.7) + 1.0) / 2.0

                e = norm_energies[int(abs(math.sin(angle) * n)) % n] if n > 0 else 0.0
                intensity = max(0.0, min(1.0, e * 1.1 + pulse * 0.7 + grid * 0.5 - r * 0.3))
                idx = int(intensity * (nl - 1))
                ch = layers[idx]

                if colors:
                    color = colors[(idx + int(r * 10)) % len(colors)]
                    row.append(color + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen