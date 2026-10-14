"""An endlessly running cat chasing a mouse across the terminal."""

import math

from terminal import animate, color_row


CAT = [
    "  ╭╮   /\\_/\\",
    "  ╰╯──( o.o )>",
    "   ╲    > ^ <",
    "    ╲__/   \\_",
]
CAT_LEGS = [
    "      /_/ \\_\\",
    "     /_/   \\_\\",
    "     \\_\\ /_/",
    "      \\_\\   /_/",
]
MOUSE = [
    "   (\\_/)",
    "~~( •_•)>",
]
MOUSE_FEET = ["   / \\" , "   \\ / "]


def render(t, width, height, color):
    ground = height - 2
    cycle = (t / 24 + 0.16) % 1
    daytime = cycle < 0.5
    sky_progress = cycle * 2 if daytime else (cycle - 0.5) * 2
    high_in_sky = math.sin(math.pi * sky_progress)
    if daytime:
        sky_bg = "48;5;24" if high_in_sky > 0.4 else "48;5;60"
    else:
        sky_bg = "48;5;17" if high_in_sky > 0.3 else "48;5;53"
    canvas = [[(" ", sky_bg if color and y < ground else None, -1)
               for _ in range(width)] for y in range(height)]

    def put(x, y, char, shade=None, priority=0):
        if 0 <= x < width and 0 <= y < height and priority >= canvas[y][x][2]:
            if color and y < ground:
                code = f"{shade};{sky_bg}" if shade else sky_bg
            else:
                code = shade if color else None
            canvas[y][x] = (char, code, priority)

    def sprite(x, y, lines, shade, priority=4):
        for dy, line in enumerate(lines):
            for dx, char in enumerate(line):
                if char != " ":
                    put(x + dx, y + dy, char, shade, priority)

    cat_motion = 4.6 * t + 1.5 / 0.75 * (1 - math.cos(0.75 * t))
    mouse_motion = 5.0 * t + 1.8 / 0.65 * (math.cos(0.9) - math.cos(0.65 * t + 0.9))
    cat_phase = int(cat_motion) % 4
    mouse_phase = int(mouse_motion) % 2
    scroll = int(cat_motion * 2)

    if daytime:
        clouds = ["  .--.  ", ".(    ).", "(______) "]
        for offset, speed in ((0.2, 0.8), (0.7, 0.5)):
            cloud_x = round((width * offset - t * speed) % (width + 12)) - 6
            sprite(cloud_x, 2, clouds, "97", 1)
    else:
        for y in range(max(0, ground - 5)):
            for x in range(width):
                seed = (x * 71 + y * 103 + x * y * 13) % 263
                if seed in (0, 11):
                    put(x, y, "+" if math.sin(t * 1.5 + x) > 0.3 else ".",
                        "97" if seed == 0 else "90", 1)
    sky_horizon = max(3, ground - 8)
    celestial_x = round(width * (0.1 + 0.8 * sky_progress))
    celestial_y = round(sky_horizon - (sky_horizon - 2) * high_in_sky)
    put(celestial_x, celestial_y, "☀" if daytime else "☾",
        "93" if daytime else "97", 2)

    for x in range(width):
        put(x, ground, "─", "32", 1)
        if (x + scroll) % 13 in (0, 1):
            put(x, ground - 1, "'" if (x + scroll) % 13 else "ˇ", "32", 1)
        if (x + scroll // 2) % 23 == 0:
            put(x, height - 1, "·", "90", 1)

    cat_width = max(map(len, CAT + CAT_LEGS))
    cat_x = round(width * 0.16 + 2 * math.sin(cat_motion * 0.16))
    gap = max(7, round(width * 0.14)) + round(
        4 * math.sin(mouse_motion * 0.18 - cat_motion * 0.13))
    mouse_x = cat_x + cat_width + gap
    # On narrow windows keep both characters visible as often as possible.
    if mouse_x + max(map(len, MOUSE)) >= width:
        shift = mouse_x + max(map(len, MOUSE)) - width + 1
        cat_x -= shift
        mouse_x -= shift

    cat_y = ground - 5 - (1 if cat_phase == 1 else 0)
    sprite(cat_x, cat_y, CAT, "93")
    sprite(cat_x, cat_y + len(CAT), [CAT_LEGS[cat_phase]], "33")
    if int(t * 3) % 23 == 12:
        for eye, char in enumerate(CAT[1]):
            if char == "o":
                put(cat_x + eye, cat_y + 1, "-", "97", 5)

    mouse_y = ground - 3 - (1 if mouse_phase else 0)
    sprite(mouse_x, mouse_y, MOUSE, "37")
    sprite(mouse_x, mouse_y + len(MOUSE), [MOUSE_FEET[mouse_phase]], "37")

    # Little dust puffs trail the cat's paws and move with the ground.
    for distance in (2, 5, 9):
        dust_x = cat_x - distance - cat_phase
        dust_y = ground - 1 - (distance % 2)
        put(dust_x, dust_y, "·" if distance != 5 else "°", "90", 2)

    return "\n".join(color_row([(char, shade) for char, shade, _ in row], color)
                     for row in canvas)


if __name__ == "__main__":
    animate("A cat endlessly chasing a mouse", render,
            default_fps=12, continuous=True)
