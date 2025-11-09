from .base import BaseSkin

class DepthGridSkin(BaseSkin):
    name = "depthgrid"

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
        phase = avg * math.pi * 4.0

        layers = " .'`^\",:;Il!i~+_-?][}{1)(|\\/*tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
        nl = len(layers)

        colors = None
        if self.has_color:
            colors = [self.Fore.CYAN, self.Fore.BLUE, self.Fore.MAGENTA, self.Fore.WHITE]

        screen = []
        for y in range(h):
            row = []
            depth = (h - y) / h
            z = depth + 0.1
            for x in range(w):
                band = x % n if n > 0 else 0
                e = norm_energies[band] if n > 0 else 0.0

                # perspective warp + horizontal motion
                x_norm = (x - w / 2) / max(1, w / 2)
                move = math.sin(phase + x_norm * 5.0) * e * 0.4

                # simulate horizon depth fade
                intensity = max(0.0, min(1.0, (1.0 - z*z) * e * 1.5 + move * 0.6))
                idx = int(intensity * (nl - 1))
                ch = layers[idx]

                if colors:
                    color = colors[int((depth * 3 + idx) % len(colors))]
                    row.append(color + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen