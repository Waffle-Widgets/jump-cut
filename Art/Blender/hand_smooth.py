"""Melt a generated mitten hand's ragged ends into one clean closed hand.

    blender -b --factory-startup --python Art/Blender/hand_smooth.py -- IN.fbx OUT.fbx
    env: ITER=40 (smoothing passes), FIST=1.0 (size of the fist against the hand it replaces)

WHY (Sun Nov 15, GameStation, Blender 5.3.0). The coworker's hands "still look crumpled up". They are: Meshy gave
her a fused mitten with shallow grooves and jagged finger ends, and the game's ink outline draws a line down every
jag. She has no fingers to pose, so the honest fix is the shape. Run AFTER hand_body_untangle.py, which leaves every
hand vertex wholly on its palm bone - that is how this knows which vertices are hand.

HOW. Two stages. First each hand vertex moves toward the average of its neighbours, ITER times, with the wrist ring
pinned. That removes the jags and leaves a curled claw. Then (see "A FIST AROUND IT" below) the convex hull of the
hand's vertices replaces the curled faces: a closed, smooth fist on the palm bone. The egg projection in between is
switched off (ROUND=0) and kept only because the comments beside it say why it cannot work. Bones and the rest of
the body are untouched; the hands lose their painted texture for one skin colour.
"""
import bpy, sys, os
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index('--') + 1:]
IN, OUT = argv[0], argv[1]
ITER = int(os.environ.get('ITER', 40)); KEEP = float(os.environ.get('KEEP', 0.92))

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=IN)
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
mesh = max([o for o in bpy.data.objects if o.type == 'MESH'], key=lambda o: len(o.data.vertices))
me = mesh.data
B = arm.data.bones
hands = []; palms = []; fo_name = {}; wr_name = {}
for n in ('Bone_022', 'Bone_027'):
    wr = B[n].children[0].children[0]
    palm = wr
    while len(palm.children) < 3 and palm.children:
        palm = palm.children[0]
    palms.append(palm.name)
    fo_name[palm.name] = B[n].children[0].name; wr_name[palm.name] = wr.name
gi = {g.name: g.index for g in mesh.vertex_groups}
P = np.array([v.co[:] for v in me.vertices], dtype=np.float64)
nb = [[] for _ in me.vertices]
for e in me.edges:
    a, b = e.vertices
    nb[a].append(b); nb[b].append(a)
