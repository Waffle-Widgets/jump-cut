"""Read-only audit of a skinned character body: root weight, sole pitch, and skin that tears when posed like a person.

    blender -b --factory-startup --python Art/Blender/skin_audit.py -- BODY.fbx [RENDER_FOLDER|-] [CLIP.fbx ...]

Prints one line, `SKINAUDIT {json}`. Writes nothing unless RENDER_FOLDER is given; then, for the rest pose and each
test pose, it saves <stem>_<pose>_front.png, _side.png, _hands.png, _feet.png and one contact sheet
<stem>_sheet.png (rows: rest, hang, stride, guard, then any clips; columns: front, side, his +X hand, his -X hand,
his +X shoe and his -X shoe each from its own outer side).

WHY (Sun Nov 15, GameStation, Blender 5.3.0). Three faults were found on the player's body one at a time, each only
after a person saw it in the game (devlog 2026-11-15, three entries). This measures all three on any body first:

  root    On a Meshy Smart Rig the root bone rests at pelvis height, but clips retargeted from Epic's mannequin
          keep it on the FLOOR. A vertex weighted to the root is dragged down by (its root weight x that height).
          Fix: root_weight_to_hip.py.
  soles   A shoe pitched toes-up in the rest pose is tipped up in every clip. Measured exactly the way
          flatten_feet.py measures it (which is also the fix).
  torn    Weights projected from another mesh tear when the body leaves its A-pose: two connected vertices follow
          different bones. Counted as edges stretched to more than 2.5x their rest length AND by more than 1.5 cm,
          the same thresholds as idle_clip.py. Fix: smooth_weights.py.

The limbs are found by TOPOLOGY, never by bone number, because the rigs number their bones differently:
  root = the parentless bone (the one with the most bones under it); hip = its child (most bones under it);
  legs = the hip's children whose own child sits well below them (thigh > shin > foot);
  chest = the first bone up the spine with three or more children; arms = the two of its children whose bones
  lie furthest apart side to side; down each arm: [collarbone,] upper arm, forearm, wrist, hand.
The JSON lists the bones it chose and their lengths, so a wrong guess shows.

The three poses are built by turning bones about WORLD axes through their own heads (idle_clip.py's rot / aim):
  hang    arms brought down from the A-pose to hang at the sides, feet brought under the hip joints
  stride  hang, then one thigh 30 degrees forward with the knee bent, the other 20 back, opposite arms swung
  guard   hang's legs, both upper arms raised forward to shoulder height, elbows bent with the fists up
They are deliberately plain (no collarbone lift, no finger curl): they are a tear test, not a performance.

CLIP.fbx (any number): a file with the SAME skeleton and one or more actions (pose_clip.py's SK_<Name>_Down.fbx, or
the body's own source file with its Idle and Walk). Each action is sampled at its first, middle and last frame, and
the frame that tears most becomes one more pose, named clip_<Action>. This is the pose the game really plays, so
it outranks the three made-up ones. Bones the clip has and the body lacks (or the other way round) are listed.
"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index('--') + 1:]
SRC = argv[0]
OUTDIR = argv[1] if len(argv) > 1 and argv[1] != '-' else None
CLIPS = argv[2:]
STEM = os.path.splitext(os.path.basename(SRC))[0]
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
R = {'file': SRC.replace('\\', '/'), 'blender': bpy.app.version_string}

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=SRC)                       # the same plain import the three fix scripts use
sc = bpy.context.scene
rig = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
mesh = max(meshes, key=lambda o: len(o.data.vertices))
R['actions_in_file'] = sorted(a.name for a in bpy.data.actions)
R['objects'] = {'armature': rig.name, 'mesh': mesh.name, 'meshes': len(meshes)}
R['images'] = sorted(i.name for i in bpy.data.images)
# The importer leaves the export-time pose (frame 0 of an embedded clip) on the pose bones. Clear it.
if rig.animation_data:
    rig.animation_data.action = None
for pb in rig.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
RW = rig.matrix_world.copy()
me = mesh.data


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


V0w = world_verts()                                          # world units, whatever the file imports in
K = 100.0 if (V0w[:, 2].max() - V0w[:, 2].min()) < 5 else 1.0  # centimetres per world unit (metres or centimetres)
V0 = V0w * K
H = float(V0[:, 2].max() - V0[:, 2].min())
R['units'] = 'metres' if K == 100.0 else 'centimetres'
R['armature_scale'] = round(rig.scale.x, 4)
R['verts'] = len(me.vertices); R['polys'] = len(me.polygons); R['bones'] = len(rig.data.bones)
R['height_cm'] = round(H, 1); R['lowest_point_cm'] = round(float(V0[:, 2].min()), 2)

# ---------- the skeleton as plain world matrices (idle_clip.py's helpers) ----------
bones = rig.data.bones
PARENT = {b.name: (b.parent.name if b.parent else None) for b in bones}
CHILD = {b.name: [c.name for c in b.children] for b in bones}
REST = {b.name: RW @ b.matrix_local for b in bones}
RH = {n: REST[n].to_translation() for n in REST}


def under(n):
    out = []
    for c in CHILD[n]:
        out.append(c); out += under(c)
    return out


SUB = {n: under(n) for n in REST}                            # parents first
ROOT = max((n for n in REST if PARENT[n] is None), key=lambda n: len(SUB[n]))
BONES = [ROOT] + SUB[ROOT]
REL = {n: (REST[PARENT[n]].inverted() @ REST[n]) if PARENT[n] else None for n in BONES}
BASIS, W = {}, {}


def reset():
    for n in BONES:
        BASIS[n] = Matrix.Identity(4); W[n] = REST[n].copy()


def head(b): return W[b].to_translation()


def set_world(b, Wn):
    p = PARENT[b]
    base = (W[p] @ REL[b]) if p else REST[b]
    BASIS[b] = base.inverted() @ Wn; W[b] = Wn
    for c in SUB[b]:
        W[c] = W[PARENT[c]] @ REL[c] @ BASIS[c]


def rot(bone, axis, deg):
    """Turn a bone, and everything under it, about a WORLD axis through its own head."""
    if abs(deg) < 1e-7: return
    h = head(bone)
    set_world(bone, Matrix.Translation(h) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-h) @ W[bone])


def aim(bone, end, d):
    """Swing `bone` the short way so the line from its head to `end`'s head points along d."""
    cur = head(end) - head(bone); ax = cur.cross(d)
    if ax.length < 1e-9 * max(cur.length, 1e-9) * max(d.length, 1e-9): return
    rot(bone, ax.normalized(), math.degrees(cur.angle(d)))


