"""Rebuild SK_CafeCoworkerV2 from Meshy's high-poly, keeping the high-poly's OWN UVs and texture.

    blender -b -noaudio --python rebuild_coworker_v2.py -- HI.glb SHIPPED.fbx OUT.fbx OUTTEX.png [TRIS]

    HI       Meshy-AI-Teal-Apron-Welcome-1114220918-texture.glb  (383,852 tris, packed Image_0 2048x2048)
             NOT the Open-Armed-Barista GLB - that one (365,038 tris) is the player.
    SHIPPED  Meshy-AI-Teal-Apron-Welcome-20261114-character-meshyrig.fbx, which is byte-for-byte what
             SK_CafeCoworkerV2.fbx was before this script replaced it (56,498 tris, 28 bones).
             Keep a copy: this script needs it as the source of the armature and the skin weights.

jump-cut: the shipped coworker's base colour was BAKED from the high-poly onto the remeshed low-poly's
regenerated UVs, and the bake is lossy (stair-stepped island edges, torn fringe, shredded collar, skin
streaks down the trousers, navy bleeding onto the arms). It was never necessary: the high-poly GLB has its
own clean UVs and texture and a Blender DECIMATE (COLLAPSE) keeps both. Same idea as fit_rig_to_mesh.py
did for the player - but the coworker keeps Meshy's own 28-bone armature, which already matches her pose,
so there is NO rig refit here.

    1.  decimate the UNWELDED high-poly, then stitch the UV seams shut   (see the long note at step 1 -
        welding first, as the brief suggested, smears the atlas across every seam)
    1b. measure the result against the high-poly: colour under every triangle, facing, open borders
    2.  seat it on the shipped frame (uniform scale + translation, least squares on nearest-surface pairs)
    3.  copy the skin weights from the shipped mesh (nearest surface point, barycentric), max 4 influences
    4.  bind to the shipped armature, export

Knobs (environment): JC_ATTEMPTS (tries at hitting the triangle count, default 6), JC_NORMALS
(welded | glb | auto, default welded), JC_NSMOOTH (normal relaxation passes, default 3), JC_DEBUG.

Two things this script does differently from fit_rig_to_mesh.py ON PURPOSE:
  * the texture is written as a REAL PNG. img.save() on a packed image writes the packed JPEG bytes under
    whatever name it is given, so T_CafeWalkerV2_BaseColor.png is in fact a JPEG.
  * the FBX does not embed textures; the material is named after the shipped slot and points at OUTTEX.
"""
import bpy, bmesh, sys, os, json
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from mathutils.interpolate import poly_3d_calc

argv = sys.argv[sys.argv.index("--") + 1:]
HI, SHIPPED, OUT, OUTTEX = argv[0], argv[1], argv[2], argv[3]
TARGET_TRIS = int(argv[4]) if len(argv) > 4 else 56498
MAX_INFLUENCES = 4
REPORT = {'input_glb': HI, 'input_fbx': SHIPPED}


def co_np(me):
    a = np.empty(len(me.vertices) * 3, dtype=np.float32)
    me.vertices.foreach_get('co', a)
    return a.reshape(-1, 3).astype(np.float64)


def set_co(me, a):
    me.vertices.foreach_set('co', np.ascontiguousarray(a, dtype=np.float32).ravel())
    me.update()


def tri_count(me):
    me.calc_loop_triangles()
    return len(me.loop_triangles)


def uv_stats(me):
    """(islands, total UV area). Islands = connected components of faces joined through a shared
    (vertex, uv) corner, so it is meaningful both before and after the seam vertices are welded."""
    me.calc_loop_triangles()
    nl = len(me.loops)
    uv = np.empty(nl * 2, dtype=np.float32)
    me.uv_layers.active.data.foreach_get('uv', uv)
    uv = uv.reshape(-1, 2).astype(np.float64)
    lv = np.empty(nl, dtype=np.int32)
    me.loops.foreach_get('vertex_index', lv)
    tl = np.empty(len(me.loop_triangles) * 3, dtype=np.int32)
    me.loop_triangles.foreach_get('loops', tl)
    tl = tl.reshape(-1, 3)
    a, b, c = uv[tl[:, 0]], uv[tl[:, 1]], uv[tl[:, 2]]
    area = float(np.abs((b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (c[:, 0] - a[:, 0]) * (b[:, 1] - a[:, 1])).sum() / 2)
    # corner id = unique (vertex, quantised uv)
    key = np.stack([lv.astype(np.int64), np.round(uv[:, 0] * 1e6).astype(np.int64),
                    np.round(uv[:, 1] * 1e6).astype(np.int64)], 1)
    _, cid = np.unique(key, axis=0, return_inverse=True)
    cid = cid.ravel()
    n = int(cid.max()) + 1
    par = list(range(n))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    tc = cid[tl]
    for i0, i1, i2 in tc.tolist():
        r0 = find(i0)
        r1 = find(i1)
        if r1 != r0:
            par[r1] = r0
        r2 = find(i2)
        if r2 != r0:
            par[r2] = r0
    labels = np.array([find(x) for x in tc[:, 0].tolist()], dtype=np.int64)
    _, labels = np.unique(labels, return_inverse=True)
    uv_stats.last = (labels.ravel(), uv[tl], tl)      # island id per triangle, uv per triangle corner, loops
    return int(labels.max()) + 1, area


def topo_stats(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    boundary = sum(1 for e in bm.edges if len(e.link_faces) == 1)
    nonman = sum(1 for e in bm.edges if len(e.link_faces) > 2)
    loose = sum(1 for v in bm.verts if not v.link_faces)
    bm.free()
    return {'boundary_edges': boundary, 'edges_3plus_faces': nonman, 'loose_verts': loose}


def bvh_of(me, pts=None):
    me.calc_loop_triangles()
    if pts is None:
        pts = co_np(me)
    tris = np.empty(len(me.loop_triangles) * 3, dtype=np.int32)
    me.loop_triangles.foreach_get('vertices', tris)
    tris = tris.reshape(-1, 3)
    return BVHTree.FromPolygons([Vector(p) for p in pts.tolist()], tris.tolist()), tris


def smooth_no_custom_normals(me):
    if 'custom_normal' in me.attributes:       # the seam-split normals; let the welded surface shade itself
        me.attributes.remove(me.attributes['custom_normal'])
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    me.update()


bpy.ops.wm.read_factory_settings(use_empty=True)

# ---------------------------------------------------------------- load
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=HI)
new = [o for o in bpy.data.objects if o not in before]
hi = max((o for o in new if o.type == 'MESH'), key=lambda o: len(o.data.vertices))
for o in new:
    if o is not hi:
        bpy.data.objects.remove(o, do_unlink=True)
bpy.context.view_layer.update()
hi.data.transform(hi.matrix_world)          # mesh data = world space; never rely on transform_apply
hi.parent = None
hi.matrix_world = Matrix.Identity(4)
bpy.context.view_layer.update()
me = hi.data

before = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=SHIPPED)
new = [o for o in bpy.data.objects if o not in before]
sh_mesh = next(o for o in new if o.type == 'MESH')
sh_arm = next(o for o in new if o.type == 'ARMATURE')
bpy.context.view_layer.update()
sh_w = np.array([list(sh_mesh.matrix_world @ v.co) for v in sh_mesh.data.vertices])   # bind pose, world space
REPORT['shipped'] = {'tris': tri_count(sh_mesh.data), 'verts': len(sh_mesh.data.vertices),
                     'bones': len(sh_arm.data.bones), 'vgroups': len(sh_mesh.vertex_groups),
                     'bbox_min': sh_w.min(0).round(4).tolist(), 'bbox_max': sh_w.max(0).round(4).tolist()}
