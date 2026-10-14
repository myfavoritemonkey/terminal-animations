"""Endless Conway's Game of Life for the terminal."""

from collections import Counter, deque
import random

from orange_theme import ACCENT, COPPER, GOLD, LIGHT, fg
from terminal import animate, color_row


class Life:
    def __init__(self):
        self.random = random.Random()
        self.size = None
        self.live = set()
        self.ages = {}
        self.generation = 0
        self.restarts = 0
        self.recent = deque(maxlen=8)
        self.repeats = 0

    def reset(self, width, height):
        self.size = (width, height)
        self.live = {(x, y) for y in range(height) for x in range(width)
                     if self.random.random() < 0.26}
        self.ages = {cell: 0 for cell in self.live}
        self.generation = 0
        self.restarts += 1
        self.recent.clear()
        self.repeats = 0

    def step(self):
        width, height = self.size
        neighbors = Counter()
        for x, y in self.live:
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx or dy:
                        neighbors[((x + dx) % width, (y + dy) % height)] += 1
        new_live = {cell for cell, count in neighbors.items()
                    if count == 3 or (count == 2 and cell in self.live)}
        self.ages = {cell: min(9, self.ages.get(cell, -1) + 1)
                     for cell in new_live}
        self.live = new_live
        self.generation += 1

        state = frozenset(new_live)
        self.repeats = self.repeats + 1 if state in self.recent else 0
        self.recent.append(state)
        if not new_live or self.repeats >= 8:
            self.reset(width, height)

    def render(self, _time, width, height, color):
        board_width = width // 2
        board_height = height
        if self.size != (board_width, board_height):
            self.reset(board_width, board_height)
        else:
            self.step()

        rows = []
        for y in range(board_height):
            cells = []
            for x in range(board_width):
                age = self.ages.get((x, y))
                if age is None:
                    cells.append(("  ", None))
                elif age == 0:
                    cells.append(("██", fg(LIGHT)))
                elif age < 3:
                    cells.append(("██", fg(ACCENT)))
                elif age < 6:
                    cells.append(("██", fg(GOLD)))
                else:
                    cells.append(("██", fg(COPPER)))
            rows.append(color_row(cells, color) + (" " if width % 2 else ""))

        return "\n".join(rows)


render = Life().render


if __name__ == "__main__":
    animate("Endless Conway's Game of Life", render,
            default_fps=10, continuous=True)