def unturn(bone):
    """Give a bone its rest orientation back, where it now is (keeps a foot level after its leg swung)."""
    set_world(bone, Matrix.Translation(head(bone) - RH[bone]) @ REST[bone])


def apply_pose():
    for pb in rig.pose.bones:
        pb.matrix_basis = BASIS.get(pb.name, Matrix.Identity(4))
    bpy.context.view_layer.update()


# ---------- find the limbs by topology ----------
def cm(v): return round(float(v) * K, 1)


HIP = max(CHILD[ROOT], key=lambda n: len(SUB[n])) if CHILD[ROOT] else None
if HIP is None:
    raise SystemExit('SKINAUDIT-REFUSING: the root bone %s has no child' % ROOT)
THIGHS = [c for c in CHILD[HIP] if CHILD[c] and (RH[CHILD[c][0]].z - RH[c].z) * K < -0.10 * H]
if len(THIGHS) != 2:
    raise SystemExit('SKINAUDIT-REFUSING: expected two leg chains under %s, found %s' % (HIP, THIGHS))
THIGHS.sort(key=lambda n: -RH[n].x)                          # +X side first
LEG = {}
for s, th in zip('PN', THIGHS):                              # P: on +X, N: on -X
    shin = CHILD[th][0]; foot = CHILD[shin][0]
    LEG[s] = (th, shin, foot)
# which way he faces: from the ankle to the end of the foot chain, flattened
toes = []
for s in 'PN':
    ft = LEG[s][2]; end = SUB[ft][-1] if SUB[ft] else None
    tip = RH[end] if end else RW @ bones[ft].tail_local
    toes.append(Vector((tip.x - RH[ft].x, tip.y - RH[ft].y, 0.0)))
F = (toes[0] + toes[1])
F = Vector((0.0, -1.0, 0.0)) if F.length < 1e-9 else F.normalized()
if abs(F.y) > 0.8: F = Vector((0.0, math.copysign(1.0, F.y), 0.0))    # snap: these bodies face straight down an axis
R['faces'] = [round(c, 2) for c in F]
AXF = (-Z).cross(F).normalized()                             # turning a hanging limb about this swings it FORWARD

spine = [c for c in CHILD[HIP] if c not in THIGHS]
if not spine:
    raise SystemExit('SKINAUDIT-REFUSING: no spine under %s' % HIP)
b = max(spine, key=lambda n: len(SUB[n]))
SPINE = [b]
while len(CHILD[b]) == 1:
    b = CHILD[b][0]; SPINE.append(b)
CHEST = b
if len(CHILD[CHEST]) < 3:
    raise SystemExit('SKINAUDIT-REFUSING: the bone at the top of the spine, %s, has %d children (need neck + two arms)' % (CHEST, len(CHILD[CHEST])))


def mean_x(n):
    return sum(RH[k].x for k in [n] + SUB[n]) / (1 + len(SUB[n]))


cands = [c for c in CHILD[CHEST] if len(SUB[c]) >= 2]
pair = max(((a_, b_) for a_ in cands for b_ in cands if a_ < b_), key=lambda p: abs(mean_x(p[0]) - mean_x(p[1])))
ARM = {}
for top in pair:
    ch = [top]
    while len(CHILD[ch[-1]]) == 1:
        ch.append(CHILD[ch[-1]][0])
    # ch ends at the first bone that branches (the hand, where the fingers start) or at a leaf
    # A rig may carry an extra bone inside the forearm (the street goon's does), so the wrist and hand are counted
    # from the END of the chain and the forearm is everything from the elbow to the wrist.
    if len(ch) >= 5:   clav, up, fo, wr, hand = ch[0], ch[1], ch[2], ch[-2], ch[-1]
    elif len(ch) == 4: clav, up, fo, wr, hand = ch[0], ch[1], ch[2], ch[3], ch[3]
    elif len(ch) == 3: clav, up, fo, wr, hand = None, ch[0], ch[1], ch[2], ch[2]
    else:
        raise SystemExit('SKINAUDIT-REFUSING: arm chain from %s is only %d bones long' % (top, len(ch)))
    s = 'P' if mean_x(top) > mean_x([p for p in pair if p != top][0]) else 'N'
    ARM[s] = {'clav': clav, 'up': up, 'fo': fo, 'wr': wr, 'hand': hand, 'chain': ch}
