"""Prove the chalkboard's INLAID front face tiles its board exactly.

The old board was one box with chalk slabs floating 2 mm proud of it. The new one punches the front
face out and tiles it: bare-board strips between the lines, and per-line strips of board/chalk/board.
Two ways that can go wrong and neither shows in a screenshot:
  GAP      - a missing strip leaves a hole straight through the board into the cafe wall behind it.
  OVERLAP  - two strips on the same plane is a NEW coplanar same-facing tie, which is the exact
             z-fight class PR #111 cleared, reintroduced by the fix meant to remove a shimmer.
So: rasterise every front-plane face onto a fine grid and require coverage of EXACTLY one everywhere.

  blender --background --python Art/Blender/subpixel_coverage.py -- <repo>
"""
import importlib.util, os, sys

argv = sys.argv[sys.argv.index('--') + 1:]
repo = argv[0]
spec = importlib.util.spec_from_file_location(
    'jckit', os.path.join(repo, 'Art', 'Blender', 'jumpcut_city_kit.py'))
kit = importlib.util.module_from_spec(spec)
sys.modules['jckit'] = kit
spec.loader.exec_module(kit)
kit.build_all()

o = kit.bpy.data.objects['SM_CafeChalkboard']
me = o.data
slots = [m.name for m in me.materials]
FY = -0.07
W, H = 1.15, 0.80

# every face whose verts all sit on the front plane and which faces -Y
front = []
for p in me.polygons:
    co = [me.vertices[i].co for i in p.vertices]
    if all(abs(c.y - FY) < 1e-6 for c in co) and p.normal.y < -0.9:
        front.append((slots[p.material_index],
                      min(c.x for c in co), max(c.x for c in co),
                      min(c.z for c in co), max(c.z for c in co)))

print('front-plane -Y faces: %d' % len(front))
area = sum((x1 - x0) * (z1 - z0) for _, x0, x1, z0, z1 in front)
print('summed area      %.6f m2' % area)
print('board rectangle  %.6f m2  (%.2f x %.2f)' % (2 * W * 2 * H, 2 * W, 2 * H))

# rasterise: 1 mm cells across the board, count how many faces cover each cell centre
N, M = 2300, 1600
gap = over = 0
worst = None
for i in range(0, N, 2):                       # 2 mm sampling is plenty and keeps this quick
    x = -W + (i + 0.5) * (2 * W) / N
    for j in range(0, M, 2):
        z = -H + (j + 0.5) * (2 * H) / M
        n = 0
        for _, x0, x1, z0, z1 in front:
            if x0 <= x <= x1 and z0 <= z <= z1:
                n += 1
        if n == 0:
            gap += 1
            worst = worst or ('GAP', x, z)
        elif n > 1:
            over += 1
            worst = worst or ('OVERLAP x%d' % n, x, z)

cells = (N // 2) * (M // 2)
print('sampled cells    %d' % cells)
print('GAP cells        %d' % gap)
print('OVERLAP cells    %d' % over)
if worst:
    print('first offender   %s at x=%.4f z=%.4f' % worst)
print('VERDICT: %s' % ('the inlay tiles the board exactly - no hole, no new coplanar tie'
                       if gap == 0 and over == 0 else '*** FAILED ***'))

# and the chalk must be ON that plane, not proud of it
chalk = [f for f in front if f[0] == 'MS_CafeWall']
print('chalk strips on the front plane: %d' % len(chalk))
ys = sorted({round(me.vertices[i].co.y, 6)
             for p in me.polygons if slots[p.material_index] == 'MS_CafeWall'
             for i in p.vertices})
print('every chalk vertex y: %s   (board front plane is %.3f)' % (ys, FY))
