from .base import BaseSkin

class SunburstSkin(BaseSkin):
    name = "sunburst"

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

        # character ramp from faint to strong
        ramp = [' ', '.', ':', '-', '=', '+', '*', '#', '@']
        nr = len(ramp)

        palette = None
        if self.has_color:
            palette = [self.Fore.YELLOW, self.Fore.MAGENTA, self.Fore.CYAN, self.Fore.GREEN, self.Fore.RED]

        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0

        # number of rays scales with average energy for more complexity
        base_rays = 8
        rays = max(6, int(base_rays + avg * 20))

        screen = []
        for y in range(h):
            row = []
            for x in range(w):
                dx = x - cx
                dy = y - cy
                r = math.hypot(dx, dy)
                theta = math.atan2(dy, dx)
                if theta < 0:
                    theta += 2 * math.pi

                # determine which ray this angle falls into
                ray_pos = (theta / (2 * math.pi)) * rays
                ray_index = int(ray_pos) % rays
                ray_frac = ray_pos - int(ray_pos)

                # sample band by ray_index to get per-ray energy
                band = ray_index % n if n > 0 else 0
                e = norm_energies[band] if n > 0 else 0.0

                # radial brightness falls with radius but pulses with energy
                pulse = 0.5 + 0.5 * math.sin(r * 3.0 - avg * 6.0 + ray_index * 0.6)
                intensity = max(0.0, min(1.0, (1.0 - (r / (max(1.0, max(cx, cy))))) * (0.6 + e * 0.8) * pulse))

                # sharpen along ray center
                center_sharpness = max(0.0, 1.0 - abs(ray_frac - 0.5) * 2.0)
                intensity = intensity * (0.4 + 0.6 * center_sharpness)

                idx = int(intensity * (nr - 1))
                ch = ramp[idx]

                if palette:
                    color = palette[(ray_index + idx) % len(palette)]
                    row.append(color + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen
