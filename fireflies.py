"""An endless, gently moving field of fireflies."""

from collections import deque
import math
import random

from orange_theme import ACCENT, COPPER, DIM, GOLD, LIGHT, PALE, RUST, fg
from terminal import animate, color_row


class FireflyField:
    def __init__(self):
        self.random = random.Random()
        self.size = None
        self.fireflies = []
        self.stars = []
        self.last_time = None

    def reset(self, width, height):
        self.size = width, height
        self.last_time = None
        self.stars = [(self.random.randrange(width), self.random.randrange(max(1, height // 2)),
                       self.random.random() * math.tau) for _ in range(max(5, width // 7))]
        self.fireflies = []
        for _ in range(max(10, width // 4)):
            self.fireflies.append({
                "x": self.random.uniform(1, width - 2),
                "y": self.random.uniform(height * .25, height * .81),
                "vx": self.random.uniform(-3.2, 3.2),
                "vy": self.random.uniform(-.8, .8),
                "phase": self.random.random() * math.tau,
                "hue": self.random.choice(("gold", "ember", "peach")),
                "trail": deque(maxlen=5),
            })

    def render(self, t, width, height, color):
        if self.size != (width, height):
            self.reset(width, height)
        dt = 0 if self.last_time is None else max(0, min(.15, t - self.last_time))
        self.last_time = t
        rng = self.random
        canvas = [[(" ", None) for _ in range(width)] for _ in range(height)]

        def put(x, y, char, shade):
            x, y = round(x), round(y)
            if 0 <= x < width and 0 <= y < height:
                canvas[y][x] = char, shade

        # A quiet sky and grass keep the moving lights easy to see.
        for x, y, phase in self.stars:
            brightness = math.sin(t * 1.5 + phase)
            put(x, y, "✧" if brightness > .7 else ".", fg(COPPER) if brightness > .7 else fg(DIM))
        put(width * .82, height * .12, "☾", fg(PALE))
        grass_top = max(1, height - 3)
        for x in range(width):
            wave = math.sin(x * .41 + t * .7)
            if x % 3 == 0:
                put(x, grass_top + (wave < 0), "╱" if wave > 0 else "╲", fg(RUST))
            put(x, height - 1, "▄", fg(DIM) if x % 4 else fg(RUST))
            if x % 17 == 7 and height >= 9:
                put(x, height - 2, "│", fg(RUST))
                put(x, height - 3, "✿", fg(ACCENT))

        for bug in self.fireflies:
            bug["vx"] = max(-4.0, min(4.0, bug["vx"] + rng.uniform(-2, 2) * dt))
            bug["vy"] = max(-1.5, min(1.5, bug["vy"] + rng.uniform(-1.2, 1.2) * dt))
            bug["x"] += bug["vx"] * dt
            bug["y"] += (bug["vy"] + .35 * math.sin(t * 1.4 + bug["phase"])) * dt
            if bug["x"] < 1 or bug["x"] > width - 2:
                bug["vx"] *= -1
                bug["x"] = max(1, min(width - 2, bug["x"]))
            if bug["y"] < height * .19 or bug["y"] > height - 4:
                bug["vy"] *= -1
                bug["y"] = max(height * .19, min(height - 4, bug["y"]))
            bug["trail"].append((bug["x"], bug["y"]))
            dim = fg({"gold": DIM, "ember": RUST, "peach": COPPER}[bug["hue"]])
            bright = fg({"gold": GOLD, "ember": ACCENT, "peach": LIGHT}[bug["hue"]])
            for x, y in list(bug["trail"])[:-1]:
                put(x, y, "·", dim)
            pulse = math.sin(t * 3 + bug["phase"])
            if pulse > -.3:
                put(bug["x"] - 1, bug["y"], "·", dim)
                put(bug["x"] + 1, bug["y"], "·", dim)
            put(bug["x"], bug["y"], "✦" if pulse > .55 else "•", bright)

        return "\n".join(color_row(row, color) for row in canvas)


render = FireflyField().render


if __name__ == "__main__":
    animate("Fireflies over a meadow", render, default_fps=15, continuous=True)
