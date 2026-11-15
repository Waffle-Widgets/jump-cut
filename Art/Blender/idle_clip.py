# The player's standing idle, authored on his own rig instead of retargeted from Epic's mannequin (issue #103).
# Headless, Blender 5.3.0:
#   blender -b --factory-startup --python Art/Blender/idle_clip.py [-- norender noexport key=value ...]
# Reads the body that is in the game (CafeWalkerV2/SK_CafeWalkerV2_oldrig.fbx: the V2 mesh on the 69-bone rig every
# player clip is keyed against) and writes SK_CafeWalkerV2_Idle.fbx beside it: mesh + rig + one action, Idle,
# 121 frames at 30 fps. Frame 121 is frame 1 again, so the clip loops with no seam.
#
# WHY. The retargeted MM_Idle_CWM stands with the arms held out from the body, the hands open and clawed and the feet
# wide: it is the mannequin's idle laid over a Meshy A-pose. The Team Owner: "The models should look and move like
# normal people." So this is a person standing: feet under the hips with the toes a little out, weight a touch on his
# right leg, knees soft, arms hanging at his sides with the palms toward his thighs and the fingers loosely curled,
# breathing once in four seconds with a slow sway.
#
# The rig helpers (rot, aim, ik2, orient, fingers) and the check-sheet renderer are death_clip.py's, copied so this
# file runs by itself. Two things differ from that clip, both because this one is BLENDED with the retargeted walks
# and jogs in BS_Idle_Walk_Run_CWM instead of played alone as a montage:
#   1. The root. Those clips keep Bone_000 on the floor at the origin with its rest rotation, and let Bone_001 (the
#      hip) carry the pelvis. death_clip.py keys the pelvis on Bone_000. Blending the two conventions would slide the
#      body down by (blend weight x 90 cm). So every frame is solved on the pelvis and then RE-EXPRESSED: root to the
#      floor, hip put back where it was.
#   2. The feet never move. Both ankles are the same world point on every frame.
# LOOK at Art/Blender/cache/CafeWalkerV2_Idle_*.png. The numbers are not the test.
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector, Matrix, Quaternion

a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
NAME, CLIP = 'CafeWalkerV2', 'Idle'
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
CACHE = os.path.join(REPO, 'Art', 'Blender', 'cache'); os.makedirs(CACHE, exist_ok=True)
DIR = os.path.join(REPO, 'Art', 'Blender', 'export', 'Characters', NAME)
SRC = os.path.join(DIR, 'SK_%s_oldrig.fbx' % NAME)
OUT = os.path.join(DIR, 'SK_%s_%s.fbx' % (NAME, CLIP))
for _kv in a:                                             # src=<fbx>: try the clip on another build of the same body
    if _kv.startswith('src='): SRC = _kv[4:]
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
F0, F1, FPS = 1, 121, 30
N = F1 - F0                                                # 120 frames to a loop; frame F1 repeats frame F0
log = {'name': NAME, 'clip': CLIP, 'frames': [F0, F1], 'fps': FPS, 'blender': bpy.app.version_string}

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


# ---------- the performance ----------
P0 = RH['Bone_000'].copy()                                  # the pelvis, at rest
ANK = {s: RH[LEG[s][2]].copy() for s in 'LR'}               # the ankles, at rest: that height keeps the soles on the floor
ARMLEN = {s: (RH[ARM[s][1]] - RH[ARM[s][0]]).length + (RH[ARM[s][2]] - RH[ARM[s][1]]).length for s in 'LR'}
ROOT_FLOOR = Matrix.Translation(-P0) @ REST['Bone_000']     # the root where the retargeted clips keep it
DROP = {'L': 0.0, 'R': 0.0}                                 # how far each ankle comes down so the sole touches the floor
T = {                                                       # every number a person might want to change
    'foot_x': 10.5, 'foot_yL': -2.5, 'foot_yR': 2.5, 'toe_out': 11.0,     # cm from the centre line; cm fore/aft; degrees
    'pel_shift': -1.6, 'pel_drop': 1.2, 'hip_tilt': 1.6,                  # weight onto his right leg (his right is -X)
    'spine_back': -1.5, 'head_up': -2.0,                                  # degrees about +X (positive bends him forward)
    'hand_out': 7.0, 'hand_fwd': -3.0, 'arm_bend': 0.965,                 # wrist beside the thigh; 1.0 = dead straight
    'clav_up': 14.0, 'clav_back': 3.0,                                    # degrees: collarbones lifted / drawn back.
    # Without them the arms coming down from the A-pose drag the shoulders into a slope ("droopy", the Team Owner).
    'pron': 62.0, 'curl': 0.34,                                           # palms toward the thighs; relaxed fingers
    'breath_deg': 0.9, 'breath_cm': 0.35, 'sway_cm': 0.7, 'sway_deg': 0.5,
}
for kv in a:
    if '=' in kv and kv.split('=')[0] in T: T[kv.split('=')[0]] = float(kv.split('=')[1])
log['tuning'] = dict(T)


def cyc(f, phase=0.0):                                      # one full sine over the loop
    return math.sin(2 * math.pi * ((f - F0) / N + phase))


def build(f):
    reset()
    br = cyc(f)                                              # breath: in and out once per loop
    sw = cyc(f, 0.18)                                        # sway: the same period, a little behind the breath
    sp = (T['spine_back'] - T['breath_deg'] * br) / 3.0
    for b in ('Bone_005', 'Bone_004', 'Bone_003'):
        rot(b, X, sp); rot(b, Y, -T['sway_deg'] * sw / 3.0)
    for b, k in (('Bone_018', 0.4), ('Bone_017', 0.6)):
        rot(b, X, (T['head_up'] + T['breath_deg'] * 0.7 * br) * k); rot(b, Y, T['sway_deg'] * 0.6 * sw * k)
    pos = P0 + Vector((T['pel_shift'] + T['sway_cm'] * sw, 0.0, -T['pel_drop'] + T['breath_cm'] * br))
    R = Matrix.Rotation(math.radians(T['hip_tilt'] + T['sway_deg'] * sw), 4, Y)
    set_world('Bone_000', Matrix.Translation(pos) @ R @ Matrix.Translation(-P0) @ REST['Bone_000'])
    for s in 'LR':
        th, sh, ft = LEG[s]
        t = Vector((SGN[s] * T['foot_x'], ANK[s].y + T['foot_y' + s], ANK[s].z - DROP[s]))   # fore/aft from where the ankle rests
        out = math.radians(T['toe_out']) * SGN[s]
        toe = Vector((math.sin(out), -math.cos(out), 0.0))
        ik2('leg' + s, th, sh, ft, t, Vector((SGN[s] * 0.22, -1.0, 0.0)), -Y)
        orient(ft, toe, Z, FOOT_F0[s], Z)
    for s in 'LR':
        up, fo, wr = ARM[s]
        # Bringing the arms down from the A-pose drags the shoulder down with them unless the collarbone answers.
        rot(PARENT[up], Y, -SGN[s] * T['clav_up']); rot(PARENT[up], Z, -SGN[s] * T['clav_back'])
        sh0 = head(up)
        t = Vector((sh0.x + SGN[s] * T['hand_out'], sh0.y + T['hand_fwd'], sh0.z - ARMLEN[s] * T['arm_bend'] + 0.25 * br))
        ik2('arm' + s, up, fo, wr, t, Vector((SGN[s] * 0.35, 1.0, 0.1)), Y)
        rot(fo, (head(wr) - head(fo)).normalized(), SGN[s] * T['pron'])
        fingers(s, T['curl'])
    # re-express on the retargeted clips' convention: root on the floor, hip where it already is
    hip = W['Bone_001'].copy()
    set_world('Bone_000', ROOT_FLOOR)
    set_world('Bone_001', hip)


def apply_pose():
    for pb in rig.pose.bones: pb.matrix_basis = BASIS[pb.name]


# Put each sole ON the floor. The two shoes do not rest at the same height in the model (one is a centimetre up),
# so pose once, measure the lowest point of each shoe, and lower that ankle by exactly that much.
_vgn = {g.index: g.name for g in mesh.vertex_groups}
_domb = [_vgn[max(v.groups, key=lambda g: g.weight).group] if v.groups else '' for v in mesh.data.vertices]
SHOE = {s: np.array([i for i, d in enumerate(_domb) if d == LEG[s][2] or d in SUB[LEG[s][2]]]) for s in 'LR'}
build(F0); apply_pose(); _V = world_verts()
for s in 'LR': DROP[s] = float(_V[SHOE[s], 2].min()) - 0.05
log['sole_drop_cm'] = {s: round(DROP[s], 2) for s in 'LR'}


VERTS = {}; POSES = {}; TRACK = {}; fk_err = 0.0
for f in range(F0, F1 + 1):
    build(F0 if f == F1 else f); apply_pose(); VERTS[f] = world_verts()
    POSES[f] = {n: BASIS[n].copy() for n in BONES}
    TRACK[f] = {'ankleL': head(LEG['L'][2]).copy(), 'ankleR': head(LEG['R'][2]).copy(), 'pelvis': head('Bone_001').copy(),
                'root': head('Bone_000').copy(), 'wristL': head(ARM['L'][2]).copy(), 'wristR': head(ARM['R'][2]).copy()}
    fk_err = max(fk_err, max((RW @ pb.matrix - W[pb.name]).to_translation().length for pb in rig.pose.bones))
log['fk_check_cm'] = round(fk_err, 5); assert fk_err < 1e-2, fk_err
act = bpy.data.actions.new(CLIP)
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

# ---------- numbers ----------
def drift(key): return round(max((TRACK[f][key] - TRACK[F0][key]).length for f in range(F0, F1 + 1)), 4)
log['min_vertex_z_any_frame'] = round(min(float(v[:, 2].min()) for v in VERTS.values()), 3)
log['loop_seam_cm'] = round(float(np.abs(VERTS[F1] - VERTS[F0]).max()), 5)
log['ankle_drift_cm'] = {'L': drift('ankleL'), 'R': drift('ankleR')}
log['root_world'] = [round(v, 3) for v in TRACK[F0]['root']]; log['root_drift_cm'] = drift('root')
log['pelvis_travel_cm'] = drift('pelvis'); log['wrist_travel_cm'] = {'L': drift('wristL'), 'R': drift('wristR')}
log['fastest_vertex_cm_per_frame'] = round(max(float(np.linalg.norm(VERTS[f + 1] - VERTS[f], axis=1).max()) for f in range(F0, F1)), 3)
log['over_reach'] = {k: round(v, 2) for k, v in REACH.items() if v > 0.01}
log['stance'] = {'ankle_gap_cm': round((TRACK[F0]['ankleL'] - TRACK[F0]['ankleR']).length, 1),
                 'wrist_gap_cm': round(abs(TRACK[F0]['wristL'].x - TRACK[F0]['wristR'].x), 1),
                 'wrist_z_cm': [round(TRACK[F0]['wristL'].z, 1), round(TRACK[F0]['wristR'].z, 1)],
                 'rest_ankle_gap_cm': round((ANK['L'] - ANK['R']).length, 1)}
# ---------- torn skin: edges that got much longer than they are at rest ----------
# A pose can be right and still tear the mesh where a vertex follows the wrong bone. Count them, and say which bones.
_E = np.array([e.vertices[:] for e in mesh.data.edges])
def torn(V, ratio=2.5, min_cm=1.5):
    r0 = np.linalg.norm(V0[_E[:, 0]] - V0[_E[:, 1]], axis=1); r1 = np.linalg.norm(V[_E[:, 0]] - V[_E[:, 1]], axis=1)
    bad = np.where((r1 > ratio * np.maximum(r0, 0.05)) & (r1 - r0 > min_cm))[0]
    return bad, r1
_bad, _r1 = torn(VERTS[F0])
_vg = {g.index: g.name for g in mesh.vertex_groups}
def _dom(i):
    gs = mesh.data.vertices[int(i)].groups
    return _vg[max(gs, key=lambda g: g.weight).group] if gs else 'none'
_pairs = {}
for e in _bad:
    k = tuple(sorted((_dom(_E[e, 0]), _dom(_E[e, 1])))); _pairs[k] = _pairs.get(k, 0) + 1
log['torn_edges'] = int(len(_bad)); log['torn_longest_cm'] = round(float(_r1[_bad].max()), 1) if len(_bad) else 0.0
log['torn_by_bone_pair'] = sorted(((n, list(k)) for k, n in _pairs.items()), reverse=True)[:12]
log['limb_bones'] = {'armL': list(ARM['L']) + [HAND['L']], 'armR': list(ARM['R']) + [HAND['R']], 'legL': list(LEG['L']), 'legR': list(LEG['R'])}
F1_SAVE = F1

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


