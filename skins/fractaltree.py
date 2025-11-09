from .base import BaseSkin
import math
import random

class FractalTreeSkin(BaseSkin):
    name = "fractaltree"

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
        self.branch_memory = []

    def render(self, norm_energies):
        w = self.num_bands
        h = self.bar_height
        if w <= 0 or h <= 0:
            return []

        # Initialize canvas
        canvas = [[' ' for _ in range(w)] for _ in range(h)]
        
        avg_energy = sum(norm_energies) / len(norm_energies)
        self.time += 0.1 + avg_energy * 0.1
        
        # Tree parameters modulated by audio
        angle_variation = math.pi / 4 + avg_energy * math.pi / 8
        branch_factor = 0.7 + avg_energy * 0.2
        max_depth = 3 + int(avg_energy * 4)
        
        # Start tree from bottom center
        start_x, start_y = w // 2, h - 1
        start_length = min(h // 3, 6 + int(avg_energy * 4))
        
        # Recursive tree drawing function
        def draw_branch(x, y, angle, length, depth, energy_mod):
            if depth > max_depth or length < 1:
                return
                
            # Calculate end point
            end_x = int(x + math.sin(angle) * length)
            end_y = int(y - math.cos(angle) * length)
            
            # Draw line (simplified Bresenham)
            steps = max(abs(end_x - x), abs(end_y - y))
            if steps == 0:
                return
                
            for i in range(steps + 1):
                draw_x = int(x + (end_x - x) * i / steps)
                draw_y = int(y + (end_y - y) * i / steps)
                
                if 0 <= draw_x < w and 0 <= draw_y < h:
                    # Choose character based on depth and energy
                    chars = " |/\\*@#"[min(depth, 6)]
                    canvas[draw_y][draw_x] = chars
            
            # Audio-influenced recursion
            if depth < max_depth:
                left_energy = norm_energies[(draw_x + depth) % len(norm_energies)]
                right_energy = norm_energies[(draw_y + depth) % len(norm_energies)]
                
                # Recursive branches
                draw_branch(end_x, end_y, angle - angle_variation * (0.8 + left_energy * 0.4), 
                           length * branch_factor, depth + 1, left_energy)
                draw_branch(end_x, end_y, angle + angle_variation * (0.8 + right_energy * 0.4), 
                           length * branch_factor, depth + 1, right_energy)
                
                # Sometimes add a middle branch for denser trees
                if depth < 2 and avg_energy > 0.5:
                    middle_energy = norm_energies[(draw_x + draw_y) % len(norm_energies)]
                    draw_branch(end_x, end_y, angle, length * branch_factor * 0.8, 
                               depth + 1, middle_energy)

        # Draw the tree
        draw_branch(start_x, start_y, 0, start_length, 0, avg_energy)
        
        # Add falling "leaves" or particles based on high frequencies
        if avg_energy > 0.3:
            high_freq_energy = sum(norm_energies[-len(norm_energies)//4:]) / max(1, len(norm_energies)//4)
            num_particles = int(high_freq_energy * 10)
            
            for _ in range(num_particles):
                px = random.randint(0, w-1)
                py = random.randint(0, h//2)
                if 0 <= px < w and 0 <= py < h:
                    canvas[py][px] = random.choice("·•*◦")

        # Convert canvas to screen
        colors = None
        if self.has_color:
            colors = [self.Fore.GREEN, self.Fore.YELLOW, self.Fore.RED, 
                     self.Fore.MAGENTA, self.Fore.WHITE]
        
        screen = []
        for y, row_chars in enumerate(canvas):
            row = []
            for x, ch in enumerate(row_chars):
                if ch != ' ':
                    if colors and self.has_color:
                        # Color based on vertical position and energy
                        color_idx = int((y / h + self.time * 0.1) * len(colors)) % len(colors)
                        row.append(colors[color_idx] + ch + self.Style.RESET_ALL)
                    else:
                        row.append(ch)
                else:
                    row.append(' ')
            screen.append(''.join(row))
        return screen