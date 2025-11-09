from .base import BaseSkin
import math

class FractalLatticeSkin(BaseSkin):
    name = "fractallattice"

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
        self.iteration = 0

    def _sierpinski(self, x, y, depth, energy):
        if depth == 0:
            return 1
        step = 2 ** depth
        if (x // step) % 2 == 1 and (y // step) % 2 == 1:
            return 0
        return self._sierpinski(x, y, depth - 1, energy)

    def render(self, norm_energies):
        w, h = self.num_bands, self.bar_height
        if w <= 0 or h <= 0:
            return []

        n = len(norm_energies) if hasattr(norm_energies, '__len__') else 0
        if n == 0:
            norm_energies = [0.0] * w
            n = w

        # Dynamic recursion depth based on avg energy
        avg = sum(norm_energies) / n if n > 0 else 0.0
        max_depth = max(1, min(5, int(avg * 4) + 1))

        chars = " ▄▀█"
        colors = [self.Fore.BLUE, self.Fore.CYAN, self.Fore.WHITE] if self.has_color else None

        screen = []
        for y in range(h):
            row = []
            for x in range(w):
                band = x % n
                energy = norm_energies[band]
                # Modulate fractal presence by local energy
                if energy < 0.1:
                    ch = " "
                else:
                    val = self._sierpinski(x, y, max_depth, energy)
                    idx = int(val * (len(chars) - 1))
                    ch = chars[idx]

                if colors:
                    color = colors[(x + y + int(energy * 10)) % len(colors)]
                    row.append(color + ch + self.Style.RESET_ALL)
                else:
                    row.append(ch)
            screen.append(''.join(row))
        return screen