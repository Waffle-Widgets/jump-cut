"""Look at one clip from every side: a contact sheet of a skinned FBX animation, plus hand close-ups and a torn-skin count.

    blender -b --factory-startup --python Art/Blender/clip_sheet.py -- CLIP.fbx OUT_DIR [TEXTURE.png] [frames=8]

CLIP.fbx is a clip with its mesh, as written by tools/unreal_export_clips_fbx.py (Unreal's own export of the clip
the game plays, on the body the game uses) or by one of our authored-clip scripts.

Writes OUT_DIR/<clip>_sides.png: one column per sampled frame, four rows - front, his left, back, his right - with
the camera following the body so a clip that travels stays in frame. OUT_DIR/<clip>_hands.png: both hands, close,
at three moments. And prints one line of JSON: frame range, how far the body travels, the lowest point of the mesh
over the clip, and torn skin - edges stretched to more than 2.5 times their rest length and by more than 1.5 cm -
per sampled frame, with the bones they sit between.

WHY. Reading a retargeted clip's numbers back never showed whether it LOOKS right, and one capture from the game
camera shows one side at one moment. This shows all of it, on the real body, in a minute.
"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index('--') + 1:]
CLIP, OUT = argv[0], argv[1]
TEX = next((a for a in argv[2:] if a.lower().endswith('.png')), None)
NF = int(next((a.split('=')[1] for a in argv[2:] if a.startswith('frames=')), 8))
NAME = os.path.splitext(os.path.basename(CLIP))[0]
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=CLIP, automatic_bone_orientation=False, ignore_leaf_bones=False)
sc = bpy.context.scene
rig = [o for o in sc.objects if o.type == 'ARMATURE'][0]
meshes = [o for o in sc.objects if o.type == 'MESH']
mesh = max(meshes, key=lambda o: len(o.data.vertices))
act = rig.animation_data.action if rig.animation_data else None
if act is None:
    raise SystemExit('REFUSING: no animation on the armature in %s' % CLIP)
f0, f1 = int(round(act.frame_range[0])), int(round(act.frame_range[1]))
sc.frame_start, sc.frame_end = f0, f1


def world_verts():
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    e = mesh.evaluated_get(dg)
    m = e.to_mesh()
    co = np.empty(len(m.vertices) * 3, np.float64)
    m.vertices.foreach_get('co', co)
    M = np.array(e.matrix_world)
    e.to_mesh_clear()
    return co.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]


# rest shape: the action off and every pose bone cleared
rig.animation_data.action = None
for pb in rig.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
V0 = world_verts()
H = float(V0[:, 2].max() - V0[:, 2].min())                  # body height in scene units, whatever they are
cm = H / 175.0                                              # one centimetre, near enough, for thresholds and reports
rig.animation_data.action = act
if hasattr(rig.animation_data, 'action_slot') and rig.animation_data.action_slot is None and getattr(act, 'slots', None):
    rig.animation_data.action_slot = act.slots[0]           # Blender 5.x slotted actions

E = np.array([e.vertices[:] for e in mesh.data.edges])
r0 = np.linalg.norm(V0[E[:, 0]] - V0[E[:, 1]], axis=1)
vg = {g.index: g.name for g in mesh.vertex_groups}
dom = [vg[max(v.groups, key=lambda g: g.weight).group] if v.groups else 'none' for v in mesh.data.vertices]


def torn(V):
    r1 = np.linalg.norm(V[E[:, 0]] - V[E[:, 1]], axis=1)
    bad = np.where((r1 > 2.5 * np.maximum(r0, 0.05 * cm)) & (r1 - r0 > 1.5 * cm))[0]
    pairs = {}
    for e in bad:
        k = tuple(sorted((dom[E[e, 0]], dom[E[e, 1]])))
        pairs[k] = pairs.get(k, 0) + 1
    return len(bad), (float(r1[bad].max()) / cm if len(bad) else 0.0), sorted(((n, list(k)) for k, n in pairs.items()), reverse=True)[:5]


frames = sorted({int(round(f0 + (f1 - f0) * i / max(1, NF))) for i in range(NF)})
VERTS = {}
for f in frames:
    sc.frame_set(f)
    VERTS[f] = world_verts()

# which way he faces: the toes point forward. Take the lowest 4% of the rest mesh (the shoes) and see which
# horizontal way they stick out from the ankles (the next 4% up).
low = V0[V0[:, 2] < V0[:, 2].min() + 0.04 * H]
above = V0[(V0[:, 2] > V0[:, 2].min() + 0.05 * H) & (V0[:, 2] < V0[:, 2].min() + 0.10 * H)]
fwd = Vector((float(low[:, 0].mean() - above[:, 0].mean()), float(low[:, 1].mean() - above[:, 1].mean()), 0.0))
fwd = fwd.normalized() if fwd.length > 1e-6 else Vector((0, -1, 0))
left = Vector((0, 0, 1)).cross(fwd).normalized()            # his left

log = {'clip': NAME, 'frames': [f0, f1], 'fps': sc.render.fps, 'height_units': round(H, 3),
       'faces': [round(fwd.x, 2), round(fwd.y, 2)]}
c0 = (VERTS[frames[0]].max(0) + VERTS[frames[0]].min(0)) / 2
c1 = (VERTS[frames[-1]].max(0) + VERTS[frames[-1]].min(0)) / 2
log['travel_cm'] = round(float(np.linalg.norm((c1 - c0)[:2])) / cm, 1)
log['lowest_point_cm'] = round(min(float(V[:, 2].min()) for V in VERTS.values()) / cm, 1)
log['highest_lowest_point_cm'] = round(max(float(V[:, 2].min()) for V in VERTS.values()) / cm, 1)
log['torn'] = {}
worst = (0, 0.0, [])
for f in frames:
    n, longest, pairs = torn(VERTS[f])
    log['torn'][f] = [n, round(longest, 1)]
    if n > worst[0]:
        worst = (n, longest, pairs)
log['torn_worst'] = {'edges': worst[0], 'longest_cm': round(worst[1], 1), 'between': worst[2]}

# ---------- render ----------
if TEX and os.path.isfile(TEX):
    img = bpy.data.images.load(TEX)
    mat = bpy.data.materials.new('Look')
    mat.use_nodes = True
    n = mat.node_tree.nodes.new('ShaderNodeTexImage')
    n.image = img
    mat.node_tree.links.new(n.outputs['Color'], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    mat.node_tree.nodes.active = n
    mesh.data.materials.clear()
    mesh.data.materials.append(mat)
sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading
sh.light = 'STUDIO'
sh.color_type = 'TEXTURE' if TEX and os.path.isfile(TEX) else 'SINGLE'
sh.single_color = (0.75, 0.72, 0.68)
sh.show_cavity = True
sh.show_shadows = False
sc.render.film_transparent = False
world = bpy.data.worlds.new('W')
sc.world = world
world.color = (0.36, 0.37, 0.40)
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam'))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.type = 'ORTHO'
cam.data.clip_end = 1000 * H
bpy.ops.mesh.primitive_plane_add(size=40 * H)
floor = bpy.context.object
fm = bpy.data.materials.new('Floor')
fm.diffuse_color = (0.22, 0.22, 0.24, 1)
floor.data.materials.append(fm)
floor.color = (0.22, 0.22, 0.24, 1)


def shot(fp, ctr, v, scale, res):
    sc.render.resolution_x, sc.render.resolution_y = res
    cam.data.ortho_scale = scale
    v = Vector(v).normalized()
    cam.location = Vector(ctr) + v * 20 * H
    cam.rotation_euler = (Vector(ctr) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = fp
    bpy.ops.render.render(write_still=True)


def sheet(path, tiles, cols, res):
    w, h = res
    rows = (len(tiles) + cols - 1) // cols
    out = np.zeros((h * rows, w * cols, 4), np.float32)
    out[..., 3] = 1
    for i, fp in enumerate(tiles):
        im = bpy.data.images.load(fp)
        x = np.empty(w * h * 4, np.float32)
        im.pixels.foreach_get(x)
        r, c = divmod(i, cols)
        out[(rows - 1 - r) * h:(rows - r) * h, c * w:(c + 1) * w] = x.reshape(h, w, 4)
        bpy.data.images.remove(im)
        os.remove(fp)
    s = bpy.data.images.new('sheet', w * cols, h * rows)
    s.pixels.foreach_set(out.ravel())
    s.filepath_raw = path
    s.file_format = 'PNG'
    s.save()


up = Vector((0, 0, 0.04))
VIEWS = (('front', fwd + up), ('left', left + up), ('back', -fwd + up), ('right', -left + up))
tiles = []
for tag, v in VIEWS:
    for f in frames:
        sc.frame_set(f)
        V = VERTS[f]
        ctr = Vector((float((V[:, 0].max() + V[:, 0].min()) / 2), float((V[:, 1].max() + V[:, 1].min()) / 2), 0.5 * H))
        fp = os.path.join(OUT, '_%s_%s_%04d.png' % (NAME, tag, f))
        shot(fp, ctr, v, 1.25 * H, (230, 300))
        tiles.append(fp)
sheet(os.path.join(OUT, NAME + '_sides.png'), tiles, len(frames), (230, 300))

# hands: the two limb ends that are highest off the floor among bones with no children near the wrists - found as the
# vertices farthest to each side in the rest pose (an A-pose puts the hands at the ends of the X extent)
side = np.array([float(Vector((p[0], p[1], 0)).dot(left)) for p in V0])
hand_idx = {'L': np.argsort(side)[-max(40, len(side) // 150):], 'R': np.argsort(side)[:max(40, len(side) // 150)]}
tiles = []
for f in (frames[0], frames[len(frames) // 2], frames[-1]):
    sc.frame_set(f)
    V = VERTS[f]
    for s in 'LR':
        ctr = Vector(V[hand_idx[s]].mean(0))
        for v in ((left if s == 'L' else -left) + fwd * 0.4, fwd + up * 3):
            fp = os.path.join(OUT, '_%s_hand_%s_%04d_%d.png' % (NAME, s, f, len(tiles)))
            shot(fp, ctr, v, 0.26 * H, (240, 240))
            tiles.append(fp)
sheet(os.path.join(OUT, NAME + '_hands.png'), tiles, 4, (240, 240))
log['sheets'] = [os.path.join(OUT, NAME + '_sides.png'), os.path.join(OUT, NAME + '_hands.png')]
print('CLIPSHEET ' + json.dumps(log))
