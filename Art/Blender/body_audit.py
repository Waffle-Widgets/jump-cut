"""Measure a generated body, in the pose it was sculpted in, for the faults found on the player on Nov 15.

    blender -b --factory-startup --python Art/Blender/body_audit.py -- BODY.fbx [OUT.png]

Needs no bone names, so it runs on any rig: everything is read off the surface. Prints, in centimetres:
  head     how far the head's centre line sits sideways from the point between the feet
  chest    the same for the chest (arms excluded), which is the body's own lean
  arms     how thick each arm is 35-45 cm out from the centre line, left against right
  reach    arm span against height (a person: about 1.0)
"""
import bpy, sys
import numpy as np
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index('--') + 1:]
IN = argv[0]; OUT = argv[1] if len(argv) > 1 else None
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=IN)
arms = [o for o in bpy.data.objects if o.type == 'ARMATURE']
for a in arms:
    for pb in a.pose.bones: pb.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
mesh = max([o for o in bpy.data.objects if o.type == 'MESH'], key=lambda o: len(o.data.vertices))
V = np.array([mesh.matrix_world @ v.co for v in mesh.data.vertices])
H0 = float(V[:, 2].max() - V[:, 2].min())
V = (V - np.array([0, 0, V[:, 2].min()])) / H0 * 100.0      # percent of height; printed as cm of a 174 cm body
k = 1.74
lat = 0 if (V[:, 0].max() - V[:, 0].min()) > (V[:, 1].max() - V[:, 1].min()) else 1
X = V[:, lat]; Z = V[:, 2]
feet = V[Z < 4]; l_, r_ = feet[feet[:, lat] > np.median(feet[:, lat])], feet[feet[:, lat] <= np.median(feet[:, lat])]
c0 = (l_[:, lat].mean() + r_[:, lat].mean()) / 2
mid = lambda sel: (np.percentile(X[sel], 2) + np.percentile(X[sel], 98)) / 2 - c0
head = np.mean([mid((Z > a) & (Z < a + 1.5)) for a in np.linspace(88, 95, 6)])
chest = np.mean([mid((Z > a) & (Z < a + 1.5) & (np.abs(X - c0) < 11)) for a in np.linspace(66, 74, 6)])
hips = np.mean([mid((Z > a) & (Z < a + 1.5) & (np.abs(X - c0) < 13)) for a in np.linspace(50, 54, 4)])
th = []
for sg in (1, -1):
    sel = (sg * (X - c0) > 20) & (sg * (X - c0) < 26) & (Z > 40) & (Z < 90)
    th.append(float(np.percentile(Z[sel], 97) - np.percentile(Z[sel], 3)) if sel.sum() > 20 else float('nan'))
span = float(X.max() - X.min())
print('AUDIT %s' % IN.replace('\\', '/').split('/')[-1])
print('AUDIT   %d vertices, %d bones; sideways from the point between the feet (cm, + is +X): hips %+.1f  chest %+.1f  head %+.1f'
      % (len(V), sum(len(a.data.bones) for a in arms), hips * k, chest * k, head * k))
print('AUDIT   head against chest %+.1f cm   arm thickness 35-45 cm out: +X side %.1f, -X side %.1f (difference %.1f)   arm span / height %.2f'
      % ((head - chest) * k, th[0] * k, th[1] * k, abs(th[0] - th[1]) * k, span / 100.0))
if OUT:
    sc = bpy.context.scene
    s = H0 / 174.0
    world = bpy.data.worlds.new('W'); sc.world = world; world.use_nodes = True
    world.node_tree.nodes['Background'].inputs[0].default_value = (0.9, 0.9, 0.9, 1); world.node_tree.nodes['Background'].inputs[1].default_value = 1.2
    sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN')); sun.data.energy = 3; sun.rotation_euler = (0.7, 0.2, -0.5); sc.collection.objects.link(sun)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.type = 'ORTHO'; cam.data.clip_end = 100000 * s; cam.data.ortho_scale = 200 * s
    sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x, sc.render.resolution_y = 700, 700
    zmin = float(np.array([mesh.matrix_world @ v.co for v in mesh.data.vertices])[:, 2].min())
    ctr = Vector((0, 0, zmin + 90 * s)); d = Vector((0, -1, 0)) if lat == 0 else Vector((-1, 0, 0))
    cam.location = ctr + d * 1000 * s; cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = OUT; bpy.ops.render.render(write_still=True)
