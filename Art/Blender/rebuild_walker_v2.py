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
# WELD FIRST. Meshy's GLB splits a vertex per UV island, so the surface is topologically full of seams and
# DECIMATE cannot collapse across them - it bridges instead, leaving long thin triangles. Measured on the
# first run: 486 triangles with an edge over 8 cm, up to 20 cm, all round the waist and apron, which render
# in Unreal as a dark smear hanging off the apron to the floor. The shipped mesh has zero. UVs live on
# LOOPS, not vertices, so welding coincident vertices keeps every island intact.
bmw = bmesh.new()
bmw.from_mesh(hi.data)
v_before = len(bmw.verts)
bmesh.ops.remove_doubles(bmw, verts=bmw.verts[:], dist=1e-5)
R['weld_verts'] = [v_before, len(bmw.verts)]
bmw.to_mesh(hi.data)
bmw.free()
hi.data.update()
hi.data.calc_loop_triangles()
print('WELD %d -> %d verts' % tuple(R['weld_verts']))

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

# SAMPLE WITH THE NORMAL, not just the distance. The apron hangs a few millimetres in front of the
# trousers and the field is completely different on the two surfaces - up to 24 cm apart. Plain nearest
# surface lets one vertex of a triangle snap to the apron and its neighbour to the leg behind it, and the
# triangle is then stretched across the gap: 486 triangles with edges up to 20 cm on the first run, which
# read in Unreal as a dark smear hanging off the apron. Restricting the search to faces that face the same
# way as the vertex keeps each surface sampling itself.
inv = hi.matrix_world.inverted()
nrm = {v.index: v.normal.copy() for v in hi.data.vertices}
moved = []
fallback = 0
for v in hi.data.vertices:
    p = hi.matrix_world @ v.co
    vn = (hi.matrix_world.to_3x3() @ nrm[v.index]).normalized()
    best = None
    for loc, nor, idx, dist in lbvh.find_nearest_range(p, 0.05):
        if idx is None or nor is None:
            continue
        if nor.normalized().dot(vn) < 0.3:
            continue
        if best is None or dist < best[3]:
            best = (loc, nor, idx, dist)
    if best is None:
        fallback += 1
        best = lbvh.find_nearest(p)
    loc, nor, idx, dist = best
    if idx is None:
        moved.append(0.0)
        continue
    ia, ib, ic = ltris[idx]
    wa, wb, wc = bary(loc, lp[ia], lp[ib], lp[ic])
    d = field[ia] * wa + field[ib] * wb + field[ic] * wc
    v.co = inv @ (p + d)
    moved.append(d.length)
R['field_fallback_verts'] = fallback
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

# ------------------------------------------------------------------ 4b. nothing may ride the ROOT bone
# Bone_000 sits at pelvis height in the rest pose and on the FLOOR in every retargeted clip, so a vertex weighted
# to it is dragged toward the floor by (weight x 90 cm): the apron's waist tie streaked down to the ground between
# his feet. Bone_001 is its only child, starts in the same place and stays at the pelvis, so it takes the weight.
# (root_weight_to_hip.py is the same step for an FBX that is already built; it also verifies nothing else moved.)
_root, _hip = hi.vertex_groups.get('Bone_000'), hi.vertex_groups.get('Bone_001')
if _root is not None and _hip is not None:
    _moved = 0
    for v in hi.data.vertices:
        w0 = next((g.weight for g in v.groups if g.group == _root.index), 0.0)
        if w0 > 0.0:
            _hip.add([v.index], w0, 'ADD')
            _root.remove([v.index])
            _moved += 1
    R['root_weight_moved_to_hip_verts'] = _moved
    print('ROOT->HIP moved root weight on %d vertices' % _moved)

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

# A decimate is adaptive, so a LONG triangle is normal - it means a flat region, and the apron panel
# legitimately carries edges around 19 cm where Meshy's uniform remesh has none over 8. What is never
# normal is a long THIN one: that is a collapse that bridged a gap, and it renders as a smear. So judge
# by aspect ratio (longest edge / the height of the triangle on it), not by length.
hi.data.calc_loop_triangles()
longest = 0.0
slivers = 0
for t in hi.data.loop_triangles:
    a, b, c = (hi.matrix_world @ hi.data.vertices[i].co for i in t.vertices)
    e = max((a - b).length, (b - c).length, (c - a).length)
    longest = max(longest, e)
    area = (b - a).cross(c - a).length * 0.5
    if area > 1e-12 and e / (2.0 * area / e) > 25.0:
        slivers += 1
R['slivers_aspect_over_25'] = slivers
R['sliver_pct'] = 100.0 * slivers / max(1, len(hi.data.loop_triangles))
R['longest_edge_cm'] = longest * 100
print('SLIVERS aspect>25: %d (%.2f%%)   longest edge %.1f cm'
      % (slivers, R['sliver_pct'], longest * 100))
# Measured baselines at 55,679 triangles: Meshy's uniform remesh 0.06%, the V1 body 0.28%, this decimate
# 1.31% welded (2.21% unwelded). A decimate is adaptive so it is always worse here; it is reported rather
# than refused because the asset thumbnail - the mesh and its material with no level and no editor sprites
# in the frame - renders clean. Watch the number: a jump means the collapse started bridging gaps.
if R['sliver_pct'] > 4.0:
    raise SystemExit('REFUSING: %.2f%% needle triangles - the decimate is bridging gaps' % R['sliver_pct'])

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