shipped_mat_name = 'Material'
if sh_mesh.material_slots and sh_mesh.material_slots[0].material:
    shipped_mat_name = sh_mesh.material_slots[0].material.name

# ---------------------------------------------------------------- the high-poly's own base colour
img = None
for mat in me.materials:
    if mat and mat.node_tree:
        for n in mat.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED' and n.inputs['Base Color'].is_linked:
                fn = n.inputs['Base Color'].links[0].from_node
                if fn.type == 'TEX_IMAGE':
                    img = fn.image
if img is None or not img.packed_file:
    raise SystemExit("no packed base colour image on the high-poly")
os.makedirs(os.path.dirname(OUTTEX), exist_ok=True)
raw = bytes(img.packed_file.data)
if raw[:4] == bytes([0x89, 0x50, 0x4E, 0x47]):
    with open(OUTTEX, 'wb') as f:          # already a PNG: write the bytes untouched, no re-encode
        f.write(raw)
    how = 'packed PNG bytes written verbatim'
else:
    # Meshy packs a JPEG. img.save() on a packed image writes the PACKED BYTES whatever file_format says,
    # which leaves a JPEG wearing a .png name (fit_rig_to_mesh.py did exactly that to T_CafeWalkerV2).
    # Copy the decoded pixels into a fresh 8-bit image and save THAT, so the file really is a PNG.
    w, h = img.size
    px = np.empty(w * h * img.channels, dtype=np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(h, w, img.channels)
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[:, :, :min(4, img.channels)] = px[:, :, :4]
    opaque = bool(rgba[:, :, 3].min() > 0.999)
    out_img = bpy.data.images.new('T_out', w, h, alpha=not opaque)
    out_img.colorspace_settings.name = img.colorspace_settings.name
    out_img.pixels.foreach_set(rgba.ravel())
    out_img.filepath_raw = OUTTEX
    out_img.file_format = 'PNG'
    out_img.save()
    how = 'packed %s decoded and written as a real PNG' % ('JPEG' if raw[:2] == bytes([0xFF, 0xD8]) else 'image')
with open(OUTTEX, 'rb') as f:
    if f.read(4) != bytes([0x89, 0x50, 0x4E, 0x47]):
        raise SystemExit("REFUSING: %s is not a PNG" % OUTTEX)
REPORT['texture'] = {'name': img.name, 'size': list(img.size), 'how': how, 'bytes': os.path.getsize(OUTTEX)}
print("TEXTURE %s %dx%d -> %s (%s)" % (img.name, img.size[0], img.size[1], OUTTEX, how))

# ---------------------------------------------------------------- 1. decimate, then stitch the seams
# Meshy's atlas is a tight patchwork: 538 ragged islands packed edge to edge with no gutter to speak of.
# That makes the ORDER of weld and decimate matter a great deal:
#
#   weld -> decimate   watertight, but COLLAPSE happily drags UVs across the seams. A triangle ends up with
#                      corners in two islands and smears whatever lies between them in the atlas over the
#                      surface: dark scratches on the sleeve hems and shoulders, teal flecks on the trousers.
#                      (Tried first. 5,391 of 56,498 triangles straddled a seam. Not shippable.)
#   decimate only      every island keeps its outline, because an unwelded seam is a mesh BOUNDARY and the
#                      decimator preserves boundaries - so the texture stays clean. But the two sides of a
#                      seam are simplified independently, so they no longer share vertices: hairline cracks,
#                      a pinhole at the wrist, and per-island normals that shade the seams as facets.
#
# So: decimate UNWELDED (clean UVs), then stitch. Every boundary vertex is projected onto the boundary edge
# facing it across the seam; that edge is split there (the split interpolates the UVs along the edge, so
# the island outline in the atlas does not move) and the new vertex is welded to the one that asked for it.
# Result: one watertight surface, shared vertices and smooth normals across every seam, UVs untouched.
src = {'tris': tri_count(me), 'verts': len(me.vertices)}
src['uv_islands'], src['uv_area'] = uv_stats(me)
A_lab, A_uv, A_tl = uv_stats.last
A_cn = np.empty(len(me.loops) * 3, dtype=np.float32)      # the normals Meshy shipped in the GLB
me.corner_normals.foreach_get('vector', A_cn)
A_cn = A_cn.reshape(-1, 3).astype(np.float64)[A_tl]       # (ntri, 3, 3)
A_co = co_np(me)
src['bbox_min'], src['bbox_max'] = A_co.min(0).round(4).tolist(), A_co.max(0).round(4).tolist()
src.update(topo_stats(me))
REPORT['highpoly'] = src
print("HIGH-POLY", src)
A_tree, A_tris = bvh_of(me, A_co)
A_n = np.cross(A_co[A_tris[:, 1]] - A_co[A_tris[:, 0]], A_co[A_tris[:, 2]] - A_co[A_tris[:, 0]])
A_n /= np.maximum(np.linalg.norm(A_n, axis=1, keepdims=True), 1e-20)

STITCH_ABS = 0.004 / 0.8685       # 4 mm at shipped scale, in GLB units
SLIVER_DIST = float(os.environ.get('JC_SLIVER', '0.00005'))
SNAP_END = 0.00008                # closer than this to an existing vertex: weld to it, do not split


def stitch_pass(bm, rel, absol):
    bm.verts.index_update()
    bedges = [e for e in bm.edges if e.is_boundary]
    bverts = sorted({v for e in bedges for v in e.verts}, key=lambda v: v.index)   # deterministic
    kd = KDTree(len(bverts))
    for i, v in enumerate(bverts):
        kd.insert(v.co, i)
    kd.balance()
    inc = {v: [e for e in v.link_edges if e.is_boundary] for v in bverts}
    par = {v: v for v in bverts}

    def find(x):
        while par[x] is not x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    splits = {}
    gaps = []
    unmatched = 0
    for v in bverts:
        lmin = min(e.calc_length() for e in inc[v])
        best = None
        for (_, j, _) in kd.find_n(v.co, 16):
            w = bverts[j]
            if w is v:
                continue
            for e in inc[w]:
                if v in e.verts:
                    continue
                a, b = e.verts
                ab = b.co - a.co
                L2 = ab.dot(ab)
                t = 0.0 if L2 < 1e-18 else max(0.0, min(1.0, (v.co - a.co).dot(ab) / L2))
                d = (v.co - (a.co + ab * t)).length
                if best is None or d < best[0]:
                    best = (d, e, t)
        if best is None or best[0] > min(absol, rel * lmin + SNAP_END):
            unmatched += 1
            continue
        d, e, t = best
        gaps.append(d)
        a, b = e.verts
        L = e.calc_length()
        if t * L < SNAP_END or (1 - t) * L < SNAP_END:
            w = a if t < 0.5 else b
            ra, rb = find(v), find(w)
            if ra is not rb:
                par[ra] = rb
        else:
            splits.setdefault(e, []).append((t, v))
    made = 0
    newv = []
    for e, lst in splits.items():
        a, b = e.verts
        a_co, b_co = a.co.copy(), b.co.copy()
        cur_e, cur_a, t_prev = e, a, 0.0
        for t, v in sorted(lst, key=lambda x: x[0]):
            fac = (t - t_prev) / (1.0 - t_prev)
            if fac < 1e-4 or fac > 1 - 1e-4:
                tgt = cur_a if fac < 0.5 else b
                ra, rb = find(v), find(tgt)
                if ra is not rb:
                    par[ra] = rb
                continue
            _, nv = bmesh.utils.edge_split(cur_e, cur_a, fac)
            want = a_co.lerp(b_co, t)
            assert (nv.co - want).length < 1e-5 + 1e-3 * (b_co - a_co).length, "edge_split went the wrong way"
            newv.append((nv, v))
            par[nv] = find(v)
            made += 1
            cur_e = bm.edges.get((nv, b))
            cur_a, t_prev = nv, t
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
    targetmap = {}
    for nv, v in newv:
        nv.co = v.co
    for v in list(par.keys()):
        r = find(v)
        if r is not v:
            targetmap[v] = r
    bmesh.ops.weld_verts(bm, targetmap=targetmap)
    g = np.array(gaps) if gaps else np.zeros(1)
    return {'boundary_verts': len(bverts), 'boundary_edges_before': len(bedges), 'edge_splits': made,
            'unmatched_boundary_verts': unmatched,
            'boundary_edges_after': sum(1 for e in bm.edges if e.is_boundary),
            'nonmanifold_after': sum(1 for e in bm.edges if len(e.link_faces) > 2),
            'gap_mean_mm_shipped_scale': float(g.mean() * 868.5),
            'gap_p95_mm_shipped_scale': float(np.percentile(g, 95) * 868.5),
            'gap_max_mm_shipped_scale': float(g.max() * 868.5)}


def stitch(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    passes = []
    # the first pass closes nearly everything; the later ones only see what it left open, so they can
    # afford a looser match without any risk of pinching two unrelated borders together
    for rel, absol in ((0.45, STITCH_ABS), (0.45, STITCH_ABS), (1.0, STITCH_ABS / 2), (1.0, STITCH_ABS / 2)):
        passes.append(stitch_pass(bm, rel, absol))
        if passes[-1]['boundary_edges_after'] == 0:
            break
    # What is left is slivers. Three kinds, handled in turn and repeated until nothing changes:
    #   border vertices that all but touch          -> merge by distance (border vertices only)
    #   a FLAP: a triangle hanging off the surface by one free edge while its other edges sit on edges
    #   that already have their two faces           -> it covers nothing the surface does not; drop it
    #   a pinhole a few edges round                 -> cap it
    # A cap takes its UVs from ONE neighbouring face's island (never two - a triangle with corners in two
    # islands smears the atlas between them across itself, which is the whole bug this script exists for).
    uvl = bm.loops.layers.uv.active
    flaps_removed = filled = 0
    for _ in range(4):
        changed = 0
        bv = list({v for e in bm.edges if e.is_boundary for v in e.verts})
        if bv:
            bmesh.ops.remove_doubles(bm, verts=bv, dist=0.0003 / 0.8685)
        for _ in range(10):
            flaps = [f for f in bm.faces if any(e.is_boundary for e in f.edges)
                     and any(len(e.link_faces) > 2 for e in f.edges)]
            if not flaps:
                break
            changed += len(flaps)
            flaps_removed += len(flaps)
            bmesh.ops.delete(bm, geom=flaps, context='FACES')
        res = bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=30)
        caps = [f for f in res.get('faces', []) if f.is_valid]
        capset = set(caps)
        for f in caps:
            base = None
            for e in sorted(f.edges, key=lambda e: -e.calc_length()):
                nb = [g for g in e.link_faces if g not in capset]
                if nb:
                    base = (e, nb[0])
                    break
            if base is None:
                continue
            e, g = base
            known = {l.vert: l[uvl].uv.copy() for l in g.loops if l.vert in e.verts}
            mid = sum(known.values(), Vector((0.0, 0.0))) / len(known)
            for l in f.loops:
                if l.vert in known:
                    l[uvl].uv = known[l.vert]
                    continue
                cand = [o[uvl].uv for o in l.vert.link_loops if o.face not in capset]
                cand = [c for c in cand if (c - mid).length < 0.02]
                l[uvl].uv = min(cand, key=lambda c: (c - mid).length) if cand else mid
            f.normal_update()
            _, _, fi, _ = A_tree.find_nearest(f.calc_center_median())
            if fi is not None and float(A_n[fi] @ np.array(f.normal)) < 0.0:
                f.normal_flip()
        filled += len(caps)
        changed += len(caps)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
        if not changed:
            break
    stitch.flaps_removed = flaps_removed
    # last resort for a pinhole whose rim is not a simple loop (so it cannot be capped): if the whole rim
    # fits inside 5 mm, pull it shut onto its own centre
    pinched = 0
    for _ in range(3):
        openv = {}
        for e in bm.edges:
            if e.is_boundary:
                for v in e.verts:
                    openv.setdefault(v, []).append(e)
        done, groups = set(), []
        for v0 in sorted(openv, key=lambda v: tuple(v.co)):
            if v0 in done:
                continue
            stack, comp = [v0], []
            done.add(v0)
            while stack:
                v = stack.pop()
                comp.append(v)
                for e in openv[v]:
                    o = e.other_vert(v)
                    if o not in done:
                        done.add(o)
                        stack.append(o)
            cc = np.array([list(v.co) for v in comp])
            if np.linalg.norm(cc.max(0) - cc.min(0)) < 0.005 / 0.8685:
                groups.append((comp, Vector(cc.mean(0))))
        if not groups:
            break
        for comp, c in groups:
            comp = [v for v in comp if v.is_valid]
            if len(comp) > 1:
                bmesh.ops.pointmerge(bm, verts=comp, merge_co=c)
                pinched += 1
        bmesh.ops.dissolve_degenerate(bm, dist=1e-7, edges=bm.edges)
    stitch.pinched = pinched
    # needle triangles left along the stitches have no reliable facing; fold them away
    bmesh.ops.dissolve_degenerate(bm, dist=SLIVER_DIST, edges=bm.edges)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
    # Some triangles now face INTO the body: about 150 straight out of Blender's decimate (it folds the odd
    # triangle over next to a border) and about 300 needle slivers from the stitching, 0.4 mm2 typical.
    # The high-poly has none. Unreal culls back faces, so each would be a pinhole in game, and Blender
    # negates the shading normal on them, which is what made the clay render look pock-marked. They are
    # in the right PLACE - only the winding is wrong - so turn them round.
    turned = 0
    for f in bm.faces:
        f.normal_update()
        _, _, fi, _ = A_tree.find_nearest(f.calc_center_median())
        if fi is not None and float(A_n[fi] @ np.array(f.normal)) < 0.0:
            f.normal_flip()
            turned += 1
    stitch.turned = turned
    seen, dup = set(), []
    for f in bm.faces:
        k = frozenset(v.index for v in f.verts) if False else frozenset(id(v) for v in f.verts)
        if k in seen:
            dup.append(f)
        seen.add(k)
    if dup:
        bmesh.ops.delete(bm, geom=dup, context='FACES')
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
    bm.to_mesh(me)
    bm.free()
    me.update()
    out = dict(passes[0])
    out['edge_splits'] = sum(q['edge_splits'] for q in passes)
    out['passes'] = [(q['boundary_edges_before'], q['boundary_edges_after'], q['edge_splits'], q['nonmanifold_after']) for q in passes]
    out['holes_filled_faces'] = filled
    out['flaps_removed'] = stitch.flaps_removed
    out['pinholes_pulled_shut'] = stitch.pinched
    out['inward_facing_triangles_turned'] = stitch.turned
    out['duplicate_faces_removed'] = len(dup)
    return out


def opposing(m):
    """triangles whose facing disagrees with the high-poly surface under them -> (count, total mm2)"""
    co = co_np(m)
    m.calc_loop_triangles()
    tr = np.empty(len(m.loop_triangles) * 3, dtype=np.int32)
    m.loop_triangles.foreach_get('vertices', tr)
    tr = tr.reshape(-1, 3)
    n = np.cross(co[tr[:, 1]] - co[tr[:, 0]], co[tr[:, 2]] - co[tr[:, 0]])
    area = np.linalg.norm(n, axis=1) / 2 * (868.5 ** 2)
    cen = co[tr].mean(1)
    bad = np.zeros(len(tr), dtype=bool)
    for t, c in enumerate(cen.tolist()):
        _, _, fi, _ = A_tree.find_nearest(Vector(c))
        bad[t] = float(A_n[fi] @ n[t]) < 0.0
    return int(bad.sum()), float(area[bad].sum()), int((bad & (area > 1.0)).sum())


me_src = me
if os.environ.get('JC_DEBUG'):
    print("  DEBUG opposing in the HIGH-POLY itself (count, mm2, >1mm2):", opposing(me_src))
first_try = TARGET_TRIS
best = None
MAX_ATTEMPTS = int(os.environ.get('JC_ATTEMPTS', '6'))
for attempt in range(MAX_ATTEMPTS):
    work = me_src.copy()
    hi.data = work
    for m in list(hi.modifiers):
        hi.modifiers.remove(m)
    bpy.context.view_layer.objects.active = hi
    md = hi.modifiers.new("D", 'DECIMATE')
    md.decimate_type = 'COLLAPSE'
    md.ratio = min(1.0, first_try / src['tris'])
    md.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=md.name)
    work = hi.data
    dec_tris, dec_verts = tri_count(work), len(work.vertices)
    if os.environ.get('JC_DEBUG'):
        print('  DEBUG opposing after decimate, before stitch:', opposing(work))
    st = stitch(work)
    got = tri_count(work)
    print("  attempt %d: decimate to %d -> %d tris, stitched -> %d tris (%d splits, %d unmatched)"
          % (attempt, first_try, dec_tris, got, st['edge_splits'], st['unmatched_boundary_verts']))
    if best is None or abs(got - TARGET_TRIS) < abs(best[0] - TARGET_TRIS):
        if best is not None:
            bpy.data.meshes.remove(best[1])
        best = (got, work, dict(st, decimate_target=first_try, decimated_tris=dec_tris, decimated_verts=dec_verts))
    else:
        hi.data = best[1]                   # removing a mesh that an object still uses removes the object
        bpy.data.meshes.remove(work)
    if abs(got - TARGET_TRIS) <= 1:
        break
    first_try += TARGET_TRIS - got
