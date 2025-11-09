from .base import BaseSkin
import math

class WaveformCanvasSkin(BaseSkin):
    name = "waveformcanvas"

    def __init__(self, bar_height, num_bands):
        super().__init__(bar_height, num_bands)
        try:
            from colorama import init, Fore, Back, Style
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

        # Resample energies to match width
        sampled = []
        for x in range(w):
            idx = int(x * n / w)
            sampled.append(norm_energies[min(idx, n - 1)])

        # Character set for smooth vertical resolution
        chars = " _‾¯ "  # includes space for quiet regions

        # Precompute vertical center
        mid = h // 2

        # Build empty frame
        screen = [[' '] * w for _ in range(h)]

        for x in range(w):
            amp = sampled[x]
            if amp < 0.02:
                continue  # silence

            # Map amplitude to vertical displacement
            height = int(amp * (h // 2))
            char_idx = min(int(amp * (len(chars) - 1)), len(chars) - 1)
            ch = chars[char_idx]

            # Color: blue → cyan → yellow → red
            if self.has_color:
                hue = min(1.0, amp * 1.5)
                if hue < 0.33:
                    color = self.Fore.BLUE
                elif hue < 0.66:
                    color = self.Fore.CYAN
                elif hue < 1.0:
                    color = self.Fore.YELLOW
                else:
                    color = self.Fore.RED
                ch = color + ch + self.Style.RESET_ALL

            # Draw at center ± height
            y_top = max(0, mid - height)
            y_bottom = min(h - 1, mid + height)
            screen[y_top][x] = ch
            if y_bottom != y_top:
                screen[y_bottom][x] = ch

            # Optional: fill center for stronger signals
            if amp > 0.5:
                for y in range(y_top + 1, y_bottom):
                    screen[y][x] = ch if not self.has_color else color + "▄" + self.Style.RESET_ALL

        return [''.join(row) for row in screen]