from .base import BaseSkin
from colorama import Fore, Style
class SparklineSkin(BaseSkin):
    name = "sparkline"

    def render(self, norm_energies):
        """Render a single middle-row sparkline using unicode low-high blocks.

        Other rows are left empty so the visualization appears as a thin
        horizontal sparkline across the terminal.
        """
        levels = "▁▂▃▄▅▆▇█"
        nlevels = len(levels)
        mid = self.bar_height // 2
        screen = []
        for row in range(self.bar_height):
            if row != mid:
                screen.append(''.join(' ' for _ in norm_energies))
            else:
                line = ''.join(
                    levels[min(int(h * nlevels), nlevels - 1)] for h in norm_energies
                )
                screen.append(line)
        return screen
