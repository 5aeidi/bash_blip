from .base import BaseSkin

class AuroraFlowSkin(BaseSkin):
    name = "auroraflow"

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

        n = len(norm_energies) if hasattr(norm_energies, "__len__") else 0
        avg = (sum(norm_energies) / n) if n > 0 else 0.0

        # slow drift and flicker
        drift = avg * 0.6
        flicker = (math.sin(avg * math.pi * 4.0) + 1.0) / 2.0

        levels = " .:-=+*#%@"
        nl = len(levels)

        colors = None
        if self.has_color:
            # top (cool) -> mid (teal/cyan) -> bottom (warm magenta)
            colors = [self.Fore.MAGENTA, self.Fore.CYAN, self.Fore.GREEN, self.Fore.YELLOW]

        screen = []
        # sigma controls softness of the curtain edge
        sigma = max(0.8, 1.8 - avg * 1.2)
        for y in range(h):
            line = []
            # vertical normalized coordinate (0 top -> 1 bottom)
            vy = y / max(1, h - 1)
            for x in range(w):
                band = x % n if n > 0 else 0
                e = norm_energies[band] if n > 0 else 0.0

                # column anchor moves slowly with audio energy to create flowing curtains
                anchor = (1.0 - e) * (h * (0.25 + drift))  # base anchor height
                # distance from this row to the energetic anchor (smaller = brighter)
                distance = (y - anchor) / max(1.0, h)
                # gaussian-like falloff
                falloff = math.exp(- (distance * distance) / (2.0 * sigma * sigma))

                # subtle horizontal shimmer depending on x and global flicker
                shimmer = (math.sin((x / max(1, w)) * math.pi * 4.0 + avg * 3.0) + 1.0) / 2.0

                intensity = max(0.0, min(1.0, e * 1.4 * falloff + shimmer * 0.25 * flicker))

                idx = int(intensity * (nl - 1))
                ch = levels[idx]

                if colors:
                    # color mixes by vertical position and intensity for aurora-like bands
                    color_idx = min(len(colors) - 1, int(vy * (len(colors) - 1)))
                    color = colors[(color_idx + idx + band) % len(colors)]
                    line.append(color + ch + self.Style.RESET_ALL)
                else:
                    line.append(ch)
            screen.append(''.join(line))
        return screen