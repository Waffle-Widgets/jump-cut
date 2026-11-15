"""Stop a body's waist following its thighs: move leg weight that sits ABOVE the hip joints onto the hips.

    blender -b --factory-startup --python Art/Blender/waist_weights.py -- IN.fbx OUT.fbx

WHY (Sun Nov 15, GameStation, Blender 5.3.0). The Team Owner: "His clothes shouldn't stretch out in weird ways when
he attacks or moves." Most of the stretching was one thing. The generator (and the weight smoothing we ran on top
of it) left the THIGH bones with influence well above the hip joints: the waistband, the bottom of the shirt, the
apron's tie. So every time a leg lifts, his waist goes with it - the shirt pulled open at his side in the kick, and
the stretched-edge count in every big pose was mostly "lowest spine bone against itself", which is this.

A thigh has no business moving anything above the joint it turns about. So for every vertex, the weight it carries
on a leg bone (thigh, shin, foot, toes) is handed to the hip bone by a fraction that goes from 0 a few centimetres
BELOW the hip joints to 1 a few centimetres above them. Nothing else changes: vertices, UVs, bones and rest pose
are untouched. It prints how much moved and where.
"""
import bpy, sys
import numpy as np
from mathutils import Matrix

argv = sys.argv[sys.argv.index('--') + 1:]
IN, OUT = argv[0], argv[1]
BELOW, ABOVE = 5.0, 5.0            # cm under / over the hip joints across which the hand-over happens

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=IN)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]
me = mesh.data
for pb in arm.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
MW = mesh.matrix_world
V = np.array([MW @ v.co for v in me.vertices])
s = float(V[:, 2].max() - V[:, 2].min()) / 174.0            # scene units per centimetre
V = V / s
AW = arm.matrix_world
hip = [b for b in arm.data.bones if b.parent and b.parent.parent is None][0]
thighs = [c for c in hip.children if (AW @ c.tail_local).z < (AW @ c.head_local).z - 0.2 * s and not c.name.startswith('Apron_')]
if len(thighs) != 2:
    raise SystemExit('REFUSING: expected two leg chains under %s, found %d' % (hip.name, len(thighs)))
zj = float(np.mean([(AW @ t.head_local).z for t in thighs])) / s
legs = set()


def under(b):
    legs.add(b.name)
    for c in b.children:
        under(c)


for t in thighs:
    under(t)
gname = {g.index: g.name for g in mesh.vertex_groups}
hip_g = mesh.vertex_groups[hip.name]
t_ = np.clip((V[:, 2] - (zj - BELOW)) / (BELOW + ABOVE), 0.0, 1.0)
frac = t_ * t_ * (3 - 2 * t_)
moved, n, top = 0.0, 0, 0.0
for i in np.where(frac > 1e-4)[0]:
    v = me.vertices[int(i)]
    take = 0.0
    for g in v.groups:
        if gname[g.group] in legs and g.weight > 0:
            d = g.weight * float(frac[i])
            g.weight -= d
            take += d
    if take > 1e-6:
        hip_g.add([int(i)], take, 'ADD')
        moved += take
        n += 1
        top = max(top, float(V[i, 2]))
bad = sum(1 for v in me.vertices if abs(sum(g.weight for g in v.groups) - 1.0) > 1e-3)
print('WAIST hip joints at %.1f cm; leg weight handed to %s on %d vertices, total %.1f, reaching up to %.1f cm; weights not summing to 1: %d'
      % (zj, hip.name, n, moved, top, bad))
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, add_leaf_bones=False, bake_anim=False,
                         mesh_smooth_type='FACE', path_mode='COPY', embed_textures=True)
print('WAIST exported %s' % OUT)
