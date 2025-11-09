from .base import BaseSkin

class FireSkin(BaseSkin):
    name = "fire"

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
        if not self.has_color:
            from .blocks import BlocksSkin
            return BlocksSkin(self.bar_height, self.num_bands).render(norm_energies)

        levels = " .,:;i!*#@"
        colors = [self.Fore.YELLOW, self.Fore.RED, self.Fore.MAGENTA]

        screen = []
        for row in range(self.bar_height):
            line = ""
            for h in norm_energies:
                # determine if this row should be filled for this band
                filled = row >= (self.bar_height - int(h * self.bar_height))
                if filled:
                    # pick a character by intensity
                    idx = min(int(h * len(levels)), len(levels) - 1)
                    ch = levels[idx]
                    # color based on vertical position (top->yellow, mid->red, bottom->magenta)
                    pos = row / max(1, (self.bar_height - 1))
                    color = colors[min(int(pos * len(colors)), len(colors) - 1)]
                    line += color + ch
                else:
                    line += " "
            line += self.Style.RESET_ALL
            screen.append(line)
        return screen
