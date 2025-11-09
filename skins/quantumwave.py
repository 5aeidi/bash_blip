from .base import BaseSkin
import math

class QuantumWaveSkin(BaseSkin):
    name = "quantumwave"

    def __init__(self, bar_height, num_bands):
        super().__init__(bar_height, num_bands)
        try:
            from colorama import init, Fore, Style
            init(autoreset=True)
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

        chars = " ▁▂▃▄▅▆▇█"
        self.time += 0.1
        
        avg_energy = sum(norm_energies) / len(norm_energies)
        quantum_scale = 3.0 + avg_energy * 5.0
        
        colors = None
        if self.has_color:
            colors = [self.Fore.CYAN, self.Fore.BLUE, self.Fore.WHITE, self.Fore.MAGENTA]

        screen = []
        for y in range(h):
            row = []
            for x in range(w):
                # Multiple overlapping wave functions
                nx, ny = x / w, y / h
                
                # Wave function 1: Circular standing waves
                r = math.hypot(nx - 0.5, ny - 0.5) * quantum_scale
                wave1 = math.sin(r * 4 - self.time * 2) * math.exp(-r * 0.5)
                
                # Wave function 2: Interference pattern
                wave2 = (math.sin(nx * 8 - self.time) * math.sin(ny * 6 + self.time)) * 0.7
                
                # Wave function 3: Quantum noise
                band_idx = (x * y) % len(norm_energies)
                quantum_noise = norm_energies[band_idx] * math.sin(x * y * 0.1 + self.time)
                
                # Combine wave functions
                wave_sum = (wave1 + wave2 + quantum_noise) / 2.7
                probability = (math.sin(wave_sum * math.pi) + 1) / 2
                
                # "Collapse" the wave function based on audio intensity
                collapse_threshold = 0.3 + norm_energies[band_idx] * 0.4
                if probability > collapse_threshold:
                    intensity = (probability - collapse_threshold) / (1 - collapse_threshold)
                else:
                    intensity = 0
                
                char_idx = min(int(intensity * (len(chars) - 1)), len(chars) - 1)
                ch = chars[char_idx]
                
                if colors and self.has_color:
                    # Color based on wave phase and amplitude
                    phase = (wave_sum + 1) / 2
                    color_idx = int(phase * (len(colors) - 1))
                    row.append(colors[color_idx] + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen