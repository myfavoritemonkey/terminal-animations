"""Classic spinning ASCII torus with lighting and a depth buffer."""

import math

from terminal import animate


SHADES = ".,-~:;=!*#$@"


def render(t, width, height, color):
    image = [" "] * (width * height)
    depth = [float("-inf")] * (width * height)
    a, b = t * 1.3, t * 0.8
    ca, sa, cb, sb = math.cos(a), math.sin(a), math.cos(b), math.sin(b)
    scale = min(width / 4.0, height / 2.0)
    for theta_step in range(90):
        theta = theta_step * 2 * math.pi / 90
        ct, st = math.cos(theta), math.sin(theta)
        for phi_step in range(32):
            phi = phi_step * 2 * math.pi / 32
            cp, sp = math.cos(phi), math.sin(phi)
            circle = 2 + cp
            denominator = st * circle * sa + sp * ca + 5
            inverse_depth = 1 / denominator
            horizontal = st * circle * ca - sp * sa
            x = int(width / 2 + scale * inverse_depth * (ct * circle * cb - horizontal * sb) * 2)
            y = int(height / 2 - scale * inverse_depth * (ct * circle * sb + horizontal * cb))
            if not (0 <= x < width and 0 <= y < height):
                continue
            index = y * width + x
            if inverse_depth <= depth[index]:
                continue
            luminance = (
                (sp * sa - st * cp * ca) * cb
                - st * cp * sa - sp * ca - ct * cp * sb
            )
            shade = max(0, min(len(SHADES) - 1, int((luminance + 1) * 5.5)))
            image[index] = SHADES[shade]
            depth[index] = inverse_depth
    rows = ["".join(image[start:start + width]) for start in range(0, len(image), width)]
    if color:
        return "\x1b[33m" + "\n".join(rows)
    return "\n".join(rows)


if __name__ == "__main__":
    animate("Spinning terminal donut", render)
