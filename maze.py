"""Watch an endless series of mazes carve themselves."""

import random

from orange_theme import ACCENT, DARK, LIGHT, fg
from terminal import animate, color_row


class GrowingMaze:
    def __init__(self):
        self.random = random.Random()
        self.size = None
        self.walls = []
        self.order = []
        self.stack = []
        self.last_time = None
        self.accumulator = 0
        self.finished_at = None
        self.carved = 0

    def reset(self, width, height):
        self.size = width, height
        self.walls = [[True] * width for _ in range(height)]
        self.order = [[-1] * width for _ in range(height)]
        x = min(width - 2, max(1, (width // 2) | 1))
        y = min(height - 2, max(1, (height // 2) | 1))
        self.walls[y][x] = False
        self.order[y][x] = 0
        self.stack = [(x, y)]
        self.last_time = None
        self.accumulator = 0
        self.finished_at = None
        self.carved = 1

    def step(self):
        if not self.stack:
            return
        x, y = self.stack[-1]
        width, height = self.size
        choices = []
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            nx, ny = x + dx, y + dy
            if 1 <= nx < width - 1 and 1 <= ny < height - 1 and self.walls[ny][nx]:
                choices.append((nx, ny, dx, dy))
        if not choices:
            self.stack.pop()
            return
        nx, ny, dx, dy = self.random.choice(choices)
        self.carved += 1
        for px, py in ((x + dx // 2, y + dy // 2), (nx, ny)):
            self.walls[py][px] = False
            self.order[py][px] = self.carved
        self.stack.append((nx, ny))

    def render(self, t, width, height, color):
        if self.size != (width, height):
            self.reset(width, height)
        dt = 0 if self.last_time is None else max(0, min(.2, t - self.last_time))
        self.last_time = t
        self.accumulator += dt * 90
        while self.accumulator >= 1 and self.stack:
            self.step()
            self.accumulator -= 1
        if not self.stack:
            if self.finished_at is None:
                self.finished_at = t
            elif t - self.finished_at > 2.5:
                self.reset(width, height)

        tip = self.stack[-1] if self.stack else None
        trail = set(self.stack)
        rows = []
        for y in range(height):
            cells = []
            for x in range(width):
                if (x, y) == tip:
                    cells.append(("◆", fg(ACCENT)))
                elif (x, y) in trail:
                    cells.append(("•", fg(LIGHT)))
                elif self.walls[y][x]:
                    cells.append(("█", fg(DARK)))
                else:
                    age = self.order[y][x]
                    cells.append(("·", fg((110 + age % 5 * 13,
                                           47 + age % 7 * 8,
                                           24 + age % 4 * 6))))
            rows.append(color_row(cells, color))
        return "\n".join(rows)


render = GrowingMaze().render


if __name__ == "__main__":
    animate("Growing random mazes", render, default_fps=15, continuous=True)
