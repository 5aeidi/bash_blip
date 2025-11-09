from .base import BaseSkin

class TunnelSkin(BaseSkin):
    name = "tunnel"

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

        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0

        # movement and frequency influenced by energy
        phase = avg * math.pi * 2.0
        freq = 2.0 + avg * 6.0

        layers = " .,:;iIl!TfLJYXW#@"
        nl = len(layers)

        colors = None
        if self.has_color:
            colors = [self.Fore.MAGENTA, self.Fore.CYAN, self.Fore.YELLOW, self.Fore.GREEN, self.Fore.RED]

        screen = []
        for y in range(h):
            row = []
            for x in range(w):
                dx = (x - cx) / max(1.0, cx)
                dy = (y - cy) / max(1.0, cy)
                r = math.hypot(dx, dy)

                # simulate perspective by using inverse radius and a moving phase
                depth = (1.0 / (0.1 + r))
                ring = (math.sin(depth * freq + phase) + 1.0) / 2.0

                # sample a band to modulate intensity (safe with n)
                band = x % n if n > 0 else 0
                intensity = min(1.0, (norm_energies[band] if n > 0 else 0.0) * 1.5 + ring * 0.5)

                idx = int(intensity * (nl - 1))
                ch = layers[idx]

                if colors:
                    color = colors[(idx + band) % len(colors)]
                    row.append(color + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen
