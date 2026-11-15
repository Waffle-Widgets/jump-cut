"""Close-ups of the shoulders in chosen frames of authored clips: front, back and each side, one row per clip frame.

    blender -b --factory-startup --python Art/Blender/shoulder_sheet.py -- OUT.png Clip:frame [Clip:frame ...]
    ... -- cache/shoulders.png Idle:1 Run:1 Run:5 PunchA:4 PunchB:5 Finisher:9

Reads Art/Blender/export/Characters/CafeWalkerV2/SK_CafeWalkerV2_<Clip>.fbx. The camera follows the chest and turns
with it, so a pitched or twisted torso is still seen square-on. WHY: the four-side clip sheets are 230 px a tile; a
shoulder that wrings or pops is a few pixels there and "looks like it dislocates" in the game (owner, Nov 15).
"""
import bpy, sys, os
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
SCALE = float(next((a[6:] for a in argv[1:] if a.startswith('scale=')), 75))   # cm across the picture
AIM = next((a[4:] for a in argv[1:] if a.startswith('aim=')), 'chest')              # chest | hips
OUT, items = argv[0], [a.split(':') for a in argv[1:] if '=' not in a]
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'export', 'Characters', 'CafeWalkerV2')
W, H = 300, 300
rows = []
for clip, frame in items:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=os.path.join(DIR, 'SK_CafeWalkerV2_%s.fbx' % clip), automatic_bone_orientation=False, ignore_leaf_bones=False)
    sc = bpy.context.scene
    rig = [o for o in sc.objects if o.type == 'ARMATURE'][0]
    sc.frame_set(int(frame)); bpy.context.view_layer.update()
    P = lambda b: rig.matrix_world @ rig.pose.bones[b].head
    sL, sR, neck, hip = P('Bone_022'), P('Bone_027'), P('Bone_018'), P('Bone_001')
    s = (sL - sR).length / 38.0                                  # scene units per cm, near enough
    ctr = (sL + sR) / 2
    if AIM == 'hips': ctr = hip - Vector((0, 0, 25 * s))
    left = (sL - sR).normalized()
    up = (neck - hip).normalized()
    fwd = up.cross(left).normalized()                            # out of his chest
    if fwd.dot(Vector((0, -1, 0))) < 0: fwd = -fwd
    world = bpy.data.worlds.new('W'); sc.world = world; world.use_nodes = True
    world.node_tree.nodes['Background'].inputs[0].default_value = (0.5, 0.5, 0.52, 1); world.node_tree.nodes['Background'].inputs[1].default_value = 1.3
    sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN')); sun.data.energy = 3; sun.rotation_euler = (0.7, 0.2, -0.5); sc.collection.objects.link(sun)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.type = 'ORTHO'; cam.data.clip_end = 100000 * s; cam.data.ortho_scale = SCALE * s
    sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x, sc.render.resolution_y = W, H
    tiles = []
    for tag, v in (('front', fwd), ('back', -fwd), ('left', left), ('right', -left), ('top', up * 0.8 + fwd * 0.6)):
        cam.location = ctr + v.normalized() * 1000 * s
        z = up if tag != 'top' else -fwd
        q = (-v).to_track_quat('-Z', 'Y')
        cam.rotation_euler = q.to_euler()
        fp = os.path.join(os.path.dirname(OUT), '_sh_%s_%s_%s.png' % (clip, frame, tag)); sc.render.filepath = fp
        bpy.ops.render.render(write_still=True); tiles.append(fp)
    rows.append(tiles)
out = np.zeros((H * len(rows), W * 5, 4), np.float32); out[..., 3] = 1
for r, tiles in enumerate(rows):
    for c, fp in enumerate(tiles):
        im = bpy.data.images.load(fp); x = np.empty(W * H * 4, np.float32); im.pixels.foreach_get(x)
        out[(len(rows) - 1 - r) * H:(len(rows) - r) * H, c * W:(c + 1) * W] = x.reshape(H, W, 4)
        bpy.data.images.remove(im); os.remove(fp)
img = bpy.data.images.new('s', W * 5, H * len(rows)); img.pixels.foreach_set(out.ravel())
img.filepath_raw = OUT; img.file_format = 'PNG'; img.save()
print('SHOULDERSHEET %s rows %s' % (OUT, [':'.join(i) for i in items]))