for palm in palms:
    g = gi[palm]
    H = set()
    for v in me.vertices:
        w = {x.group: x.weight for x in v.groups}
        if w.get(g, 0.0) >= 0.99:
            H.add(v.index)
    # PIN ONLY THE WRIST. The first version pinned every vertex of the hand that touched a non-hand vertex, and the
    # hand has stray non-hand vertices in the middle of it (painted grooves the untangle pass read as cloth). Each one
    # pinned a patch round itself, so the egg never reached the thumb and the hook between thumb and fingers stayed.
    # A wrist vertex is one whose outside neighbour follows the forearm or the wrist bone.
    armset = {gi[x] for x in (fo_name[palm], wr_name[palm]) if x in gi}
    def on_arm(j):
        return any(x.group in armset and x.weight > 0.2 for x in me.vertices[j].groups)
    pinned = {i for i in H if any(j not in H and on_arm(j) for j in nb[i])}
    pinned |= {j for i in pinned for j in nb[i] if j in H}          # and one ring in, so the cuff keeps its shape
    free = sorted(H - pinned)
    if not free:
        print('HANDSMOOTH %s: nothing to smooth' % palm); continue
    c0 = P[free].mean(axis=0); r0 = np.linalg.norm(P[free] - c0, axis=1).mean()
    jag0 = np.mean([np.linalg.norm(P[i] - P[nb[i]].mean(axis=0)) for i in free])
    for _ in range(ITER):
        Q = P.copy()
        for i in free:
            Q[i] = P[i] + 0.6 * (P[nb[i]].mean(axis=0) - P[i])
        P = Q
    # A CLOSED FIST. Smoothing alone left a curled claw with a hook between thumb and fingers: the jags were gone and
    # the shape was still wrong. So each vertex is drawn onto an egg fitted to the hand (its three principal axes, 1.55
    # standard deviations each), fading in over the first few rings from the wrist so the cuff still joins, and then
    # smoothed lightly so nothing crosses. It is what a hand with no fingers reads as: a loose fist.
    depth = {i: 0 for i in pinned}
    front = list(pinned)
    while front:
        nxt = []
        for i in front:
            for j in nb[i]:
                if j in H and j not in depth:
                    depth[j] = depth[i] + 1; nxt.append(j)
        front = nxt
    c1 = P[free].mean(axis=0)
    X = P[free] - c1
    w_, V_ = np.linalg.eigh(np.cov(X.T))
    rad = np.sqrt(np.maximum(w_, 1e-12)) * float(os.environ.get('EGG', 1.55))
    rad[0] = max(rad[0], 0.5 * rad[1])               # a mitten 1 cm thick is paper: at least half as thick as it is wide
    # PROJECT FROM A POINT INSIDE THE HAND, NOT FROM THE AVERAGE OF ITS VERTICES. Her hand is curled, so the average
    # sits in the hollow between thumb and fingers, on or outside the skin. Drawing every vertex outward from there sent
    # neighbours to opposite sides of the egg, and the smoothing pulled those long edges back through the middle: the
    # hook and the creases were still there (measured: vertices from 0.48 to 2.62 egg radii). So the origin is the
    # deepest point inside the solid hand, found on a grid; each vertex goes along its own ray from there to the egg,
    # keeping a little of how far out it was (RELIEF) so a finger that lay over the palm stays on top of it.
    bvh = BVHTree.FromPolygons([tuple(q) for q in P], [tuple(f.vertices) for f in me.polygons])
    best, o = -1.0, c1
    g = np.linspace(-0.7, 0.7, 9)
    for a_ in g:
        for b_ in g:
            for c_ in g:
                cand = c1 + (np.array([a_, b_, c_]) * rad) @ V_.T
                loc, nor, _i, dist = bvh.find_nearest(Vector(cand))
                if loc is not None and (Vector(cand) - loc).dot(nor) < 0 and dist > best:
                    best, o = dist, cand
    print('HANDSMOOTH %s: projecting from a point %.2f cm inside the hand (%.2f cm from the vertex average)' % (palm, best * 100, np.linalg.norm(o - c1) * 100))
    Qp = (X @ V_) / rad
    On = ((o - c1) @ V_) / rad
    D = Qp - On
    a2 = (D * D).sum(axis=1); b2 = (D * On).sum(axis=1); c2 = float(On @ On) - 1.0
    t = (-b2 + np.sqrt(np.maximum(b2 * b2 - a2 * c2, 0.0))) / np.maximum(a2, 1e-12)
    ratio = np.clip(1.0 + float(os.environ.get('RELIEF', 0.12)) * (1.0 / np.maximum(t, 1e-6) - 1.0), 0.85, 1.2)
    Qn = On + D * (t * ratio)[:, None]
    fade = np.array([min(1.0, depth.get(i, 4) / 4.0) for i in free])[:, None] * float(os.environ.get('ROUND', 0.0))
    P[free] = c1 + ((Qp + (Qn - Qp) * fade) * rad) @ V_.T
    def _rr(sel):
        q = np.sqrt(((((P[sel] - c1) @ V_) / rad) ** 2).sum(axis=1)); return '%d verts %.2f..%.2f' % (len(sel), q.min(), q.max())
    deep = [i for i in free if depth.get(i, 4) >= 4]
    for _ in range(3):
        Q = P.copy()
        for i in free:
            Q[i] = P[i] + 0.5 * (P[nb[i]].mean(axis=0) - P[i])
        P = Q
    rr = np.sqrt(((((P[free] - c1) @ V_) / rad) ** 2).sum(axis=1))
    print('HANDSMOOTH %s: after the egg, distance from its centre in egg radii: min %.2f median %.2f max %.2f' % (palm, rr.min(), np.median(rr), rr.max()))
    hands.append((palm, set(H), dict(depth)))
    r1 = np.linalg.norm(P[free] - P[free].mean(axis=0), axis=1).mean(); k = 1.0
    jag1 = np.mean([np.linalg.norm(P[i] - P[nb[i]].mean(axis=0)) for i in free])
    print('HANDSMOOTH %s: %d vertices smoothed, %d pinned at the wrist; average radius %.4f -> %.4f (scaled back x%.2f); roughness %.5f -> %.5f'
          % (palm, len(free), len(pinned), r0, r1, k, jag0, jag1))
