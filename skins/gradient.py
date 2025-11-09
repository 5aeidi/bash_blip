from .base import BaseSkin
from colorama import Fore, Style
class GradientSkin(BaseSkin):
    name = "gradient"

    def __init__(self, bar_height, num_bands):
        super().__init__(bar_height, num_bands)
        try:

            self.has_colorama = True
            self.Fore = Fore
            self.Style = Style
        except ImportError:
            self.has_colorama = False

    def render(self, norm_energies):
        if not self.has_colorama:
            from .blocks import BlocksSkin
            return BlocksSkin(self.bar_height, self.num_bands).render(norm_energies)

        colors = [
            self.Fore.BLUE,
            self.Fore.CYAN,
            self.Fore.GREEN,
            self.Fore.YELLOW,
            self.Fore.RED,
        ]
        screen = []
        for row in range(self.bar_height):
            line = ""
            for h in norm_energies:
                if row >= (self.bar_height - int(h * self.bar_height)):
                    idx = min(int(h * len(colors)), len(colors) - 1)
                    line += colors[idx] + "█"
                else:
                    line += " "
            screen.append(line + self.Style.RESET_ALL)
        return screen