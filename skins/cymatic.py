from .base import BaseSkin
import math

class CymaticSkin(BaseSkin):
    name = "cymatic"

    def __init__(self, bar_height, num_bands):
        super().__init__(bar_height, num_bands)
        try:
            from colorama import init, Fore, Style, Back
            init(autoreset=True)
            self.has_color = True
            self.Fore = Fore
            self.Style = Style
            self.Back = Back
        except ImportError:
            self.has_color = False
        self.time = 0
        self.sand_memory = []  # Store previous frames for persistence

    def render(self, norm_energies):
        w = self.num_bands
        h = self.bar_height
        if w <= 0 or h <= 0:
            return []

        chars = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
        self.time += 0.05
        
        # Analyze frequency characteristics
        bass = sum(norm_energies[:len(norm_energies)//4]) / max(1, len(norm_energies)//4)
        mids = sum(norm_energies[len(norm_energies)//4:3*len(norm_energies)//4]) / max(1, len(norm_energies)//2)
        highs = sum(norm_energies[3*len(norm_energies)//4:]) / max(1, len(norm_energies)//4)
        avg_energy = (bass + mids + highs) / 3

        # Initialize sand canvas with persistence
        if not self.sand_memory:
            self.sand_memory = [[0.0 for _ in range(w)] for _ in range(h)]
        
        colors = None
        if self.has_color:
            # Color meaning: Bass=Red, Mids=Green, Highs=Blue, Mixed=White/Yellow
            colors = {
                'bass': self.Fore.RED + self.Back.BLACK,
                'mids': self.Fore.GREEN + self.Back.BLACK, 
                'highs': self.Fore.BLUE + self.Back.BLACK,
                'full': self.Fore.YELLOW + self.Back.BLACK,
                'rich': self.Fore.WHITE + self.Back.BLACK
            }

        screen = []
        new_sand = [[0.0 for _ in range(w)] for _ in range(h)]
        
        for y in range(h):
            row = []
            for x in range(w):
                # Normalize coordinates to 3D space
                nx = (x / w - 0.5) * 4.0
                ny = (y / h - 0.5) * 3.0
                
                # Multiple resonant frequencies (like Chladni plates)
                freq1 = 3.0 + bass * 5.0  # Bass controls base frequency
                freq2 = 7.0 + mids * 8.0   # Mids control complexity
                freq3 = 12.0 + highs * 15.0 # Highs add fine details
                
                # Standing wave patterns
                wave1 = math.sin(nx * freq1 + self.time) * math.cos(ny * freq1)
                wave2 = math.sin(nx * freq2 * 1.3) * math.cos(ny * freq2 * 0.7 + self.time * 1.5)
                wave3 = math.sin((nx + ny) * freq3 + self.time * 2) * math.cos((nx - ny) * freq3)
                
                # Combine waves with audio modulation
                combined_wave = (wave1 * (0.4 + bass * 0.3) + 
                               wave2 * (0.3 + mids * 0.2) + 
                               wave3 * (0.2 + highs * 0.1))
                
                # Add circular nodal patterns
                radius = math.hypot(nx, ny)
                circular_wave = math.sin(radius * (8.0 + avg_energy * 6.0) - self.time * 2)
                final_wave = (combined_wave + circular_wave * 0.4) / 1.4
                
                # Sand-like persistence (accumulate and fade)
                persistence = 0.7
                new_value = abs(final_wave) * (0.8 + avg_energy * 0.4)
                sand_value = max(new_value, self.sand_memory[y][x] * persistence)
                new_sand[y][x] = sand_value
                
                # Convert to character with depth perception
                depth_intensity = sand_value * (0.9 + 0.3 * math.sin(radius * 2))
                char_idx = min(int(depth_intensity * (len(chars) - 1)), len(chars) - 1)
                ch = chars[char_idx]
                
                if colors and self.has_color:
                    # Color coding based on frequency dominance and intensity
                    if bass > 0.6 and sand_value > 0.5:
                        color = colors['bass']  # Strong bass = Red
                    elif mids > 0.5 and sand_value > 0.4:
                        color = colors['mids']  # Prominent mids = Green
                    elif highs > 0.4 and sand_value > 0.3:
                        color = colors['highs'] # Crisp highs = Blue
                    elif bass > 0.4 and mids > 0.4 and highs > 0.3:
                        color = colors['rich']  # Full spectrum = White
                    else:
                        color = colors['full']  # Mixed frequencies = Yellow
                    
                    row.append(color + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        
        self.sand_memory = new_sand
        return screen