hi.data = best[1]
me = hi.data
REPORT['stitch'] = best[2]
print("STITCH", best[2])
smooth_no_custom_normals(me)
dc = {'tris': tri_count(me), 'verts': len(me.vertices)}
dc['uv_islands'], dc['uv_area'] = uv_stats(me)
dc.update(topo_stats(me))
# anything still open, by size and place, so it can be looked at rather than guessed about
bm = bmesh.new()
bm.from_mesh(me)
openv = {}
for e in bm.edges:
    if e.is_boundary:
        for v in e.verts:
            openv.setdefault(v, []).append(e)
seen, comps = set(), []
for v0 in openv:
    if v0 in seen:
        continue
    stack, comp = [v0], []
    seen.add(v0)
    while stack:
        v = stack.pop()
        comp.append(v)
        for e in openv[v]:
            o = e.other_vert(v)
            if o not in seen:
                seen.add(o)
                stack.append(o)
    cc = np.array([list(v.co) for v in comp])
    comps.append({'verts': len(comp), 'span_mm': round(float(np.linalg.norm(cc.max(0) - cc.min(0)) * 868.5), 2),
                  'at_glb': cc.mean(0).round(3).tolist()})
bm.free()
comps.sort(key=lambda c: -c['span_mm'])
dc['open_borders'] = len(comps)
dc['open_borders_largest'] = comps[:8]
REPORT['decimated'] = dc
print("DECIMATED", dc)