for v, p in zip(me.vertices, P):
    v.co = p
me.update()
# A FIST AROUND IT. The egg above is switched off (ROUND=0): her hand is a thin curled shell, so there is no point
# inside it from which the whole skin can be seen, and every projection covered only part of the egg - the hook stayed
# however the origin was chosen (three tries). What a hand with no fingers CAN honestly be is a loose fist: the convex
# hull of the hand's own vertices, skinned wholly to the palm bone, painted with one clean skin texel. The old curled
# faces inside it are deleted (the ring that joins the forearm stays, and the hull overlaps it), so nothing pokes through.
import bmesh
img = max(bpy.data.images, key=lambda i: i.size[0] * i.size[1])
iw, ih = img.size
px = np.empty(iw * ih * 4, dtype=np.float32); img.pixels.foreach_get(px); px = px.reshape(ih, iw, 4)
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
uvl = bm.loops.layers.uv.verify(); dl = bm.verts.layers.deform.verify()
old_all = []
for palm, H, depth in hands:
    bm.verts.ensure_lookup_table()
    cands = []
    for i in H:
        v = bm.verts[i]
        if not v.link_loops: continue
        u, w = v.link_loops[0][uvl].uv
        x, y = min(iw - 5, max(4, int(u * iw))), min(ih - 5, max(4, int(w * ih)))
        patch = px[y - 4:y + 5, x - 4:x + 5, :3]
        cands.append((float(patch.mean()), float(patch.std()), (u, w)))
    lum = np.median([c[0] for c in cands])
    skin_uv = min((c for c in cands if c[0] >= lum), key=lambda c: c[1])[2]
    src = [bm.verts[i] for i in H]
    mat = src[0].link_faces[0].material_index
    hb = bmesh.new()
    hv = [hb.verts.new(v.co) for v in src]
    res = bmesh.ops.convex_hull(hb, input=hv)
    bmesh.ops.delete(hb, geom=[v for v in hb.verts if not v.link_faces], context='VERTS')
    bmesh.ops.subdivide_edges(hb, edges=[e for e in hb.edges if e.calc_length() > 0.012], cuts=2, use_grid_fill=True)
    bmesh.ops.triangulate(hb, faces=list(hb.faces))
    c = sum((v.co for v in hb.verts), Vector()) / len(hb.verts)
    r0 = sum((v.co - c).length for v in hb.verts) / len(hb.verts)
    for _ in range(8):
        bmesh.ops.smooth_vert(hb, verts=list(hb.verts), factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    c2 = sum((v.co for v in hb.verts), Vector()) / len(hb.verts)
    r1 = sum((v.co - c2).length for v in hb.verts) / len(hb.verts)
    for v in hb.verts:
        v.co = c + (v.co - c2) * (r0 / r1) * float(os.environ.get('FIST', 1.0))
    bmesh.ops.recalc_face_normals(hb, faces=list(hb.faces))
    made = {}
    for v in hb.verts:
        nv = bm.verts.new(v.co); nv[dl][gi[palm]] = 1.0; made[v] = nv
    hull_f = []
    for f in hb.faces:
        nf = bm.faces.new([made[v] for v in f.verts]); nf.smooth = True; nf.material_index = mat
        for l in nf.loops:
            l[uvl].uv = skin_uv
        hull_f.append(nf)
    hull_v = list(made.values()); hb.free()
    hs = set(hull_f)
    old = [f for f in bm.faces if f not in hs and all(v.index >= 0 and v.index in H for v in f.verts)]
    print('HANDSMOOTH %s: fist of %d vertices and %d faces around the hand, skin texel at uv %.3f %.3f; %d curled faces inside it removed' % (palm, len(hull_v), len(hull_f), skin_uv[0], skin_uv[1], len(old)))
    old_all += old
bmesh.ops.delete(bm, geom=old_all, context='FACES')
bm.to_mesh(me); bm.free(); me.update()
arm.name = 'Armature'; arm.data.name = 'Armature'
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True); arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, add_leaf_bones=False, bake_anim=False,
                         mesh_smooth_type='FACE', path_mode='COPY', embed_textures=True)
print('HANDSMOOTH exported ' + OUT)
