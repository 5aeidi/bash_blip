from .base import BaseSkin

class WarpTunnelSkin(BaseSkin):
    name = "warptunnel"

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
        import math, random

        w, h = self.num_bands, self.bar_height
        if w <= 0 or h <= 0:
            return []

        n = len(norm_energies) if hasattr(norm_energies, '__len__') else 0
        avg = (sum(norm_energies) / n) if n > 0 else 0.0

        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        phase = avg * math.pi * 4.0
        zoom = 1.0 + avg * 2.0

        layers = " .,:;irsXA253hMHGS#9B&@"
        nl = len(layers)

        colors = None
        if self.has_color:
            colors = [self.Fore.BLUE, self.Fore.CYAN, self.Fore.MAGENTA, self.Fore.WHITE]

        screen = []
        for y in range(h):
            row = []
            for x in range(w):
                dx, dy = (x - cx) / cx, (y - cy) / cy
                r = math.hypot(dx, dy)
                theta = math.atan2(dy, dx)

                # concentric rings expanding forward
                z = (math.sin(r * 10.0 - phase * 3.0) + 1.0) / 2.0
                # simulate forward motion + depth compression
                depth = 1.0 / (1.0 + r * zoom)
                e = norm_energies[int(abs(math.sin(theta) * n)) % n] if n > 0 else 0.0

                intensity = max(0.0, min(1.0, e * 0.8 + z * depth * 1.4))
                idx = int(intensity * (nl - 1))
                ch = layers[idx]

                if colors:
                    color = colors[(idx + int(r * 10)) % len(colors)]
                    row.append(color + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen