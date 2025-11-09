from .base import BaseSkin
from colorama import Fore, Style
class RainbowSkin(BaseSkin):
    name = "rainbow"

    def __init__(self, bar_height, num_bands):
        super().__init__(bar_height, num_bands)
        try:

            self.has_color = True
            self.Fore = Fore
            self.Style = Style
        except ImportError:
            self.has_color = False

    def render(self, norm_energies):
        if not self.has_color:
            from .blocks import BlocksSkin
            return BlocksSkin(self.bar_height, self.num_bands).render(norm_energies)

        # rainbow colors left-to-right
        rainbow = [
            self.Fore.RED,
            self.Fore.MAGENTA,
            self.Fore.YELLOW,
            self.Fore.GREEN,
            self.Fore.CYAN,
            self.Fore.BLUE,
        ]
        screen = []
        for row in range(self.bar_height):
            line = ""
            for i, h in enumerate(norm_energies):
                if row >= (self.bar_height - int(h * self.bar_height)):
                    color = rainbow[i % len(rainbow)]
                    line += color + "@"
                else:
                    line += " "
            line += self.Style.RESET_ALL
            screen.append(line)
        return screen