# Shade it like the high-poly. Normals are taken from the WELDED high-poly surface, so every seam shades
# as the continuous surface it is, whatever the local triangulation of a stitch looks like.
tmp = me_src.copy()
bm = bmesh.new()
bm.from_mesh(tmp)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
bm.to_mesh(tmp)
bm.free()
if 'custom_normal' in tmp.attributes:
    tmp.attributes.remove(tmp.attributes['custom_normal'])
tmp.polygons.foreach_set('use_smooth', [True] * len(tmp.polygons))
tmp.update()
REPORT['highpoly_welded'] = dict(verts=len(tmp.vertices), tris=tri_count(tmp), **topo_stats(tmp))
print("HIGH-POLY WELDED (normal source)", REPORT['highpoly_welded'])
W_co = co_np(tmp)
W_tree, W_tris = bvh_of(tmp, W_co)
W_vn = np.empty(len(tmp.vertices) * 3, dtype=np.float32)
tmp.vertices.foreach_get('normal', W_vn)
W_vn = W_vn.reshape(-1, 3).astype(np.float64)
W_fn = np.cross(W_co[W_tris[:, 1]] - W_co[W_tris[:, 0]], W_co[W_tris[:, 2]] - W_co[W_tris[:, 0]])
W_fn /= np.maximum(np.linalg.norm(W_fn, axis=1, keepdims=True), 1e-20)
own = np.empty(len(me.vertices) * 3, dtype=np.float32)
me.vertices.foreach_get('normal', own)
own = own.reshape(-1, 3).astype(np.float64)
cn = np.zeros_like(own)
turned = 0
for vi, pco in enumerate(co_np(me).tolist()):
    pv = Vector(pco)
    loc, _, fi, dd = W_tree.find_nearest(pv)
    if float(W_fn[fi] @ own[vi]) < 0.0:
        alt = None
        for (l2, _, f2, d2) in W_tree.find_nearest_range(pv, dd * 2.0 + 0.003):
            if float(W_fn[f2] @ own[vi]) > 0.3 and (alt is None or d2 < alt[1]):
                alt = (l2, d2, f2)
        if alt:
            loc, fi = alt[0], alt[2]
            turned += 1
    a, b, c = W_tris[fi]
    bw = poly_3d_calc([Vector(W_co[a]), Vector(W_co[b]), Vector(W_co[c])], loc)
    n = bw[0] * W_vn[a] + bw[1] * W_vn[b] + bw[2] * W_vn[c]
    ln = np.linalg.norm(n)
    cn[vi] = n / ln if ln > 1e-9 else own[vi]
