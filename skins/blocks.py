from .base import BaseSkin

class BlocksSkin(BaseSkin):
    name = "blocks"

    def render(self, norm_energies):
        screen = []
        for row in range(self.bar_height):
            line = ''.join(
                "█" if row >= (self.bar_height - int(h * self.bar_height)) else " "
                for h in norm_energies
            )
            screen.append(line)
        return screen