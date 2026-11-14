# One-pose clips for characters that only have Walk and Idle (issue #45). Headless:
#   blender -b --factory-startup --python Art/Blender/pose_clip.py -- <Name> <Pose>
#     CrashDriver Slumped   - the dead driver sitting on the ground against the wreck, head on his chest
#     CafeCoworker Down     - the coworker on her back on the cafe floor, if the rescue fails
#     CafeCoworker Flinch   - the coworker ducking away from the blast (optional, plays once)
# Reads the committed Art/Blender/export/Characters/<Name>/SK_<Name>.fbx (so it runs on any machine, no cache
# needed), poses the SAME skeleton, and writes SK_<Name>_<Pose>.fbx beside it: mesh + rig + one short action
# named <Pose>. Nothing about the original FBX changes. Check sheets go to Art/Blender/cache/<Name>_<Pose>.png.
#
# Both rigs are Meshy Smart Rigs and share one layout (read out of the two files, Nov 13):
#   Bone_000 root (at pelvis height) > Bone_001 hip > 005 > 004 > 003 > 002 spine > 018 > 017 > 016 neck/head
#   arms hang off 002: 023 > 022 > 021 (shoulder, upper arm, forearm) and 028 > 027 > 026
#   legs hang off 001: 010 > 009 > 008 (thigh, shin, foot) and 015 > 014 > 013
# The models face -Y, Z up, feet on z = 0.
#
# Every rotation here is given in WORLD space, about a world axis through the bone's own head, parents first.
# That is deliberate: Smart Rig bones have arbitrary local axes (meshy_character.py has to probe each one for
# its sign), and a pose written in local axes for one rig is wrong on the next.
#   about +X: positive tips something that points UP toward the front (-Y); a leg (points down) goes BACK.
#   about +Y: positive tips something that points up toward +X.
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector, Matrix

a = sys.argv[sys.argv.index('--') + 1:]
NAME, POSE = a[0], a[1]
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
CACHE = os.path.join(REPO, 'Art', 'Blender', 'cache'); os.makedirs(CACHE, exist_ok=True)
DIR = os.path.join(REPO, 'Art', 'Blender', 'export', 'Characters', NAME)
SRC = os.path.join(DIR, 'SK_%s.fbx' % NAME)
OUT = os.path.join(DIR, 'SK_%s_%s.fbx' % (NAME, POSE))
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
log = {'name': NAME, 'pose': POSE}

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.scale_length = 0.01                       # centimetre scene, like meshy_character.py
bpy.ops.import_scene.fbx(filepath=SRC, automatic_bone_orientation=False, use_anim=False, ignore_leaf_bones=False)
rig = [o for o in sc.objects if o.type == 'ARMATURE'][0]
mesh = [o for o in sc.objects if o.type == 'MESH'][0]
log['bones'] = len(rig.data.bones)
# The FBX stores TWO poses: the bind pose (which becomes the rest pose here) and the pose the rig was in when it
# was exported - frame 0 of Walk, one leg back. The importer applies that second one to the pose bones even with
# use_anim=False, so without this reset every pose below would be built on top of a walking stride (the
# coworker lay "down" propped 20 cm off the floor on her trailing foot).
if rig.animation_data: rig.animation_data.action = None
for pb in rig.pose.bones:
    pb.rotation_mode = 'QUATERNION'
    pb.location = (0, 0, 0); pb.rotation_quaternion = (1, 0, 0, 0); pb.scale = (1, 1, 1)
bpy.context.view_layer.update()
log['rig_scale_on_import'] = [round(v, 5) for v in rig.scale]


def world_verts():
    dg = bpy.context.evaluated_depsgraph_get(); e = mesh.evaluated_get(dg); me = e.to_mesh()
    V = np.array([e.matrix_world @ v.co for v in me.vertices]); e.to_mesh_clear(); return V


V0 = world_verts()
log['rest_size_cm'] = [round(float(v), 1) for v in (V0.max(0) - V0.min(0))]
log['rest_min_z'] = round(float(V0[:, 2].min()), 2)
H = float(V0[:, 2].max() - V0[:, 2].min())
SIDE = {}                                                  # which arm / leg chain is on +X
for nm, chain in (('arm', ('Bone_023', 'Bone_028')), ('leg', ('Bone_010', 'Bone_015'))):
    xs = [(rig.matrix_world @ rig.data.bones[c].head_local).x for c in chain]
    SIDE[nm] = {'px': chain[0] if xs[0] > xs[1] else chain[1], 'nx': chain[1] if xs[0] > xs[1] else chain[0]}
