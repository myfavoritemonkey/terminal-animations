"""A rotating five-point star with a gentle glow and twinkling sky."""

import math

from terminal import animate, color_row


def in_polygon(x, y, vertices):
    inside = False
    previous = vertices[-1]
    for vertex in vertices:
        x1, y1 = previous
        x2, y2 = vertex
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
        previous = vertex
    return inside


def render(t, width, height, color):
    outer = min((width - 4) / 2.4, (height - 3) / 2.2)
    angle = t * 0.65
    vertices = []
    for point in range(10):
        direction = angle + math.pi / 2 + point * math.pi / 5
        radius = outer if point % 2 == 0 else outer * 0.43
        vertices.append((radius * math.cos(direction), radius * math.sin(direction)))
    rows = []
    for row in range(height):
        cells = []
        for col in range(width):
            x = (col - (width - 1) / 2) / 2
            y = (height - 1) / 2 - row
            if in_polygon(x, y, vertices):
                distance = math.hypot(x, y) / outer
                cells.append(("@" if distance < 0.28 else "*", "93" if color else None))
            elif x * x + y * y < (outer * 1.15) ** 2 and (col + 2 * row) % 3 == 0:
                cells.append((".", "33" if color else None))
            else:
                # Fixed star positions, changing brightness over time.
                seed = (col * 73 + row * 131 + col * row * 17) % 211
                if seed == 0 or seed == 7:
                    bright = math.sin(t * (1.4 + seed * 0.02) + col * 0.7 + row) > 0.2
                    cells.append(("+" if bright else ".", "97" if bright and color else ("90" if color else None)))
                else:
                    cells.append((" ", None))
        rows.append(color_row(cells, color))
    return "\n".join(rows)


if __name__ == "__main__":
    animate("Rotating terminal star", render)
