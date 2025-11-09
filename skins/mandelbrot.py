from .base import BaseSkin
from colorama import Fore, Style
import math

class MandelbrotSkin(BaseSkin):
    name = "mandelbrot"

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

        chars = " ·∙°○●◎◍◆◘@"
        self.time += 0.05
        
        avg_energy = sum(norm_energies) / len(norm_energies)
        
        # Audio-modulated fractal parameters
        zoom = 1.5 + math.sin(self.time * 0.5) * 0.3 + avg_energy * 0.5
        move_x = math.sin(self.time * 0.3) * 0.5 + avg_energy * 0.2
        move_y = math.cos(self.time * 0.2) * 0.3
        max_iter = 10 + int(avg_energy * 15)

        colors = None
        if self.has_color:
            colors = [self.Fore.BLUE, self.Fore.CYAN, self.Fore.GREEN, 
                     self.Fore.YELLOW, self.Fore.RED, self.Fore.MAGENTA]

        screen = []
        for y in range(h):
            row = []
            for x in range(w):
                # Convert pixel to complex plane coordinates
                zx = 1.5 * (x - w / 2) / (0.5 * zoom * w) + move_x
                zy = (y - h / 2) / (0.5 * zoom * h) + move_y
                
                # Audio influence on initial point
                band_x = int((zx + 2) / 4 * len(norm_energies)) % len(norm_energies)
                band_y = int((zy + 2) / 4 * len(norm_energies)) % len(norm_energies)
                audio_influence = (norm_energies[band_x] + norm_energies[band_y]) * 0.1
                
                cx = zx + audio_influence * math.sin(self.time)
                cy = zy + audio_influence * math.cos(self.time)
                
                # Modified Mandelbrot iteration
                zx, zy = 0, 0
                iter_count = 0
                while zx * zx + zy * zy < 4 and iter_count < max_iter:
                    tmp = zx * zx - zy * zy + cx
                    zy = 2 * zx * zy + cy + audio_influence * 0.1
                    zx = tmp
                    iter_count += 1

                # Map iteration count to character
                intensity = iter_count / max_iter
                char_idx = min(int(intensity * (len(chars) - 1)), len(chars) - 1)
                ch = chars[char_idx]

                if colors and self.has_color:
                    color_idx = int((iter_count + self.time * 5) * 0.5) % len(colors)
                    row.append(colors[color_idx] + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen