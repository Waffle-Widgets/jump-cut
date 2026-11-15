"""The coworker's standing idle: her sculpted A-pose with the arms lowered, breathing. Blender 5.3.0, headless:

    blender -b --factory-startup --python Art/Blender/coworker_idle.py [-- norender]

Reads  Art/Blender/export/Characters/CafeCoworkerV2/SK_CafeCoworkerV2_oldrig_skinfix.fbx  (the body in the game)
Writes .../CafeCoworkerV2/SK_CafeCoworkerV2_Idle.fbx (mesh + rig + one 4 s looping action) and a check sheet
       Art/Blender/cache/CafeCoworkerV2_Idle.png (front and side, at rest breath and full breath).

WHY (Sun Nov 15). Her only idle, SK_CafeCoworkerArmature_Idle, holds the pose she was sculpted in: arms out from
her sides, hands flared. It is the first other person the player sees. Same cure as the player's idle: change as
little as possible from the A-pose - lower the arms, hang the hands, breathe. Nothing below the chest is touched and
the root and hip bones stay at rest, so she stands exactly where the old clip stood her.

Each bone is turned about a WORLD axis through its own head and the view layer is updated after every bone
(pose_bone.matrix resolves against the parent's current matrix - skip the update and the chain tears).
Her LEFT is +X and she faces -Y, like the player.
"""
import bpy, sys, os, math
from mathutils import Vector, Matrix

a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
E = lambda k, d: float(os.environ.get(k, d))
ARM_OUT, ARM_FWD = E('ARM_OUT', 9.0), E('ARM_FWD', 3.0)      # degrees from straight down: sideways, forward
ELBOW = E('ELBOW', 9.0)                                      # forearm forward of the upper arm, degrees
HAND_IN = E('HAND_IN', 1.0)                                  # 1 = hand hangs straight down from the wrist
SH_UP = E('SH_UP', 8.0)                                      # collarbone lift so the lowered arm does not pinch the sleeve
BREATH, SWAY = E('BREATH', 1.1), E('SWAY', 0.35)
FRAMES, FPS = 120, 30
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
DIR = os.path.join(REPO, 'Art', 'Blender', 'export', 'Characters', 'CafeCoworkerV2')
SRC = os.path.join(DIR, 'SK_CafeCoworkerV2_oldrig_skinfix.fbx')
OUT = os.path.join(DIR, 'SK_CafeCoworkerV2_Idle.fbx')
CACHE = os.path.join(REPO, 'Art', 'Blender', 'cache'); os.makedirs(CACHE, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.scale_length = 0.01; sc.render.fps = FPS
bpy.ops.import_scene.fbx(filepath=SRC, automatic_bone_orientation=False, use_anim=False, ignore_leaf_bones=False)
rig = [o for o in sc.objects if o.type == 'ARMATURE'][0]
mesh = max([o for o in sc.objects if o.type == 'MESH'], key=lambda o: len(o.data.vertices))
if rig.animation_data: rig.animation_data.action = None
PB = rig.pose.bones


def reset():
    for pb in PB:
        pb.rotation_mode = 'QUATERNION'; pb.location = (0, 0, 0); pb.rotation_quaternion = (1, 0, 0, 0); pb.scale = (1, 1, 1)
    bpy.context.view_layer.update()


reset()
RW = rig.matrix_world.copy(); RWI = RW.inverted()
head = lambda n: RW @ PB[n].head
kid = lambda n: PB[n].children[0].name


def rot(n, axis, deg):
    if abs(deg) < 1e-6: return
    h = head(n)
    Wn = Matrix.Translation(h) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-h) @ (RW @ PB[n].matrix)
    PB[n].matrix = RWI @ Wn
    bpy.context.view_layer.update()


def aim(n, end_pt, d):
    cur = end_pt - head(n); ax = cur.cross(d)
    if ax.length < 1e-9: return
    rot(n, ax.normalized(), math.degrees(cur.angle(d)))


X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
UP = ('Bone_022', 'Bone_027') if head('Bone_022').x > head('Bone_027').x else ('Bone_027', 'Bone_022')   # (her left, her right)
CLAV = [PB[u].parent.name for u in UP]


def hand_tip(w):
    """The far end of the hand: the point furthest from the wrist among the bones under it."""
    pts = [RW @ b.tail for b in PB[w].children_recursive] or [RW @ PB[w].tail]
    return max(pts, key=lambda p: (p - head(w)).length)


def pose(f):
    reset()
    u = f / FRAMES
    br = 0.5 - 0.5 * math.cos(2 * math.pi * u)               # 0 = out, 1 = full breath, once per loop
    sw = math.sin(2 * math.pi * u)
    rot('Bone_005', Y, SWAY * sw)                            # the faintest sway, waist up
    rot('Bone_004', X, BREATH * br)                          # chest lifts (she faces -Y: +X turn leans her back)
    rot('Bone_017', X, -0.7 * BREATH * br)                   # the head stays level
    for i, up in enumerate(UP):
        sg = 1.0 if i == 0 else -1.0
        fo = kid(up); wr = kid(fo)
        rot(CLAV[i], Y, -sg * (SH_UP + 0.8 * br))
        so, sf = math.sin(math.radians(ARM_OUT)), math.sin(math.radians(ARM_FWD))
        aim(up, head(fo), Vector((sg * so, -sf, -1)).normalized())
        aim(fo, head(wr), Vector((sg * so * 0.6, -math.sin(math.radians(ARM_FWD + ELBOW)), -1)).normalized())
        tip = hand_tip(wr); cur = (tip - head(wr)).normalized()
        want = Vector((sg * 0.04, -0.12, -1)).normalized()
        aim(wr, tip, cur.lerp(want, HAND_IN).normalized())


rig.animation_data_create()
act = bpy.data.actions.new('Idle'); rig.animation_data.action = act
for f in range(FRAMES + 1):
    pose(f % FRAMES)
    for pb in PB:
        pb.location = (0, 0, 0); pb.scale = (1, 1, 1)
        pb.keyframe_insert('rotation_quaternion', frame=f); pb.keyframe_insert('location', frame=f)
sc.frame_start, sc.frame_end = 0, FRAMES
print('CWIDLE keyed %d frames on %d bones' % (FRAMES + 1, len(PB)))

if 'norender' not in a:
    world = bpy.data.worlds.new('W'); sc.world = world; world.use_nodes = True
    world.node_tree.nodes['Background'].inputs[0].default_value = (0.9, 0.9, 0.9, 1); world.node_tree.nodes['Background'].inputs[1].default_value = 1.2
    sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN')); sun.data.energy = 3; sun.rotation_euler = (0.7, 0.2, -0.5); sc.collection.objects.link(sun)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.type = 'ORTHO'; cam.data.clip_end = 100000; cam.data.ortho_scale = 190
    sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x, sc.render.resolution_y = 500, 700
    tiles = []
    for f in (0, FRAMES // 2):
        sc.frame_set(f)
        for tag, d in (('front', Vector((0, -1, 0))), ('side', Vector((1, 0, 0))), ('back', Vector((0, 1, 0)))):
            ctr = Vector((0, 0, 88)); cam.location = ctr + d * 1000
            cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
            fp = os.path.join(CACHE, '_cwi_%d_%s.png' % (f, tag)); sc.render.filepath = fp; bpy.ops.render.render(write_still=True); tiles.append(fp)
    imgs = [bpy.data.images.load(t) for t in tiles]
    import numpy as np
    w, h = imgs[0].size
    rows = []
    for r in range(2):
        rows.append(np.concatenate([np.array(imgs[r * 3 + c].pixels[:]).reshape(h, w, 4) for c in range(3)], axis=1))
    sheet = np.concatenate(rows[::-1], axis=0)
    out = bpy.data.images.new('sheet', w * 3, h * 2); out.pixels[:] = sheet.ravel().tolist()
    out.filepath_raw = os.path.join(CACHE, 'CafeCoworkerV2_Idle.png'); out.file_format = 'PNG'; out.save()
    for o in (sun, cam): bpy.data.objects.remove(o)
    print('CWIDLE sheet %s' % out.filepath_raw)

if 'noexport' not in a:
    for o in sc.objects: o.select_set(o in (mesh, rig))
    bpy.context.view_layer.objects.active = rig
    for other in list(bpy.data.actions):
        if other != act: bpy.data.actions.remove(other)
    bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, object_types={'ARMATURE', 'MESH'}, axis_forward='-Z', axis_up='Y',
                             global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', mesh_smooth_type='FACE',
                             add_leaf_bones=False, primary_bone_axis='Y', secondary_bone_axis='X', bake_anim=True,
                             bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False, bake_anim_force_startend_keying=True,
                             bake_anim_simplify_factor=0.0, path_mode='STRIP', embed_textures=False)
    print('CWIDLE exported %s' % OUT)
