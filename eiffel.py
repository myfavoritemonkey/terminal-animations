"""An illuminated Eiffel Tower with twinkling lights and a moving spotlight."""

import math

from terminal import animate, color_row


def render(t, width, height, color):
    canvas = [[(" ", None, -1) for _ in range(width)] for _ in range(height)]
    center = (width - 1) / 2
    top = 1
    ground = height - 2
    tower_height = ground - top
    half_base = min((width - 4) * 0.32, tower_height * 1.0)

    def put(x, y, character, shade, priority):
        col, row = round(x), round(y)
        if 0 <= col < width and 0 <= row < height and priority >= canvas[row][col][2]:
            canvas[row][col] = (character, shade if color else None, priority)

    def line(x1, y1, x2, y2, shade="33", priority=2, character=None):
        dx, dy = x2 - x1, y2 - y1
        steps = max(1, math.ceil(max(abs(dx), abs(dy)) * 3))
        glyph = character or ("-" if abs(dy) < 0.3 else
                              "|" if abs(dx) < 0.3 else
                              "\\" if dx * dy > 0 else "/")
        for step in range(steps + 1):
            fraction = step / steps
            put(x1 + dx * fraction, y1 + dy * fraction, glyph, shade, priority)

    # A few fixed stars pulse at different rates.
    for row in range(1, ground - 2):
        for col in range(width):
            seed = (col * 53 + row * 97 + col * row * 11) % 191
            if seed in (0, 7):
                bright = math.sin(t * 1.8 + seed + col * 0.4) > 0.45
                put(col, row, "+" if bright else ".", "97" if bright else "90", 0)

    # The moving ray starts at the top platform and stays behind the tower.
    beam_y = top + tower_height * 0.17
    ray_angle = math.sin(t * 0.75) * 0.9
    ray_x = center + math.sin(ray_angle) * width * 0.42
    line(center, beam_y, ray_x, 0, "96", 1, ".")

    # Three levels make the shape recognizable even in a short terminal.
    levels = [
        (top + tower_height * 0.12, half_base * 0.06),
        (top + tower_height * 0.36, half_base * 0.24),
        (top + tower_height * 0.68, half_base * 0.55),
        (ground, half_base),
    ]
    line(center, top, center, levels[0][0], "93", 4, "|")
    put(center, top, "*", "97", 5)

    for index in range(len(levels) - 1):
        y1, spread1 = levels[index]
        y2, spread2 = levels[index + 1]
        # Exterior legs and crossed iron braces.
        for side in (-1, 1):
            line(center + side * spread1, y1, center + side * spread2, y2,
                 "93", 4)
            inner1, inner2 = spread1 * 0.62, spread2 * 0.62
            line(center + side * inner1, y1, center + side * inner2, y2,
                 "33", 2)
            sections = max(2, round((y2 - y1) / 3))
            for section in range(sections):
                fraction1 = section / sections
                fraction2 = (section + 1) / sections
                ya = y1 + (y2 - y1) * fraction1
                yb = y1 + (y2 - y1) * fraction2
                outer_a = spread1 + (spread2 - spread1) * fraction1
                outer_b = spread1 + (spread2 - spread1) * fraction2
                line(center + side * outer_a, ya,
                     center + side * outer_b * 0.62, yb, "33", 2, "x")
                line(center + side * outer_a * 0.62, ya,
                     center + side * outer_b, yb, "33", 2, "x")

    # Observation decks, railings, and the large arch between the feet.
    for index, (deck_y, spread) in enumerate(levels[1:3]):
        extra = max(2, round(half_base * (0.13 if index == 0 else 0.16)))
        line(center - spread - extra, deck_y, center + spread + extra,
             deck_y, "93", 5, "=")
        line(center - spread - extra + 1, deck_y - 1,
             center + spread + extra - 1, deck_y - 1, "33", 3, "-")
    arch_radius = half_base * 0.64
    arch_height = tower_height * 0.22
    for step in range(round(arch_radius * 8) + 1):
        x = -arch_radius + 2 * arch_radius * step / max(1, round(arch_radius * 8))
        y = ground - arch_height * math.sqrt(max(0, 1 - (x / arch_radius) ** 2))
        put(center + x, y, "^" if abs(x) < 1 else "/" if x < 0 else "\\", "93", 4)

    line(center - half_base - 2, ground, center - half_base + 2,
         ground, "93", 5, "=")
    line(center + half_base - 2, ground, center + half_base + 2,
         ground, "93", 5, "=")
    line(0, height - 1, width - 1, height - 1, "90", 1, "_")

    # Deterministic sparkles travel across the ironwork.
    tick = int(t * 8)
    for row in range(height):
        for col in range(width):
            character, _, priority = canvas[row][col]
            if priority >= 2 and (col * 37 + row * 71 + tick * 13) % 43 == 0:
                put(col, row, "*", "97", 6)

    return "\n".join(color_row([(ch, shade) for ch, shade, _ in row], color)
                     for row in canvas)


if __name__ == "__main__":
    animate("Illuminated terminal Eiffel Tower", render)
