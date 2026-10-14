"""Endless rain, splashes and ripples over a pond."""

import math
import random

from orange_theme import ACCENT, COPPER, DARK, DIM, LIGHT, PALE, RUST, fg
from terminal import animate, color_row


class RainyPond:
    def __init__(self):
        self.random = random.Random()
        self.size = None
        self.drops = []
        self.ripples = []
        self.last_time = None
        self.spawn_credit = 0
        self.next_lightning = 0
        self.flash_until = 0
        self.lightning_x = 0

    def reset(self, width, height):
        self.size = width, height
        self.last_time = None
        self.spawn_credit = 0
        self.ripples = []
        self.drops = [{"x": self.random.uniform(0, width - 1),
                       "y": self.random.uniform(2, max(3, height - 5)),
                       "speed": self.random.uniform(9, 17)}
                      for _ in range(max(8, width // 3))]
        self.next_lightning = self.random.uniform(7, 13)
        self.flash_until = 0

    def render(self, t, width, height, color):
        if self.size != (width, height):
            self.reset(width, height)
        dt = 0 if self.last_time is None else max(0, min(.15, t - self.last_time))
        self.last_time = t
        rng = self.random
        waterline = max(2, height - 4)
        self.spawn_credit += width * .52 * dt
        while self.spawn_credit >= 1:
            self.drops.append({"x": rng.uniform(0, width - 1), "y": 2,
                               "speed": rng.uniform(9, 17)})
            self.spawn_credit -= 1

        canvas = [[(" ", None) for _ in range(width)] for _ in range(height)]

        def put(x, y, char, shade):
            x, y = round(x), round(y)
            if 0 <= x < width and 0 <= y < height:
                canvas[y][x] = char, shade

        for y in range(min(3, height)):
            for x in range(width):
                shape = math.sin(x * .17 + t * .17) + math.sin(x * .071 - t * .11)
                if shape + y * .36 > -.35:
                    put(x, y, "░" if y == 2 else "▒", fg(DIM))
        for x in range(width):
            if x % 2 == 0:
                put(x, waterline + 1, "~", fg(COPPER))
            for y in range(waterline + 2, height):
                put(x, y, "█", fg(DIM) if y == waterline + 2 else fg(DARK))

        active_drops = []
        wind = math.sin(t * .55) * 1.4
        for drop in self.drops:
            drop["x"] += wind * dt
            drop["y"] += drop["speed"] * dt
            if drop["y"] >= waterline:
                if rng.random() < .28:
                    self.ripples.append({"x": drop["x"], "age": 0})
                continue
            active_drops.append(drop)
            put(drop["x"], drop["y"] - 1, "·", fg(RUST))
            put(drop["x"], drop["y"], "│", fg(ACCENT))
        self.drops = active_drops

        active_ripples = []
        for ripple in self.ripples:
            ripple["age"] += dt
            if ripple["age"] > 1.25:
                continue
            active_ripples.append(ripple)
            radius = min(5, round(ripple["age"] * 4))
            x = ripple["x"]
            if radius == 0:
                put(x, waterline, "✧", fg(LIGHT))
            else:
                put(x - radius, waterline + 1, "(", fg(ACCENT))
                put(x + radius, waterline + 1, ")", fg(ACCENT))
                if radius > 2:
                    put(x, waterline + 1, "·", fg(RUST))
        self.ripples = active_ripples

        if t >= self.next_lightning:
            self.flash_until = t + .18
            self.lightning_x = rng.randrange(max(1, width // 5), max(2, width * 4 // 5))
            self.next_lightning = t + rng.uniform(7, 13)
        if t < self.flash_until:
            x = self.lightning_x
            for y in range(2, waterline - 1):
                x += -1 if y % 3 == 0 else 1 if y % 3 == 2 else 0
                put(x, y, "╲" if y % 2 else "╱", fg(PALE))

        return "\n".join(color_row(row, color) for row in canvas)


render = RainyPond().render


if __name__ == "__main__":
    animate("Rain falling into a pond", render, default_fps=15, continuous=True)
