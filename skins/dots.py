from .base import BaseSkin

class DotsSkin(BaseSkin):
    name = "dots"

    def render(self, norm_energies):
        screen = [" " * self.num_bands for _ in range(self.bar_height)]
        for col, h in enumerate(norm_energies):
            if h > 0:
                row = self.bar_height - int(h * self.bar_height)
                if row < self.bar_height:
                    lst = list(screen[row])
                    lst[col] = "●"
                    screen[row] = "".join(lst)
        return screen[::-1]