log['sheets'] = []
if 'norender' not in a:
    Vf = VERTS[F0]
    c = Vector((0.0, 0.0, float(Vf[:, 2].max()) / 2)); span = float(Vf[:, 2].max()) * 1.12
    tiles = []
    for f in (1, 31, 61, 91):                               # breath: neutral, full, neutral, empty
        for tag, v in (('front', (0.001, -1, 0.05)), ('three', (0.75, -1, 0.25)), ('side', (1, 0.001, 0.03)), ('back', (0.001, 1, 0.05))):
            sc.frame_set(f); fp = os.path.join(CACHE, '_idle_%s_%03d.png' % (tag, f)); shot(fp, c, v, span, (360, 480)); tiles.append(fp)
    log['sheets'].append(sheet('body', tiles, 4, (360, 480)))
    tiles = []
    sc.frame_set(F0); bpy.context.view_layer.update()
    for s, v in (('L', (0.3, -1, 0.1)), ('L', (1, 0.05, 0.1)), ('R', (-0.3, -1, 0.1)), ('R', (-1, 0.05, 0.1))):
        cc = RW @ rig.pose.bones[HAND[s]].tail
        fp = os.path.join(CACHE, '_idle_hand_%s_%d.png' % (s, len(tiles))); shot(fp, cc, v, 44, (400, 400)); tiles.append(fp)
    log['sheets'].append(sheet('hands', tiles, 4, (400, 400)))
    tiles = []
    for tag, v, ctr, sp_ in (('waist_front', (0.001, -1, 0.0), (0, 0, 88), 70), ('waist_three', (0.8, -1, 0.1), (0, 0, 88), 70),
                             ('feet_front', (0.001, -1, 0.25), (0, 0, 14), 70), ('feet_top', (0.001, -0.02, 1), (0, -4, 0), 70)):
        fp = os.path.join(CACHE, '_idle_%s.png' % tag); shot(fp, Vector(ctr), v, sp_, (400, 400)); tiles.append(fp)
    log['sheets'].append(sheet('detail', tiles, 4, (400, 400)))
    # shoulders and feet, close, in the idle pose AND in the rest pose the body was modelled in: a part that looks
    # wrong in both is the model, a part that only looks wrong in the idle is this clip (or the weights)
    tiles = []
    for which in ('idle', 'rest'):
        if which == 'rest':
            rig.animation_data.action = None
            for pb in rig.pose.bones: pb.matrix_basis = Matrix.Identity(4)
        else:
            sc.frame_set(F0)
        bpy.context.view_layer.update()
        for tag, v, ctr, sp_ in (('sh_front', (0.001, -1, 0.0), (0, 0, 140), 80), ('sh_back', (0.001, 1, 0.0), (0, 0, 140), 80),
                                 ('feet_side', (1, 0.001, 0.0), (0, 0, 14), 60), ('feet_three', (0.7, -1, 0.35), (0, 0, 12), 60)):
            fp = os.path.join(CACHE, '_idle_%s_%s.png' % (which, tag)); shot(fp, Vector(ctr), v, sp_, (400, 400)); tiles.append(fp)
    rig.animation_data.action = act
    log['sheets'].append(sheet('shoulders_feet', tiles, 4, (400, 400)))
for o in [ground] + strips: bpy.data.objects.remove(o)

# ---------- export: mesh + rig + this one action, the same call as death_clip.py ----------
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

    def read_back(path, with_anim):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.scene.unit_settings.scale_length = 0.01
        bpy.ops.import_scene.fbx(filepath=path, automatic_bone_orientation=False, use_anim=with_anim, ignore_leaf_bones=False)
        r = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE'][0]
        m = [o for o in bpy.context.scene.objects if o.type == 'MESH'][0]
        return r, m, {b.name: (r.matrix_world @ b.head_local) for b in r.data.bones}

    r0, m0, rest0 = read_back(SRC, False)
    r1, m1, rest1 = read_back(OUT, True)
    same = set(rest0) == set(rest1)

    def rb(f):
        bpy.context.scene.frame_set(f); bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get(); e = m1.evaluated_get(dg); me = e.to_mesh()
        Vb = np.array([e.matrix_world @ v.co for v in me.vertices]); e.to_mesh_clear()
        return Vb, (r1.matrix_world @ r1.pose.bones['Bone_000'].head).copy(), (r1.matrix_world @ r1.pose.bones['Bone_001'].head).copy()
    Va, roota, hipa = rb(F0); Vz, rootz, hipz = rb(F1_SAVE)
    log['verify'] = {'bones_src': len(rest0), 'bones_out': len(rest1), 'same_bone_names': same,
                     'max_rest_drift_cm': round(max((rest0[n] - rest1[n]).length for n in rest0), 4) if same else -1,
                     'actions': [(a_.name, [int(a_.frame_range[0]), int(a_.frame_range[1])]) for a_ in bpy.data.actions],
                     'readback_root_world_cm': [round(v, 2) for v in roota], 'readback_hip_world_cm': [round(v, 2) for v in hipa],
                     'readback_loop_seam_cm': round(float(np.abs(Vz - Va).max()), 4),
                     'readback_min_vertex_z': round(float(min(Va[:, 2].min(), Vz[:, 2].min())), 3),
                     'readback_height_cm': round(float(Va[:, 2].max()), 1)}
print('IDLECLIP ' + json.dumps(log))
