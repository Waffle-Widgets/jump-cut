# The player's death (issue #14), authored here instead of retargeted from Epic's mannequin (issue #103). Headless:
#   blender -b --factory-startup --python Art/Blender/death_clip.py
# Reads the committed Art/Blender/export/Characters/CafeWalker/SK_CafeWalker.fbx (the mesh and 69-bone skeleton
# BP_Player wears), animates the SAME skeleton, and writes SK_CafeWalker_Death.fbx beside it: mesh + rig + one
# action named Death, 60 frames at 30 fps. Nothing about the original FBX changes. Always author from the committed
# FBX, never from a previous export of this script: the exporter re-prefixes action names on every round trip.
# Check sheets go to Art/Blender/cache/CafeWalker_Death_<view>.png - LOOK at them, the numbers are not the test.
#
# The clip: he takes a last hook to the jaw, reels a step back, his legs go, he sits down hard, his back and head
# slam, and he stays down - on his back, head rolled away, one knee fallen open, one arm up by his head. The final
# 9 frames are identical, because the montage is imported with auto blend-out off and the last frame is held.
#
# Rig (Meshy Smart Rig, same layout as pose_clip.py documents; the model faces -Y, Z up, his left is +X):
#   Bone_000 root (at PELVIS height, 90 cm, and it carries skin weight) > Bone_001 hip > 005 > 004 > 003 > 002 spine
#   > 018 > 017 > 016 neck/head. Arms off 002: 023/028 clavicle > 022/027 upper > 021/026 fore > 020/025 wrist
#   > 019/024 hand > five 4-bone finger chains. Legs off 001: 010/015 thigh > 009/014 shin > 008/013 foot > toes.
#   The bind pose is a wide A-pose with OPEN, SPLAYED palms facing forward - that is where the "paddle hands" of the
#   retargeted clips come from (#72). Here every finger bone is curled on every frame.
# Because the root is the pelvis, the whole fall is keyed on Bone_000 (translation + rotation). In Unreal this clip
# must play with root motion OFF: with it on, RootMotionRootLock = AnimFirstFrame pins the pelvis at standing height
# and the body hangs in the air.
#
# How it is built. Not a handful of key poses with Blender interpolating bone rotations between them - that lets
# planted feet skate. Instead the CONTROLS are keyed (pelvis path, body pitch, spine, head, foot and hand targets),
# and for every one of the 60 frames the pose is solved and every bone is keyed:
#   1. spine, neck, head: rot() - a turn about a WORLD axis through the bone's own head, parents first, exactly
#      pose_clip.py's convention (about +X: positive bends him forward; about +Y: positive leans him to +X; about
#      +Z: positive turns him to his left). Done while the root is still upright, so world axes are body axes.
#   2. the root is placed (heading, pitch, lean, twist, pelvis position).
#   3. legs and arms: two-bone IK to a world-space ankle / wrist target with a pole direction for the knee / elbow,
#      then the foot is set to an absolute orientation. A planted foot is the same world point on every frame.
#   4. fingers curl.
#   5. floor: body, each limb and the head are tested against z = 0 and pushed up out of it (never down), so a part
#      whose target is keyed slightly under the floor lands ON it. Nothing floats, nothing sinks.
# rot() here is pose_clip.py's helper with the same maths, but it tracks the bone matrices itself instead of calling
# view_layer.update() - it runs ~20 000 times. The result is asserted against Blender's own pose evaluation.
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector, Matrix, Quaternion

a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
NAME, CLIP = 'CafeWalker', 'Death'
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
CACHE = os.path.join(REPO, 'Art', 'Blender', 'cache'); os.makedirs(CACHE, exist_ok=True)
DIR = os.path.join(REPO, 'Art', 'Blender', 'export', 'Characters', NAME)
SRC = os.path.join(DIR, 'SK_%s.fbx' % NAME)
OUT = os.path.join(DIR, 'SK_%s_%s.fbx' % (NAME, CLIP))
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
F0, F1, FPS = 1, 60, 30
log = {'name': NAME, 'clip': CLIP, 'frames': [F0, F1], 'fps': FPS}

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.scale_length = 0.01                       # centimetre scene, like meshy_character.py
sc.render.fps = FPS
bpy.ops.import_scene.fbx(filepath=SRC, automatic_bone_orientation=False, use_anim=False, ignore_leaf_bones=False)
rig = [o for o in sc.objects if o.type == 'ARMATURE'][0]
mesh = [o for o in sc.objects if o.type == 'MESH'][0]
log['bones_in'] = len(rig.data.bones); log['verts_in'] = len(mesh.data.vertices); log['polys_in'] = len(mesh.data.polygons)
# The importer applies the export-time pose (frame 0 of Walk) to the pose bones even with use_anim=False. Reset it,
# or the whole clip is built on top of a walking stride (see pose_clip.py).
if rig.animation_data: rig.animation_data.action = None
for pb in rig.pose.bones:
    pb.rotation_mode = 'QUATERNION'
    pb.location = (0, 0, 0); pb.rotation_quaternion = (1, 0, 0, 0); pb.scale = (1, 1, 1)
bpy.context.view_layer.update()
RW = rig.matrix_world.copy()


def world_verts():
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); e = mesh.evaluated_get(dg); me = e.to_mesh()
    co = np.empty(len(me.vertices) * 3, np.float64); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    M = np.array(e.matrix_world); e.to_mesh_clear()
    return co @ M[:3, :3].T + M[:3, 3]


V0 = world_verts()
H = float(V0[:, 2].max() - V0[:, 2].min())
log['rest_size_cm'] = [round(float(v), 1) for v in (V0.max(0) - V0.min(0))]; log['rest_min_z'] = round(float(V0[:, 2].min()), 2)

# ---------- the skeleton, kept as plain matrices ----------
BONES = []
def _walk(b):
    BONES.append(b.name)
    for c in b.children: _walk(c)
for b in rig.data.bones:
    if not b.parent: _walk(b)                              # parents first
PARENT = {b.name: (b.parent.name if b.parent else None) for b in rig.data.bones}
REST = {b.name: RW @ b.matrix_local for b in rig.data.bones}                       # world rest matrices
REL = {n: (REST[PARENT[n]].inverted() @ REST[n]) if PARENT[n] else None for n in BONES}
SUB = {n: [] for n in BONES}
for n in BONES:
    p = PARENT[n]
    while p: SUB[p].append(n); p = PARENT[p]               # SUB[n]: everything under n, parents first
RH = {n: REST[n].to_translation() for n in BONES}          # rest head positions
BASIS, W = {}, {}


def reset():
    for n in BONES: BASIS[n] = Matrix.Identity(4); W[n] = REST[n].copy()


def head(b): return W[b].to_translation()


def set_world(b, Wn):
    p = PARENT[b]
    base = (W[p] @ REL[b]) if p else REST[b]
    BASIS[b] = base.inverted() @ Wn; W[b] = Wn
    for c in SUB[b]: W[c] = W[PARENT[c]] @ REL[c] @ BASIS[c]


def rot(bone, axis, deg):
    """Turn a bone (and everything under it) about a WORLD axis through its own head. Same as pose_clip.rot()."""
    if abs(deg) < 1e-7: return
    h = head(bone)
    set_world(bone, Matrix.Translation(h) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-h) @ W[bone])


def aim(bone, end, d):
    """Swing `bone` the short way so the line from its head to `end`'s head points along d."""
    cur = head(end) - head(bone); ax = cur.cross(d)
    if ax.length < 1e-9: return
    rot(bone, ax.normalized(), math.degrees(cur.angle(d)))


def carried(bone, v):
    """A rest-pose world direction, carried along with the bone."""
    return (W[bone].to_3x3() @ REST[bone].to_3x3().inverted()) @ v


def twist_to(bone, end, rest_vec, want):
    """Spin `bone` about its own length until the rest-pose direction rest_vec, carried with it, lines up with want."""
    ax = (head(end) - head(bone)).normalized()
    c = carried(bone, rest_vec); c = c - ax * c.dot(ax); w = want - ax * want.dot(ax)
    if c.length < 1e-6 or w.length < 1e-6: return
    rot(bone, ax, math.degrees(math.atan2(ax.dot(c.cross(w)), c.dot(w))))


def frame3(f, u):
    f = f.normalized(); s = f.cross(u).normalized(); u = s.cross(f)
    return Matrix((f, u, s)).transposed()


def orient(bone, f, u, f0, u0):
    """Absolute orientation: the bone is turned from rest so that rest directions f0 / u0 point along f / u."""
    R = frame3(f, u) @ frame3(f0, u0).transposed()
    set_world(bone, Matrix.Translation(head(bone)) @ R.to_4x4() @ Matrix.Translation(-RH[bone]) @ REST[bone])


REACH = {}                                                 # how far past full stretch an IK target was, per limb

def ik2(tag, up, lo, end, target, pole, rest_pole):
    """Two-bone IK. up/lo/end: thigh, shin, foot (or upper arm, forearm, wrist). The knee / elbow goes toward pole,
    and the upper bone is twisted so the joint's real hinge - which bends away from rest_pole in the bind pose -
    does the bending, instead of the skin being wrung."""
    h = head(up); L1 = (RH[lo] - RH[up]).length; L2 = (RH[end] - RH[lo]).length
    d = target - h; dist = d.length
    REACH[tag] = max(0.0, dist - (L1 + L2))
    dist = min(max(dist, abs(L1 - L2) + 0.5), L1 + L2 - 0.02); dn = d.normalized()
    p = pole - dn * pole.dot(dn)
    if p.length < 1e-6: p = Z - dn * Z.dot(dn)
    p.normalize()
    al = (L1 * L1 - L2 * L2 + dist * dist) / (2 * dist); hh = math.sqrt(max(L1 * L1 - al * al, 0.0))
    aim(up, lo, dn * al + p * hh)
    twist_to(up, lo, rest_pole, p)
    aim(lo, end, (h + dn * dist) - head(lo))


# which chain is on +X (his left), and the bones of each limb
def _px(c): return c if RH[c[0]].x > RH[c[1]].x else (c[1], c[0])
ARM_UP = dict(zip('LR', _px(('Bone_022', 'Bone_027'))))
LEG_UP = dict(zip('LR', _px(('Bone_010', 'Bone_015'))))
def _child(n): return [c for c in BONES if PARENT[c] == n]
ARM = {s: (ARM_UP[s], _child(ARM_UP[s])[0], _child(_child(ARM_UP[s])[0])[0]) for s in 'LR'}        # upper, fore, wrist
HAND = {s: _child(ARM[s][2])[0] for s in 'LR'}
LEG = {s: (LEG_UP[s], _child(LEG_UP[s])[0], _child(_child(LEG_UP[s])[0])[0]) for s in 'LR'}        # thigh, shin, foot
SGN = {'L': 1.0, 'R': -1.0}
FOOT_F0 = {s: Vector((RH[_child(LEG[s][2])[0]].x - RH[LEG[s][2]].x, RH[_child(LEG[s][2])[0]].y - RH[LEG[s][2]].y, 0)).normalized() for s in 'LR'}

# fingers: every chain under the hand. Each bone gets a hinge axis (in its own local frame) that folds it toward the
# palm; the thumb - the chain that leaves the hand sideways - also gets an axis that swings it in under the fingers.
FING = {}
for s in 'LR':
    chains = []
    for root in _child(HAND[s]):
        ch = [root]
        while _child(ch[-1]): ch.append(_child(ch[-1])[0])
        chains.append(ch)
    dirs = [(RH[c[-1]] - RH[c[0]]).normalized() for c in chains]
    thumb = min(range(len(chains)), key=lambda i: sum(dirs[i].dot(dirs[j]) for j in range(len(chains))))
    fdir = sum((dirs[i] for i in range(len(chains)) if i != thumb), Vector()).normalized()
    roots = sorted((RH[chains[i][0]] for i in range(len(chains)) if i != thumb), key=lambda v: v.x)
    palm = (roots[-1] - roots[0]).cross(fdir).normalized()
    if palm.dot(-Y) < 0: palm = -palm                      # the palm faces forward in the bind pose
    out = []
    for i, ch in enumerate(chains):
        for k, b in enumerate(ch):
            tail = RH[ch[k + 1]] if k + 1 < len(ch) else RW @ rig.data.bones[b].tail_local
            d = (tail - RH[b]).normalized()
            hinge = REST[b].to_3x3().inverted() @ d.cross(palm).normalized()
            swing = None                                   # (local axis, degrees at full curl) for the chain's first bone
            if k == 0:
                fd = (RH[ch[-1]] - RH[ch[0]]).normalized(); ax = fd.cross(fdir)
                if i == thumb:                             # the thumb comes in under the fingers
                    swing = (REST[b].to_3x3().inverted() @ ax.normalized(), 0.72 * math.degrees(fd.angle(fdir)))
                elif ax.length > 1e-4:                     # the fingers close up their fan
                    swing = (REST[b].to_3x3().inverted() @ ax.normalized(), 0.8 * math.degrees(fd.angle(fdir)))
            out.append((b, k, i == thumb, hinge.normalized(), swing))
    FING[s] = out
CURL = (62.0, 70.0, 42.0, 20.0)                            # degrees per joint down a finger at curl = 1
THUMB = (18.0, 40.0, 34.0, 12.0)


def fingers(s, curl):
    for b, k, is_thumb, hinge, swing in FING[s]:
        q = Quaternion(hinge, math.radians((THUMB if is_thumb else CURL)[min(k, 3)] * curl))
        if swing is not None: q = Quaternion(swing[0], math.radians(swing[1] * min(curl * 1.5, 1.0))) @ q
        BASIS[b] = q.to_matrix().to_4x4(); W[b] = W[PARENT[b]] @ REL[b] @ BASIS[b]


# ---------- the performance: keyed controls ----------
# A key is (frame, value[, kind]). kind: 's' smooth through (default), 'z' stop here (ease in and out), 'hit' arrive
# accelerating and stop dead (something landing; 'land' is the softer version, for a limb), 'lin' straight lines.
# Targets carry a space: 'w' world, 'c' riding the chest (given in bind-pose coordinates), 'g' on the ground under
# the pelvis, turned with his heading (x to his left, y toward his head once he is on his back).
P0 = RH['Bone_000'].copy()
CH = {
    # --- the body ---
    'pel_xy':  [(1, (0, 0)), (4, (0, 2)), (12, (-3, 21)), (17, (-4, 30)), (28, (-5, 70)), (34, (-5, 75), 'z')],
    'pel_z':   [(1, -4), (4, -3), (12, -6), (17, -10), (29, -92, 'hit')],                 # the floor pass stops it
    'pitch':   [(1, 6), (4, -6), (11, -15), (17, -11), (23, -28), (28, -54), (33, -90, 'hit'), (36, -86.5, 'z'), (40, -90, 'z')],
    'heading': [(1, 0), (4, -3), (12, -8), (34, -11, 'z')],
    'lean':    [(1, 0), (8, 4), (17, -3), (23, -8), (31, 0, 'z')],
    'twist':   [(1, 0), (4, -8), (11, -13), (20, -8), (30, 0, 'z')],
    'spine':   [(1, (12, 0, 0)), (4, (-9, 0, -10)), (8, (-17, 3, -14)), (17, (5, -4, -6)), (26, (28, -3, 0)), (30, (18, -2, 0)),
                (33, (5, 0, 0), 'hit'), (37, (0, 0, 2), 'z')],
    'head':    [(1, (-6, 0, 0)), (3, (-22, 6, -34), 'lin'), (8, (-30, 10, -30)), (14, (-8, 8, -18)), (21, (20, 5, -8)),
                (29, (34, 0, 0)), (32, (24, 0, -2)), (35, (-10, 0, -6), 'hit'), (38, (4, 0, -14)), (42, (-8, 3, -30)),
                (51, (-14, 5, -46), 'z')],
    # --- feet: ankle target, kneecap direction, toe direction, top-of-foot direction ---
    'footL':   [(1, ('w', (17, -6, 12)), 'z'), (22, ('w', (17, -6, 12)), 'z'), (28, ('w', (17, -7, 9))),
                (32, ('w', (19, -3, 24))), (38, ('w', (21, -6, 0)), 'hit')],
    'kneeL':   [(1, ('w', (0.15, -1, 0))), (24, ('w', (0.15, -1, 0.5))), (38, ('w', (0.35, 0, 1)), 'z')],
    'toeL':    [(1, (0.2, -1, 0), 'z'), (20, (0.2, -1, 0), 'z'), (28, (0.2, -0.8, 0.6)), (38, (0.7, -0.2, 0.7), 'z')],
    'topL':    [(1, (0, 0, 1), 'z'), (20, (0, 0, 1), 'z'), (28, (0, 0.6, 0.8)), (38, (-0.1, 1, 0.15), 'z')],
    'footR':   [(1, ('w', (-17, 12, 12)), 'z'), (5, ('w', (-17, 12, 12)), 'z'), (8, ('w', (-19, 27, 21))),
                (11, ('w', (-21, 38, 12)), 'hit'), (33, ('w', (-21, 38, 12)), 'z'), (47, ('w', (-30, 17, 0)), 'z')],
    'kneeR':   [(1, ('w', (-0.3, -1, 0))), (28, ('w', (-0.3, -1, 0.6))), (34, ('w', (-0.25, -0.2, 1))),
                (48, ('w', (-1, -0.1, 0.75)), 'z')],
    'toeR':    [(1, (-0.45, -1, 0), 'z'), (5, (-0.45, -1, 0), 'z'), (8, (-0.4, -1, -0.5)), (11, (-0.5, -1, 0), 'z'),
                (33, (-0.5, -1, 0), 'z'), (47, (-0.75, -0.65, 0.2), 'z')],
    'topR':    [(1, (0, 0, 1), 'z'), (33, (0, 0, 1), 'z'), (47, (-0.55, 0.3, 0.8), 'z')],
    # --- hands: wrist target, elbow direction, forearm pronation (degrees), finger curl (0 open .. 1 fist) ---
    # The arms are a beat behind the body all the way down: thrown up by the punch, limp while he hangs, left
    # behind in the air when he drops, and the last thing to land.
    # An elbow direction must stay well off the line from shoulder to wrist, or the elbow flips sides between frames.
    'handL':   [(1, ('c', (20, -24, 112))), (5, ('c', (30, -30, 122))), (9, ('c', (47, -30, 137))), (14, ('c', (46, -8, 116))),
                (18, ('c', (33, -4, 96))), (24, ('c', (46, -16, 126))), (30, ('c', (55, -18, 146))), (37, ('g', (62, 30, 0)), 'land'),
                (40, ('g', (63, 30, 9))), (44, ('g', (63, 30, 0)), 'land')],
    'elbowL':  [(1, ('c', (0.7, 0.6, -0.3))), (9, ('c', (0.4, 0.4, -1))), (16, ('c', (0.5, 1, 0))), (26, ('c', (0, 0.5, -1))),
                (32, ('c', (0, 0.5, -1))), (37, ('g', (0, -1, -0.2)), 'z')],
    'pronL':   [(1, 80), (10, 60), (30, 50), (38, 30, 'z')],
    'curlL':   [(1, 1.0), (5, 0.78), (17, 0.7), (38, 0.74), (46, 0.7, 'z')],
    'handR':   [(1, ('c', (-22, -18, 104))), (5, ('c', (-32, -24, 110))), (10, ('c', (-50, -16, 127))), (15, ('c', (-45, -2, 110))),
                (19, ('c', (-33, -3, 93))), (25, ('c', (-47, -14, 120))), (31, ('c', (-56, -14, 138))), (38, ('g', (-37, 3, 0)), 'land'),
                (41, ('g', (-38, 2, 12))), (45, ('g', (-38, 2, 0)), 'land')],
    'elbowR':  [(1, ('c', (-0.7, 0.6, -0.3))), (10, ('c', (-0.4, 0.4, -1))), (17, ('c', (-0.5, 1, 0))), (27, ('c', (-0.4, 0.8, 0.6))),
                (33, ('c', (-0.5, 0.4, 0.8))), (38, ('g', (-0.7, 0.7, -0.15)), 'z')],
    'pronR':   [(1, 80), (11, 60), (30, 60), (39, 70, 'z')],
    'curlR':   [(1, 1.0), (5, 0.8), (17, 0.7), (39, 0.76), (47, 0.72, 'z')],
}


