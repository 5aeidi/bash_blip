from .base import BaseSkin
from colorama import Fore, Style
import math
import random

class PlasmaStormSkin(BaseSkin):
    name = "plasmastorm"

    def __init__(self, bar_height, num_bands):
        super().__init__(bar_height, num_bands)
        try:

            self.has_color = True
            self.Fore = Fore
            self.Style = Style
        except ImportError:
            self.has_color = False
        self.time = 0

    def render(self, norm_energies):
        w = self.num_bands
        h = self.bar_height
        if w <= 0 or h <= 0:
            return []

        chars = " ░▒▓█"
        self.time += 0.08
        
        avg_energy = sum(norm_energies) / len(norm_energies)
        
        # Multiple octaves for fractal noise
        def plasma(x, y, t):
            value = math.sin(x * 3 + t)
            value += math.sin(y * 4 + t * 1.3) * 0.7
            value += math.sin((x + y) * 5 + t * 0.7) * 0.5
            value += math.sin(math.hypot(x, y) * 6 + t * 1.7) * 0.3
            
            # Add audio-influenced turbulence
            band_x = int(abs(x) * len(norm_energies)) % len(norm_energies)
            band_y = int(abs(y) * len(norm_energies)) % len(norm_energies)
            audio_turbulence = (norm_energies[band_x] + norm_energies[band_y]) * 0.4
            
            value += math.sin(x * 12 + t * 2) * audio_turbulence * 0.2
            value += math.cos(y * 10 + t * 1.5) * audio_turbulence * 0.2
            
            return (math.sin(value) + 1) / 2

        colors = None
        if self.has_color:
            colors = [self.Fore.BLUE, self.Fore.CYAN, self.Fore.GREEN, 
                     self.Fore.YELLOW, self.Fore.RED, self.Fore.MAGENTA]

        screen = []
        for y in range(h):
            row = []
            for x in range(w):
                # Normalize coordinates with audio-influenced scaling
                nx = (x / w - 0.5) * (4 + avg_energy * 2)
                ny = (y / h - 0.5) * (3 + avg_energy * 1.5)
                
                # Get plasma value
                p_val = plasma(nx, ny, self.time)
                
                # Add spiral vortex effect
                angle = math.atan2(ny, nx) + self.time
                radius = math.hypot(nx, ny)
                spiral = (math.sin(radius * 8 - angle * 3 + self.time) + 1) / 2
                
                # Combine plasma with spiral and audio
                band_idx = int((angle / (2 * math.pi)) * len(norm_energies)) % len(norm_energies)
                combined = (p_val * 0.6 + spiral * 0.2 + norm_energies[band_idx] * 0.2)
                
                # Pulsing effect from bass frequencies
                bass_energy = sum(norm_energies[:len(norm_energies)//4]) / max(1, len(norm_energies)//4)
                pulse = math.sin(self.time * 3 + x * 0.2) * 0.1 * bass_energy
                final_intensity = min(1.0, max(0.0, combined + pulse))
                
                char_idx = min(int(final_intensity * (len(chars) - 1)), len(chars) - 1)
                ch = chars[char_idx]

                if colors and self.has_color:
                    # Dynamic color cycling based on position and time
                    hue = (p_val + self.time * 0.2 + x * 0.05) % 1.0
                    color_idx = int(hue * (len(colors) - 1))
                    row.append(colors[color_idx] + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen