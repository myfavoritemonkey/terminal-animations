"""A shaded 3D monkey head that rotates in the terminal."""

import math

from terminal import animate


BACKGROUND = (8, 12, 22)


def ellipsoid(cx, cy, cz, rx, ry, rz, color, texture=False):
    return (cx, cy, cz, rx, ry, rz, color, texture)


SHAPES = [
    # Ears and the round fur-covered skull.
    ellipsoid(-0.92, 0.05, 0.00, 0.30, 0.37, 0.20, (117, 65, 36), True),
    ellipsoid(0.92, 0.05, 0.00, 0.30, 0.37, 0.20, (117, 65, 36), True),
    ellipsoid(-0.99, 0.03, 0.17, 0.18, 0.25, 0.09, (171, 92, 84)),
    ellipsoid(0.99, 0.03, 0.17, 0.18, 0.25, 0.09, (171, 92, 84)),
    ellipsoid(0, 0.01, 0, 0.83, 0.99, 0.68, (119, 68, 38), True),
    # Three tufts break up the top of the head.
    ellipsoid(-0.15, 0.92, 0.12, 0.12, 0.20, 0.13, (100, 55, 32), True),
    ellipsoid(0, 1.00, 0.13, 0.13, 0.24, 0.14, (111, 59, 33), True),
    ellipsoid(0.15, 0.92, 0.12, 0.12, 0.20, 0.13, (100, 55, 32), True),
    # The tan facial mask, raised brows, eye sockets and eyes.
    ellipsoid(0, -0.06, 0.53, 0.64, 0.73, 0.25, (207, 149, 91)),
    ellipsoid(-0.29, 0.43, 0.75, 0.22, 0.10, 0.08, (76, 42, 29)),
    ellipsoid(0.29, 0.43, 0.75, 0.22, 0.10, 0.08, (76, 42, 29)),
    ellipsoid(-0.28, 0.21, 0.76, 0.18, 0.23, 0.10, (88, 51, 34)),
    ellipsoid(0.28, 0.21, 0.76, 0.18, 0.23, 0.10, (88, 51, 34)),
    ellipsoid(-0.28, 0.21, 0.84, 0.10, 0.13, 0.07, (245, 222, 182)),
    ellipsoid(0.28, 0.21, 0.84, 0.10, 0.13, 0.07, (245, 222, 182)),
    ellipsoid(-0.25, 0.20, 0.90, 0.050, 0.072, 0.035, (25, 22, 20)),
    ellipsoid(0.25, 0.20, 0.90, 0.050, 0.072, 0.035, (25, 22, 20)),
    ellipsoid(-0.23, 0.24, 0.925, 0.018, 0.025, 0.012, (255, 250, 236)),
    ellipsoid(0.27, 0.24, 0.925, 0.018, 0.025, 0.012, (255, 250, 236)),
    # Cheeks, a protruding muzzle, a small nose and nostrils.
    ellipsoid(-0.37, -0.34, 0.72, 0.24, 0.23, 0.12, (216, 157, 99)),
    ellipsoid(0.37, -0.34, 0.72, 0.24, 0.23, 0.12, (216, 157, 99)),
    ellipsoid(0, -0.47, 0.77, 0.48, 0.31, 0.25, (227, 174, 113)),
    ellipsoid(0, -0.30, 1.01, 0.14, 0.09, 0.065, (91, 49, 37)),
    ellipsoid(-0.075, -0.32, 1.065, 0.035, 0.028, 0.020, (35, 26, 25)),
    ellipsoid(0.075, -0.32, 1.065, 0.035, 0.028, 0.020, (35, 26, 25)),
]

# A curved smile lies on the visible surface of the muzzle.
for step in range(-10, 11):
    mouth_x = step * 0.027
    mouth_y = -0.60 + 0.11 * (mouth_x / 0.27) ** 2
    muzzle_depth = 0.77 + 0.25 * math.sqrt(max(
        0, 1 - (mouth_x / 0.48) ** 2 - ((mouth_y + 0.47) / 0.31) ** 2))
    SHAPES.append(ellipsoid(mouth_x, mouth_y, muzzle_depth + 0.01,
                            0.022, 0.023, 0.018, (73, 39, 31)))


def pixel_at(x, y, cosine, sine, shapes):
    """Cast a front-facing ray through every ellipsoid, keeping the nearest hit."""
    if abs(x) > 1.35 or abs(y) > 1.27:
        return BACKGROUND
    nearest = -100.0
    winner = None
    for shape in shapes:
        (cx, cy, cz, rx, ry, rz, base, textured,
         inv_x, inv_y, inv_z, a, center_x, extent_x) = shape
        delta_y = y - cy
        if abs(delta_y) > ry or abs(x - center_x) > extent_x:
            continue
        local_x = cosine * x - cx
        local_z = sine * x - cz
        b = 2 * (-sine * local_x * inv_x + cosine * local_z * inv_z)
        c = local_x * local_x * inv_x + delta_y * delta_y * inv_y + local_z * local_z * inv_z - 1
        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            continue
        depth = (-b + math.sqrt(discriminant)) / (2 * a)
        if depth <= nearest:
            continue
        nearest = depth
        winner = shape
    if winner is None:
        return BACKGROUND

    (cx, cy, cz, rx, ry, rz, base, textured,
     inv_x, inv_y, inv_z, _a, _center_x, _extent_x) = winner
    hit_x = cosine * x - sine * nearest - cx
    hit_z = sine * x + cosine * nearest - cz
    normal_x = hit_x * inv_x
    normal_y = (y - cy) * inv_y
    normal_z = hit_z * inv_z
    world_nx = cosine * normal_x + sine * normal_z
    world_nz = -sine * normal_x + cosine * normal_z
    length = math.sqrt(world_nx * world_nx + normal_y * normal_y + world_nz * world_nz)
    brightness = max(0, (-0.40 * world_nx + 0.60 * normal_y + 0.88 * world_nz) / length)
    light = 0.38 + 0.63 * brightness
    if textured:
        grain = math.sin(hit_x * 47 + (y - cy) * 25) * math.sin(hit_z * 39 - (y - cy) * 31)
        light *= 1 + 0.065 * grain
    return tuple(max(0, min(255, round(channel * light))) for channel in base)


def render(t, width, height, color):
    angle = t * 0.66
    cosine, sine = math.cos(angle), math.sin(angle)
    shapes = []
    for cx, cy, cz, rx, ry, rz, base, textured in SHAPES:
        inv_x, inv_y, inv_z = 1 / (rx * rx), 1 / (ry * ry), 1 / (rz * rz)
        a = sine * sine * inv_x + cosine * cosine * inv_z
        center_x = cosine * cx + sine * cz
        extent_x = math.hypot(cosine * rx, sine * rz)
        shapes.append((cx, cy, cz, rx, ry, rz, base, textured,
                       inv_x, inv_y, inv_z, a, center_x, extent_x))
    pixel_height = height * 2
    scale = max(1, min((width - 4) / 2.8, (pixel_height - 4) / 2.8))
    picture = []
    for row in range(pixel_height):
        y = ((pixel_height - 1) / 2 - row) / scale
        pixels = []
        for col in range(width):
            x = (col - (width - 1) / 2) / scale
            pixels.append(pixel_at(x, y, cosine, sine, shapes))
        picture.append(pixels)

    output = []
    for row in range(height):
        upper = picture[row * 2]
        lower = picture[row * 2 + 1]
        line = []
        styled = False
        for top, bottom in zip(upper, lower):
            if top == BACKGROUND and bottom == BACKGROUND:
                if styled:
                    line.append("\x1b[0m")
                    styled = False
                line.append(" ")
            elif color:
                line.append("\x1b[38;2;{};{};{};48;2;{};{};{}m▀".format(
                    *top, *bottom))
                styled = True
            else:
                level = sum(top) + sum(bottom)
                line.append(" .:-=+*#%@"[min(9, level * 10 // 1530)])
        if styled:
            line.append("\x1b[0m")
        output.append("".join(line))
    return "\n".join(output)


if __name__ == "__main__":
    animate("Detailed rotating 3D monkey head", render,
            default_fps=12, continuous=True)
