"""Two shaded ground dishes exchange a signal through an orbiting relay."""

import math

from terminal import animate, color_row


LARGE_DISH = [
    "      ╭────────╮         ",
    "   ╭──╯▒▒▒▒▒▒▒▒╲        ",
    "  ╱▒▒▒▒▒▒▒▒▒▒▒▒▒╲    ◉   ",
    " ╱▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒╲  ╱    ",
    " ╲▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒╱─╯     ",
    "  ╲▒▒▒▒▒▒▒▒▒▒▒▒▒╱        ",
    "   ╰──╮▒▒▒▒▒▒╱          ",
    "      ╰──────╯           ",
    "         ╲               ",
    "          ║              ",
    "       ╔══╩══╗           ",
]
SMALL_DISH = [
    "   ╭────╮       ",
    " ╭─╯▒▒▒▒╲   ◉   ",
    "╱▒▒▒▒▒▒▒▒╲ ╱    ",
    "╲▒▒▒▒▒▒▒▒╱─╯    ",
    " ╰─╮▒▒▒╱        ",
    "   ╰───╯         ",
    "     ║           ",
    "   ╔═╩═╗         ",
]
LARGE_RELAY = [
    "╔══════╗   ╭───╮   ╔══════╗",
    "║▦▦▦▦▦▦║═══╡ ◉ ╞═══║▦▦▦▦▦▦║",
    "╚══════╝   ╰───╯   ╚══════╝",
]
SMALL_RELAY = [
    "╔════╗ ╭─╮ ╔════╗",
    "║▦▦▦▦║═╡◉╞═║▦▦▦▦║",
    "╚════╝ ╰─╯ ╚════╝",
]
MIRROR = str.maketrans("╭╮╰╯╱╲╔╗╚╝", "╮╭╯╰╲╱╗╔╝╚")


def render(t, width, height, color):
    canvas = [[(" ", None, -1) for _ in range(width)] for _ in range(height)]

    def put(x, y, char, shade=None, priority=0):
        col, row = round(x), round(y)
        if 0 <= col < width and 0 <= row < height and priority >= canvas[row][col][2]:
            canvas[row][col] = (char, shade if color else None, priority)

    def write(x, y, value, shade="97", priority=4):
        for offset, char in enumerate(value):
            put(x + offset, y, char, shade, priority)

    def sprite(x, y, art, mirrored=False, mask_spaces=False):
        sprite_width = max(map(len, art))
        feed = None
        for row, raw in enumerate(art):
            source = raw.ljust(sprite_width)
            if mirrored:
                source = source[::-1].translate(MIRROR)
            for col, char in enumerate(source):
                if char == " ":
                    if mask_spaces:
                        put(x + col, y + row, " ", None, 3)
                    continue
                if char == "◉":
                    feed = (x + col, y + row)
                if char == "▒":
                    local_col = sprite_width - 1 - col if mirrored else col
                    light = (0.62 * (1 - row / (len(art) - 3))
                             + 0.38 * local_col / sprite_width)
                    if light > 0.68:
                        glyph, shade = "░", "96"
                    elif light > 0.48:
                        glyph, shade = "▒", "36"
                    elif light > 0.29:
                        glyph, shade = "▓", "34"
                    else:
                        glyph, shade = "█", "34"
                    if (col * 7 + row * 11 + int(t * 7)) % 41 == 0:
                        glyph, shade = "✦", "93"
                    put(x + col, y + row, glyph, shade, 4)
                else:
                    if char == "◉":
                        shade = "93"
                    elif char in "╭╮╰╯╱╲":
                        shade = "97" if row < len(art) / 2 else "90"
                    else:
                        shade = "37"
                    put(x + col, y + row, char, shade, 5)
        return feed

    large = width >= 70 and height >= 21
    dish_art = LARGE_DISH if large else SMALL_DISH
    relay_art = LARGE_RELAY if large else SMALL_RELAY
    dish_width = max(map(len, dish_art))
    ground = height - 3
    dish_top = ground - len(dish_art) + 1
    margin = max(1, round(width * 0.06)) if large else max(0, round(width * 0.03))
    left_x = margin
    right_x = width - margin - dish_width

    for row in range(max(0, ground)):
        for col in range(width):
            seed = (col * 41 + row * 83 + col * row * 7) % 211
            if seed in (0, 9):
                bright = math.sin(t * 1.4 + col * 0.5 + row) > 0.45
                put(col, row, "✦" if bright else "·", "97" if bright else "90")
    write(0, ground + 1, "─" * width, "32", 1)

    left_feed = sprite(left_x, dish_top, dish_art)
    right_feed = sprite(right_x, dish_top, dish_art, mirrored=True)
    left_base = left_x + (10 if large else 5)
    right_base = right_x + dish_width - 1 - (10 if large else 5)
    write(left_base - 10, ground + 1, "··░░▒▒▒▓▓▓", "90", 2)
    write(right_base + 1, ground + 1, "▓▓▓▒▒▒░░··", "90", 2)

    relay_width = max(map(len, relay_art))
    relay_x = (width - relay_width) // 2
    relay_top = max(1, min(3, dish_top - 5))
    relay_center = sprite(relay_x, relay_top, relay_art, mask_spaces=True)
    put(*relay_center, "◆" if int(t * 5) % 2 else "◉", "93", 6)

    paths = [(left_feed, (relay_center[0] - 2, relay_center[1] + 1)),
             ((relay_center[0] + 2, relay_center[1] + 1), right_feed)]
    stage = int(t / 2.4) % 2
    progress = (t % 2.4) / 2.4
    for index, (start, end) in enumerate(paths):
        steps = max(1, round(math.dist(start, end) * 2))
        for step in range(0, steps + 1, 3):
            fraction = step / steps
            x = start[0] + (end[0] - start[0]) * fraction
            y = start[1] + (end[1] - start[1]) * fraction
            put(x, y, "•" if index == stage else "·",
                "36" if index == stage else "90", 2)
        if index == stage:
            for trail, glyph, shade in ((0.16, "·", "36"),
                                        (0.08, "●", "96"),
                                        (0, "◆", "93")):
                fraction = progress - trail
                if fraction >= 0:
                    put(start[0] + (end[0] - start[0]) * fraction,
                        start[1] + (end[1] - start[1]) * fraction,
                        glyph, shade, 7)

    if large:
        write(left_base + 3, ground + 1, "TX", "93", 6)
        write(right_base - 4, ground + 1, "RX", "93", 6)
    status = "TX  ──▶  SATELLITE" if stage == 0 else "SATELLITE  ──▶  RX"
    write(max(0, (width - len(status)) // 2), height - 1, status, "93", 6)
    return "\n".join(color_row([(char, shade) for char, shade, _ in row], color)
                     for row in canvas)


if __name__ == "__main__":
    animate("Ground antennas relaying through a satellite", render)
