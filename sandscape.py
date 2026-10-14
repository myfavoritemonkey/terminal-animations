"""Endless falling-sand and flowing-water simulation."""

import random

from orange_theme import ACCENT, DIM, LIGHT, fg
from terminal import animate, color_row


EMPTY, SAND, WATER, STONE = range(4)


class Sandscape:
    def __init__(self):
        self.random = random.Random()
        self.size = None
        self.grid = []
        self.last_time = None
        self.accumulator = 0
        self.age = 0

    def reset(self, width, height):
        self.size = width, height
        self.grid = [[EMPTY] * width for _ in range(height)]
        self.last_time = None
        self.accumulator = 0
        self.age = 0
        for x in range(width):
            self.grid[height - 1][x] = STONE
        for left, right, y in ((.10, .39, .48), (.61, .90, .57)):
            row = min(height - 3, max(3, round(height * y)))
            for x in range(round(width * left), round(width * right)):
                self.grid[row][x] = STONE

    def step(self):
        grid = self.grid
        width, height = self.size
        rng = self.random
        self.age += 1
        if self.age > 12 * 42:
            self.reset(width, height)
            grid = self.grid

        for center, material in ((width // 3, SAND), (width * 2 // 3, WATER)):
            for _ in range(2):
                x = min(width - 2, max(1, center + rng.choice((-1, 0, 0, 1))))
                if grid[0][x] == EMPTY:
                    grid[0][x] = material

        moved = set()
        for y in range(height - 2, -1, -1):
            columns = range(width - 1, -1, -1) if rng.randrange(2) else range(width)
            for x in columns:
                material = grid[y][x]
                if material not in (SAND, WATER) or (x, y) in moved:
                    continue
                diagonals = [(-1, 1), (1, 1)]
                if rng.randrange(2):
                    diagonals.reverse()
                directions = [(0, 1), *diagonals]
                if material == WATER:
                    directions += [(dx, 0) for dx, _ in diagonals]
                for dx, dy in directions:
                    nx = x + dx
                    ny = y + dy
                    if not (0 <= nx < width and ny < height):
                        continue
                    destination = grid[ny][nx]
                    if destination == EMPTY or (material == SAND and destination == WATER):
                        grid[ny][nx], grid[y][x] = material, destination
                        moved.add((nx, ny))
                        break

    def render(self, t, width, height, color):
        if self.size != (width, height):
            self.reset(width, height)
        dt = 0 if self.last_time is None else max(0, min(.2, t - self.last_time))
        self.last_time = t
        self.accumulator += dt
        while self.accumulator >= 1 / 12:
            self.step()
            self.accumulator -= 1 / 12

        symbols = (" ", "●", "≈", "▓")
        shades = (None, fg(LIGHT), fg(ACCENT), fg(DIM))
        rows = []
        for y, row in enumerate(self.grid):
            cells = [(symbols[value], shades[value]) for value in row]
            rows.append(color_row(cells, color))
        return "\n".join(rows)


render = Sandscape().render


if __name__ == "__main__":
    animate("Falling sand and flowing water", render, default_fps=15, continuous=True)
