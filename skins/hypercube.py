from .base import BaseSkin
from colorama import Fore, Style
import math

class HypercubeSkin(BaseSkin):
    name = "hypercube"

    def __init__(self, bar_height, num_bands):
        super().__init__(bar_height, num_bands)
        try:

            self.has_color = True
            self.Fore = Fore
            self.Style = Style
        except ImportError:
            self.has_color = False
        self.t = 0.0

    def render(self, norm_energies):
        w, h = self.num_bands, self.bar_height
        if w <= 0 or h <= 0:
            return []

        n = len(norm_energies) if hasattr(norm_energies, '__len__') else 0
        avg = sum(norm_energies) / n if n > 0 else 0.0

        # Update time based on audio activity
        self.t += 0.02 + avg * 0.05

        # Define 4D hypercube vertices (16 points: all combinations of ±1 in 4D)
        vertices_4d = []
        for i in range(16):
            coords = [1 if (i >> j) & 1 else -1 for j in range(4)]
            vertices_4d.append(coords)

        # Rotation matrices in XY, XZ, XW, YZ, YW, ZW planes
        def rotate_4d(v, t):
            x, y, z, w = v
            # Apply multiple planar rotations
            c1, s1 = math.cos(t), math.sin(t)
            c2, s2 = math.cos(t * 0.7), math.sin(t * 0.7)
            c3, s3 = math.cos(t * 1.3), math.sin(t * 1.3)

            # XY rotation
            x, y = x * c1 - y * s1, x * s1 + y * c1
            # ZW rotation
            z, w = z * c2 - w * s2, z * s2 + w * c2
            # XZ rotation
            x, z = x * c3 - z * s3, x * s3 + z * c3
            return [x, y, z, w]

        # Project 4D → 3D → 2D (perspective)
        projected = []
        for v in vertices_4d:
            v = rotate_4d(v, self.t)
            # 4D → 3D (drop W with perspective)
            factor = 2.0 / (2.5 - v[3])
            x3 = v[0] * factor
            y3 = v[1] * factor
            z3 = v[2] * factor
            # 3D → 2D (isometric-like)
            x2 = x3 - z3 * 0.5
            y2 = y3 - z3 * 0.3
            projected.append((x2, y2))

        # Normalize to screen
        xs = [p[0] for p in projected]
        ys = [p[1] for p in projected]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        range_x = max(0.1, max_x - min_x)
        range_y = max(0.1, max_y - min_y)

        screen_points = set()
        for i, (x, y) in enumerate(projected):
            nx = (x - min_x) / range_x
            ny = (y - min_y) / range_y
            px = int(nx * (w - 1))
            py = int(ny * (h - 1))
            if 0 <= px < w and 0 <= py < h:
                screen_points.add((px, py, i))

        # Build screen
        grid = [[" "] * w for _ in range(h)]
        chars = ".:+=*#%@"
        colors = [self.Fore.MAGENTA, self.Fore.BLUE, self.Fore.CYAN] if self.has_color else None

        for px, py, idx in screen_points:
            energy = norm_energies[idx % n] if n > 0 else avg
            char_idx = min(int(energy * len(chars)), len(chars) - 1)
            ch = chars[char_idx]
            if colors:
                color = colors[idx % len(colors)]
                grid[py][px] = color + ch + self.Style.RESET_ALL
            else:
                grid[py][px] = ch

        return [''.join(row) for row in grid]