"""An endless sky of procedurally launched fireworks."""

import math
import random

from orange_theme import ACCENT, COPPER, DARK, DIM, GOLD, LIGHT, PALE, RUST, fg
from terminal import animate, color_row


PALETTES = (
    (ACCENT, GOLD, PALE),
    (COPPER, ACCENT, LIGHT),
    (RUST, GOLD, PALE),
    (ACCENT, LIGHT, PALE),
)


class Fireworks:
    def __init__(self):
        self.random = random.Random()
        self.size = None
        self.rockets = []
        self.sparks = []
        self.stars = []
        self.next_launch = 0
        self.last_time = None

    def reset(self, width, height):
        self.size = width, height
        self.last_time = None
        self.next_launch = 0
        self.rockets = []
        self.sparks = []
        self.stars = [(self.random.randrange(width), self.random.randrange(max(1, height - 4)),
                       self.random.random() * math.tau) for _ in range(max(8, width // 6))]

    def launch(self, width, height):
        rng = self.random
        self.rockets.append({
            "x": rng.uniform(width * .16, width * .84),
            "y": height - 3,
            "vx": rng.uniform(-2.2, 2.2),
            "vy": -rng.uniform(7, 11),
            "target": rng.uniform(2, max(3, height * .42)),
            "palette": rng.choice(PALETTES),
        })

    def burst(self, rocket, width):
        rng = self.random
        count = min(48, max(22, width // 2))
        for index in range(count):
            angle = math.tau * (index + rng.uniform(-.18, .18)) / count
            speed = rng.uniform(3.3, 9.5)
            life = rng.uniform(1.1, 2.0)
            self.sparks.append({
                "x": rocket["x"], "y": rocket["y"],
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed * .58,
                "life": life, "max_life": life,
                "color": rng.choice(rocket["palette"]),
            })

    def render(self, t, width, height, color):
        if self.size != (width, height):
            self.reset(width, height)
        dt = 0 if self.last_time is None else max(0, min(.15, t - self.last_time))
        self.last_time = t
        if t >= self.next_launch:
            self.launch(width, height)
            self.next_launch = t + self.random.uniform(.6, 1.1)

        canvas = [[(" ", None) for _ in range(width)] for _ in range(height)]

        def put(x, y, char, rgb):
            x, y = round(x), round(y)
            if 0 <= x < width and 0 <= y < height:
                canvas[y][x] = char, fg(rgb)

        for x, y, phase in self.stars:
            put(x, y, "·" if math.sin(t + phase) > 0 else ".", DIM)
        for x in range(width):
            roof = height - 2 - (x // 7 % 3)
            for y in range(roof, height):
                put(x, y, "█", DARK)
            if x % 4 == 1 and roof + 1 < height:
                put(x, roof + 1, "▪", COPPER)

        active_rockets = []
        for rocket in self.rockets:
            rocket["x"] += rocket["vx"] * dt
            rocket["y"] += rocket["vy"] * dt
            if rocket["y"] <= rocket["target"]:
                self.burst(rocket, width)
            else:
                active_rockets.append(rocket)
                put(rocket["x"], rocket["y"] + 1, "·", RUST)
                put(rocket["x"], rocket["y"], "↑", PALE)
        self.rockets = active_rockets

        active_sparks = []
        for spark in self.sparks:
            old_x, old_y = spark["x"], spark["y"]
            spark["x"] += spark["vx"] * dt
            spark["y"] += spark["vy"] * dt
            spark["vy"] += 4.5 * dt
            spark["vx"] *= max(0, 1 - .25 * dt)
            spark["life"] -= dt
            if spark["life"] <= 0 or spark["y"] >= height - 3:
                continue
            active_sparks.append(spark)
            fraction = spark["life"] / spark["max_life"]
            rgb = tuple(round(component * max(.25, fraction)) for component in spark["color"])
            if fraction > .55:
                put(old_x, old_y, "·", tuple(component // 3 for component in rgb))
            put(spark["x"], spark["y"], "✦" if fraction > .75 else "•" if fraction > .4 else "·", rgb)
        self.sparks = active_sparks
        return "\n".join(color_row(row, color) for row in canvas)


render = Fireworks().render


if __name__ == "__main__":
    animate("Endless fireworks", render, default_fps=15, continuous=True)
