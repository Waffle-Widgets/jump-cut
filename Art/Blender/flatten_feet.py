"""Put a body's shoes flat on the floor in its REST pose, without touching the skeleton.

    blender -b --factory-startup --python Art/Blender/flatten_feet.py -- IN.fbx OUT.fbx [RENDER.png]

WHY (Sun Nov 15, GameStation, Blender 5.3.0). The Team Owner on the player's V2 body: "his feet are looking oddly
folded upwards". They are, and it is the model, not a clip: in the rest pose each shoe is pitched toes-up, the toe
cap several centimetres off the ground with the heel down. Every clip plants the FOOT BONE the way the rig rests,
so every clip - the authored idle and all 40 retargeted ones - shows the same tipped-up shoe.

Fixing it in one clip would leave it in the other forty. So fix the mesh: turn each foot about its ankle until the
sole is level, bake that shape into the vertices, and leave every bone exactly where it was. The clips do not
change and they all get flat shoes.

How: the sole's pitch is measured from the mesh (the underside of the front quarter of the shoe against the
underside of the back quarter), the foot bone is posed to cancel it, the armature deform is applied to the mesh as
its new rest shape, and the pose is cleared. Only vertices that follow a foot or toe bone move.
"""
import bpy, sys, math
import numpy as np
from mathutils import Matrix

argv = sys.argv[sys.argv.index('--') + 1:]
IN, OUT = argv[0], argv[1]
RENDER = argv[2] if len(argv) > 2 else None

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=IN)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]
me = mesh.data
bones = arm.data.bones
for pb in arm.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()


def desc(b):
    out = [b.name]
    for c in b.children:
        out += desc(c)
    return out


hip = [b for b in bones if b.parent and b.parent.parent is None][0]
thighs = [c for c in hip.children if (arm.matrix_world @ c.tail_local).z < (arm.matrix_world @ c.head_local).z - 0.2]
if len(thighs) != 2:
    raise SystemExit('REFUSING: expected two leg chains under %s' % hip.name)
FEET = {}
for th in thighs:
    foot = th.children[0].children[0]                       # thigh > shin > foot
    FEET[foot.name] = set(desc(foot))
gname = {g.index: g.name for g in mesh.vertex_groups}
dom = [gname[max(v.groups, key=lambda g: g.weight).group] if v.groups else '' for v in me.vertices]
IDX = {f: np.array([i for i, d in enumerate(dom) if d in names]) for f, names in FEET.items()}


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


def sole(V, idx):
    """(pitch in degrees, toes-up positive; lowest z) of one shoe. The model faces -Y, so the toe is at low y."""
    P = V[idx]
    y0, y1 = np.percentile(P[:, 1], 2), np.percentile(P[:, 1], 98)
    front = P[P[:, 1] < y0 + 0.25 * (y1 - y0)]
    back = P[P[:, 1] > y1 - 0.25 * (y1 - y0)]
    zt, zh = np.percentile(front[:, 2], 3), np.percentile(back[:, 2], 3)
    return math.degrees(math.atan2(zt - zh, back[:, 1].mean() - front[:, 1].mean())), float(P[:, 2].min())


def pose_foot(name, deg):
    pb = arm.pose.bones[name]
    pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()
    h = arm.matrix_world @ pb.head
    R = Matrix.Translation(h) @ Matrix.Rotation(math.radians(deg), 4, 'X') @ Matrix.Translation(-h)
    pb.matrix = arm.matrix_world.inverted() @ R @ arm.matrix_world @ pb.matrix
    bpy.context.view_layer.update()


V0 = world_verts()
scale = 1.0 if V0[:, 2].max() < 5 else 100.0               # metres or centimetres, whichever the scene is in
report = {}
for f, idx in IDX.items():
    p0, z0 = sole(V0, idx)
    # which way does a positive turn about +X tip this shoe? measure, don't assume
    pose_foot(f, 5.0)
    p5, _ = sole(world_verts(), idx)
    k = (p5 - p0) / 5.0
    deg = 0.0
    for _ in range(6):                                      # secant on the measured pitch
        pose_foot(f, deg)
        p, _ = sole(world_verts(), idx)
        if abs(p) < 0.05:
            break
        deg -= p / k
    # Height is left alone: the foot bone is connected to the shin, so it cannot be slid down, and a shoe that
    # rests a centimetre high is a clip's job (the ankle target), not the mesh's. The lowest point is reported.
    p1, z1 = sole(world_verts(), idx)
    report[f] = (p0, z0 / scale * 100, deg, p1, z1 / scale * 100, len(idx))
    print('FEET %s: sole pitch %.1f deg (toes up), lowest point %.2f cm  ->  turned %.1f deg, pitch %.2f, lowest %.2f cm  (%d vertices)'
          % (f, p0, z0 / scale * 100, deg, p1, z1 / scale * 100, len(idx)))

V1 = world_verts()
moved = np.linalg.norm(V1 - V0, axis=1) / scale * 100
print('FEET vertices moved more than 0.01 cm: %d of %d; farthest %.2f cm; whole-body lowest point %.3f cm'
      % (int((moved > 0.01).sum()), len(moved), float(moved.max()), float(V1[:, 2].min()) / scale * 100))

if RENDER:
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'FLAT'
    sc.display.shading.color_type = 'TEXTURE'
    sc.render.resolution_x, sc.render.resolution_y = 900, 450
    cam = bpy.data.objects.new('C', bpy.data.cameras.new('C'))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 0.7 * scale
    cam.location = (3 * scale, 0, 0.12 * scale)
    cam.rotation_euler = (math.radians(90), 0, math.radians(90))
    cam.data.clip_end = 100 * scale
    bpy.ops.mesh.primitive_plane_add(size=4 * scale)
    floor = bpy.context.object
    sc.render.filepath = RENDER
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(floor)

# bake the posed shape into the mesh, then put the rig back to rest: bones untouched, shoes flat
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True)
bpy.context.view_layer.objects.active = mesh
mod = [m for m in mesh.modifiers if m.type == 'ARMATURE'][0]
bpy.ops.object.modifier_apply(modifier=mod.name)
for pb in arm.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
new = mesh.modifiers.new('Armature', 'ARMATURE')
new.object = arm
bpy.context.view_layer.update()
V2 = world_verts()
print('FEET after baking, rig at rest: differs from the posed shape by %.4f cm at most' % (float(np.abs(V2 - V1).max()) / scale * 100))

bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, add_leaf_bones=False, bake_anim=False,
                         mesh_smooth_type='FACE', path_mode='COPY', embed_textures=True)
print('FEET exported %s' % OUT)
