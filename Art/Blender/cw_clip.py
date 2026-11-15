"""Author a clip for the player (CafeWalker) on his own rig: the shared half of every clip script.

A clip script is short. It imports this module, writes one function that poses frame f, and calls author():

    import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import cw_clip as C

    def build(f, u):                 # f = frame number, u = 0..1 through the clip
        C.body(dz=-2, pitch=8)       # pelvis: move / lean
        C.spine(x=4); C.neck(x=-4)
        C.foot('L', x=10, fwd=20, up=0, pitch=0)
        C.foot('R', x=-10, fwd=-30, up=12, pitch=35)
        C.hand('L', out=6, fwd=-18, up=-34, pron=40, curl=0.6)
        C.hand('R', out=6, fwd=22, up=-26, pron=40, curl=0.6)

    C.author('Run', frames=18, build=build, loop=True)

Run headless with Blender 5.3.0:
    blender -b --factory-startup --python Art/Blender/clip_<name>.py [-- norender noexport src=<other body fbx>]
It writes Art/Blender/export/Characters/CafeWalkerV2/SK_CafeWalkerV2_<Clip>.fbx (mesh + rig + one action) and check
sheets in Art/Blender/cache/CafeWalkerV2_<Clip>_sides.png / _hands.png, and prints one line: CWCLIP {json}.
LOOK at the sheets. The numbers are not the test.

DIRECTIONS (all centimetres and degrees, all from HIS point of view):
    x     toward his LEFT is positive ('L' side is +x, 'R' side is -x)
    fwd   the way he faces is positive
    up    up is positive
The model itself faces -Y in Blender; this module hides that. Feet are placed from the spot under the hips where
they rest; hands are placed from that side's shoulder joint, wherever the body pose has put it.

WHAT author() DOES FOR YOU
  * solves every frame, keys every bone, checks its own bone maths against Blender's;
  * re-expresses each frame the way the game's other clips are stored - root bone on the floor at the origin, hip
    bone carrying the pelvis - so the clip blends with them instead of sinking through the floor on the way;
  * a looping clip gets one extra frame equal to the first, so it loops with no seam;
  * reports: lowest point of the body per frame (0 = soles on the floor), torn skin (edges stretched past 2.5x),
    limbs asked to reach further than they are long, the ankle positions through the clip (so planted feet can be
    checked for sliding), and how fast the fastest vertex moves;
  * renders front / his left / back / his right across the clip, and both hands close up;
  * exports, reads the file back and checks the skeleton did not move.

The rig helpers below (rot, aim, ik2, orient, fingers) are death_clip.py's, by way of idle_clip.py.
"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector, Matrix, Quaternion

a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
NAME = 'CafeWalkerV2'
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
CACHE = os.path.join(REPO, 'Art', 'Blender', 'cache'); os.makedirs(CACHE, exist_ok=True)
DIR = os.path.join(REPO, 'Art', 'Blender', 'export', 'Characters', NAME)
SRC = os.path.join(DIR, 'SK_%s_oldrig.fbx' % NAME)
for _kv in a:                                             # src=<fbx>: try the clip on another build of the same body
    if _kv.startswith('src='): SRC = _kv[4:]
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
FPS = 30
log = {'name': NAME, 'fps': FPS, 'blender': bpy.app.version_string}

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


# ====================================================================================================
# The posing API. Call these inside build(f, u). Order matters: body() first, then spine/neck, then feet,
# then hands (a hand is placed from the shoulder, which the body and spine have just moved).
# ====================================================================================================
P0 = RH['Bone_000'].copy()                                  # the pelvis, at rest
ANK = {s: RH[LEG[s][2]].copy() for s in 'LR'}               # the ankles, at rest
ANK_Y = (ANK['L'].y + ANK['R'].y) / 2
ARMLEN = {s: (RH[ARM[s][1]] - RH[ARM[s][0]]).length + (RH[ARM[s][2]] - RH[ARM[s][1]]).length for s in 'LR'}
LEGLEN = {s: (RH[LEG[s][1]] - RH[LEG[s][0]]).length + (RH[LEG[s][2]] - RH[LEG[s][1]]).length for s in 'LR'}
HIP_Z = {s: RH[LEG[s][0]].z for s in 'LR'}                  # hip joint height at rest
ROOT_FLOOR = Matrix.Translation(-P0) @ REST['Bone_000']     # the root where the game's other clips keep it
DROP = {'L': 0.0, 'R': 0.0}                                 # how far each ankle comes down so a flat sole touches the floor
CLAV = {s: PARENT[ARM[s][0]] for s in 'LR'}
SPINE = ('Bone_005', 'Bone_004', 'Bone_003')
NECK = (('Bone_018', 0.4), ('Bone_017', 0.6))
_state = {}


def body(dx=0.0, fwd=0.0, dz=0.0, pitch=0.0, lean=0.0, twist=0.0):
    """Start a frame and place the pelvis. dx: toward his left. fwd: forward. dz: up (negative sinks him, which bends
    the knees). pitch: positive leans him FORWARD. lean: positive tips him toward his LEFT. twist: positive turns the
    hips toward his LEFT (anticlockwise seen from above)."""
    reset()
    pos = P0 + Vector((dx, -fwd, dz))
    R = Matrix.Rotation(math.radians(twist), 4, Z) @ Matrix.Rotation(math.radians(pitch), 4, X) @ Matrix.Rotation(math.radians(-lean), 4, Y)
    set_world('Bone_000', Matrix.Translation(pos) @ R @ Matrix.Translation(-P0) @ REST['Bone_000'])
    _state['done'] = False


def spine(x=0.0, y=0.0, z=0.0):
    """Bend the back, shared over three bones. x: positive curls him FORWARD. y: positive bends toward his LEFT.
    z: positive twists the chest toward his LEFT."""
    for b in SPINE:
        rot(b, X, x / 3.0); rot(b, Y, -y / 3.0); rot(b, Z, z / 3.0)


def neck(x=0.0, y=0.0, z=0.0):
    """Head and neck. x: positive nods DOWN. y: positive tilts toward his LEFT. z: positive looks to his LEFT."""
    for b, k in NECK:
        rot(b, X, x * k); rot(b, Y, -y * k); rot(b, Z, z * k)


def clav(s, up=14.0, back=3.0):
    """Collarbone of side s ('L' or 'R'). hand() calls this with these defaults; call it yourself first to shrug or
    drop a shoulder. Without lift, arms brought down from the A-pose drag the shoulder into a slope."""
    rot(CLAV[s], Y, -SGN[s] * up); rot(CLAV[s], Z, -SGN[s] * back)
    _state['clav' + s] = True


def foot(s, x=None, fwd=0.0, up=0.0, pitch=0.0, yaw=8.0, knee_out=0.22):
    """Place the ANKLE of side s. x: cm toward his left of the centre line (default 10.5 on his own side). fwd: cm in
    front of where it rests under the hip. up: cm above standing height. pitch: positive points the TOES DOWN (heel
    up), negative lifts the toes. yaw: toe-out. A foot flat on the floor is up=0, pitch=0."""
    th, sh, ft = LEG[s]
    if x is None: x = SGN[s] * 10.5
    t = Vector((x, ANK_Y - fwd, ANK[s].z - DROP[s] + up))
    ik2('leg' + s, th, sh, ft, t, Vector((SGN[s] * knee_out, -1.0, 0.0)), -Y)
    yw = math.radians(yaw) * SGN[s]; p = math.radians(pitch)
    f = Vector((math.sin(yw) * math.cos(p), -math.cos(yw) * math.cos(p), -math.sin(p)))
    u = Vector((math.sin(yw) * -math.sin(p) * -1.0, -math.cos(yw) * math.sin(p), math.cos(p)))
    orient(ft, f, u - f * u.dot(f), FOOT_F0[s], Z)


def hand(s, out=7.0, fwd=3.0, up=None, pron=62.0, curl=0.34, elbow=(0.35, -1.0, -0.1)):
    """Place the WRIST of side s from that side's shoulder joint. out: cm away from the body sideways. fwd: cm in
    front of the shoulder. up: cm above the shoulder (negative = below; default hangs the arm almost straight down).
    pron: forearm roll, 62 turns the palm to the thigh for a hanging arm, 0 leaves it as modelled (palm forward).
    curl: 0 open hand .. 1 fist. elbow: which way the elbow points, as (outward, forward, up); the default is back
    and a little out. Keep it well off the line from shoulder to wrist or the elbow flips between frames."""
    up_, fo, wr = ARM[s]
    if not _state.get('clav' + s): clav(s)
    sh0 = head(up_)
    if up is None: up = -ARMLEN[s] * 0.965
    t = Vector((sh0.x + SGN[s] * out, sh0.y - fwd, sh0.z + up))
    pole = Vector((SGN[s] * elbow[0], -elbow[1], elbow[2]))
    ik2('arm' + s, up_, fo, wr, t, pole, Y)
    rot(fo, (head(wr) - head(fo)).normalized(), SGN[s] * pron)
    fingers(s, curl)


def wrist(s, bend=0.0, side=0.0):
    """After hand(): flex the wrist. bend: positive folds the palm toward the forearm's inside. side: positive tips
    the hand toward the thumb. Small numbers; a straight wrist is 0, 0."""
    up_, fo, wr = ARM[s]; hd = HAND[s]
    ax = (head(wr) - head(fo)).normalized()
    palm = carried(hd, -Y)
    hinge = ax.cross(palm)
    if hinge.length > 1e-6:
        rot(wr, hinge.normalized(), bend)
        rot(wr, palm.normalized(), SGN[s] * side)


def _finish():
    hip = W['Bone_001'].copy()
    set_world('Bone_000', ROOT_FLOOR)
    set_world('Bone_001', hip)
    _state.clear()


def apply_pose():
    for pb in rig.pose.bones: pb.matrix_basis = BASIS[pb.name]


def smooth(u, a, b):
    """0 before a, 1 after b, an eased ramp between. For timing: smooth(u, 0.2, 0.3) is a quick move at 20-30%."""
    if b <= a: return 1.0 if u >= b else 0.0
    t = min(1.0, max(0.0, (u - a) / (b - a)))
    return t * t * (3 - 2 * t)


def keys(u, pts):
    """Eased interpolation through (u, value) points; holds the first and last. value may be a number or a tuple."""
    if u <= pts[0][0]: return pts[0][1]
    if u >= pts[-1][0]: return pts[-1][1]
    for (u0, v0), (u1, v1) in zip(pts, pts[1:]):
        if u0 <= u <= u1:
            t = smooth(u, u0, u1)
            if isinstance(v0, (tuple, list)): return tuple(p + (q - p) * t for p, q in zip(v0, v1))
            return v0 + (v1 - v0) * t


# soles: the two shoes do not rest at the same height in the model, so stand him once and measure
_vgn = {g.index: g.name for g in mesh.vertex_groups}
_domb = [_vgn[max(v.groups, key=lambda g: g.weight).group] if v.groups else '' for v in mesh.data.vertices]
SHOE = {s: np.array([i for i, d in enumerate(_domb) if d == LEG[s][2] or d in SUB[LEG[s][2]]]) for s in 'LR'}
body(); foot('L'); foot('R'); apply_pose(); _V = world_verts()
for _s in 'LR': DROP[_s] = float(_V[SHOE[_s], 2].min()) - 0.05
log['sole_drop_cm'] = {s: round(DROP[s], 2) for s in 'LR'}
_E = np.array([e.vertices[:] for e in mesh.data.edges])
_R0 = np.linalg.norm(V0[_E[:, 0]] - V0[_E[:, 1]], axis=1)


def _torn(V):
    r1 = np.linalg.norm(V[_E[:, 0]] - V[_E[:, 1]], axis=1)
    bad = np.where((r1 > 2.5 * np.maximum(_R0, 0.05)) & (r1 - _R0 > 1.5))[0]
    pairs = {}
    for e in bad:
        k = tuple(sorted((_domb[_E[e, 0]], _domb[_E[e, 1]]))); pairs[k] = pairs.get(k, 0) + 1
    return int(len(bad)), (float(r1[bad].max()) if len(bad) else 0.0), sorted(((n, list(k)) for k, n in pairs.items()), reverse=True)[:5]


def author(clip, frames, build, loop=True, sheet_frames=8):
    """Solve, key, measure, render, export. frames = how many frames the motion takes (a loop gets one more, equal to
    the first). build(f, u) poses frame f (1-based) where u runs 0..1; for a loop u=1 is the same pose as u=0."""
    F0 = 1; F1 = frames + 1 if loop else frames
    N = frames if loop else max(1, frames - 1)
    OUT = os.path.join(DIR, 'SK_%s_%s.fbx' % (NAME, clip))
    log.update({'clip': clip, 'frames': [F0, F1], 'loop': loop, 'seconds': round(N / FPS, 3)})
    VERTS, POSES, TRACK, reach, fk_err = {}, {}, {}, {}, 0.0
    for f in range(F0, F1 + 1):
        g = F0 if (loop and f == F1) else f
        REACH.clear()
        build(g, (g - F0) / N); _finish(); apply_pose(); VERTS[f] = world_verts()
        POSES[f] = {n: BASIS[n].copy() for n in BONES}
        TRACK[f] = {'L': head(LEG['L'][2]).copy(), 'R': head(LEG['R'][2]).copy(), 'hip': head('Bone_001').copy(),
                    'wL': head(ARM['L'][2]).copy(), 'wR': head(ARM['R'][2]).copy()}
        for k, v in REACH.items():
            if v > 0.05: reach[k] = max(reach.get(k, 0.0), round(v, 1))
        fk_err = max(fk_err, max((RW @ pb.matrix - W[pb.name]).to_translation().length for pb in rig.pose.bones))
    log['fk_check_cm'] = round(fk_err, 5); assert fk_err < 1e-2, fk_err
    act = bpy.data.actions.new(clip)
    rig.animation_data_create(); rig.animation_data.action = act
    prev = {}
    for f in range(F0, F1 + 1):
        for pb in rig.pose.bones:
            loc, q, _ = POSES[f][pb.name].decompose()
            if pb.name in prev and prev[pb.name].dot(q) < 0: q.negate()
            prev[pb.name] = q.copy()
            pb.location = loc; pb.rotation_quaternion = q
            pb.keyframe_insert('location', frame=f); pb.keyframe_insert('rotation_quaternion', frame=f)
    sc.frame_start, sc.frame_end = F0, F1

    lows = {f: round(float(VERTS[f][:, 2].min()), 1) for f in VERTS}
    log['lowest_point_cm'] = {'min': min(lows.values()), 'max': max(lows.values())}
    log['lowest_by_frame'] = lows
    log['loop_seam_cm'] = round(float(np.abs(VERTS[F1] - VERTS[F0]).max()), 5) if loop else None
    log['over_reach_cm'] = reach                              # a limb asked to reach further than it is long
    log['fastest_vertex_cm_per_frame'] = round(max(float(np.linalg.norm(VERTS[f + 1] - VERTS[f], axis=1).max()) for f in range(F0, F1)), 1)
    # ankles as (toward his left, forward, up) per frame: a planted foot holds x and up and moves back at one speed
    log['ankles'] = {f: {s: [round(TRACK[f][s].x, 1), round(ANK_Y - TRACK[f][s].y, 1), round(TRACK[f][s].z - (ANK[s].z - DROP[s]), 1)] for s in 'LR'} for f in range(F0, F1 + 1)}
    log['hip_height_cm'] = {'min': round(min(TRACK[f]['hip'].z for f in TRACK), 1), 'max': round(max(TRACK[f]['hip'].z for f in TRACK), 1)}
    step = max(1, (F1 - F0) // sheet_frames)
    picks = list(range(F0, F1 + (0 if loop else 1), step))[:sheet_frames + 2]
    worst = (0, 0.0, [])
    log['torn'] = {}
    for f in picks:
        n, lg, pr = _torn(VERTS[f]); log['torn'][f] = [n, round(lg, 1)]
        if n > worst[0]: worst = (n, lg, pr)
    log['torn_worst'] = {'edges': worst[0], 'longest_cm': round(worst[1], 1), 'between': worst[2]}

    log['sheets'] = []
    if 'norender' not in a:
        world = bpy.data.worlds.new('W'); sc.world = world; world.use_nodes = True
        world.node_tree.nodes['Background'].inputs[0].default_value = (0.5, 0.5, 0.52, 1); world.node_tree.nodes['Background'].inputs[1].default_value = 1.2
        sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN')); sun.data.energy = 3; sun.rotation_euler = (0.7, 0.2, -0.5); sc.collection.objects.link(sun)
        bpy.ops.mesh.primitive_plane_add(size=1200); ground = bpy.context.object
        gm = bpy.data.materials.new('G'); gm.use_nodes = True
        gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.30, 0.30, 0.32, 1); ground.data.materials.append(gm)
        cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); sc.collection.objects.link(cam); sc.camera = cam
        cam.data.type = 'ORTHO'; cam.data.clip_end = 100000
        sc.render.engine = 'BLENDER_EEVEE'

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
            s.filepath_raw = os.path.join(CACHE, '%s_%s_%s.png' % (NAME, clip, name)); s.file_format = 'PNG'; s.save()
            return s.filepath_raw

        picks8 = picks[:sheet_frames]
        tiles = []
        for tag, v in (('front', (0.001, -1, 0.04)), ('left', (1, 0.001, 0.04)), ('back', (0.001, 1, 0.04)), ('right', (-1, 0.001, 0.04))):
            for f in picks8:
                sc.frame_set(f); V = VERTS[f]
                ctr = Vector((float(V[:, 0].max() + V[:, 0].min()) / 2, float(V[:, 1].max() + V[:, 1].min()) / 2, 88))
                fp = os.path.join(CACHE, '_cw_%s_%s_%03d.png' % (clip, tag, f)); shot(fp, ctr, v, 215, (230, 300)); tiles.append(fp)
        log['sheets'].append(sheet('sides', tiles, len(picks8), (230, 300)))
        tiles = []
        for f in (picks8[0], picks8[len(picks8) // 3], picks8[(2 * len(picks8)) // 3]):
            sc.frame_set(f); bpy.context.view_layer.update()
            for s, v in (('L', (0.3, -1, 0.1)), ('L', (1, 0.05, 0.1)), ('R', (-0.3, -1, 0.1)), ('R', (-1, 0.05, 0.1))):
                cc = RW @ rig.pose.bones[HAND[s]].tail
                fp = os.path.join(CACHE, '_cw_%s_hand_%s_%d.png' % (clip, s, len(tiles))); shot(fp, cc, v, 44, (300, 300)); tiles.append(fp)
        log['sheets'].append(sheet('hands', tiles, 4, (300, 300)))
        for o in (ground, sun, cam): bpy.data.objects.remove(o)

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
        rest0 = {b.name: (RW @ b.head_local).copy() for b in rig.data.bones}
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.scene.unit_settings.scale_length = 0.01
        bpy.ops.import_scene.fbx(filepath=OUT, automatic_bone_orientation=False, use_anim=True, ignore_leaf_bones=False)
        r1 = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE'][0]
        rest1 = {b.name: (r1.matrix_world @ b.head_local) for b in r1.data.bones}
        same = set(rest0) == set(rest1)
        bpy.context.scene.frame_set(F0); bpy.context.view_layer.update()
        log['verify'] = {'bones': len(rest1), 'same_bone_names': same,
                         'max_rest_drift_cm': round(max((rest0[n] - rest1[n]).length for n in rest0), 4) if same else -1,
                         'actions': [(x.name, [int(x.frame_range[0]), int(x.frame_range[1])]) for x in bpy.data.actions],
                         'root_world_cm': [round(v, 2) for v in (r1.matrix_world @ r1.pose.bones['Bone_000'].head)],
                         'hip_world_cm': [round(v, 2) for v in (r1.matrix_world @ r1.pose.bones['Bone_001'].head)]}
    print('CWCLIP ' + json.dumps(log))
    return log
