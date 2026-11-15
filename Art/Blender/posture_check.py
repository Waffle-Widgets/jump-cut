"""Measure a standing clip against a plumb line, and render it large from the side and the front.

    blender -b --factory-startup --python Art/Blender/posture_check.py -- Clip[:frame] OUT.png

WHY (Sun Nov 15). The Team Owner sent photographs of people standing idle from the side. What they share: the ear,
the shoulder, the hip and the ankle sit on ONE vertical line, the knees are straight, the arms hang straight down
with the hand at mid-thigh, the head is level. A contact-sheet tile is too small to see whether ours does that, and
"looks about right" is how the bowed legs and bent arms got through. This prints how far forward of the ankle each
landmark is (centimetres, + is forward), the bend at knee and elbow, and where the hand hangs, then renders the pose
with the plumb line drawn through the ankle.
"""
import bpy, sys, os, math
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
clip, _, frame = argv[0].partition(':')
OUT = argv[1]
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'export', 'Characters', 'CafeWalkerV2')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=os.path.join(DIR, 'SK_CafeWalkerV2_%s.fbx' % clip), automatic_bone_orientation=False, ignore_leaf_bones=False)
sc = bpy.context.scene
rig = [o for o in sc.objects if o.type == 'ARMATURE'][0]
mesh = max([o for o in sc.objects if o.type == 'MESH'], key=lambda o: len(o.data.vertices))
sc.frame_set(int(frame or 1))
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
ev = mesh.evaluated_get(dg)
me = ev.to_mesh()
V = np.array([ev.matrix_world @ v.co for v in me.vertices])
ev.to_mesh_clear()
s = float(V[:, 2].max() - V[:, 2].min()) / 174.0            # scene units per cm, near enough
P = lambda b: (rig.matrix_world @ rig.pose.bones[b].head) / s
T = lambda b: (rig.matrix_world @ rig.pose.bones[b].tail) / s
side = 'L'
B = {'L': dict(sh='Bone_022', el='Bone_021', wr='Bone_020', hip='Bone_010', kn='Bone_009', an='Bone_008'),
     'R': dict(sh='Bone_027', el='Bone_026', wr='Bone_025', hip='Bone_015', kn='Bone_014', an='Bone_013')}
if P(B['L']['sh']).x < P(B['R']['sh']).x:
    B['L'], B['R'] = B['R'], B['L']


def bend(a, b, c):
    return 180.0 - math.degrees((a - b).angle(c - b))


fwd = lambda p, ref: round(ref.y - p.y, 1)                 # he faces -Y
head_top = Vector((0, float(V[V[:, 2] > V[:, 2].max() - 12 * s][:, 1].mean()) / s, 0))
print('POSTURE %s frame %s' % (clip, frame or 1))
for sd in 'LR':
    b = B[sd]
    an = P(b['an'])
    print('POSTURE  %s: forward of the ankle (cm): knee %+.1f  hip %+.1f  shoulder %+.1f  ear/head %+.1f  wrist %+.1f   | knee bend %.0f deg, elbow bend %.0f deg'
          % (sd, fwd(P(b['kn']), an), fwd(P(b['hip']), an), fwd(P(b['sh']), an), fwd(head_top, an), fwd(P(b['wr']), an),
             bend(P(b['hip']), P(b['kn']), P(b['an'])), bend(P(b['sh']), P(b['el']), P(b['wr']))))
    print('POSTURE     wrist height %.0f cm (hip joint %.0f, knee %.0f): %.0f %% of the way from hip to knee; wrist %.1f cm outside the hip joint'
          % (P(b['wr']).z, P(b['hip']).z, P(b['kn']).z, 100 * (P(b['hip']).z - P(b['wr']).z) / max(1e-6, P(b['hip']).z - P(b['kn']).z),
             abs(P(b['wr']).x) - abs(P(b['hip']).x)))
neck, headb = P('Bone_018'), P('Bone_016')
ht = T('Bone_016')
print('POSTURE  head tilt (forward of vertical, deg): %.0f   spine hip-to-neck lean: %.0f'
      % (math.degrees(math.atan2(headb.y - ht.y, ht.z - headb.z)), math.degrees(math.atan2(P('Bone_001').y - neck.y, neck.z - P('Bone_001').z))))

# level? Seen from the front: how much higher his LEFT shoulder joint is than his right, and how far the head leans.
shL, shR = P(B['L']['sh']), P(B['R']['sh'])
print('POSTURE  shoulders: left is %+.1f cm higher than right (%.1f deg)   head: leans %+.1f deg toward his left, turned %+.1f deg to his left'
      % (shL.z - shR.z, math.degrees(math.atan2(shL.z - shR.z, abs(shL.x - shR.x))),
         math.degrees(math.atan2(ht.x - headb.x, ht.z - headb.z)),
         math.degrees(math.atan2(-((rig.matrix_world @ rig.pose.bones['Bone_016'].matrix).to_3x3() @ Vector((1, 0, 0))).y,
                                 ((rig.matrix_world @ rig.pose.bones['Bone_016'].matrix).to_3x3() @ Vector((1, 0, 0))).x))))
world = bpy.data.worlds.new('W'); sc.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.9, 0.9, 0.9, 1); world.node_tree.nodes['Background'].inputs[1].default_value = 1.2
sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN')); sun.data.energy = 3; sun.rotation_euler = (0.7, 0.2, -0.5); sc.collection.objects.link(sun)
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = 'ORTHO'; cam.data.clip_end = 100000 * s; cam.data.ortho_scale = 190 * s
sc.render.engine = 'BLENDER_EEVEE'
W_, H_ = 420, 760
sc.render.resolution_x, sc.render.resolution_y = W_, H_
# the plumb line: a thin red post through the mean ankle
an = (P(B['L']['an']) + P(B['R']['an'])) / 2
bpy.ops.mesh.primitive_cylinder_add(radius=0.25 * s, depth=185 * s, location=(60 * s, an.y * s, 92 * s))
post = bpy.context.object
m = bpy.data.materials.new('red'); m.use_nodes = True
m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (1, 0, 0, 1)
m.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (1, 0, 0, 1)
m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 2
post.data.materials.append(m)
tiles = []
for tag, v, px_ in (('left', (1, 0, 0), 60), ('right', (-1, 0, 0), -60), ('front', (0, -1, 0), None)):
    post.hide_render = px_ is None
    if px_ is not None: post.location.x = px_ * s
    ctr = Vector((0, an.y * s, 88 * s))
    cam.location = ctr + Vector(v) * 1000 * s
    cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
    fp = os.path.join(os.path.dirname(OUT), '_post_%s.png' % tag); sc.render.filepath = fp
    bpy.ops.render.render(write_still=True); tiles.append(fp)
out = np.zeros((H_, W_ * 3, 4), np.float32); out[..., 3] = 1
for c, fp in enumerate(tiles):
    im = bpy.data.images.load(fp); x = np.empty(W_ * H_ * 4, np.float32); im.pixels.foreach_get(x)
    out[:, c * W_:(c + 1) * W_] = x.reshape(H_, W_, 4); bpy.data.images.remove(im); os.remove(fp)
img = bpy.data.images.new('s', W_ * 3, H_); img.pixels.foreach_set(out.ravel())
img.filepath_raw = OUT; img.file_format = 'PNG'; img.save()
print('POSTURE wrote %s' % OUT)
