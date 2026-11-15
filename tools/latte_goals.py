"""The GOAL pictures for the latte mini game, drawn from the shapes real latte art has.

    python tools/latte_goals.py        (plain Python, no packages)
Writes Art/UI/Latte/T_LatteGoal_0.png (heart), _1 (rosetta), _2 (tulip): 256 px, red = foam, green = the fine
layering inside the foam. They are data for M_LatteSurface, which colours them like the cup - not pictures to look at.

WHY DRAWN (Sun Nov 15): the first goals were frozen from the game's own simulated pour, and the owner said they
"don't really look like what they are supposed to be". They were also upside-down next to any photo: latte art is
shown with the small heart at the top and the stem running down to a point.

x runs UP the picture, y to the right, both -0.5..0.5 (the cup's own surface coordinates).
"""
import math
import os
import struct
import zlib

N = 256
SS = 3
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Art', 'UI', 'Latte')


ROUND = 0.6          # 1.0 is the playing-card heart; poured foam is rounder, with a shallower cleft and a softer point


def heart(x, y, cx, s):
    """<= 0 inside a heart: lobes up (+x), point down."""
    a, b = y / s, (x - cx) / s
    return (a * a + b * b - 1.0) ** 3 - ROUND * a * a * b * b * b


def goal_heart(x, y):
    return heart(x, y, 0.02, 0.215) <= 0


def goal_tulip(x, y):
    layers = ((-0.13, 0.18), (0.04, 0.14), (0.19, 0.1))          # base first, the small heart last and on top
    white = False
    for i, (cx, s) in enumerate(layers):
        if heart(x, y, cx, s) <= 0:
            white = True
        elif i > 0 and heart(x, y, cx, s * 1.34) <= 0:
            white = False                                             # the thin line of coffee each layer pushes ahead of it
    return white


def goal_rosetta(x, y):
    if heart(x, y, 0.255, 0.062) <= 0:
        return True                                                   # the small heart at the top
    t = (x + 0.33) / 0.53
    if not 0.0 < t < 1.0:
        return False
    w = 0.31 * math.sin(math.pi * t) ** 0.6 * (1.0 - 0.3 * t)          # a leaf: widest low down, a point at the bottom
    ay = abs(y)
    if ay > w or ay < 0.011:                                          # outside the leaf, or the stem's hairline
        return False
    return ((x - 0.75 * ay) * 11.0) % 1.0 < 0.66                      # leaves: bands dragged DOWN at the centre by the cut


def render(fn, path):
    rows = []
    for v in range(N):
        row = bytearray([0])
        for u in range(N):
            hit = 0
            for i in range(SS):
                for j in range(SS):
                    x = (u + (i + 0.5) / SS) / N - 0.5
                    y = (v + (j + 0.5) / SS) / N - 0.5
                    if x * x + y * y < 0.2116 and fn(x, y):
                        hit += 1
            x, y = (u + 0.5) / N - 0.5, (v + 0.5) / N - 0.5
            ring = 0.5 + 0.5 * math.sin(math.hypot(x - 0.03, y) * 150.0)
            row += bytes((round(255 * hit / (SS * SS)), round(255 * ring), 0))
        rows.append(bytes(row))
    raw = zlib.compress(b''.join(rows), 9)

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', N, N, 8, 2, 0, 0, 0)) + chunk(b'IDAT', raw) + chunk(b'IEND', b''))


def render_all(path):
    """All three goals in one picture for the MATCH meter: red = heart, green = rosetta, blue = tulip."""
    fns = (goal_heart, goal_rosetta, goal_tulip)
    rows = []
    for v in range(N):
        row = bytearray([0])
        for u in range(N):
            hit = [0, 0, 0]
            for i in range(SS):
                for j in range(SS):
                    x = (u + (i + 0.5) / SS) / N - 0.5
                    y = (v + (j + 0.5) / SS) / N - 0.5
                    if x * x + y * y < 0.2116:
                        for k in range(3):
                            hit[k] += bool(fns[k](x, y))
            row += bytes(round(255 * h / (SS * SS)) for h in hit)
        rows.append(bytes(row))
    raw = zlib.compress(b''.join(rows), 9)

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    with open(path, 'wb') as f:
        f.write(bytes((137, 80, 78, 71, 13, 10, 26, 10)) + chunk(b'IHDR', struct.pack('>IIBBBBB', N, N, 8, 2, 0, 0, 0)) + chunk(b'IDAT', raw) + chunk(b'IEND', b''))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    render_all(os.path.normpath(os.path.join(OUT, 'T_LatteGoals.png')))
    for i, fn in enumerate((goal_heart, goal_rosetta, goal_tulip)):
        p = os.path.normpath(os.path.join(OUT, 'T_LatteGoal_%d.png' % i))
        render(fn, p)
        print('wrote', p)
