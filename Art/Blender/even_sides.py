"""Make a generated body's shoulders and arms the same on both sides.

    blender -b --factory-startup --python Art/Blender/even_sides.py -- IN.fbx OUT.fbx [RENDER.png]

WHY (Sun Nov 15, GameStation, Blender 5.3.0). The Team Owner: "his shoulders are not even". The skeleton was level
to a millimetre in the running game. The SURFACE is not: Meshy's model has its right shoulder's cloth about 1 cm
higher than its left and its right sleeve 3 to 4 cm fatter. Tipping the collarbones to hide it tilts the joints (4 cm
at 9 degrees) long before the cloth is level, so the mesh itself has to change.

HOW. In the bind pose, each vertex of the shoulders and arms is mirrored across the body's centre plane and the
nearest point of the surface over there is found. Mirror that point back and it is where this vertex would be if
this side were shaped like the other. Every vertex moves HALF way, so the two sides meet in the middle and neither is
"the right one". The move is clamped, smoothed over the mesh, and faded out toward the chest, the neck and the
hands, so the head (hair parted to one side on purpose), the apron and the towel are left alone. Vertices, faces,
UVs, weights and bones are untouched; only positions change.
"""
import bpy, sys, bmesh
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index('--') + 1:]
IN, OUT = argv[0], argv[1]
RENDER = argv[2] if len(argv) > 2 else None
CLAMP = 3.0                        # cm: the most a vertex may move
NECK_LO, NECK_HI = 145.0, 150.0    # nothing above NECK_HI moves (the head, the hair)
CHEST_LO, CHEST_HI = 122.0, 132.0  # torso vertices fade in between these heights (the shoulders' own cloth)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=IN)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
mesh = max([o for o in bpy.data.objects if o.type == 'MESH'], key=lambda o: len(o.data.vertices))
me = mesh.data
for pb in arm.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
MW = mesh.matrix_world
V = np.array([MW @ v.co for v in me.vertices])
s = float(V[:, 2].max() - V[:, 2].min()) / 174.0            # scene units per centimetre
V = V / s
AW = arm.matrix_world
B = arm.data.bones
head = lambda n: (AW @ B[n].head_local) / s
up = ['Bone_022', 'Bone_027']
cx = (head(up[0]).x + head(up[1]).x) / 2
kids = lambda n: [c.name for c in B[n].children]
armb, handb, clav = set(), set(), set()
for u in up:
    fo = kids(u)[0]; wr = kids(fo)[0]
    armb |= {u, fo}; clav.add(B[u].parent.name)
    st = [wr]
    while st:
        n = st.pop(); handb.add(n); st += kids(n)
headb = set()
st = ['Bone_018']
while st:
    n = st.pop(); headb.add(n); st += [k for k in kids(n)]
gname = {g.index: g.name for g in mesh.vertex_groups}
zsh = (head(up[0]).z + head(up[1]).z) / 2
print('EVEN centre plane x %.2f cm, shoulder joints at %.1f cm (L-R height difference %.2f)' % (cx, zsh, head(up[0]).z - head(up[1]).z))

# how much each vertex takes part: all of it on the arms and collarbones, fading in up the chest, none on the head or hands
mask = np.zeros(len(V))
for v in me.vertices:
    a = h = hd = t = 0.0
    for g in v.groups:
        n = gname[g.group]
        if n in armb or n in clav: a += g.weight
        elif n in handb: h += g.weight
        elif n in headb: hd += g.weight
        else: t += g.weight
    z = V[v.index, 2]
    k = min(1.0, max(0.0, (z - CHEST_LO) / (CHEST_HI - CHEST_LO))); k = k * k * (3 - 2 * k)
    # The neck's own bones carry the collar and the slope from neck to shoulder, which is where the two sides differ
    # most (1.2 cm, 10 to 13 cm out). So the head is kept out by HEIGHT, not by bone: everything fades out between
    # the base of the neck and the chin.
    n_ = min(1.0, max(0.0, (NECK_HI - z) / (NECK_HI - NECK_LO))); n_ = n_ * n_ * (3 - 2 * n_)
    mask[v.index] = max(0.0, min(1.0, a + (t + hd) * k)) * n_


def profile(P, tag):
    body = P[P[:, 2] < zsh + 12.0]
    row = []
    for d in (10, 13, 16, 19):
        l = body[(body[:, 0] - cx > d - 1) & (body[:, 0] - cx < d + 1)]; r = body[(cx - body[:, 0] > d - 1) & (cx - body[:, 0] < d + 1)]
        row.append('%d cm out %+.1f' % (d, l[:, 2].max() - r[:, 2].max()))
    # sleeve: how far the arm's surface stands off the upper-arm bone, each side
    th = []
    for u in up:
        a, b_ = head(u), head(kids(u)[0]); ax = (b_ - a).normalized()
        idx = [v.index for v in me.vertices if any(gname[g.group] == u and g.weight > 0.5 for g in v.groups)]
        r_ = [((Vector(P[i]) - a) - ax * (Vector(P[i]) - a).dot(ax)).length for i in idx]
        th.append(np.percentile(r_, 90))
    print('EVEN %s: shoulder surface, his left minus right: %s | sleeve radius (90th pct) %s %.1f cm, %s %.1f cm'
          % (tag, '  '.join(row), up[0], th[0], up[1], th[1]))


profile(V, 'before')
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
bvh = BVHTree.FromPolygons([Vector(p) for p in V], [[v.index for v in f.verts] for f in bm.faces])
D = np.zeros_like(V)
nrm = np.array([(MW.to_3x3() @ v.normal).normalized() for v in bm.verts])
miss = 0
for i in np.where(mask > 1e-3)[0]:
    p = Vector(V[i]); pm = Vector((2 * cx - p.x, p.y, p.z))
    q, qn, _, dist = bvh.find_nearest(pm, CLAMP * 2)
    if q is None: miss += 1; continue
    nm = Vector((-nrm[i][0], nrm[i][1], nrm[i][2]))
    if qn.dot(nm) < 0.3: miss += 1; continue            # the nearest thing over there faces another way: not the same part
    d = Vector((2 * cx - q.x, q.y, q.z)) - p              # where this vertex would be on the other side's shape
    if d.length > CLAMP: d = d * (CLAMP / d.length)
    D[i] = np.array(d) * 0.5
# smooth the move over the mesh so it is a reshaping, not noise
nb = [[e.other_vert(v).index for e in v.link_edges] for v in bm.verts]
for _ in range(12):
    D = np.array([(D[i] + sum(D[j] for j in nb[i])) / (1 + len(nb[i])) if nb[i] else D[i] for i in range(len(V))])
D *= mask[:, None]
V2 = V + D
profile(V2, 'after ')
mv = np.linalg.norm(D, axis=1)
print('EVEN moved %d vertices: mean %.2f cm, 95th pct %.2f, most %.2f; no match on the other side for %d'
      % (int((mv > 0.02).sum()), float(mv[mv > 0.02].mean()), float(np.percentile(mv[mv > 0.02], 95)), float(mv.max()), miss))
MI = MW.inverted()
for v in me.vertices:
    v.co = MI @ (Vector(V2[v.index]) * s)
bm.free(); me.update()

if RENDER:
    import os
    sc = bpy.context.scene
    world = bpy.data.worlds.new('W'); sc.world = world; world.use_nodes = True
    world.node_tree.nodes['Background'].inputs[0].default_value = (0.9, 0.9, 0.9, 1); world.node_tree.nodes['Background'].inputs[1].default_value = 1.2
    sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN')); sun.data.energy = 3; sun.rotation_euler = (0.7, 0.2, -0.5); sc.collection.objects.link(sun)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.type = 'ORTHO'; cam.data.clip_end = 100000 * s; cam.data.ortho_scale = 150 * s
    sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x, sc.render.resolution_y = 900, 600
    for tag, vdir in (('front', (0, -1, 0)), ('back', (0, 1, 0))):
        ctr = Vector((cx * s, 0, 120 * s)); cam.location = ctr + Vector(vdir) * 1000 * s
        cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = RENDER.replace('.png', '_%s.png' % tag); bpy.ops.render.render(write_still=True)

bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.type in ('MESH', 'ARMATURE'): o.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, add_leaf_bones=False, bake_anim=False,
                         mesh_smooth_type='FACE', path_mode='COPY', embed_textures=True)
print('EVEN exported %s' % OUT)