def herm(keys, f):
    n = len(keys)
    if f <= keys[0][0]: return keys[0][1]
    if f >= keys[-1][0]: return keys[-1][1]
    i = max(j for j in range(n - 1) if keys[j][0] <= f)
    f0, v0 = keys[i][0], keys[i][1]; f1, v1 = keys[i + 1][0], keys[i + 1][1]; h = f1 - f0; s = (f - f0) / h

    def tan(j, side):
        fj, vj, kj = keys[j]
        if kj == 'z': return 0 * vj
        if kj in ('hit', 'land'):
            return 0 * vj if side == 'out' else (2.0 if kj == 'hit' else 1.4) * (vj - keys[j - 1][1]) / (fj - keys[j - 1][0])
        if kj == 'lin':
            if side == 'out' and j < n - 1: return (keys[j + 1][1] - vj) / (keys[j + 1][0] - fj)
            if side == 'in' and j > 0: return (vj - keys[j - 1][1]) / (fj - keys[j - 1][0])
            return 0 * vj
        if j == 0 or j == n - 1: return 0 * vj
        return (keys[j + 1][1] - keys[j - 1][1]) / (keys[j + 1][0] - keys[j - 1][0])
    m0 = tan(i, 'out') * h; m1 = tan(i + 1, 'in') * h; s2 = s * s; s3 = s2 * s
    return (2 * s3 - 3 * s2 + 1) * v0 + (s3 - 2 * s2 + s) * m0 + (-2 * s3 + 3 * s2) * v1 + (s3 - s2) * m1


def ev(name, f):
    return herm([(k[0], np.asarray(k[1], np.float64), k[2] if len(k) > 2 else 's') for k in CH[name]], f)


def evs(name, f, spaces, direction=False):
    """A channel whose keys carry a space: bring every key into the world AS OF THIS FRAME, then interpolate."""
    ks = []
    for k in CH[name]:
        sp, v = k[1]; M = spaces[sp]; v = Vector(v)
        v = (M.to_3x3() @ v) if direction else (M @ v)
        ks.append((k[0], np.array(v, np.float64), k[2] if len(k) > 2 else 's'))
    return Vector(herm(ks, f))


def build(f, lift, raise_, elbow_up, headfix):
    """Solve the pose of frame f into BASIS / W."""
    reset()
    sp = ev('spine', f) / 3.0
    for b in ('Bone_005', 'Bone_004', 'Bone_003'):
        rot(b, X, sp[0]); rot(b, Y, sp[1]); rot(b, Z, sp[2])
    hd = ev('head', f)
    for b, k in (('Bone_018', 0.4), ('Bone_017', 0.6)):
        rot(b, X, hd[0] * k); rot(b, Y, hd[1] * k); rot(b, Z, hd[2] * k)
    xy = ev('pel_xy', f); pos = P0 + Vector((xy[0], xy[1], float(ev('pel_z', f)) + lift))
    Rg = Matrix.Rotation(math.radians(float(ev('heading', f))), 4, Z)
    R = Rg @ Matrix.Rotation(math.radians(float(ev('pitch', f))), 4, X) @ Matrix.Rotation(math.radians(float(ev('lean', f))), 4, Y) \
        @ Matrix.Rotation(math.radians(float(ev('twist', f))), 4, Z)
    set_world('Bone_000', Matrix.Translation(pos) @ R @ Matrix.Translation(-P0) @ REST['Bone_000'])
    if headfix: rot('Bone_017', (R.to_3x3() @ X).normalized(), headfix)
    spaces = {'w': Matrix.Identity(4), 'c': W['Bone_002'] @ REST['Bone_002'].inverted(),
              'g': Matrix.Translation(Vector((pos.x, pos.y, 0))) @ Rg}
    for s in 'LR':
        th, sh, ft = LEG[s]
        t = evs('foot' + s, f, spaces); t.z = max(t.z, 0.0) + raise_['leg' + s]
        ik2('leg' + s, th, sh, ft, t, evs('knee' + s, f, spaces, True), -Y)
        orient(ft, Vector(ev('toe' + s, f)), Vector(ev('top' + s, f)), FOOT_F0[s], Z)
    for s in 'LR':
        up, fo, wr = ARM[s]
        t = evs('hand' + s, f, spaces); t.z = max(t.z, 0.0) + raise_['arm' + s]
        ik2('arm' + s, up, fo, wr, t, evs('elbow' + s, f, spaces, True).normalized() + Z * elbow_up['uarm' + s], Y)
        rot(fo, (head(wr) - head(fo)).normalized(), SGN[s] * float(ev('pron' + s, f)))
        fingers(s, float(ev('curl' + s, f)))


def apply_pose():
    for pb in rig.pose.bones: pb.matrix_basis = BASIS[pb.name]


# vertex groups for the floor pass: each vertex goes with the bone that weighs most on it
vg = {g.index: g.name for g in mesh.vertex_groups}
dom = [vg[max(v.groups, key=lambda g: g.weight).group] if v.groups else 'Bone_000' for v in mesh.data.vertices]
PART = {}
for s in 'LR':
    PART[ARM[s][0]] = 'uarm' + s
    for b in [ARM[s][1]] + SUB[ARM[s][1]]: PART[b] = 'arm' + s          # forearm, hand, fingers
    for b in [LEG[s][1]] + SUB[LEG[s][1]]: PART[b] = 'leg' + s          # shin and foot; the thigh goes with the body
for b in ('Bone_017', 'Bone_016'): PART[b] = 'head'
part_of = np.array([PART.get(b, 'body') for b in dom])
IDX = {p: np.where(part_of == p)[0] for p in ('body', 'head', 'armL', 'armR', 'uarmL', 'uarmR', 'legL', 'legR')}
TOL = 0.02; FLOOR = 0.05                                   # contact is 0.5 mm above z = 0, so nothing is ever below it


def solve(f):
    """The floor pass. The body settles first; only then are the limbs and the head tested, or they would be
    corrected against a body that is about to move (which left the hands hanging 15 cm in the air)."""
    lift = 0.0; raise_ = {'armL': 0.0, 'armR': 0.0, 'legL': 0.0, 'legR': 0.0}; up = {'uarmL': 0.0, 'uarmR': 0.0}; headfix = 0.0
    for it in range(24):
        build(f, lift, raise_, up, headfix); apply_pose(); V = world_verts()
        lo = {p: float(V[IDX[p], 2].min()) - FLOOR for p in IDX}
        # every correction can also come back DOWN as far as zero (the keyed value), so a part that was pushed up
        # while something else was still moving ends on the floor, not above it
        n = max(0.0, lift - lo['body'])
        if abs(n - lift) > TOL: lift = n; continue
        ok = True
        for p in raise_:
            n = max(0.0, raise_[p] - lo[p])
            if abs(n - raise_[p]) > TOL: raise_[p] = n; ok = False
        for p in up:                                       # an elbow under the floor: tip the elbow up
            n = max(0.0, up[p] - lo[p] / 12.0)
            if abs(n - up[p]) > TOL / 12.0: up[p] = n; ok = False
        n = max(0.0, headfix - math.degrees(lo['head'] / 18.0))
        if abs(n - headfix) > 0.1: headfix = n; ok = False
        if ok: break
    guard = 0.0
    if V[:, 2].min() < 0.0:                                # whatever is left: the whole body comes up. Logged.
        guard = float(-V[:, 2].min()); lift += guard
        build(f, lift, raise_, up, headfix); apply_pose(); V = world_verts()
    return V, {'lift': round(lift, 2), 'guard': round(guard, 2), 'head_fix': round(headfix, 1),
               'raise': {k: round(v, 2) for k, v in raise_.items()}, 'elbow_up': {k: round(v, 2) for k, v in up.items()},
               'iters': it + 1, 'over_reach': {k: round(v, 2) for k, v in REACH.items() if v > 0.01}}


# Solve first, key afterwards: once the action has keys, every depsgraph update re-evaluates it and overwrites the
# pose being solved, and the floor pass would be measuring the wrong body.
VERTS = {}; DIAG = {}; TRACK = {}; POSES = {}; fk_err = 0.0
for f in range(F0, F1 + 1):
    V, d = solve(min(f, 52))                               # 52..60 are one pose: the pose the body holds
    VERTS[f] = V; DIAG[f] = d; POSES[f] = {n: BASIS[n].copy() for n in BONES}
    TRACK[f] = {'ankleL': head(LEG['L'][2]).copy(), 'ankleR': head(LEG['R'][2]).copy(), 'pelvis': head('Bone_000').copy()}
    # the matrices tracked here must be what Blender itself evaluates
    fk_err = max(fk_err, max((RW @ pb.matrix - W[pb.name]).to_translation().length for pb in rig.pose.bones))
log['fk_check_cm'] = round(fk_err, 5); assert fk_err < 1e-2, fk_err
act = bpy.data.actions.new(CLIP)
rig.animation_data_create(); rig.animation_data.action = act
prev = {}
for f in range(F0, F1 + 1):
    for pb in rig.pose.bones:
        loc, q, _ = POSES[f][pb.name].decompose()
        if pb.name in prev and prev[pb.name].dot(q) < 0: q.negate()      # keep the quaternions on one side
        prev[pb.name] = q.copy()
        pb.location = loc; pb.rotation_quaternion = q
        pb.keyframe_insert('location', frame=f); pb.keyframe_insert('rotation_quaternion', frame=f)
sc.frame_start, sc.frame_end = F0, F1

# ---------- numbers ----------
def bone_low(f):
    sc.frame_set(f); bpy.context.view_layer.update()
    pts = [(min((RW @ pb.head).z, (RW @ pb.tail).z), pb.name) for pb in rig.pose.bones]
    return min(pts)
bl = bone_low(F1); Vf = world_verts()
log['final'] = {'lowest_vertex_z': round(float(Vf[:, 2].min()), 3), 'lowest_bone_z': round(bl[0], 2), 'lowest_bone': bl[1],
                'size_cm': [round(float(v), 1) for v in (Vf.max(0) - Vf.min(0))],
                'part_min_z': {p: round(float(Vf[IDX[p], 2].min()), 2) for p in IDX},
                'pelvis': [round(v, 1) for v in TRACK[F1]['pelvis']], 'diag': DIAG[F1]}
log['min_vertex_z_any_frame'] = round(min(float(v[:, 2].min()) for v in VERTS.values()), 3)
log['max_guard_cm'] = max(d['guard'] for d in DIAG.values())
log['guard_by_frame'] = {f: (d['guard'], d['iters']) for f, d in DIAG.items() if d['guard'] > 0.05}
log['raise_by_frame'] = {f: [DIAG[f]['lift']] + list(DIAG[f]['raise'].values()) + list(DIAG[f]['elbow_up'].values()) + [DIAG[f]['head_fix']] for f in range(F0, F1 + 1)}
log['step_by_frame'] = {f: round(float(np.linalg.norm(VERTS[f + 1] - VERTS[f], axis=1).max()), 1) for f in range(F0, F1)}
log['over_reach'] = {f: d['over_reach'] for f, d in DIAG.items() if d['over_reach']}
log['lift_by_frame'] = {f: DIAG[f]['lift'] for f in range(F0, F1 + 1, 3)}
log['head_fix_by_frame'] = {f: DIAG[f]['head_fix'] for f in range(F0, F1 + 1) if DIAG[f]['head_fix']}
# a planted foot must not move: the left ankle until it rocks onto the heel, the right from its step to the slide
def drift(key, fa, fb): return round(max((TRACK[f][key] - TRACK[fa][key]).length for f in range(fa, fb + 1)), 3)
log['plant_drift_cm'] = {'left_1_22': drift('ankleL', 1, 22), 'right_11_33': drift('ankleR', 11, 33)}
log['step_cm'] = round(max((VERTS[f + 1] - VERTS[f]).__abs__().max() for f in range(F0, F1)), 1)   # fastest any vertex moves
log['hold_still_cm'] = round(float(np.abs(VERTS[F1] - VERTS[52]).max()), 4)

# ---------- check sheets: 12 frames each from the side, three-quarter and above; the final pose; the hands ----------
world = bpy.data.worlds.new('W'); sc.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.5, 0.5, 0.52, 1); world.node_tree.nodes['Background'].inputs[1].default_value = 1.2
sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN')); sun.data.energy = 3; sun.rotation_euler = (0.7, 0.2, -0.5); sc.collection.objects.link(sun)
bpy.ops.mesh.primitive_plane_add(size=900); ground = bpy.context.object
def flat(name, rgb):
    m = bpy.data.materials.new(name); m.use_nodes = True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*rgb, 1); return m
ground.data.materials.append(flat('G', (0.30, 0.30, 0.32)))
# floor tape: a 50 cm grid of thin dark strips, so sliding feet and a floating body show
strips = []
for i in range(-6, 7):
    for along in (0, 1):
        bpy.ops.mesh.primitive_plane_add(size=1); st = bpy.context.object
        st.scale = (2.5, 900, 1) if along else (900, 2.5, 1); st.location = (i * 50, 0, 0.3) if along else (0, i * 50, 0.3)
        strips.append(st)
sm = flat('S', (0.05, 0.05, 0.06))
for st in strips: st.data.materials.append(sm)
# a dark slab under the floor: the side view is dead level, so anything floating shows as a gap above this edge
bpy.ops.mesh.primitive_cube_add(size=1); slab = bpy.context.object; slab.scale = (900, 900, 10); slab.location = (0, 0, -5.02)
slab.data.materials.append(sm); strips.append(slab)
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = 'ORTHO'; cam.data.clip_end = 100000
sc.render.engine = 'BLENDER_EEVEE'
ALLV = np.concatenate([VERTS[f] for f in range(F0, F1 + 1, 4)] + [VERTS[F1]])
lo3, hi3 = ALLV.min(0), ALLV.max(0)
CTR = Vector(((lo3[0] + hi3[0]) / 2, (lo3[1] + hi3[1]) / 2, hi3[2] / 2))
SPAN = float(max(hi3[1] - lo3[1], hi3[2]))


def shot(fp, ctr, v, scale, res):
    sc.render.resolution_x, sc.render.resolution_y = res
    cam.data.ortho_scale = scale; v = Vector(v).normalized(); cam.location = Vector(ctr) + v * 1000
    cam.rotation_euler = (Vector(ctr) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = fp; bpy.ops.render.render(write_still=True)


def sheet(name, tiles, cols, res):
    w, h = res; rows = (len(tiles) + cols - 1) // cols
    out = np.zeros((h * rows, w * cols, 4), np.float32); out[..., 3] = 1
    for i, fp in enumerate(tiles):
        im = bpy.data.images.load(fp); x = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(x)
        r, c = divmod(i, cols); out[(rows - 1 - r) * h:(rows - r) * h, c * w:(c + 1) * w] = x.reshape(h, w, 4)
        bpy.data.images.remove(im); os.remove(fp)
    s = bpy.data.images.new(name, w * cols, h * rows); s.pixels.foreach_set(out.ravel())
    s.filepath_raw = os.path.join(CACHE, '%s_%s_%s.png' % (NAME, CLIP, name)); s.file_format = 'PNG'; s.save()
    return s.filepath_raw


SHEET_FRAMES = [1, 3, 5, 8, 11, 14, 17, 20, 23, 26, 28, 30, 32, 34, 36, 38, 41, 45, 52, 60]
log['sheets'] = []
if 'norender' not in a:
    for tag, v, scale, res in (('side', (1, 0, 0), SPAN * 1.12, (380, 300)), ('three', (0.75, -1, 0.6), SPAN * 1.25, (380, 300)),
                               ('top', (0.001, -0.02, 1), SPAN * 1.15, (300, 380))):
        tiles = []
        for f in SHEET_FRAMES:
            sc.frame_set(f); fp = os.path.join(CACHE, '_death_%s_%02d.png' % (tag, f)); shot(fp, CTR, v, scale, res); tiles.append(fp)
        log['sheets'].append(sheet(tag, tiles, 5, res))
    # the pose he holds, larger, from four sides
    sc.frame_set(F1)
    fc = Vector(((Vf[:, 0].min() + Vf[:, 0].max()) / 2, (Vf[:, 1].min() + Vf[:, 1].max()) / 2, 15))
    fs = float(max(Vf[:, 0].max() - Vf[:, 0].min(), Vf[:, 1].max() - Vf[:, 1].min())) * 1.1
    tiles = []
    for tag, v in (('top', (0.001, -0.02, 1)), ('three', (0.8, -0.6, 0.55)), ('left', (1, 0, 0)), ('right', (-1, 0, 0))):
        fp = os.path.join(CACHE, '_death_final_%s.png' % tag); shot(fp, fc, v, fs, (640, 640)); tiles.append(fp)
    log['sheets'].append(sheet('final', tiles, 2, (640, 640)))
    # the hands, close: first frame (fists), mid fall, and both hands on the floor
    tiles = []
    for f, s, v in ((1, 'L', (0.4, -1, 0.3)), (1, 'R', (-0.4, -1, 0.3)), (24, 'L', (1, -0.6, 0.3)), (24, 'R', (-1, -0.6, 0.3)),
                    (F1, 'L', (0.3, -0.5, 1)), (F1, 'L', (1, 0.2, 0.25)), (F1, 'R', (-0.3, -0.5, 1)), (F1, 'R', (-1, -0.2, 0.25))):
        sc.frame_set(f); bpy.context.view_layer.update()
        c = RW @ rig.pose.bones[HAND[s]].tail
        fp = os.path.join(CACHE, '_death_hand_%s_%02d_%d.png' % (s, f, len(tiles))); shot(fp, c, v, 42, (400, 400)); tiles.append(fp)
    log['sheets'].append(sheet('hands', tiles, 4, (400, 400)))
for o in [ground] + strips: bpy.data.objects.remove(o)

# ---------- export: mesh + rig + this one action, same settings as pose_clip.py / meshy_character.py ----------
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
    log['fbx'] = OUT

    # ---------- verify: read the new FBX and the original back and compare ----------
    def read_back(path, with_anim):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.scene.unit_settings.scale_length = 0.01
        bpy.ops.import_scene.fbx(filepath=path, automatic_bone_orientation=False, use_anim=with_anim, ignore_leaf_bones=False)
        r = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE'][0]
        m = [o for o in bpy.context.scene.objects if o.type == 'MESH'][0]
        return r, m, {b.name: (r.matrix_world @ b.head_local) for b in r.data.bones}

    r0, m0, rest0 = read_back(SRC, False)
    n0 = (len(m0.data.vertices), len(m0.data.polygons), sum(len(p.vertices) - 2 for p in m0.data.polygons))
    r1, m1, rest1 = read_back(OUT, True)
    n1 = (len(m1.data.vertices), len(m1.data.polygons), sum(len(p.vertices) - 2 for p in m1.data.polygons))
    drift_ = max((rest0[n] - rest1[n]).length for n in rest0) if set(rest0) == set(rest1) else -1.0
    ver = {'bones_src': len(rest0), 'bones_out': len(rest1), 'same_bone_names': set(rest0) == set(rest1),
           'max_rest_drift_cm': round(drift_, 4), 'verts_polys_tris_src': n0, 'verts_polys_tris_out': n1,
           'actions': [(a_.name, [int(a_.frame_range[0]), int(a_.frame_range[1])]) for a_ in bpy.data.actions],
           'fps': bpy.context.scene.render.fps}

    def rb(f):
        bpy.context.scene.frame_set(f); bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get(); e = m1.evaluated_get(dg); me = e.to_mesh()
        Vb = np.array([e.matrix_world @ v.co for v in me.vertices]); e.to_mesh_clear()
        bz = min(min((r1.matrix_world @ pb.head).z, (r1.matrix_world @ pb.tail).z) for pb in r1.pose.bones)
        return Vb, bz
    Vb, bz = rb(F1)
    ver['readback_final_lowest_vertex_z'] = round(float(Vb[:, 2].min()), 3); ver['readback_final_lowest_bone_z'] = round(bz, 2)
    ver['readback_final_size_cm'] = [round(float(v), 1) for v in (Vb.max(0) - Vb.min(0))]
    ver['readback_min_vertex_z_any_frame'] = round(min(float(rb(f)[0][:, 2].min()) for f in range(F0, F1 + 1, 3)), 3)
    Vb1, _ = rb(F0); ver['readback_first_frame_height_cm'] = round(float(Vb1[:, 2].max()), 1)
    log['verify'] = ver
print('DEATHCLIP ' + json.dumps(log))