NORMALS_FROM = os.environ.get('JC_NORMALS', 'welded')
if NORMALS_FROM == 'glb':
    for vi, pco in enumerate(co_np(me).tolist()):
        pv = Vector(pco)
        loc, _, fi, dd = A_tree.find_nearest(pv)
        if float(A_n[fi] @ own[vi]) < 0.0:
            alt = None
            for (l2, _, f2, d2) in A_tree.find_nearest_range(pv, dd * 2.0 + 0.003):
                if float(A_n[f2] @ own[vi]) > 0.3 and (alt is None or d2 < alt[1]):
                    alt = (l2, d2, f2)
            if alt:
                loc, fi = alt[0], alt[2]
        a, b, c = A_tris[fi]
        bw = poly_3d_calc([Vector(A_co[a]), Vector(A_co[b]), Vector(A_co[c])], loc)
        n = bw[0] * A_cn[fi, 0] + bw[1] * A_cn[fi, 1] + bw[2] * A_cn[fi, 2]
        ln = np.linalg.norm(n)
        cn[vi] = n / ln if ln > 1e-9 else own[vi]
# Relax the normal field a little. A normal read off a 384k sculpt at one of only 28k vertices is a
# point sample of something that wiggles faster than the rebuilt triangles can follow (eye rims, strap
# edges), and interpolating point samples across big triangles shades as dents that are not there.
NSMOOTH = int(os.environ.get('JC_NSMOOTH', '3'))
if NSMOOTH:
    ev = np.empty(len(me.edges) * 2, dtype=np.int32)
    me.edges.foreach_get('vertices', ev)
    ev = ev.reshape(-1, 2)
    deg = np.bincount(ev.ravel(), minlength=len(me.vertices)).astype(np.float64)[:, None]
    for _ in range(NSMOOTH):
        acc = np.zeros_like(cn)
        np.add.at(acc, ev[:, 0], cn[ev[:, 1]])
        np.add.at(acc, ev[:, 1], cn[ev[:, 0]])
        mix = 0.5 * cn + 0.5 * acc / np.maximum(deg, 1.0)
        ln = np.linalg.norm(mix, axis=1, keepdims=True)
        cn = np.where(ln > 1e-9, mix / np.maximum(ln, 1e-9), cn)
