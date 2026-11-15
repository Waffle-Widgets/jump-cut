"""Correct a generated body's proportions ONCE, in its rest pose: longer arms and a head centred over the chest.

    blender -b --factory-startup --python Art/Blender/model_tuneup.py -- IN.fbx OUT.fbx [RENDER.png]
    env: ARM=1.15 (arm length and thickness), HAND=1.06, HEAD_MAX=4.0 (cm, the most the head may be moved)

WHY (Sun Nov 15, GameStation, Blender 5.3.0). Seven rounds on the idle were seven rounds of posing around the model.
Measured against a person of his height (posture_check.py): shoulder to wrist 48 cm where a person has 58, so his
fingertips stop at the hip and the owner saw arms that "look shriveled up"; and his head sits to his right of his
chest, so he reads as leaning whatever the pose. No pose makes an arm longer. These are fixed here, in the mesh
AND the skeleton's rest pose, so every clip built afterwards has them for free.

HOW. Arms: everything the upper-arm and forearm bones carry is scaled about the shoulder joint, by vertex weight,
so the shoulder's own cloth stays put and the change fades in down the sleeve. The hand rides the wrist and grows a
little less. Head: the head's centre line is measured ear to ear in slices and the head is slid sideways to sit over
the point between the shoulder joints, fading out down the neck. Bones move with their vertices. Faces, UVs and
weights are untouched, bone names and parents are untouched; bone LENGTHS and positions change, so every clip must
be rebuilt on the new body.
"""
import bpy, sys, os
import numpy as np
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index('--') + 1:]
IN, OUT = argv[0], argv[1]
RENDER = argv[2] if len(argv) > 2 else None
K_ARM = float(os.environ.get('ARM', 1.15)); K_HAND = float(os.environ.get('HAND', 1.06)); HEAD_MAX = float(os.environ.get('HEAD_MAX', 4.0))

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=IN)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
mesh = max([o for o in bpy.data.objects if o.type == 'MESH'], key=lambda o: len(o.data.vertices))
me = mesh.data
for pb in arm.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
MW, AW = mesh.matrix_world.copy(), arm.matrix_world.copy()
V = np.array([MW @ v.co for v in me.vertices])
s = float(V[:, 2].max() - V[:, 2].min()) / 174.0            # scene units per centimetre
B = arm.data.bones
kids = lambda n: [c.name for c in B[n].children]
wh = lambda n: AW @ B[n].head_local


def tree(n):
    out, st = [], [n]
    while st:
        x = st.pop(); out.append(x); st += kids(x)
    return out


UP = ['Bone_022', 'Bone_027']
gname = {g.index: g.name for g in mesh.vertex_groups}
W = [{gname[g.group]: g.weight for g in v.groups if g.weight > 0} for v in me.vertices]
Vn = V.copy()
bone_xf = {}                                                # bone -> function(world point) for its head and tail
for u in UP:
    fo = kids(u)[0]; wr = kids(fo)[0]
    piv = wh(u).copy(); wrist0 = wh(wr).copy()
    S_arm = lambda p, piv=piv: piv + (p - piv) * K_ARM
    wrist1 = S_arm(wrist0)
    S_hand = lambda p, a=wrist0, b=wrist1: b + (p - a) * K_HAND
    hand = set(tree(wr))
    for i, w in enumerate(W):
        wa = w.get(u, 0.0) + w.get(fo, 0.0); wd = sum(x for n, x in w.items() if n in hand)
        if wa + wd < 1e-4: continue
        p = Vector(V[i])
        Vn[i] = np.array(p * (1 - wa - wd) + S_arm(p) * wa + S_hand(p) * wd)
    bone_xf[u] = (None, S_arm); bone_xf[fo] = (S_arm, S_arm)
    for n in hand: bone_xf[n] = (S_hand, S_hand)
    print('TUNE %s: shoulder to wrist %.1f -> %.1f cm' % (u, (wrist0 - piv).length / s, (wrist1 - piv).length / s))

# the head, sideways
cx = (wh(UP[0]).x + wh(UP[1]).x) / 2
neck0 = 'Bone_018'
hb = tree(neck0); upper = set(hb) - {neck0}
idx = np.array([i for i, w in enumerate(W) if sum(x for n, x in w.items() if n in upper) > 0.9])
P = V[idx]
z0, z1 = np.percentile(P[:, 2], 20), np.percentile(P[:, 2], 70)
mids = []
for a in np.linspace(z0, z1, 12):
    sl = P[(P[:, 2] > a - 0.8 * s) & (P[:, 2] < a + 0.8 * s)]
    if len(sl) > 20: mids.append((np.percentile(sl[:, 0], 2) + np.percentile(sl[:, 0], 98)) / 2)
off = (float(np.mean(mids)) - cx) / s
shift = float(np.clip(-off, -HEAD_MAX, HEAD_MAX))
print('TUNE head: its centre line (ear to ear, 12 slices) is %+.1f cm toward his left of the point between the shoulder joints; sliding it %+.1f cm' % (off, shift))
if abs(shift) > 0.5:
    d = Vector((shift * s, 0, 0))
    for i, w in enumerate(W):
        k = sum(x for n, x in w.items() if n in upper) + 0.5 * w.get(neck0, 0.0)
        if k > 1e-4: Vn[i] = Vn[i] + np.array(d) * min(1.0, k)
    T_ = lambda p, d=d: p + d
    bone_xf[neck0] = (None, T_)
    for n in upper: bone_xf[n] = (T_, T_)

MI = MW.inverted()
for v in me.vertices:
    v.co = MI @ Vector(Vn[v.index])
me.update()
AI = AW.inverted()
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones
new = {}
for n, (fh, ft) in bone_xf.items():
    h, t = AW @ eb[n].head, AW @ eb[n].tail
    new[n] = (AI @ (fh(h) if fh else h), AI @ ft(t))
for b in eb:
    if b.name in new: b.use_connect = False
for n, (h, t) in new.items():
    eb[n].head, eb[n].tail = h, t
bpy.ops.object.mode_set(mode='OBJECT')
print('TUNE moved %d bones; %d vertices moved more than 0.1 cm (most %.1f cm)' % (len(new), int((np.linalg.norm(Vn - V, axis=1) > 0.1 * s).sum()), float(np.linalg.norm(Vn - V, axis=1).max() / s)))

if RENDER:
    sc = bpy.context.scene
    world = bpy.data.worlds.new('W'); sc.world = world; world.use_nodes = True
    world.node_tree.nodes['Background'].inputs[0].default_value = (0.9, 0.9, 0.9, 1); world.node_tree.nodes['Background'].inputs[1].default_value = 1.2
    sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN')); sun.data.energy = 3; sun.rotation_euler = (0.7, 0.2, -0.5); sc.collection.objects.link(sun)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.type = 'ORTHO'; cam.data.clip_end = 100000 * s; cam.data.ortho_scale = 200 * s
    sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x, sc.render.resolution_y = 900, 900
    ctr = Vector((cx, 0, 90 * s)); cam.location = ctr + Vector((0, -1, 0)) * 1000 * s
    cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = RENDER; bpy.ops.render.render(write_still=True)

bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.type in ('MESH', 'ARMATURE'): o.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, add_leaf_bones=False, bake_anim=False,
                         mesh_smooth_type='FACE', path_mode='COPY', embed_textures=True)
print('TUNE exported %s (%d bones)' % (OUT, len(arm.data.bones)))
