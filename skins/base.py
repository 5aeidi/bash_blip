class BaseSkin:
    name = "base"

    def __init__(self, bar_height, num_bands):
        self.bar_height = bar_height
        self.num_bands = num_bands

    def render(self, norm_energies):
        raise NotImplementedError