if NORMALS_FROM != 'auto':
    me.normals_split_custom_set_from_vertices([tuple(x) for x in cn.tolist()])
me.update()
_lv = np.empty(len(me.loops), dtype=np.int32)
me.loops.foreach_get('vertex_index', _lv)
_cn = np.empty(len(me.loops) * 3, dtype=np.float32)
me.corner_normals.foreach_get('vector', _cn)
_cn = _cn.reshape(-1, 3)
_ang = np.degrees(np.arccos(np.clip((_cn * cn[_lv]).sum(1), -1, 1)))
print("NORMALS stored vs wanted: mean %.3f deg, max %.2f deg; has_custom=%s domain=%s"
      % (_ang.mean(), _ang.max(), me.has_custom_normals, me.normals_domain))
REPORT['normals'] = {'from': 'welded high-poly, barycentric', 'mean_angle_to_own_deg':
                     float(np.degrees(np.arccos(np.clip((cn * own).sum(1), -1, 1))).mean()),
                     'layer_disambiguated': turned}
print("NORMALS", REPORT['normals'])
bpy.data.meshes.remove(tmp)

# ---------------------------------------------------------------- 1b. does the surface still show the same colours?
# Sample four points on every rebuilt triangle; compare the texel its UVs fetch with the texel the high-poly
# shows at the nearest point of ITS surface. This is the number that caught the weld-first smearing.
TEXPX = np.empty(img.size[0] * img.size[1] * img.channels, dtype=np.float32)
img.pixels.foreach_get(TEXPX)
TEXPX = TEXPX.reshape(img.size[1], img.size[0], img.channels)[:, :, :3]


def texel(uv):
    x = np.clip((uv[:, 0] * img.size[0]).astype(np.int64), 0, img.size[0] - 1)
    y = np.clip((uv[:, 1] * img.size[1]).astype(np.int64), 0, img.size[1] - 1)
    return TEXPX[y, x]


_, D_uv, _ = uv_stats.last
D_co = co_np(me)
D_tris = np.empty(len(me.loop_triangles) * 3, dtype=np.int32)
me.loop_triangles.foreach_get('vertices', D_tris)
D_tris = D_tris.reshape(-1, 3)
D_n = np.cross(D_co[D_tris[:, 1]] - D_co[D_tris[:, 0]], D_co[D_tris[:, 2]] - D_co[D_tris[:, 0]])
D_n /= np.maximum(np.linalg.norm(D_n, axis=1, keepdims=True), 1e-20)
BARY = np.array([[1 / 3, 1 / 3, 1 / 3], [.6, .2, .2], [.2, .6, .2], [.2, .2, .6]])
nT = len(D_tris)
S_pos = np.einsum('sk,tkc->tsc', BARY, D_co[D_tris])
S_auv = np.zeros((nT, 4, 2))
for t in range(nT):
    for k in range(4):
        pv = Vector(S_pos[t, k])
        loc, _, fi, dd = A_tree.find_nearest(pv)
        if float(A_n[fi] @ D_n[t]) < 0.2:
            alt = None
            for (l2, _, f2, d2) in A_tree.find_nearest_range(pv, dd * 2.0 + 0.004):
                if float(A_n[f2] @ D_n[t]) > 0.5 and (alt is None or d2 < alt[1]):
                    alt = (l2, d2, f2)
            if alt:
                loc, fi = alt[0], alt[2]
        a, b, c = A_tris[fi]
        bw = poly_3d_calc([Vector(A_co[a]), Vector(A_co[b]), Vector(A_co[c])], loc)
        S_auv[t, k] = bw[0] * A_uv[fi, 0] + bw[1] * A_uv[fi, 1] + bw[2] * A_uv[fi, 2]
