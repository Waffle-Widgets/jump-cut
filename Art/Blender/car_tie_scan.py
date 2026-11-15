# Coplanar-tie scan for ONE exported kit FBX, plus its bounds and triangle count.
#
# Why this exists (2026-11-15, "the car is flickering badly"): #67 was caused by the city kit
# drawing a detail FLUSH with the surface it sits on - two faces of different materials on one
# plane facing the same way, which ties in the depth test and breaks differently every frame the
# camera moves. `stand_proud()` in the kit's finish() cured it for the 41 meshes that were
# re-imported on Nov 14. GC_CrashCar was cut from SM_CrashCar, and a Geometry Collection EMBEDS a
# copy of the geometry at cut time - so if it was cut from the pre-fix mesh, the car on screen is
# still the flush one while the static mesh beside it is fixed. This script measures the two FBX
# revisions so the GC's own bounds can decide which one it carries.
#
# Usage: blender -b --factory-startup --python Art/Blender/car_tie_scan.py -- <file.fbx> [tag]
import bpy, sys, json, math
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
path = argv[0]
tag = argv[1] if len(argv) > 1 else path

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=path)

PLANE_TOL = 1e-4          # metres: how close two planes must be to count as the same plane
NORMAL_TOL = 1e-3         # 1 - dot(n1, n2)

out = {'tag': tag, 'file': path, 'objects': []}

for ob in [o for o in bpy.context.scene.objects if o.type == 'MESH']:
    me = ob.data
    me.calc_loop_triangles()
    mw = ob.matrix_world
    verts = [mw @ v.co for v in me.vertices]
    lo = Vector((min(v.x for v in verts), min(v.y for v in verts), min(v.z for v in verts)))
    hi = Vector((max(v.x for v in verts), max(v.y for v in verts), max(v.z for v in verts)))

    faces = []
    for p in me.polygons:
        n = (mw.to_3x3() @ p.normal).normalized()
        pts = [verts[i] for i in p.vertices]
        c = sum(pts, Vector((0, 0, 0))) / len(pts)
        faces.append({'n': n, 'd': n.dot(c), 'pts': pts, 'mat': p.material_index,
                      'area': p.area, 'c': c})

    # bucket faces by quantised plane so the pair scan stays cheap
    buckets = {}
    for i, f in enumerate(faces):
        key = (round(f['n'].x, 3), round(f['n'].y, 3), round(f['n'].z, 3), round(f['d'], 4))
        buckets.setdefault(key, []).append(i)

    tied_area = 0.0
    tied_pairs = 0
    worst = []
    for key, idxs in buckets.items():
        if len(idxs) < 2:
            continue
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                fa, fb = faces[idxs[a]], faces[idxs[b]]
                if fa['mat'] == fb['mat']:
                    continue                      # same flat colour either way - left alone
                if 1.0 - fa['n'].dot(fb['n']) > NORMAL_TOL:
                    continue                      # opposite facing: not a tie, a back face
                if abs(fa['d'] - fb['d']) > PLANE_TOL:
                    continue
                # 2D overlap of the two polygons projected into the shared plane
                n = fa['n']
                u = n.cross(Vector((0, 0, 1)))
                if u.length < 1e-6:
                    u = n.cross(Vector((1, 0, 0)))
                u.normalize()
                v = n.cross(u)
                def box(f):
                    xs = [p.dot(u) for p in f['pts']]
                    ys = [p.dot(v) for p in f['pts']]
                    return min(xs), max(xs), min(ys), max(ys)
                ax0, ax1, ay0, ay1 = box(fa)
                bx0, bx1, by0, by1 = box(fb)
                ox = min(ax1, bx1) - max(ax0, bx0)
                oy = min(ay1, by1) - max(ay0, by0)
                if ox <= 1e-6 or oy <= 1e-6:
                    continue
                tied_pairs += 1
                tied_area += ox * oy
                worst.append({'mats': [fa['mat'], fb['mat']],
                              'overlap_cm2': round(ox * oy * 10000, 2),
                              'at': [round(fa['c'].x, 4), round(fa['c'].y, 4), round(fa['c'].z, 4)]})

    worst.sort(key=lambda w: -w['overlap_cm2'])
    out['objects'].append({
        'name': ob.name,
        'tris': len(me.loop_triangles),
        'polys': len(me.polygons),
        'verts': len(me.vertices),
        'mats': [m.name if m else None for m in me.materials],
        'bounds_min': [round(c, 5) for c in lo],
        'bounds_max': [round(c, 5) for c in hi],
        'size': [round(hi[i] - lo[i], 5) for i in range(3)],
        'tied_pairs': tied_pairs,
        'tied_area_cm2': round(tied_area * 10000, 2),
        'worst': worst[:8],
    })

print('CARSCAN ' + json.dumps(out))
