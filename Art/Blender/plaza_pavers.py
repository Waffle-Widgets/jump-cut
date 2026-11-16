"""Draws the boss plaza's paving texture: stone setts in a running bond, 2 m x 2 m, tiling.

    blender -b --factory-startup --python Art/Blender/plaza_pavers.py -- Art/Textures/T_PlazaPavers.png

Sun Nov 15, GameStation. The plaza floor was three flat colours (a cream and grey checker inside a brick border) and
read as a grey box. The mesh already has real-scale UVs (1 unit = 1 m), so a tiling texture needs no new geometry.
Near-white stone with a darker joint, so each material instance can tint it. Sizes chosen against the 2-pixel floor
in CLAUDE.md: setts 50 x 25 cm with a 3 cm joint, and LOW contrast (joint 0.70 of the stone), so the ink pass does
not draw every joint and nothing narrower than the joint exists to shimmer.
"""
import bpy, sys, random
import numpy as np
out = sys.argv[sys.argv.index('--') + 1]
N = 1024; rows, cols = 8, 4                 # 2 m: 8 courses of 25 cm, 4 setts of 50 cm
rh, cw, j = N // rows, N // cols, 15        # joint 15 px = 2.9 cm
rnd = random.Random(7)
img = np.zeros((N, N), dtype=np.float32)
yy, xx = np.mgrid[0:N, 0:N]
for r in range(rows):
    off = (cw // 2) if r % 2 else 0
    for c in range(cols):
        v = rnd.uniform(0.80, 1.0)
        x0 = (c * cw + off) % N
        m = (yy >= r * rh + j // 2) & (yy < (r + 1) * rh - j // 2) & ((((xx - x0) % N) >= j // 2) & (((xx - x0) % N) < cw - j // 2))
        img[m] = v
img[img == 0] = 0.62
# a little grain so a sett is not a flat fill, kept coarse (8 px blocks) for the same 2-pixel reason
g = np.random.RandomState(3).uniform(-0.035, 0.035, (N // 8, N // 8)).astype(np.float32)
img = np.clip(img + np.kron(g, np.ones((8, 8), dtype=np.float32)), 0, 1)
rgba = np.dstack([img, img * 0.985, img * 0.96, np.ones_like(img)]).astype(np.float32)
im = bpy.data.images.new('T_PlazaPavers', N, N, alpha=False)
im.pixels.foreach_set(rgba.ravel())
im.filepath_raw = out; im.file_format = 'PNG'; im.save()
print('PAVERS wrote %s' % out)
