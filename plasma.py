"""Continuous color waves generated from moving interference sources."""

import math

from orange_theme import ACCENT, PALE
from terminal import animate


STOPS = ((10, 8, 7), (64, 28, 18), (170, 70, 26), ACCENT, PALE)
SHADES = " .:-=+*#%@"


def palette_color(value):
    position = max(0, min(3.999, value * 4))
    index = int(position)
    fraction = position - index
    return tuple(round(a * (1 - fraction) + b * fraction)
                 for a, b in zip(STOPS[index], STOPS[index + 1]))


PALETTE = [palette_color(index / 255) for index in range(256)]


def render(t, width, height, color):
    source_a = (width * (.33 + .13 * math.sin(t * .39)),
                height * (.76 + .21 * math.cos(t * .53)))
    source_b = (width * (.67 + .15 * math.cos(t * .31)),
                height * (1.18 + .27 * math.sin(t * .47)))

    def pixel(x, y):
        first = math.hypot(x - source_a[0], (y - source_a[1]) * .72)
        second = math.hypot(x - source_b[0], (y - source_b[1]) * .72)
        wave = (math.sin(first * .43 - t * 2.1)
                + math.sin(second * .52 + t * 1.6)
                + .47 * math.sin(x * .16 + y * .12 - t * .8))
        return max(0, min(255, round((wave + 2.47) * 255 / 4.94)))

    rows = []
    for row in range(height):
        parts = []
        for col in range(width):
            upper = pixel(col, row * 2)
            lower = pixel(col, row * 2 + 1)
            if color:
                top = PALETTE[upper]
                bottom = PALETTE[lower]
                parts.append("\x1b[38;2;{};{};{};48;2;{};{};{}m▀".format(*top, *bottom))
            else:
                parts.append(SHADES[(upper + lower) * (len(SHADES) - 1) // 510])
        if color:
            parts.append("\x1b[0m")
        rows.append("".join(parts))
    return "\n".join(rows)


if __name__ == "__main__":
    animate("Procedural color waves", render, default_fps=12, continuous=True)