# faces that look the wrong way: Unreal culls back faces, so each one of these is a hole in game even
# though Blender (two-sided, custom normals) draws it as if nothing were wrong
opp = np.zeros(nT, dtype=bool)
for t in range(nT):
    _, _, fi, _ = A_tree.find_nearest(Vector(S_pos[t, 0]))
    opp[t] = float(A_n[fi] @ D_n[t]) < 0.0
D_area = np.linalg.norm(np.cross(D_co[D_tris[:, 1]] - D_co[D_tris[:, 0]], D_co[D_tris[:, 2]] - D_co[D_tris[:, 0]]), axis=1) / 2 * (868.5 ** 2)
REPORT['faces_opposing_highpoly'] = {'count': int(opp.sum()),
                                     'area_mm2_median': float(np.median(D_area[opp])) if opp.any() else 0.0,
                                     'area_mm2_p90': float(np.percentile(D_area[opp], 90)) if opp.any() else 0.0,
                                     'area_mm2_total': float(D_area[opp].sum()),
                                     'over_1mm2': int((D_area[opp] > 1.0).sum()),
                                     'all_faces_area_mm2_median': float(np.median(D_area))}
print("FACES OPPOSING the high-poly surface:", REPORT['faces_opposing_highpoly'])
ref = texel(S_auv.reshape(-1, 2)).reshape(nT, 4, 3)
got = texel(np.einsum('sk,tkc->tsc', BARY, D_uv).reshape(-1, 2)).reshape(nT, 4, 3)
err = np.abs(got - ref).max(2)
REPORT['uv_colour_error'] = {'mean': float(err.mean()), 'samples_off_by_0.10': float((err > 0.10).mean()),
                             'samples_off_by_0.25': float((err > 0.25).mean()),
                             'tris_with_a_bad_sample': int((err > 0.25).any(1).sum()),
                             'weld_first_for_comparison': {'mean': 0.0149, 'samples_off_by_0.25': 0.0089,
                                                           'tris_with_a_bad_sample': 1596}}
print("UV COLOUR ERROR vs high-poly:", REPORT['uv_colour_error'])

# ---------------------------------------------------------------- 2. seat onto the shipped frame
# Same body, different unit/origin: GLB is centred and 1.90 m, the rig FBX is feet-at-zero and 1.65 m.
# Bounding box first, then a few rounds of scale+translation least squares on nearest-surface pairs
# (no rotation - the two exports share axes).
sh_tree, sh_tris = bvh_of(sh_mesh.data, sh_w)
pts = co_np(me)
hmin, hmax = pts.min(0), pts.max(0)
smin, smax = sh_w.min(0), sh_w.max(0)
s = (smax[2] - smin[2]) / (hmax[2] - hmin[2])
pts = (pts - (hmin + hmax) / 2) * s + (smin + smax) / 2
S_total, T_total = s, (smin + smax) / 2 - (hmin + hmax) / 2 * s


def residual(p):
    """shipped vertex -> nearest point on the rebuilt surface."""
    set_co(me, p)
    tree, _ = bvh_of(me, p)
    q = np.array([list(tree.find_nearest(Vector(v))[0]) for v in sh_w.tolist()])
    return q, np.linalg.norm(q - sh_w, axis=1)


q, d = residual(pts)
REPORT['seat_bbox_only'] = {'scale': float(s), 'mean_cm': float(d.mean() * 100),
                            'p95_cm': float(np.percentile(d, 95) * 100)}
print("SEAT bbox only : scale %.5f  residual mean %.3f cm  p95 %.3f cm"
      % (s, d.mean() * 100, np.percentile(d, 95) * 100))
for it in range(8):
    keep = d <= np.percentile(d, 90)        # trimmed: genuine remesh differences must not drag the fit
    Q, P = q[keep], sh_w[keep]
    qm, pm = Q.mean(0), P.mean(0)
    ds = float(((Q - qm) * (P - pm)).sum() / ((Q - qm) ** 2).sum())
    dt = pm - ds * qm
    pts = pts * ds + dt
    S_total, T_total = S_total * ds, T_total * ds + dt
    q, d = residual(pts)
REPORT['seat'] = {'scale': float(S_total), 'translation': T_total.tolist(), 'mean_cm': float(d.mean() * 100),
                  'p95_cm': float(np.percentile(d, 95) * 100), 'max_cm': float(d.max() * 100)}
print("SEAT refined   : scale %.5f  T %s  residual mean %.3f cm  p95 %.3f cm  max %.2f cm"
      % (S_total, T_total.round(4).tolist(), d.mean() * 100, np.percentile(d, 95) * 100, d.max() * 100))
set_co(me, pts)
bpy.context.view_layer.update()
chk = np.array([list(hi.matrix_world @ v.co) for v in me.vertices])
assert np.abs(chk - pts).max() < 1e-5, "rebuilt mesh is not where we think it is"
REPORT['out_bbox_min'], REPORT['out_bbox_max'] = chk.min(0).round(4).tolist(), chk.max(0).round(4).tolist()

