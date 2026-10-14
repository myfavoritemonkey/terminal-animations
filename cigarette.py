"""A lighter ignites a cigarette; the ember travels and smoke curls upward."""

import math

from terminal import animate, color_row


CYCLE_SECONDS = 28
LIGHT_SECONDS = 3
BURN_SECONDS = 20


def render(t, width, height, color):
    canvas = [[(" ", None, -1) for _ in range(width)] for _ in range(height)]

    def put(x, y, char, shade=None, priority=0):
        col, row = round(x), round(y)
        if 0 <= col < width and 0 <= row < height and priority >= canvas[row][col][2]:
            canvas[row][col] = (char, shade if color else None, priority)

    def line(x1, x2, y, char, shade, priority):
        for x in range(x1, x2 + 1):
            put(x, y, char, shade, priority)

    cycle = t % CYCLE_SECONDS
    cigarette_y = max(3, min(round(height * 0.57), height - 9))
    tube_radius = 2 if width >= 65 and height >= 20 else 1
    initial_tip = round(width * 0.27)
    filter_start = round(width * 0.72)
    filter_end = min(width - 2, filter_start + max(5, round(width * 0.09)))
    burn = max(0, min(1, (cycle - LIGHT_SECONDS) / BURN_SECONDS))
    tip = initial_tip + round(burn * max(0, filter_start - initial_tip - 2))

    # Smoke is drawn behind the cigarette and appears gradually after ignition.
    if cycle > 2.1:
        rise_limit = min(cigarette_y - tube_radius, int((cycle - 2.1) * 3.2))
        for rise in range(1, rise_limit + 1):
            for strand in (0, 1):
                drift = -rise * 0.23 + 2.1 * math.sin(rise * 0.72 - t * 1.7 + strand * 1.9)
                x = tip + drift + strand
                y = cigarette_y - tube_radius - rise
                if (rise + strand + int(t * 7)) % 3:
                    glyph = "░" if rise < 5 else "·" if rise % 2 else "○"
                    put(x, y, glyph, "37" if rise < 5 else "90", 1)

    # A tiny falling ash trail makes the burn point visibly active.
    if LIGHT_SECONDS <= cycle < LIGHT_SECONDS + BURN_SECONDS:
        ash_drop = (cycle * 1.4) % 4
        put(tip - 2, cigarette_y + tube_radius + 1 + ash_drop, "·", "90", 1)
        put(tip - 1, cigarette_y + tube_radius + ash_drop * 0.6, "░", "90", 1)

    # Rounded paper tube with a shaded underside and a wrapper seam.
    if tip < filter_start:
        for dy in range(-tube_radius, tube_radius + 1):
            if dy == -tube_radius:
                glyph, shade = "─", "97"
            elif dy == tube_radius:
                glyph, shade = "─", "90"
            elif dy < 0:
                glyph, shade = "░", "97"
            elif dy == 0:
                glyph, shade = "▒", "37"
            else:
                glyph, shade = "▓", "90"
            line(tip, filter_start - 1, cigarette_y + dy, glyph, shade, 3)
        seam_x = filter_start - 8
        if tip < seam_x:
            for dy in range(-tube_radius + 1, tube_radius):
                put(seam_x, cigarette_y + dy, "│", "90", 4)
        put(tip, cigarette_y - tube_radius, "╭", "97", 4)
        put(tip, cigarette_y + tube_radius, "╰", "90", 4)

    # The filter has its own golden paper, bands, and a darker end cap.
    for x in range(filter_start, filter_end + 1):
        for dy in range(-tube_radius, tube_radius + 1):
            if abs(dy) == tube_radius:
                glyph, shade = "═", "33"
            elif dy < 0:
                glyph, shade = "▒", "93"
            else:
                glyph, shade = ("▓" if x % 2 else "▒"), "33"
            put(x, cigarette_y + dy, glyph, shade, 3)
    for dy in range(-tube_radius, tube_radius + 1):
        for x, glyph, shade in ((filter_start, "║", "33"),
                                (filter_start + 2, "│", "93"),
                                (filter_end + 1, "║", "33")):
            put(x, cigarette_y + dy, glyph, shade, 4)
    put(filter_end + 1, cigarette_y - tube_radius, "╮", "33", 5)
    put(filter_end + 1, cigarette_y + tube_radius, "╯", "33", 5)

    # Granular ash and an orange-red ember travel as the cigarette shortens.
    if cycle >= 2.3:
        for dy in range(-tube_radius, tube_radius + 1):
            put(tip - 2, cigarette_y + dy,
                "▒" if (dy + int(t * 5)) % 2 else "░", "90", 4)
            put(tip - 1, cigarette_y + dy,
                "◆" if dy == 0 and int(t * 8) % 2 else "▓",
                "91" if abs(dy) <= 1 else "33", 5)

    # Metal ignition wheel, fuel body, and a flame touching the paper tip.
    if cycle < LIGHT_SECONDS:
        approach = min(1, cycle / 1.1)
        lighter_x = round(initial_tip - 12 + approach * 9)
        lighter_top = cigarette_y + 3
        lighter_art = ("  ╔◉╗  ", " ╔╩═╩╗ ", " ║░░░║ ",
                       " ║░✧░║ ", " ║░░░║ ", " ╚═══╝ ")
        for row, art in enumerate(lighter_art):
            for col, char in enumerate(art):
                if char != " ":
                    put(lighter_x + col, lighter_top + row, char,
                        "97" if row < 2 else "36", 4)
        if cycle > 0.5:
            flame_x = lighter_x + 3
            flame_y = lighter_top - 1
            put(flame_x, flame_y, "▲", "93", 5)
            put(flame_x, flame_y - 1, "◆", "91", 5)
            put(flame_x, flame_y - 2, "✦", "93", 6)
            put(flame_x + (1 if int(t * 12) % 2 else -1), flame_y - 3,
                "·", "93", 4)

    return "\n".join(color_row([(char, shade) for char, shade, _ in row], color)
                     for row in canvas)


if __name__ == "__main__":
    animate("A cigarette lit by a lighter, burning with curling smoke",
            render, default_fps=12, continuous=True)
