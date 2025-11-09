from .base import BaseSkin
import math

class HarmonicFieldSkin(BaseSkin):
    name = "harmonicfield"

    def __init__(self, bar_height, num_bands):
        super().__init__(bar_height, num_bands)
        try:
            from colorama import Fore, Style, Back
            self.has_color = True
            self.Fore = Fore
            self.Style = Style
            self.Back = Back
        except ImportError:
            self.has_color = False
        self.time = 0
        self.phase_history = []

    def render(self, norm_energies):
        w = self.num_bands
        h = self.bar_height
        if w <= 0 or h <= 0:
            return []

        chars = " ░▒▓█"
        self.time += 0.06
        
        # Spectral analysis
        spectral_centroid = sum(i * energy for i, energy in enumerate(norm_energies)) / sum(norm_energies) if sum(norm_energies) > 0 else 0
        brightness = sum(norm_energies[len(norm_energies)//2:]) / max(1, len(norm_energies)//2)
        warmth = sum(norm_energies[:len(norm_energies)//3]) / max(1, len(norm_energies)//3)
        
        colors = None
        if self.has_color:
            # Color meaning: Warmth=Red/Orange, Brightness=Cyan/Blue, Complexity=Purple, Richness=White
            colors = {
                'warm': [self.Fore.RED, self.Fore.YELLOW, self.Fore.MAGENTA],
                'bright': [self.Fore.CYAN, self.Fore.BLUE, self.Fore.WHITE],
                'complex': [self.Fore.MAGENTA, self.Fore.GREEN, self.Fore.CYAN],
                'rich': [self.Fore.WHITE, self.Fore.YELLOW, self.Fore.CYAN]
            }

        screen = []
        for y in range(h):
            row = []
            for x in range(w):
                # 3D spherical coordinates
                nx = (x / w - 0.5) * 2.0
                ny = (y / h - 0.5) * 1.5
                
                # Convert to spherical for 3D effect
                theta = math.atan2(ny, nx)
                phi = math.hypot(nx, ny) * math.pi
                r = math.hypot(nx, ny)
                
                # Harmonic series influenced by spectral centroid
                base_freq = 2.0 + spectral_centroid / len(norm_energies) * 8.0
                harmonics = 0.0
                
                # Generate harmonic overtones
                for overtone in range(1, 6):  # 5 harmonics
                    harmonic_gain = norm_energies[min(overtone * 2, len(norm_energies)-1)]
                    phase = self.time * (0.5 + overtone * 0.3)
                    harmonics += (math.sin(theta * base_freq * overtone + phase) * 
                                math.cos(phi * base_freq * overtone * 0.7 + phase) * 
                                harmonic_gain / overtone)
                
                # Main carrier wave with audio modulation
                carrier = math.sin(theta * base_freq * 3 + self.time * 2) * math.cos(phi * base_freq * 2)
                
                # Combine with harmonics
                combined = (carrier * (0.6 + warmth * 0.3) + harmonics * (0.4 + brightness * 0.3))
                
                # Add amplitude modulation from bass
                am_depth = warmth * 0.5
                am_wave = (1.0 - am_depth) + am_depth * math.sin(self.time * 3 + r * 8)
                modulated = combined * am_wave
                
                # 3D depth effect - closer objects are brighter
                depth_factor = 1.0 / (1.0 + r * 2.0)
                final_intensity = (modulated + 1.0) / 2.0 * depth_factor
                final_intensity = min(1.0, final_intensity * (1.2 + brightness * 0.3))
                
                char_idx = min(int(final_intensity * (len(chars) - 1)), len(chars) - 1)
                ch = chars[char_idx]
                
                if colors and self.has_color:
                    # Determine sound quality for color selection
                    if warmth > 0.6 and brightness < 0.3:
                        palette = colors['warm']  # Warm, bass-heavy
                        color_idx = int((r + self.time) * 2) % len(palette)
                    elif brightness > 0.5 and warmth < 0.4:
                        palette = colors['bright']  # Bright, treble-heavy
                        color_idx = int((theta + self.time) * 3) % len(palette)
                    elif spectral_centroid > len(norm_energies) * 0.6 and len(set(norm_energies)) > 10:
                        palette = colors['complex']  # Complex, wide spectrum
                        color_idx = int((phi + self.time) * 2) % len(palette)
                    else:
                        palette = colors['rich']  # Balanced, rich sound
                        color_idx = int((r + theta + self.time) * 1.5) % len(palette)
                    
                    row.append(palette[color_idx] + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen