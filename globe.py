"""A tilted, rotating Earth with latitude/longitude lines and rough continents."""

import math

from terminal import animate, color_row


# Hand-drawn outlines in (longitude, latitude) degrees; intentionally simplified.
LAND = [
    [(-168, 65), (-150, 71), (-130, 70), (-124, 59), (-132, 53), (-125, 48),
     (-123, 39), (-115, 32), (-108, 31), (-97, 25), (-82, 25), (-81, 30),
     (-97, 31), (-82, 43), (-67, 45), (-58, 53), (-79, 59), (-95, 71), (-130, 73)],
    [(-80, 12), (-72, 10), (-62, 11), (-50, 3), (-35, -5), (-38, -18),
     (-46, -24), (-54, -35), (-70, -55), (-76, -38), (-82, -15), (-77, -2)],
    [(-73, 60), (-48, 59), (-40, 72), (-44, 84), (-61, 84), (-70, 76)],
    [(-12, 36), (4, 38), (12, 37), (24, 32), (34, 31), (43, 12),
     (51, 11), (44, -12), (33, -26), (18, -35), (11, -34), (10, -18),
     (2, -5), (-9, 5), (-17, 22)],
    [(-11, 36), (-10, 44), (2, 46), (10, 53), (24, 55), (30, 69),
     (55, 73), (80, 76), (115, 71), (145, 59), (160, 52), (145, 43),
     (132, 34), (120, 24), (105, 15), (100, 2), (115, -8), (106, -11),
     (96, 3), (77, 8), (69, 23), (57, 26), (48, 30), (34, 36),
     (30, 42), (22, 40), (15, 36), (3, 42), (-8, 42)],
    [(112, -11), (129, -13), (138, -12), (153, -24), (151, -37),
     (138, -39), (124, -34), (113, -23)],
    [(43, -13), (50, -15), (51, -25), (46, -26)],
]


def inside_polygon(lon, lat, points):
    inside = False
    previous = points[-1]
    for point in points:
        x1, y1 = previous
        x2, y2 = point
        if (y1 > lat) != (y2 > lat):
            crossing = x1 + (lat - y1) * (x2 - x1) / (y2 - y1)
            if lon < crossing:
                inside = not inside
        previous = point
    return inside


def render(t, width, height, color):
    radius = min((width - 2) / 2.2, (height - 2) / 2.1)
    tilt = math.radians(23.5)
    ct, st = math.cos(tilt), math.sin(tilt)
    rows = []
    for row in range(height):
        cells = []
        for col in range(width):
            x = (col - (width - 1) / 2) / (2 * radius)
            y = ((height - 1) / 2 - row) / radius
            distance = x * x + y * y
            if distance > 1:
                cells.append((" ", None))
                continue
            z = math.sqrt(1 - distance)
            local_x = x * ct - y * st
            local_y = x * st + y * ct
            lat = math.degrees(math.asin(max(-1, min(1, local_y))))
            lon = ((math.degrees(math.atan2(local_x, z)) - t * 24 + 180) % 360) - 180
            land = lat < -72 or any(inside_polygon(lon, lat, shape) for shape in LAND)
            # A soft light from the upper left makes the sphere read as 3D.
            light = max(0, 0.45 * x + 0.45 * y + 0.8 * z)
            shade = max(0, min(3, int(light * 4)))
            latitude_grid = abs(lat % 30 - 15) > 14.0
            longitude_grid = abs(lon % 30 - 15) > 14.0
            if (latitude_grid or longitude_grid) and light > 0.22:
                cells.append(("+", "96" if color else None))
            elif land:
                cells.append((".:*#"[shade], ("32", "32", "92", "93")[shade] if color else None))
            else:
                cells.append((".oO@"[shade], ("34", "34", "36", "96")[shade] if color else None))
        rows.append(color_row(cells, color))
    return "\n".join(rows)


if __name__ == "__main__":
    animate("Tilted, rotating terminal globe", render)
