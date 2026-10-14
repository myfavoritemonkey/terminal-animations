"""Warm terminal colors matching the desktop accent (#ff9a3c)."""

ACCENT = (255, 154, 60)
GOLD = (255, 193, 105)
LIGHT = (255, 220, 163)
PALE = (255, 239, 211)
COPPER = (187, 91, 39)
RUST = (133, 62, 29)
DIM = (86, 47, 29)
DARK = (30, 20, 18)


def fg(rgb):
    return "38;2;{};{};{}".format(*rgb)


def fg_bg(foreground, background):
    return "{};48;2;{};{};{}".format(fg(foreground), *background)
