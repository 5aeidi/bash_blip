from .base import BaseSkin

class SpectrumRainSkin(BaseSkin):
    name = "spectrumrain"

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

    def render(self, norm_energies):
        w = self.num_bands
        h = self.bar_height
        if w <= 0 or h <= 0:
            return []

        n = len(norm_energies) if hasattr(norm_energies, '__len__') else 0
        if n == 0:
            norm_energies = [0.0] * w
            n = w

        # Map frequency index to hue: low (red) → high (magenta)
        rainbow = [
            self.Fore.RED,
            self.Fore.YELLOW,
            self.Fore.GREEN,
            self.Fore.CYAN,
            self.Fore.BLUE,
            self.Fore.MAGENTA
        ] if self.has_color else None

        # Character intensity levels
        levels = " ▏▎▍▌▋▊▉█"

        screen = [[' '] * w for _ in range(h)]

        for x in range(w):
            band_idx = min(x * n // w, n - 1)
            energy = norm_energies[band_idx]

            if energy <= 0.01:
                continue

            # How many rows to light up (from bottom)
            filled_rows = max(1, int(energy * h))

            # Choose color based on frequency position (not amplitude)
            if rainbow:
                hue_pos = band_idx / max(1, n - 1)  # 0.0 → 1.0
                color_idx = int(hue_pos * (len(rainbow) - 1))
                color = rainbow[color_idx]

            # Draw from bottom up
            for y in range(filled_rows):
                row = h - 1 - y
                if row < 0:
                    break
                char_idx = min(int(energy * len(levels)), len(levels) - 1)
                ch = levels[char_idx]
                if rainbow:
                    screen[row][x] = color + ch + self.Style.RESET_ALL
                else:
                    screen[row][x] = ch

        return [''.join(row) for row in screen]