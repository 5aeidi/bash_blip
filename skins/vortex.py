from .base import BaseSkin
from colorama import Fore, Style

import math

class VortexSkin(BaseSkin):
    name = "vortex"

    def __init__(self, bar_height, num_bands):
        super().__init__(bar_height, num_bands)
        try:

            self.has_color = True
            self.Fore = Fore
            self.Style = Style
        except ImportError:
            self.has_color = False

    def render(self, norm_energies):
        w = self.num_bands
        h = self.bar_height
        if w <= 0 or h <= 0:
            return []

        chars = " ░▒▓█"
        center_x, center_y = w / 2, h / 2
        max_radius = min(center_x, center_y)
        avg_energy = sum(norm_energies) / len(norm_energies)
        
        # Dynamic spiral parameters based on audio
        spiral_tightness = 2.0 + avg_energy * 3.0
        phase_shift = avg_energy * math.pi * 2
        
        colors = None
        if self.has_color:
            colors = [self.Fore.BLUE, self.Fore.CYAN, self.Fore.MAGENTA, self.Fore.WHITE]

        screen = []
        for y in range(h):
            row = []
            for x in range(w):
                # Convert to polar coordinates
                dx, dy = x - center_x, y - center_y
                radius = math.hypot(dx, dy) / max_radius
                angle = math.atan2(dy, dx) + phase_shift
                
                # Create spiral pattern
                spiral_value = (angle % (2 * math.pi)) + radius * spiral_tightness
                spiral_wave = (math.sin(spiral_value) + 1) / 2
                
                # Modulate with audio energy
                band_idx = int((angle / (2 * math.pi)) * len(norm_energies)) % len(norm_energies)
                energy = norm_energies[band_idx]
                combined = (spiral_wave * 0.7 + energy * 0.3)
                
                char_idx = min(int(combined * (len(chars) - 1)), len(chars) - 1)
                ch = chars[char_idx]
                
                if colors and self.has_color:
                    color_idx = int((angle / (2 * math.pi)) * len(colors)) % len(colors)
                    row.append(colors[color_idx] + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen