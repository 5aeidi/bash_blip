from .base import BaseSkin

class VortexMotionSkin(BaseSkin):
    name = "vortexmotion"

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
        phase = avg * math.pi * 2.0
        depth_shift = avg * 3.0

        layers = " .:-=+*#%@"
        nl = len(layers)

        colors = None
        if self.has_color:
            colors = [self.Fore.CYAN, self.Fore.BLUE, self.Fore.MAGENTA, self.Fore.RED, self.Fore.YELLOW]

        screen = []
        for y in range(h):
            row = []
            for x in range(w):
                dx, dy = (x - cx), (y - cy)
                r = math.sqrt(dx*dx + dy*dy) / max(1.0, cx)
                angle = math.atan2(dy, dx)

                # spiral vortex depth with rotational motion
                spin = angle + r * 8.0 - phase * 2.5
                depth = (math.sin(spin) + 1.0) / 2.0

                band = (int((angle / (2 * math.pi) + 1.0) * n)) % n if n > 0 else 0
                e = norm_energies[band] if n > 0 else 0.0

                # combine energy with depth and radial falloff
                intensity = max(0.0, min(1.0, e * 1.2 + depth * 0.8 - r * 0.4 + depth_shift * 0.05))
                idx = int(intensity * (nl - 1))
                ch = layers[idx]

                if colors:
                    color = colors[(idx + band + int(y*0.3)) % len(colors)]
                    row.append(color + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen