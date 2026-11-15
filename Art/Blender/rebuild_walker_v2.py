"""Rebuild SK_CafeWalkerV2 from Meshy's high-poly WITHOUT re-baking a texture and WITHOUT moving the rig.

    blender -b -noaudio --python rebuild_walker_v2.py -- HI.glb MESHYLOW.fbx CONFORMED.fbx OUT.fbx TEX.png [TRIS]

      HI.glb      Meshy's 365k textured high-poly (pre-remesh). Carries its own clean UVs and texture.
      MESHYLOW.fbx  Meshy's rigged 55,679-tri export, in Meshy's NATURAL pose (Art/.../SK_CafeWalkerV2.fbx).
      CONFORMED.fbx The body currently in the game: the same 27,976 vertices, already moved into the
                    69-bone rig's rest pose by conform_rest_pose.py (#117), carrying its weights.

WHAT WAS WRONG WITH THE SHIPPED BODY - two independent faults, and only one of them was ever the rig's.

1. TEXTURE (the loud one: "the apron got all messed up"). Meshy's remesh discards the texture, so PR #112
   BAKED the 365k high-poly's colour onto the remeshed body's regenerated UVs. The bake is lossy: a dark
   blotch smeared across the apron, a sawtooth hem, a mottled white-and-grey collar, speckled waist ties.
   None of that was ever necessary. The high-poly keeps its OWN UVs and its OWN clean texture, and a
   DECIMATE preserves both. So: decimate, don't bake. 0 Meshy credits, and the damage simply never happens.

2. SILHOUETTE. #117 fixed the skinning by deforming the mesh into the rig's rest pose with Meshy's coarse
   28-bone rig. It worked, and it cost: every vertex moved (mean 7.15 cm), the apron gained 7.7 cm of
   front-to-back depth and the shoulders slumped.

WHY THIS DOES NOT SIMPLY MOVE THE BONES INSTEAD. That was the obvious fix and it is wrong, measurably.
Unreal's UAnimSequence tracks are ABSOLUTE LOCAL transforms: playback puts each bone where the clip says
regardless of what the mesh was bound in, and the mesh is skinned (clip pose) * (bind)^-1. So a bind pose
that is not the rest pose the 48 clips were keyed against shows up as extra twist on EVERY frame. Fitting
the rig to the mesh produced a rest pose 75.7 deg from the clip rig's on average, 171 deg at worst, 47 of
69 bones past 20 deg - and it renders beautifully standing still and shreds the head and one arm the moment
Idle plays. rest_delta must read 0.0 deg or the body is broken in motion.

SO: keep the rig exactly as it is, and carry the clean geometry into the pose the rig needs by reusing the
displacement #117 already measured. The conformed body and Meshy's low-poly are the SAME 27,976 vertices in
the same order, so (conformed[i] - natural[i]) is an exact per-vertex field. Sample it at the nearest point
on the low-poly surface and the decimated high-poly lands in the rig's rest pose with no new distortion -
the same silhouette the game has today, minus the bake damage.
"""
import bpy, bmesh, sys, os, json
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

argv = sys.argv[sys.argv.index("--") + 1:]
HI, LOW, CONF, OUT, OUTTEX = argv[:5]
TARGET_TRIS = int(argv[5]) if len(argv) > 5 else 55679
R = {}

EX = (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))


def imp(path, tag, gltf=False):
    before = set(bpy.data.objects)
    (bpy.ops.import_scene.gltf if gltf else bpy.ops.import_scene.fbx)(filepath=path)
    added = [o for o in bpy.data.objects if o not in before]
    for o in added:
        o.name = tag + '_' + o.name
    return added


def world_pts(ob):
    return [ob.matrix_world @ v.co for v in ob.data.vertices]


def bake_matrix(ob, M):
    """transform_apply() silently no-ops in background mode; move the mesh data directly."""
    for v in ob.data.vertices:
        v.co = M @ v.co
    ob.data.update()


def tri_index(ob):
    """Triangles as ORIGINAL vertex indices, plus a BVH over them in world space."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.verts.ensure_lookup_table()
    tris = [[v.index for v in f.verts] for f in bm.faces]
    bm.free()
    pts = world_pts(ob)
    return pts, tris, BVHTree.FromPolygons(pts, tris, all_triangles=True)


def bary(p, a, b, c):
    w = barycentric_transform(p, a, b, c, EX[0], EX[1], EX[2])
    s = w.x + w.y + w.z
    return (w.x / s, w.y / s, w.z / s) if abs(s) > 1e-9 else (1.0, 0.0, 0.0)


bpy.ops.wm.read_factory_settings(use_empty=True)

hi = next(o for o in imp(HI, 'HI', gltf=True) if o.type == 'MESH')
for o in list(bpy.data.objects):
    if o.name.startswith('HI_') and o is not hi:
        bpy.data.objects.remove(o, do_unlink=True)

low_objs = imp(LOW, 'LOW')
low = next(o for o in low_objs if o.type == 'MESH')

conf_objs = imp(CONF, 'CONF')
conf = next(o for o in conf_objs if o.type == 'MESH')
arm = next(o for o in conf_objs if o.type == 'ARMATURE')

if len(low.data.vertices) != len(conf.data.vertices):
    raise SystemExit('REFUSING: %d vs %d vertices - the two bodies are not the same mesh, so there is no '
                     'per-vertex displacement field' % (len(low.data.vertices), len(conf.data.vertices)))
R['field_verts'] = len(low.data.vertices)

# ------------------------------------------------------------------ 1. seat the high-poly onto the low-poly
# Meshy's two exports of one body differ in units and origin (GLB centred and 1.902 m; FBX feet-at-zero and
# 1.75 m). Uniform scale + translation is enough; bake_meshy_basecolor.py gets under 2 mm this way.
hp, lp = world_pts(hi), world_pts(low)


def bbox(p):
    return (Vector((min(v.x for v in p), min(v.y for v in p), min(v.z for v in p))),
            Vector((max(v.x for v in p), max(v.y for v in p), max(v.z for v in p))))


hmin, hmax = bbox(hp)
lmin, lmax = bbox(lp)
s = (lmax.z - lmin.z) / (hmax.z - hmin.z)
hi.matrix_world = Matrix.Identity(4)
bake_matrix(hi, Matrix.Translation(((lmin + lmax) / 2.0) - ((hmin + hmax) / 2.0) * s)
            @ Matrix.Diagonal((s, s, s, 1.0)))
R['seat_scale'] = s

from mathutils.kdtree import KDTree
hp = world_pts(hi)
kd = KDTree(len(hp))
for i, p in enumerate(hp):
    kd.insert(p, i)
kd.balance()
step = max(1, len(lp) // 3000)
res = [kd.find(p)[2] for p in lp[::step]]
R['seat_residual_mean_cm'] = sum(res) / len(res) * 100
R['seat_residual_p95_cm'] = sorted(res)[int(len(res) * 0.95)] * 100
print('SEAT scale=%.5f residual mean=%.2f mm p95=%.2f mm'
      % (s, R['seat_residual_mean_cm'] * 10, R['seat_residual_p95_cm'] * 10))

# ------------------------------------------------------------------ 2. decimate, keeping the high-poly's UVs
tris_in = len(hi.data.loop_triangles) or sum(len(p.vertices) - 2 for p in hi.data.polygons)
R['tris_source'] = tris_in
mod = hi.modifiers.new('dec', 'DECIMATE')
mod.decimate_type = 'COLLAPSE'
mod.ratio = min(1.0, float(TARGET_TRIS) / float(tris_in))
dg = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(hi.evaluated_get(dg))
hi.modifiers.remove(mod)
hi.data = me
hi.data.update()
hi.data.calc_loop_triangles()
R['tris_out'] = len(hi.data.loop_triangles)
R['verts_out'] = len(hi.data.vertices)
print('DECIMATE %d -> %d tris, %d verts' % (tris_in, R['tris_out'], R['verts_out']))
if not hi.data.uv_layers:
    raise SystemExit('REFUSING: the decimated high-poly has no UV layer - its own texture cannot be applied')

# ------------------------------------------------------------------ 3. carry it into the rig's rest pose
lp, ltris, lbvh = tri_index(low)
cp = world_pts(conf)
field = [cp[i] - lp[i] for i in range(len(lp))]
fl = sorted(v.length for v in field)
R['field_mean_cm'] = sum(fl) / len(fl) * 100
R['field_max_cm'] = fl[-1] * 100

moved = []
for v in hi.data.vertices:
    p = hi.matrix_world @ v.co
    loc, nor, idx, dist = lbvh.find_nearest(p)
    if idx is None:
        moved.append(0.0)
        continue
    a, b, c = (lp[i] for i in ltris[idx])
    wa, wb, wc = bary(loc, a, b, c)
    ia, ib, ic = ltris[idx]
    d = field[ia] * wa + field[ib] * wb + field[ic] * wc
    v.co = hi.matrix_world.inverted() @ (p + d)
    moved.append(d.length)
hi.data.update()
moved.sort()
R['applied_mean_cm'] = sum(moved) / len(moved) * 100
R['applied_max_cm'] = moved[-1] * 100
print('FIELD applied: mean %.2f cm  max %.2f cm  (source field mean %.2f cm max %.2f cm)'
      % (R['applied_mean_cm'], R['applied_max_cm'], R['field_mean_cm'], R['field_max_cm']))

# ------------------------------------------------------------------ 4. weights, from the body in that pose
cpts, ctris, cbvh = tri_index(conf)
names = [g.name for g in conf.vertex_groups]
cw = [{} for _ in range(len(cpts))]
for vi, v in enumerate(conf.data.vertices):
    for g in v.groups:
        if g.weight > 1e-4:
            cw[vi][g.group] = g.weight

hi.vertex_groups.clear()
groups = [hi.vertex_groups.new(name=n) for n in names]
src_d = []
for v in hi.data.vertices:
    p = hi.matrix_world @ v.co
    loc, nor, idx, dist = cbvh.find_nearest(p)
    if idx is None:
        continue
    src_d.append(dist)
    a, b, c = (cpts[i] for i in ctris[idx])
    ws = bary(loc, a, b, c)
    acc = {}
    for w, vi in zip(ws, ctris[idx]):
        for gi, gw in cw[vi].items():
            acc[gi] = acc.get(gi, 0.0) + w * gw
    tot = sum(acc.values())
    if tot <= 1e-6:
        continue
    for gi, gw in acc.items():
        groups[gi].add([v.index], gw / tot, 'REPLACE')
src_d.sort()
R['weight_src_dist_mean_cm'] = sum(src_d) / len(src_d) * 100
R['vgroups'] = len(names)
R['vgroups_with_weight'] = sum(1 for g in groups
                               if any(g.index in {gr.group for gr in v.groups} for v in hi.data.vertices))
print('WEIGHTS %d groups, %d carry weight, source distance mean %.2f cm'
      % (R['vgroups'], R['vgroups_with_weight'], R['weight_src_dist_mean_cm']))

# ------------------------------------------------------------------ 5. bind to the UNTOUCHED rig
for o in (low, conf):
    bpy.data.objects.remove(o, do_unlink=True)
hi.parent = arm
hi.matrix_parent_inverse = arm.matrix_world.inverted()
m = hi.modifiers.new('Armature', 'ARMATURE')
m.object = arm
hi.name = 'SK_CafeWalkerV2'
# Unreal makes the armature OBJECT's name the root bone, and refuses to merge a bone tree whose root does
# not match the skeleton's. It is NOT a fatal import: the mesh is still created and still reports the
# skeleton you asked for. Only the engine log says otherwise. (PR #112.)
arm.name = 'Armature'
arm.data.name = 'Armature'

# ------------------------------------------------------------------ 6. the high-poly's own texture
img = None
for mat in hi.data.materials:
    if mat and mat.use_nodes:
        for n in mat.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                ln = n.inputs['Base Color'].links
                if ln and ln[0].from_node.type == 'TEX_IMAGE':
                    img = ln[0].from_node.image
if img is None:
    raise SystemExit('could not find the base colour image on the high-poly')
img.filepath_raw = OUTTEX
img.file_format = 'PNG'
img.save()
R['texture'] = list(img.size)
print('TEXTURE saved %s (%dx%d)' % (OUTTEX, img.size[0], img.size[1]))

# ------------------------------------------------------------------ 7. report + export
pts = world_pts(hi)
R['height_cm'] = (max(p.z for p in pts) - min(p.z for p in pts)) * 100
R['feet_z_cm'] = min(p.z for p in pts) * 100
R['bbox_x_cm'] = [min(p.x for p in pts) * 100, max(p.x for p in pts) * 100]
R['bbox_y_cm'] = [min(p.y for p in pts) * 100, max(p.y for p in pts) * 100]

bpy.ops.object.select_all(action='DESELECT')
hi.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, add_leaf_bones=False, bake_anim=False,
                         mesh_smooth_type='FACE', path_mode='COPY', embed_textures=True)
print('EXPORTED ' + OUT)
with open(os.path.splitext(OUT)[0] + '_report.json', 'w') as f:
    json.dump(R, f, indent=1)
print(json.dumps(R, indent=1))