# ---------------------------------------------------------------- 3. weights: nearest shipped SURFACE point
# Interpolated across the shipped triangle (barycentric), not snapped to a vertex. Where two body parts
# sit close together, prefer a source face that looks the same way as the vertex does.
names = [g.name for g in sh_mesh.vertex_groups]
SW = np.zeros((len(sh_mesh.data.vertices), len(names)))
for v in sh_mesh.data.vertices:
    for g in v.groups:
        SW[v.index, g.group] = g.weight
SW /= np.maximum(SW.sum(1, keepdims=True), 1e-12)
REPORT['source_max_influences'] = int((SW > 1e-4).sum(1).max())
tri_n = np.cross(sh_w[sh_tris[:, 1]] - sh_w[sh_tris[:, 0]], sh_w[sh_tris[:, 2]] - sh_w[sh_tris[:, 0]])
tri_n /= np.maximum(np.linalg.norm(tri_n, axis=1, keepdims=True), 1e-20)
vn = np.empty(len(me.vertices) * 3, dtype=np.float32)
me.vertices.foreach_get('normal', vn)
vn = vn.reshape(-1, 3).astype(np.float64)

W = np.zeros((len(me.vertices), len(names)))
dist = np.zeros(len(me.vertices))
flipped = 0
for vi, p in enumerate(pts.tolist()):
    pv = Vector(p)
    loc, _, fi, dd = sh_tree.find_nearest(pv)
    if float(tri_n[fi] @ vn[vi]) < 0.0:
        best = None
        for (l2, _, f2, d2) in sh_tree.find_nearest_range(pv, dd * 2.0 + 0.01):
            if float(tri_n[f2] @ vn[vi]) > 0.3 and (best is None or d2 < best[3]):
                best = (l2, None, f2, d2)
        if best:
            loc, _, fi, dd = best
            flipped += 1
    a, b, c = sh_tris[fi]
    bw = poly_3d_calc([Vector(sh_w[a]), Vector(sh_w[b]), Vector(sh_w[c])], loc)
    W[vi] = bw[0] * SW[a] + bw[1] * SW[b] + bw[2] * SW[c]
    dist[vi] = dd
# at most MAX_INFLUENCES per vertex, then normalise
order = np.argsort(-W, axis=1)
mask = np.zeros_like(W, dtype=bool)
np.put_along_axis(mask, order[:, :MAX_INFLUENCES], True, axis=1)
W = np.where(mask & (W > 1e-4), W, 0.0)
tot = W.sum(1, keepdims=True)
if (tot <= 0).any():
    raise SystemExit("REFUSING: %d vertices got no weight" % int((tot <= 0).sum()))
W /= tot

hi.vertex_groups.clear()
for gi, name in enumerate(names):
    g = hi.vertex_groups.new(name=name)
    col = W[:, gi]
    for vi in np.nonzero(col)[0].tolist():
        g.add([vi], float(col[vi]), 'REPLACE')
src_used = [names[i] for i in range(len(names)) if SW[:, i].max() > 1e-3]
out_used = [names[i] for i in range(len(names)) if W[:, i].max() > 1e-3]
REPORT['weights'] = {'vgroups': len(names), 'with_weight': len(out_used), 'source_with_weight': len(src_used),
                     'unweighted_groups': [n for n in names if n not in out_used],
                     'source_unweighted_groups': [n for n in names if n not in src_used],
                     'src_dist_mean_cm': float(dist.mean() * 100),
                     'src_dist_p95_cm': float(np.percentile(dist, 95) * 100),
                     'src_dist_max_cm': float(dist.max() * 100), 'normal_disambiguated': flipped,
                     'max_influences': int((W > 0).sum(1).max())}
print("WEIGHTS", REPORT['weights'])
if set(out_used) != set(src_used):
    raise SystemExit("REFUSING TO EXPORT: weighted groups differ from the shipped mesh")

# ---------------------------------------------------------------- 4. bind + export
mat = bpy.data.materials.new('tmp')
mat.use_nodes = True
bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
tex.image = bpy.data.images.load(OUTTEX)
mat.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
me.materials.clear()
me.materials.append(mat)

bpy.data.objects.remove(sh_mesh, do_unlink=True)
for m in [m for m in bpy.data.materials if m is not mat]:
    bpy.data.materials.remove(m)
mat.name = shipped_mat_name                 # keep the slot name Unreal already knows

hi.parent = sh_arm
bpy.context.view_layer.update()
hi.matrix_parent_inverse = sh_arm.matrix_world.inverted()
am = hi.modifiers.new("Armature", 'ARMATURE')
am.object = sh_arm
sh_arm.name = 'Armature'
sh_arm.data.name = 'Armature'
hi.name = 'Mesh0'
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
dg.update()
ev = hi.evaluated_get(dg)
evm = ev.to_mesh()
chk = np.array([list(ev.matrix_world @ v.co) for v in evm.vertices])
ev.to_mesh_clear()
assert np.abs(chk - pts).max() < 1e-4, "binding moved the mesh by %.4f m" % np.abs(chk - pts).max()

bpy.ops.object.select_all(action='DESELECT')
hi.select_set(True)
sh_arm.select_set(True)
bpy.context.view_layer.objects.active = sh_arm
os.makedirs(os.path.dirname(OUT), exist_ok=True)
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, add_leaf_bones=False, bake_anim=False,
                         mesh_smooth_type='FACE', path_mode='RELATIVE', embed_textures=False)
print("EXPORTED " + OUT)
with open(os.path.splitext(OUT)[0] + "_report.json", "w") as f:
    json.dump(REPORT, f, indent=1)
print(json.dumps(REPORT, indent=1))
