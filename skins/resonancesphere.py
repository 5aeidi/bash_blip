from .base import BaseSkin
import math
import numpy as np

class ResonanceSphereSkin(BaseSkin):
    name = "resonancesphere"

    def __init__(self, bar_height, num_bands):
        super().__init__(bar_height, num_bands)
        try:
            from colorama import Fore, Style, Back
            # init(autoreset=True)
            self.has_color = True
            self.Fore = Fore
            self.Style = Style
            self.Back = Back
        except ImportError:
            self.has_color = False
        self.time = 0
        self.resonance_buffer = []

    def render(self, norm_energies):
        w = self.num_bands
        h = self.bar_height
        if w <= 0 or h <= 0:
            return []

        # chars = " ·∙°○●◎◍◆◘@#"
        chars = " ·∙*○●+◍◆◘@#"

        self.time += 0.04
        
        if hasattr(norm_energies, 'size'):
            # It's a numpy array
            if norm_energies.size == 0:
                dynamic_range = 0
                spectral_spread = 0
                peak_energy = 0
            else:
                dynamic_range = np.max(norm_energies) - np.min(norm_energies)
                mean_energy = np.mean(norm_energies)
                spectral_spread = np.mean(np.abs(norm_energies - mean_energy))
                peak_energy = np.max(norm_energies)
        else:
            # It's a regular list
            if len(norm_energies) == 0:
                dynamic_range = 0
                spectral_spread = 0
                peak_energy = 0
            else:
                dynamic_range = max(norm_energies) - min(norm_energies)
                mean_energy = sum(norm_energies) / len(norm_energies)
                spectral_spread = sum(abs(e - mean_energy) for e in norm_energies) / len(norm_energies)
                peak_energy = max(norm_energies)

        colors = None
        if self.has_color:
            # Color semantics: 
            # - Dynamic=Red/Orange (energy variation)
            # - Dense=Blue/Purple (spectral density)  
            # - Pure=Green/Cyan (focused frequencies)
            # - Complex=White/Yellow (rich harmonics)
            colors = {
                'dynamic': [self.Fore.RED, self.Fore.YELLOW, self.Fore.MAGENTA],
                'dense': [self.Fore.BLUE, self.Fore.CYAN, self.Fore.MAGENTA],
                'pure': [self.Fore.GREEN, self.Fore.CYAN, self.Fore.WHITE],
                'complex': [self.Fore.WHITE, self.Fore.YELLOW, self.Fore.GREEN]
            }

        screen = []
        for y in range(h):
            row = []
            for x in range(w):
                # Project 3D sphere onto 2D screen
                nx = (x / w - 0.5) * 2.0
                ny = (y / h - 0.5) * 2.0
                
                # Check if point is inside sphere
                r_squared = nx*nx + ny*ny
                if r_squared > 1.0:
                    row.append(' ')
                    continue
                
                # Calculate 3D position on sphere surface
                z = math.sqrt(1.0 - r_squared)  # Depth
                r = math.sqrt(r_squared)
                
                # Spherical coordinates
                theta = math.atan2(ny, nx)
                phi = math.asin(r) if r > 0 else 0
                
                # Multiple resonant modes on sphere surface
                resonance = 0.0
                modes = [
                    (0, 0, 1.0),  # Fundamental
                    (1, 0, 0.8),  # Dipole
                    (2, 0, 0.6),  # Quadrupole
                    (2, 1, 0.5),  # Higher modes
                    (3, 0, 0.4),
                    (3, 1, 0.3)
                ]
                
                for l, m, weight in modes:
                    # Spherical harmonics simplified
                    if l == 0:  # Fundamental
                        mode_val = 1.0
                    elif l == 1 and m == 0:  # Z-dipole
                        mode_val = z
                    elif l == 2 and m == 0:  # Z^2 quadrupole
                        mode_val = 3*z*z - 1
                    elif l == 2 and m == 1:  # XZ
                        mode_val = nx * z
                    elif l == 3 and m == 0:  # Higher
                        mode_val = 5*z*z*z - 3*z
                    elif l == 3 and m == 1:  # Higher
                        mode_val = nx * (5*z*z - 1)
                    else:
                        mode_val = math.sin(l * theta) * math.cos(m * phi)
                    
                    # FIXED: Safe band index calculation
                    band_idx = min(l * 2 + m, len(norm_energies) - 1)
                    # FIXED: Safe array access
                    if len(norm_energies) > 0:
                        audio_amp = norm_energies[band_idx] if band_idx < len(norm_energies) else 0.5
                    else:
                        audio_amp = 0.5
                    phase = self.time * (1.0 + l * 0.5 + m * 0.3)
                    
                    resonance += mode_val * weight * audio_amp * math.sin(phase)
                
                # Add radial standing waves
                radial_waves = math.sin(r * (8.0 + peak_energy * 10.0) - self.time * 3) * (1.0 - r)
                
                combined = (resonance * 0.7 + radial_waves * 0.3) * (1.0 + dynamic_range * 0.5)
                
                # 3D lighting effect based on surface normal
                light_dir = [0.3, 0.5, 1.0]  # Direction to light
                light_len = math.sqrt(sum(c*c for c in light_dir))
                normal = [nx, ny, z]
                normal_len = math.sqrt(sum(c*c for c in normal))
                
                if normal_len > 0 and light_len > 0:
                    dot_product = sum(n*c for n, c in zip(normal, light_dir)) / (normal_len * light_len)
                    lighting = max(0.3, (dot_product + 1.0) / 2.0)
                else:
                    lighting = 0.7
                
                final_intensity = abs(combined) * lighting
                final_intensity = min(1.0, final_intensity * (1.0 + spectral_spread * 0.8))
                
                char_idx = min(int(final_intensity * (len(chars) - 1)), len(chars) - 1)
                ch = chars[char_idx]
                
                if colors and self.has_color:
                    # Color based on sound characteristics
                    if dynamic_range > 0.3:
                        palette = colors['dynamic']  # High dynamic range
                        color_idx = int((theta + self.time * 2) * 2) % len(palette)
                    elif spectral_spread < 0.2:
                        palette = colors['pure']  # Focused frequencies
                        color_idx = int((phi + self.time) * 3) % len(palette)
                    elif peak_energy > 0.7 and len(norm_energies) > 0:
                        # FIXED: Count energies above threshold safely
                        high_energies = sum(1 for e in norm_energies if e > 0.3)
                        if high_energies > 5:
                            palette = colors['complex']  # Complex sound
                            color_idx = int((r + self.time * 1.5) * 2) % len(palette)
                        else:
                            palette = colors['dense']  # Dense spectrum
                            color_idx = int((theta + phi + self.time) * 2) % len(palette)
                    else:
                        palette = colors['dense']  # Dense spectrum
                        color_idx = int((theta + phi + self.time) * 2) % len(palette)
                    
                    row.append(palette[color_idx] + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen