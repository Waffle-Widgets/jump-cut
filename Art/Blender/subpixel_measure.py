"""Verify the issue-67 sub-pixel pass against the BUILT geometry, not against the source.

Two jobs:
  1. Whole-kit regression: no model may contain a coplanar, same-facing, DIFFERENT-material overlap.
     That is the z-fight class PR #111 cleared, and a flush inlay is exactly the edit most likely to
     put one back, so this is the check that must pass for all 85 models.
  2. Measure the four features the playtest named, in real units and in SCREEN PIXELS at the distance
     the player sees each one, so the claim is a measurement rather than an intention.

  blender --background --python Art/Blender/subpixel_measure.py -- <repo>
"""
import importlib.util
import math
import os
import sys
from collections import defaultdict

argv = sys.argv[sys.argv.index('--') + 1:]
repo = argv[0]
spec = importlib.util.spec_from_file_location(
    'jckit', os.path.join(repo, 'Art', 'Blender', 'jumpcut_city_kit.py'))
kit = importlib.util.module_from_spec(spec)
sys.modules['jckit'] = kit
spec.loader.exec_module(kit)
kit.build_all()

RENDER_W, FOV, EYE = 1709.0, 90.0, 1.7          # PIE's real render width, horizontal FOV, eye height
HALF = (RENDER_W / 2.0) / math.tan(math.radians(FOV / 2.0))


def px_ground(size_m, horiz_m):
    """Screen pixels for a GROUND feature of the given size, measured across the view direction."""
    slant = math.hypot(EYE, horiz_m)
    return size_m * (EYE / slant) * (HALF / slant)


def px_upright(size_m, horiz_m):
    """Screen pixels for an UPRIGHT feature (a wall, a riser) at that distance."""
    slant = math.hypot(EYE, horiz_m)
    return size_m * (horiz_m / slant) * (HALF / slant)


def px_face_on(size_m, dist_m):
    return size_m * (HALF / dist_m)


# --------------------------------------------------------------- 1. kit-wide z-fight regression check
def tri2d(co, n):
    n = n.normalized()
    u = n.cross(kit.Vector((1, 0, 0)) if abs(n.x) < 0.9 else kit.Vector((0, 1, 0))).normalized()
    v = n.cross(u)
    return [(p.dot(u), p.dot(v)) for p in co]


worst = []
for name, _ in kit.MODELS:
    me = kit.bpy.data.objects[name].data
    planes = defaultdict(list)
    for p in me.polygons:
        nv = p.normal
        if nv.length < 0.5:
            continue
        co = [me.vertices[i].co for i in p.vertices]
        key = (round(nv.x, 3), round(nv.y, 3), round(nv.z, 3), round(nv.dot(co[0]), 4))
        planes[key].append((p.material_index, co, nv))
    area = 0.0
    for key, fs in planes.items():
        if len({m for m, _, _ in fs}) < 2:
            continue
        for i in range(len(fs)):
            for j in range(i + 1, len(fs)):
                if fs[i][0] == fs[j][0]:
                    continue
                a, b = tri2d(fs[i][1], fs[i][2]), tri2d(fs[j][1], fs[j][2])
                for ta in ([a] if len(a) == 3 else [a[:3], [a[0], a[2], a[3]]]):
                    for tb in ([b] if len(b) == 3 else [b[:3], [b[0], b[2], b[3]]]):
                        area += kit._tri_overlap(ta, tb)
    if area > 1e-6:
        worst.append((area * 1e4, name))

print('== Z-FIGHT REGRESSION (coplanar, same-facing, different material, inside one mesh) ==')
if worst:
    for a, n in sorted(worst, reverse=True):
        print('   FAIL %-22s %10.1f cm2' % (n, a))
else:
    print('   PASS  0.00 cm2 of tied face area across all %d models' % len(kit.MODELS))
print()


# ------------------------------------------------------------------- 2. the four named features
def faces_of(name):
    me = kit.bpy.data.objects[name].data
    return me, [(p.material_index, p.normal, [me.vertices[i].co for i in p.vertices]) for p in me.polygons]


print('== THE FOUR FEATURES THE PLAYTEST NAMED ==')
print('   (PIE renders %d px wide at %d deg; a feature needs ~2 px to hold still)' % (RENDER_W, FOV))
print()

# --- sidewalk joints: the gap between flag slabs on the top plane, and the groove depth
me, fs = faces_of('SM_Kerb')
tops = sorted({round(c.z, 4) for _, nv, co in fs if nv.z > 0.9 for c in co})
xs = sorted({round(c.x, 4) for _, nv, co in fs if nv.z > 0.9 for c in co})
gaps = sorted({round(xs[i + 1] - xs[i], 4) for i in range(len(xs) - 1)} - {0.0})
print('SM_Kerb   pavement joints')
print('   top planes present     %s m' % tops)
dep = tops[1] - tops[0]            # groove floor -> flag top; tops[2] is the kerb stone, not a joint
print('   groove depth           %.3f m   riser %.2f px upright' % (dep, px_upright(dep, 4.9)))
print('   joint width            %.3f m   %.2f px  (was 0.020 m = %.2f px)'
      % (gaps[0], px_ground(gaps[0], 4.9), px_ground(0.020, 4.9)))

# --- manhole: radii and risers
me, fs = faces_of('SM_Manhole')
rs = sorted({round(math.hypot(c.x, c.y), 4) for _, _, co in fs for c in co})
zs = sorted({round(c.z, 4) for _, nv, co in fs if nv.z > 0.9 for c in co})
print('SM_Manhole   street circle rim')
print('   radii present          %s m' % rs)
print('   rim annulus            %.3f m   %.2f px  (was 0.060 m = %.2f px)'
      % (rs[-1] - rs[0], px_ground(rs[-1] - rs[0], 7.2), px_ground(0.060, 7.2)))
# Measure the two risers from RADIUS and Z directly, not from the up-facing z set. `tube` winds its
# bottom cap up-facing, so that set is {0.0, 0.025} - it contains the buried underside and MISSES the
# centre plate's top at 0.037. Reading it naively reported the outer wall as 0.000 m, i.e. a real 2.5 cm
# feature as absent, which is the most misleading thing a verifier can print.
R = max(math.hypot(v.co.x, v.co.y) for v in me.vertices)
outer_z = [v.co.z for v in me.vertices if abs(math.hypot(v.co.x, v.co.y) - R) < 1e-4]
wall = max(outer_z) - min(outer_z)
plate = max(round(v.co.z, 4) for v in me.vertices) - wall
print('   outer side wall        %.3f m   %.2f px upright  (sunlit metal: the high-contrast feature)'
      % (wall, px_upright(wall, 7.2)))
print('   centre plate riser     %.3f m   %.2f px upright  (dark-on-dark: the tolerated residual)'
      % (plate, px_upright(plate, 7.2)))

# --- chalkboard: is the chalk flush with the board, and is there any relief left at all?
me, fs = faces_of('SM_CafeChalkboard')
front = [(mi, co) for mi, nv, co in fs if nv.y < -0.9]
ys = sorted({round(c.y, 5) for mi, co in front for c in co if -0.08 < c.y < -0.06})
chalk = kit.bpy.data.objects['SM_CafeChalkboard'].data.materials
ci = [m.name for m in chalk].index('MS_CafeWall')
bars = [co for mi, co in front if mi == ci]
hts = sorted({round(max(c.z for c in co) - min(c.z for c in co), 4) for co in bars})
print('SM_CafeChalkboard   the "ladder" behind the register')
print('   front-facing planes    %s m   (one plane = the chalk is inlaid, not proud)' % ys)
rel = max(ys) - min(ys)            # across the BOARD only: frame and chalk ledge are different planes
print('   chalk relief           %.4f m   %.2f px  (was 0.0060 m = %.2f px)'
      % (rel, px_face_on(rel, 6.9), px_face_on(0.0060, 6.9)))
cy = sorted({round(c.y, 5) for mi, co in front if mi == ci for c in co})
by = sorted({round(c.y, 5) for mi, co in front if mi != ci for c in co if -0.08 < c.y < -0.06})
print('   chalk plane / board    %s  /  %s   %s' % (cy, by, 'FLUSH' if cy == by else 'NOT FLUSH'))
print('   chalk stroke height    %s m   %.2f px' % (hts, px_face_on(hts[0], 6.9)))
print('   chalk faces on board   %d' % len(bars))

# --- drain grate bars
me, fs = faces_of('SM_DrainGrate')
mi_metal = [m.name for m in kit.bpy.data.objects['SM_DrainGrate'].data.materials].index('MS_CityMetal')
bx = sorted({(round(min(c.x for c in co), 4), round(max(c.x for c in co), 4))
             for mi, nv, co in fs if mi == mi_metal and nv.z > 0.9})
print('SM_DrainGrate   road gully bars')
print('   bars                   %d  (was 7)' % len(bx))
if bx:
    print('   bar width              %.3f m   %.2f px  (was 0.042 m = %.2f px)'
          % (bx[0][1] - bx[0][0], px_ground(bx[0][1] - bx[0][0], 7.0), px_ground(0.042, 7.0)))
if len(bx) > 1:
    print('   pitch                  %.3f m   %.2f px  (was 0.070 m = %.2f px)  Nyquist needs > 2 px'
          % (bx[1][0] - bx[0][0], px_ground(bx[1][0] - bx[0][0], 7.0), px_ground(0.070, 7.0)))

# --- fire escape railing
me, fs = faces_of('SM_FireEscape')
mi_trim = [m.name for m in kit.bpy.data.objects['SM_FireEscape'].data.materials].index('MS_CityTrim')
rail = [co for mi, nv, co in fs if mi == mi_trim and nv.y < -0.9
        and 3.2 < min(c.z for c in co) < 4.3 and min(c.x for c in co) > -1.31]
spans = sorted({(round(min(c.z for c in co), 3), round(max(c.z for c in co), 3),
                 round(max(c.x for c in co) - min(c.x for c in co), 3)) for co in rail})
print('SM_FireEscape   railings at a distance (43 m)')
for z0, z1, wx in spans:
    print('   z %5.2f-%5.2f  width %.3f m   %.2f px wide, %.2f px tall'
          % (z0, z1, wx, px_face_on(wx, 42.9), px_face_on(z1 - z0, 42.9)))
print('   was: 8 balusters of 0.030 m = %.2f px wide on a 0.300 m = %.2f px pitch'
      % (px_face_on(0.030, 42.9), px_face_on(0.300, 42.9)))