NEXT = {'Bone_023': ('Bone_022', 'Bone_021'), 'Bone_028': ('Bone_027', 'Bone_026'),
        'Bone_010': ('Bone_009', 'Bone_008'), 'Bone_015': ('Bone_014', 'Bone_013')}


def rot(bone, axis, deg):
    """Turn a pose bone (and everything under it) about a WORLD axis through its own head."""
    pb = rig.pose.bones[bone]
    bpy.context.view_layer.update()
    mw = rig.matrix_world @ pb.matrix
    head = mw.to_translation()
    R = Matrix.Translation(head) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-head)
    pb.matrix = rig.matrix_world.inverted() @ (R @ mw)
    bpy.context.view_layer.update()


def move(bone, vec):
    pb = rig.pose.bones[bone]
    bpy.context.view_layer.update()
    mw = rig.matrix_world @ pb.matrix
    pb.matrix = rig.matrix_world.inverted() @ (Matrix.Translation(vec) @ mw)
    bpy.context.view_layer.update()


def arm(side, upper_in, fore_fwd, upper_fwd=0.0):
    """side 'px'/'nx'. upper_in: degrees the upper arm swings in toward the body (negative = out and up).
    upper_fwd: degrees it swings forward. fore_fwd: degrees the forearm bends forward at the elbow."""
    sh = SIDE['arm'][side]; up, fore = NEXT[sh]
    sgn = 1.0 if side == 'px' else -1.0
    rot(up, Y, sgn * upper_in)          # about the front-back axis: +X arm swings in with a positive turn
    if upper_fwd: rot(up, X, -upper_fwd)
    if fore_fwd: rot(fore, X, -fore_fwd)


def leg(side, thigh_fwd, knee_back, splay=0.0):
    th = SIDE['leg'][side]; shin, foot = NEXT[th]
    sgn = 1.0 if side == 'px' else -1.0
    rot(th, X, -thigh_fwd)              # a leg points down, so forward is a negative turn about +X
    if splay: rot(th, Z, sgn * splay)
    if knee_back: rot(shin, X, knee_back)


def floor(bone='Bone_000', below_rest_z=None):
    """Drop (or lift) the whole body so its lowest vertex sits on z = 0.
    below_rest_z: only count vertices that were below this height in the rest pose. A body lying on its back
    must rest on its shoulders and hips, not on its hair: the coworker's ponytail sticks 20 cm out behind her
    head and, counted, it propped her whole body up off the floor like a kickstand. The hair goes into the floor
    instead, where nobody sees it."""
    Vw = world_verts()
    if below_rest_z is not None: Vw = Vw[V0[:, 2] < below_rest_z]
    lo = float(Vw[:, 2].min())
    move(bone, Vector((0, 0, -lo)))
    return lo


def recentre(part_bone):
    """Slide the body in X/Y so `part_bone`'s head is over the origin - the actor's location in the level."""
    bpy.context.view_layer.update()
    p = (rig.matrix_world @ rig.pose.bones[part_bone].matrix).to_translation()
    move('Bone_000', Vector((-p.x, -p.y, 0)))


frames = (1, 30)
if (NAME, POSE) == ('CrashDriver', 'Slumped'):
    # Sitting on the ground with his back against the car's sill under the open door: legs out in front, one knee
    # up, spine curled forward and tipped to his right, chin on his chest, arms hanging with the hands by his hips.
    rot('Bone_000', X, -14)                       # lean back against the car
    leg('px', 78, 8, splay=10)                    # one leg nearly flat along the ground
    leg('nx', 118, 104, splay=-6)                 # the other knee drawn up, foot planted
    rot('Bone_004', X, 14); rot('Bone_003', X, 14); rot('Bone_002', X, 10)   # the slump: spine curls forward
    rot('Bone_003', Y, 9)                         # and sags to one side
    rot('Bone_018', X, 22); rot('Bone_017', X, 26); rot('Bone_017', Y, 10)   # chin down, head rolled
    arm('px', 34, 18, upper_fwd=6)
    arm('nx', 30, 38, upper_fwd=16)               # this hand ends up on the raised thigh
    floor(); recentre('Bone_001')
elif (NAME, POSE) == ('CafeCoworker', 'Down'):
    # On her back on the cafe floor, head toward +Y (away from where she was facing), one knee bent, one arm
    # flung out and the other across her waist, head rolled to the side. Nothing gory: she is simply down.
    rot('Bone_000', X, -90)                       # onto her back: her front now faces up
    # she is lying down now, so "forward" for her limbs is UP (+Z) and her length runs along Y
    th = SIDE['leg']['px']; shin, _ = NEXT[th]
    rot(th, X, -38); rot(shin, X, 70)             # near knee raised, foot on the floor
    rot(SIDE['leg']['nx'], Z, -9)                 # other leg lies a little open
    up = NEXT[SIDE['arm']['px']][0]
    rot(up, Z, -52)                               # +X arm flung out to the side, flat on the floor
    up2, fore2 = NEXT[SIDE['arm']['nx']]
    rot(up2, Z, -12); rot(fore2, Z, -74); rot(fore2, X, -10)   # -X arm folded across her waist
    rot('Bone_018', X, 10)                        # neck lifted a little, so the back of the head just touches
    rot('Bone_017', Y, 38)                        # head rolled to the side, swinging the ponytail off the floor
    floor(below_rest_z=0.80 * H); recentre('Bone_001')
elif (NAME, POSE) == ('CafeCoworker', 'Flinch'):
    # Standing, ducking away from the blast: knees bent, shoulders hunched, both forearms thrown up in front of
    # her face, head turned away. Keyed neutral -> flinch in 5 frames, then held, so it plays once and stays.
    frames = (1, 6, 30)
    leg('px', 22, 40); leg('nx', 14, 28)
    rot('Bone_005', X, 10); rot('Bone_003', X, 12)
    arm('px', 22, 122, upper_fwd=58); arm('nx', 22, 116, upper_fwd=64)
    rot('Bone_017', X, 16); rot('Bone_017', Z, 28)
    floor()
else:
    sys.exit('POSECLIP unknown pose %s %s' % (NAME, POSE))

# ---------- key it ----------
bpy.context.view_layer.update()
posed = {pb.name: pb.matrix_basis.copy() for pb in rig.pose.bones}
act = bpy.data.actions.new(POSE)
rig.animation_data_create(); rig.animation_data.action = act
for pb in rig.pose.bones: pb.rotation_mode = 'QUATERNION'


def key(frame, basis):
    for pb in rig.pose.bones:
        pb.matrix_basis = basis[pb.name] if basis else Matrix.Identity(4)
        pb.keyframe_insert('location', frame=frame); pb.keyframe_insert('rotation_quaternion', frame=frame)


if len(frames) == 3:
    key(frames[0], None); key(frames[1], posed); key(frames[2], posed)
else:
    key(frames[0], posed); key(frames[1], posed)
sc.frame_start, sc.frame_end = frames[0], frames[-1]
sc.frame_set(frames[-1]); bpy.context.view_layer.update()

V = world_verts()
log['posed_min_z'] = round(float(V[:, 2].min()), 2)
log['posed_size_cm'] = [round(float(v), 1) for v in (V.max(0) - V.min(0))]
log['posed_min'] = [round(float(v), 1) for v in V.min(0)]
log['posed_max'] = [round(float(v), 1) for v in V.max(0)]
hd = (rig.matrix_world @ rig.pose.bones['Bone_016'].matrix).to_translation()
log['head_at'] = [round(v, 1) for v in hd]

# ---------- check sheet: front, side, three-quarter, top ----------
world = bpy.data.worlds.new('W'); sc.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.5, 0.5, 0.52, 1); world.node_tree.nodes['Background'].inputs[1].default_value = 1.2
sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN')); sun.data.energy = 3; sun.rotation_euler = (0.7, 0.2, -0.5); sc.collection.objects.link(sun)
bpy.ops.mesh.primitive_plane_add(size=600); ground = bpy.context.object
gm = bpy.data.materials.new('G'); gm.diffuse_color = (0.42, 0.42, 0.45, 1); ground.data.materials.append(gm)
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = H * 1.45; cam.data.clip_end = 100000
sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x = 420; sc.render.resolution_y = 420
ctr = Vector(((V[:, 0].min() + V[:, 0].max()) / 2, (V[:, 1].min() + V[:, 1].max()) / 2, (V[:, 2].max()) / 2))
tiles = []
views = [('front', Vector((0, -1, 0.12))), ('side', Vector((1, 0, 0.12))), ('three', Vector((0.7, -1, 0.55))), ('top', Vector((0.001, -0.02, 1)))]
for tag, v in views:
    v = v.normalized(); cam.location = ctr + v * H * 4
    cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
    fp = os.path.join(CACHE, '%s_%s_%s.png' % (NAME, POSE, tag)); sc.render.filepath = fp
    bpy.ops.render.render(write_still=True); tiles.append(fp)
W = 420; out = np.zeros((W, W * len(tiles), 4), np.float32)
for i, fp in enumerate(tiles):
    im = bpy.data.images.load(fp); x = np.empty(W * W * 4, np.float32); im.pixels.foreach_get(x); out[:, i * W:(i + 1) * W] = x.reshape(W, W, 4)
s = bpy.data.images.new('sheet', W * len(tiles), W); s.pixels.foreach_set(out.ravel())
s.filepath_raw = os.path.join(CACHE, '%s_%s.png' % (NAME, POSE)); s.file_format = 'PNG'; s.save()
for fp in tiles: os.remove(fp)
log['sheet'] = s.filepath_raw
bpy.data.objects.remove(ground)

# ---------- export: mesh + rig + this one action, same settings as meshy_character.py ----------
for o in sc.objects: o.select_set(o in (mesh, rig))
bpy.context.view_layer.objects.active = rig
for other in list(bpy.data.actions):
    if other != act: bpy.data.actions.remove(other)
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, object_types={'ARMATURE', 'MESH'}, axis_forward='-Z', axis_up='Y',
                         global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', mesh_smooth_type='FACE',
                         add_leaf_bones=False, primary_bone_axis='Y', secondary_bone_axis='X', bake_anim=True,
                         bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False, bake_anim_force_startend_keying=True,
                         bake_anim_simplify_factor=0.0, path_mode='STRIP', embed_textures=False)
log['fbx'] = OUT

# ---------- verify: read the new FBX and the original back and compare the skeletons ----------
def read_back(path, with_anim):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.scale_length = 0.01
    bpy.ops.import_scene.fbx(filepath=path, automatic_bone_orientation=False, use_anim=with_anim, ignore_leaf_bones=False)
    r = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE'][0]
    m = [o for o in bpy.context.scene.objects if o.type == 'MESH'][0]
    rest = {b.name: (r.matrix_world @ b.head_local) for b in r.data.bones}
    return r, m, rest


r0, m0, rest0 = read_back(SRC, False)
tris0 = sum(len(p.vertices) - 2 for p in m0.data.polygons)
r1, m1, rest1 = read_back(OUT, True)
tris1 = sum(len(p.vertices) - 2 for p in m1.data.polygons)
drift = max((rest0[n] - rest1[n]).length for n in rest0) if set(rest0) == set(rest1) else -1.0
log['verify'] = {'bones_src': len(rest0), 'bones_out': len(rest1), 'same_bone_names': set(rest0) == set(rest1),
                 'max_rest_drift_cm': round(drift, 4), 'tris_src': tris0, 'tris_out': tris1,
                 'actions': [(a_.name, [int(a_.frame_range[0]), int(a_.frame_range[1])]) for a_ in bpy.data.actions]}
bpy.context.scene.frame_set(int(bpy.data.actions[0].frame_range[1]) if bpy.data.actions else 1)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get(); e = m1.evaluated_get(dg); me = e.to_mesh()
Vb = np.array([e.matrix_world @ v.co for v in me.vertices]); e.to_mesh_clear()
log['verify']['readback_min_z'] = round(float(Vb[:, 2].min()), 2)
log['verify']['readback_size_cm'] = [round(float(v), 1) for v in (Vb.max(0) - Vb.min(0))]
print('POSECLIP ' + json.dumps(log))