SGN = {'P': 1.0, 'N': -1.0}
R['limbs'] = {
    'root': ROOT, 'hip': HIP, 'root_children': len(CHILD[ROOT]), 'root_to_hip_cm': cm((RH[HIP] - RH[ROOT]).length),
    'spine': SPINE, 'chest': CHEST,
    'legs': {s: {'thigh': LEG[s][0], 'shin': LEG[s][1], 'foot': LEG[s][2], 'thigh_cm': cm((RH[LEG[s][1]] - RH[LEG[s][0]]).length),
                 'shin_cm': cm((RH[LEG[s][2]] - RH[LEG[s][1]]).length), 'ankle_x_cm': cm(RH[LEG[s][2]].x)} for s in 'PN'},
    'arms': {s: {'collarbone': ARM[s]['clav'], 'upper': ARM[s]['up'], 'fore': ARM[s]['fo'], 'wrist': ARM[s]['wr'], 'hand': ARM[s]['hand'],
                 'upper_cm': cm((RH[ARM[s]['fo']] - RH[ARM[s]['up']]).length), 'fore_cm': cm((RH[ARM[s]['wr']] - RH[ARM[s]['fo']]).length),
                 'bones_under_hand': len(SUB[ARM[s]['hand']]),
                 'rest_angle_below_level_deg': round(math.degrees(math.asin(max(-1.0, min(1.0, -(RH[ARM[s]['wr']] - RH[ARM[s]['up']]).normalized().z)))), 1)}
             for s in 'PN'},
}

# ---------- weights ----------
gname = {g.index: g.name for g in mesh.vertex_groups}
nv = len(me.vertices)
dom = []
rootw = np.zeros(nv)
unweighted = 0
for v in me.vertices:
    tot = sum(g.weight for g in v.groups)
    if not v.groups or tot <= 1e-9:
        dom.append('none'); unweighted += 1
        continue
    dom.append(gname[max(v.groups, key=lambda g: g.weight).group])
    rootw[v.index] = sum(g.weight for g in v.groups if gname[g.group] == ROOT) / tot
root_h = float(RH[ROOT].z) * K
R['root'] = {'rest_height_cm': round(root_h, 2), 'verts_any': int((rootw > 1e-4).sum()), 'verts_over_5pct': int((rootw > 0.05).sum()),
             'verts_over_20pct': int((rootw > 0.20).sum()), 'max_weight': round(float(rootw.max()), 3),
             'worst_drag_cm': round(float(rootw.max()) * root_h, 1)}
R['unweighted_verts'] = unweighted

# ---------- soles: flatten_feet.py's measurement ----------
FEETSET = {s: set([LEG[s][2]] + SUB[LEG[s][2]]) for s in 'PN'}
FIDX = {s: np.array([i for i, d in enumerate(dom) if d in FEETSET[s]], dtype=np.int64) for s in 'PN'}


def sole(V, idx):
    """(pitch in degrees, toes-up positive; lowest z in cm). t runs from the toe (low) to the heel (high); for a
    body facing -Y it is plain y, which makes this flatten_feet.py's sole() exactly."""
    P = V[idx]
    t = -(P[:, 0] * F.x + P[:, 1] * F.y)
    t0, t1 = np.percentile(t, 2), np.percentile(t, 98)
    front = t < t0 + 0.25 * (t1 - t0); back = t > t1 - 0.25 * (t1 - t0)
    zt, zh = np.percentile(P[front, 2], 3), np.percentile(P[back, 2], 3)
    return math.degrees(math.atan2(zt - zh, t[back].mean() - t[front].mean())), float(P[:, 2].min())


R['soles'] = {}
for s in 'PN':
    if len(FIDX[s]) < 20:
        R['soles'][LEG[s][2]] = {'error': 'only %d vertices follow this foot' % len(FIDX[s])}
        continue
    p, z = sole(V0, FIDX[s])
    R['soles'][LEG[s][2]] = {'side': '+X' if s == 'P' else '-X', 'pitch_deg_toes_up': round(p, 1), 'lowest_cm': round(z, 2), 'verts': int(len(FIDX[s]))}

# ---------- the poses ----------
def legs_under_hips():
    for s in 'PN':
        th, sh, ft = LEG[s]
        t = Vector((RH[th].x, RH[ft].y, RH[ft].z))           # the ankle straight below its own hip joint
        aim(th, ft, t - head(th))
        unturn(ft)


def arms_down():
    for s in 'PN':
        a = ARM[s]
        aim(a['up'], a['wr'], X * (SGN[s] * math.sin(math.radians(9))) - Z * math.cos(math.radians(9)))


def pose_hang():
    reset(); legs_under_hips(); arms_down()


def pose_stride():
    pose_hang()
    lead, trail = 'P', 'N'
    rot(LEG[lead][0], AXF, 30); rot(LEG[lead][1], AXF, -22); unturn(LEG[lead][2])
    rot(LEG[trail][0], AXF, -20); rot(LEG[trail][1], AXF, -14)
    rot(ARM[trail]['up'], AXF, 28); rot(ARM[trail]['fo'], AXF, 24)       # the arm opposite the leading leg comes forward
    rot(ARM[lead]['up'], AXF, -20); rot(ARM[lead]['fo'], AXF, 12)


def pose_guard():
    reset(); legs_under_hips()
    for s in 'PN':
        a = ARM[s]
        aim(a['up'], a['fo'], F + X * (SGN[s] * 0.12))                    # upper arm level, pointing forward
        aim(a['fo'], a['wr'], F * 0.30 + Z * 0.90 - X * (SGN[s] * 0.28))   # elbow bent, fist up and a little in


POSES = [('hang', pose_hang), ('stride', pose_stride), ('guard', pose_guard)]
E = np.array([e.vertices[:] for e in me.edges], dtype=np.int64)
r0 = np.linalg.norm(V0[E[:, 0]] - V0[E[:, 1]], axis=1)


def torn(V, ratio=2.5, min_cm=1.5):
    r1 = np.linalg.norm(V[E[:, 0]] - V[E[:, 1]], axis=1)
    bad = np.where((r1 > ratio * np.maximum(r0, 0.05)) & (r1 - r0 > min_cm))[0]
    return bad, r1


def from_basis(Bd):
    def fn():
        reset()
        for n in BONES:
            p = PARENT[n]
            BASIS[n] = Bd.get(n, Matrix.Identity(4))
            W[n] = ((W[p] @ REL[n]) if p else REST[n]) @ BASIS[n]
    return fn


R['clips'] = []
for cp in CLIPS:
    mine = set(bpy.data.objects)
    acts0 = set(bpy.data.actions)
    bpy.ops.import_scene.fbx(filepath=cp)
    new = [o for o in bpy.data.objects if o not in mine]
    crig = [o for o in new if o.type == 'ARMATURE'][0]
    info = {'file': cp.replace('\\', '/'), 'bones_missing_from_body': sorted(set(b.name for b in crig.data.bones) - set(BONES)),
            'bones_missing_from_clip': sorted(set(BONES) - set(b.name for b in crig.data.bones)),
            'max_rest_difference_cm': round(max(((crig.matrix_world @ b.matrix_local).to_translation() - RH[b.name]).length
                                                for b in crig.data.bones if b.name in RH) * K, 3), 'actions': {}}
    for act in [a_ for a_ in bpy.data.actions if a_ not in acts0]:
        crig.animation_data_create(); crig.animation_data.action = act
        try: crig.animation_data.action_slot = act.slots[0]
        except Exception: pass
        f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
        best = None
        for f in sorted(set([f0, (f0 + f1) // 2, f1])):
            sc.frame_set(f); bpy.context.view_layer.update()
            Bd = {pb.name: pb.matrix_basis.copy() for pb in crig.pose.bones}
            from_basis(Bd)(); apply_pose()
            n = int(len(torn(world_verts() * K)[0]))
            if best is None or n > best[0]: best = (n, f, Bd)
        short = act.name.split('|')[-1]
        info['actions'][short] = {'frames': [f0, f1], 'worst_frame': best[1]}
        POSES.append(('clip_' + short, from_basis(best[2])))
    for o in new: bpy.data.objects.remove(o)
    R['clips'].append(info)
if rig.animation_data: rig.animation_data.action = None

VP = {'rest': V0}
WP = {'rest': {n: REST[n].copy() for n in BONES}}
R['torn'] = {}
for name, fn in POSES:
    fn(); apply_pose()
    fk = max((RW @ pb.matrix - W[pb.name]).to_translation().length for pb in rig.pose.bones if pb.name in W) * K
    V = world_verts() * K
    VP[name] = V; WP[name] = {n: W[n].copy() for n in BONES}
    bad, r1 = torn(V)
    pairs = {}
    for e in bad:
        k = tuple(sorted((dom[E[e, 0]], dom[E[e, 1]]))); pairs[k] = pairs.get(k, 0) + 1
    # where on the body the tears are, by the dominant bone's limb
    R['torn'][name] = {'edges': int(len(bad)), 'longest_cm': round(float(r1[bad].max()), 1) if len(bad) else 0.0,
                       'by_bone_pair': [[n, list(k)] for k, n in sorted(pairs.items(), key=lambda kv: -kv[1])[:8]],
                       'fk_check_cm': round(fk, 4),
                       'ankle_gap_cm': cm((W[LEG['P'][2]].to_translation() - W[LEG['N'][2]].to_translation()).length),
                       'wrist_gap_cm': cm((W[ARM['P']['wr']].to_translation() - W[ARM['N']['wr']].to_translation()).length)}
R['torn_total'] = sum(R['torn'][n]['edges'] for n, _ in POSES)
# name the limb each bone belongs to, so the pairs can be read without a bone chart
part = {}
for s in 'PN':
    side = '+X' if s == 'P' else '-X'
    for n in [LEG[s][0]]: part[n] = 'thigh' + side
    part[LEG[s][1]] = 'shin' + side
    for n in FEETSET[s]: part[n] = 'foot' + side
    a = ARM[s]
    if a['clav']: part[a['clav']] = 'collarbone' + side
    part[a['up']] = 'upperarm' + side; part[a['fo']] = 'forearm' + side; part[a['wr']] = 'wrist' + side
    for n in [a['hand']] + SUB[a['hand']]: part.setdefault(n, 'hand/fingers' + side)
part[ROOT] = 'root'; part[HIP] = 'hip'
for n in SPINE: part.setdefault(n, 'spine')
for n in BONES: part.setdefault(n, 'head/neck/other')
used = set(k for name, _ in POSES for _n, pr in R['torn'][name]['by_bone_pair'] for k in pr)
R['bone_parts'] = {n: part.get(n, '?') for n in sorted(used)}

# ---------- pictures ----------
if OUTDIR:
    os.makedirs(OUTDIR, exist_ok=True)
    U = 1.0 / K                                              # world units per centimetre
    sc.render.engine = 'BLENDER_WORKBENCH'
    sh = sc.display.shading
    sh.light = 'STUDIO'
    textured = any(i.size[0] > 0 for i in bpy.data.images)
    sh.color_type = 'TEXTURE' if textured else 'MATERIAL'
    sh.show_cavity = True
    R['render_textured'] = bool(textured)
    cam = bpy.data.objects.new('AuditCam', bpy.data.cameras.new('AuditCam'))
    sc.collection.objects.link(cam); sc.camera = cam
    cam.data.type = 'ORTHO'; cam.data.clip_start = 0.01 * U; cam.data.clip_end = 5000 * U
    sc.render.image_settings.file_format = 'PNG'
    TW, TH = 420, 560
    ALL = np.concatenate(list(VP.values()))
    lo, hi = ALL.min(0), ALL.max(0)
    CTR = Vector(((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2))
    SPAN = float(max(hi[2] - lo[2], (hi[0] - lo[0]) * TH / TW, (hi[1] - lo[1]) * TH / TW)) * 1.06

    def shot(fp, ctr_cm, v, span_cm, res):
        sc.render.resolution_x, sc.render.resolution_y = res
        sc.render.resolution_percentage = 100
        cam.data.ortho_scale = span_cm * U                   # spans the longer side of the picture: its height, here
        v = Vector(v).normalized()
        c = Vector(ctr_cm) * U
        cam.location = c + v * (1500 * U)
        cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = fp
        bpy.ops.render.render(write_still=True)

    def load_px(fp, w, h):
        im = bpy.data.images.load(fp)
        x = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(x)
        bpy.data.images.remove(im)
        return x.reshape(h, w, 4)

    def save_px(fp, px):
        h, w = px.shape[:2]
        im = bpy.data.images.new('sheet', w, h); im.pixels.foreach_set(px.ravel().astype(np.float32))
        im.filepath_raw = fp; im.file_format = 'PNG'; im.save()
        bpy.data.images.remove(im)

    R['renders'] = []
    rows = []
    for name in ['rest'] + [n for n, _ in POSES]:
        for n in BONES:
            W[n] = WP[name][n]
        for pb in rig.pose.bones:
            p = PARENT[pb.name]
            base = (W[p] @ REL[pb.name]) if p else REST[pb.name]
            pb.matrix_basis = base.inverted() @ W[pb.name]
        bpy.context.view_layer.update()
        ff = os.path.join(OUTDIR, '%s_%s_front.png' % (STEM, name))
        fs = os.path.join(OUTDIR, '%s_%s_side.png' % (STEM, name))
        fh = os.path.join(OUTDIR, '%s_%s_hands.png' % (STEM, name))
        lo, hi = VP[name].min(0), VP[name].max(0)            # frame each pose on itself: a seated body fills the tile too
        CTR = Vector(((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2))
        SPAN = float(max(hi[2] - lo[2], (hi[0] - lo[0]) * TH / TW, (hi[1] - lo[1]) * TH / TW)) * 1.08
        shot(ff, CTR, F + Z * 0.03, SPAN, (TW, TH))
        shot(fs, CTR, X + F * 0.001 + Z * 0.03, SPAN, (TW, TH))
        tiles = []
        for s in 'PN':
            a = ARM[s]
            hb = a['hand']
            tipn = SUB[hb][-1] if SUB[hb] else hb
            c = (W[a['wr']].to_translation() + W[tipn].to_translation()) * 0.5 * K if SUB[hb] else (RW @ rig.pose.bones[hb].tail) * K
            tmp = os.path.join(OUTDIR, '_tmp_hand_%s.png' % s)
            shot(tmp, c, X * (SGN[s] * 0.75) + F * 0.65 + Z * 0.12, 46, (TW, TH))
            tiles.append(load_px(tmp, TW, TH)); os.remove(tmp)
        save_px(fh, np.concatenate(tiles, axis=1))
        fx = os.path.join(OUTDIR, '%s_%s_feet.png' % (STEM, name))
        ftiles = []
        for s in 'PN':                                       # each shoe from its own outer side, dead level
            c = W[LEG[s][2]].to_translation() * K + F * 7.0
            c.z = max(c.z - 2.0, 0.0) + 8.0
            tmp = os.path.join(OUTDIR, '_tmp_foot_%s.png' % s)
            shot(tmp, c, X * SGN[s] + F * 0.001, 46, (TW, TH))
            ftiles.append(load_px(tmp, TW, TH)); os.remove(tmp)
        save_px(fx, np.concatenate(ftiles, axis=1))
        tiles = tiles + ftiles
        R['renders'].append(fx.replace('\\', '/'))
        rows.append(np.concatenate([load_px(ff, TW, TH), load_px(fs, TW, TH)] + tiles, axis=1))
        R['renders'] += [ff.replace('\\', '/'), fs.replace('\\', '/'), fh.replace('\\', '/')]
    sheet = os.path.join(OUTDIR, '%s_sheet.png' % STEM)
    save_px(sheet, np.concatenate(rows[::-1], axis=0))     # image rows run bottom-up: rest ends on top
    R['sheet'] = sheet.replace('\\', '/')

print('SKINAUDIT ' + json.dumps(R))
