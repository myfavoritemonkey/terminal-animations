"""An endless little aquarium with swimming fish and rising bubbles."""

import math
import random

from orange_theme import ACCENT, COPPER, DIM, GOLD, LIGHT, PALE, RUST, fg_bg
from terminal import animate, color_row


class Aquarium:
    def __init__(self):
        self.random = random.Random()
        self.size = None
        self.fish = []
        self.bubbles = []
        self.last_time = None

    def reset(self, width, height):
        self.size = width, height
        self.last_time = None
        rng = self.random
        self.fish = [{
            "x": rng.uniform(0, max(0, width - 8)),
            "y": rng.uniform(2, max(2, height - 7)),
            "speed": rng.choice((-1, 1)) * rng.uniform(2.4, 5.0),
            "phase": rng.random() * math.tau,
            "color": rng.choice((ACCENT, GOLD, LIGHT, COPPER)),
        } for _ in range(max(3, width // 18))]
        self.bubbles = [{
            "x": rng.uniform(1, width - 2),
            "y": rng.uniform(1, height - 2),
            "speed": rng.uniform(1.2, 3.3),
            "phase": rng.random() * math.tau,
        } for _ in range(max(7, width // 6))]

    def render(self, t, width, height, color):
        if self.size != (width, height):
            self.reset(width, height)
        dt = 0 if self.last_time is None else max(0, min(.15, t - self.last_time))
        self.last_time = t
        rng = self.random
        backgrounds = [(22 + int(y * 13 / height), 14 + int(y * 10 / height),
                        12 + int(y * 5 / height))
                       for y in range(height)]
        canvas = [[(" ", None) for _ in range(width)] for _ in range(height)]

        def put(x, y, char, rgb):
            x, y = round(x), round(y)
            if 0 <= x < width and 0 <= y < height:
                canvas[y][x] = char, rgb

        # Ripples, pebbles and swaying seaweed make a stable backdrop.
        for x in range(width):
            if (x + int(t * 2)) % 11 < 4:
                put(x, 0, "~", COPPER)
            put(x, height - 1, "▄" if x % 5 else "█", DIM if x % 3 else RUST)
            if x % 13 == 4:
                put(x, height - 2, "•", COPPER)
        for base in range(5, width, 12):
            length = min(height - 3, 4 + base % 4)
            for step in range(length):
                y = height - 2 - step
                x = base + round(math.sin(t * 1.2 + step * .6 + base) * step * .3)
                put(x, y, "╱" if x < base else "╲" if x > base else "│",
                    RUST if step < 3 else COPPER)
                if step in (2, 4):
                    put(x + 1, y, "╲", COPPER)
            put(base, height - 2, "✿", ACCENT)

        for bubble in self.bubbles:
            bubble["y"] -= bubble["speed"] * dt
            if bubble["y"] < 1:
                bubble["y"] = height - 3
                bubble["x"] = rng.uniform(1, width - 2)
            x = bubble["x"] + math.sin(t * 1.8 + bubble["phase"]) * .8
            put(x, bubble["y"], "○" if bubble["speed"] > 2 else "°", GOLD)

        for fish in self.fish:
            fish["x"] += fish["speed"] * dt
            right = fish["speed"] > 0
            sprite = "><(((°>" if right else "<°)))><"
            if right and fish["x"] > width:
                fish["x"] = -len(sprite)
                fish["y"] = rng.uniform(2, max(2, height - 7))
            elif not right and fish["x"] < -len(sprite):
                fish["x"] = width
                fish["y"] = rng.uniform(2, max(2, height - 7))
            y = fish["y"] + math.sin(t * 1.4 + fish["phase"]) * .6
            for offset, char in enumerate(sprite):
                put(fish["x"] + offset, y, char,
                    PALE if char == "°" else fish["color"])

        rows = []
        for y, row in enumerate(canvas):
            bg = backgrounds[y]
            cells = [(char, fg_bg(foreground or RUST, bg))
                     for char, foreground in row]
            rows.append(color_row(cells, color))
        return "\n".join(rows)


render = Aquarium().render


if __name__ == "__main__":
    animate("Swimming fish in an aquarium", render, default_fps=15, continuous=True)
