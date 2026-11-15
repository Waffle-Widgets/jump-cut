"""Put a generated mesh INTO an existing rig's rest pose, using the generator's own rig to get there.

    blender --background --python Art/Blender/conform_rest_pose.py -- SRC.fbx REF.fbx OUT.fbx

WHY THIS EXISTS. jump-cut #96. A skinned mesh has to be modelled in its skeleton's rest pose; if it is not,
every frame of every clip is wrong by that difference. reskin_to_existing_rig.py checks the two meshes agree
on height, feet-at-zero and arm span - and all three can match while the ELBOWS, WRISTS and KNEES are a hand's
width apart. On SK_CafeWalkerV2 they were: measured against the 69-bone rig's rest pose, Meshy's own rig for
the same body puts the elbow 8.3 cm out, the wrist 12.7 cm and the knee 8.2 cm. V1's A-pose splays the legs
and hangs the forearms down and back; Meshy stood the character up straight.

That is the real cause of the paddle hands. The rig's twenty finger bones ended up in EMPTY SPACE - 11 to 17 cm
from the nearest vertex of the hand they are supposed to drive - so a proximity weight transfer had nothing
sensible to find, dumped the fingers into the palm, and left 17 of 40 finger bones moving nothing at all. No
amount of re-weighting fixes that, because a bone 15 cm from the finger it drives does not curl the finger, it
swings it.

So: before transferring any weights, pose the generated mesh's OWN rig to match the target rig's rest pose,
bake it, and transfer afterwards. Then the bones are inside the geometry they drive.

HOW. Joint directions, parents first. For each mapped pair, rotate the source bone so the direction to its
mapped child matches the same direction in the target's rest pose. Two sweeps, because rotating a parent moves
its children. Then the root is translated onto the target's root, which is what brings the hips down to where
splayed legs put them. Finally each HAND gets a roll search, because direction alignment cannot determine a
bone's ROLL and the roll is exactly what decides whether the finger bones land along the fingers or across
them - Meshy's rig has no finger bones to align against, so the fingers themselves are the objective: minimise
the distance from the hand's vertices to the target rig's hand-and-finger segments.
"""
import bpy, sys, os, math
from mathutils import Vector, Matrix, Quaternion

argv = sys.argv[sys.argv.index("--")+1:]
SRC, REF, OUT = argv[0], argv[1], argv[2]

# The five fingertip bones of each hand. Their mean stands in for "where the hand points".
L_TIPS = ('Bone_029', 'Bone_033', 'Bone_037', 'Bone_041', 'Bone_045')
R_TIPS = ('Bone_049', 'Bone_053', 'Bone_057', 'Bone_061', 'Bone_065')

# (source bone, source child, target bone, target child). Meshy's "Left" is +x and so is the 69-rig's
# Bone_019 side, so Left maps to Bone_019/020/021 and Right to the mirror. Checked against measured x signs.
# A target child may be a tuple of bone names, meaning "the mean of their heads".
MAP = [
    ('Hips', 'Spine02', 'Bone_001', 'Bone_005'),
    ('Spine02', 'Spine01', 'Bone_005', 'Bone_004'),
    ('Spine01', 'Spine', 'Bone_004', 'Bone_003'),
    ('Spine', 'neck', 'Bone_002', 'Bone_018'),
    ('neck', 'Head', 'Bone_018', 'Bone_017'),
    ('Head', 'head_end', 'Bone_017', 'Bone_016'),
    ('LeftShoulder', 'LeftArm', 'Bone_023', 'Bone_022'),
    ('LeftArm', 'LeftForeArm', 'Bone_022', 'Bone_021'),
    ('LeftForeArm', 'LeftHand', 'Bone_021', 'Bone_020'),
    # Meshy's LeftHand -> LeftHand_End spans the WHOLE hand, fingers included. Bone_020 -> Bone_019 is only
    # the 5 cm wrist-to-palm stub and points somewhere else entirely, so matching those two rolled the hand
    # down and cost the arm 9 cm of reach. The hand's real axis is wrist -> the middle of the fingertips.
    ('LeftHand', 'LeftHand_End', 'Bone_020', L_TIPS),
    ('RightShoulder', 'RightArm', 'Bone_028', 'Bone_027'),
    ('RightArm', 'RightForeArm', 'Bone_027', 'Bone_026'),
    ('RightForeArm', 'RightHand', 'Bone_026', 'Bone_025'),
    ('RightHand', 'RightHand_End', 'Bone_025', R_TIPS),
    ('LeftUpLeg', 'LeftLeg', 'Bone_010', 'Bone_009'),
    ('LeftLeg', 'LeftFoot', 'Bone_009', 'Bone_008'),
    ('LeftFoot', 'LeftToeBase', 'Bone_008', 'Bone_007'),
    ('RightUpLeg', 'RightLeg', 'Bone_015', 'Bone_014'),
    ('RightLeg', 'RightFoot', 'Bone_014', 'Bone_013'),
    ('RightFoot', 'RightToeBase', 'Bone_013', 'Bone_012'),
]
HANDS = [('LeftHand', 'Bone_019'), ('RightHand', 'Bone_024')]
# Translate by the LEG ROOTS, not by the hip bone. Meshy's 'Hips' sits 9.7 cm above its own leg roots where
# the 69-rig's 'Bone_001' sits 2.1 cm above its own - they are not the same anatomical point, and matching
# them put the whole body 11.9 cm through the floor.
ROOT_PAIRS = [('LeftUpLeg', 'Bone_010'), ('RightUpLeg', 'Bone_015')]
ROOT_DRIVER = 'Hips'


def imp(path, tag):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    added = [o for o in bpy.data.objects if o not in before]
    for o in added:
        o.name = tag + '_' + o.name
    return added


bpy.ops.wm.read_factory_settings(use_empty=True)
src = imp(SRC, 'SRC')
ref = imp(REF, 'REF')
src_mesh = next(o for o in src if o.type == 'MESH')
src_arm = next(o for o in src if o.type == 'ARMATURE')
ref_arm = next(o for o in ref if o.type == 'ARMATURE')
for o in ref:
    if o.type == 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)

RM = ref_arm.matrix_world


def thead(n):
    if isinstance(n, (tuple, list)):
        acc = Vector((0, 0, 0))
        for x in n:
            acc += thead(x)
        return acc / len(n)
    b = ref_arm.data.bones.get(n)
    if b is None:
        raise SystemExit("target rig has no bone %r" % n)
    return RM @ b.head_local


def shead(n):
    pb = src_arm.pose.bones.get(n)
    if pb is None:
        raise SystemExit("source rig has no bone %r" % n)
    return src_arm.matrix_world @ pb.head


def seg_dist(p, a, b):
    ab = b - a
    L2 = ab.dot(ab)
    if L2 < 1e-12:
        return (p - a).length
    t = max(0.0, min(1.0, (p - a).dot(ab) / L2))
    return (p - (a + ab * t)).length


def subtree(b):
    out = [b]
    for c in b.children:
        out += subtree(c)
    return out


bpy.context.view_layer.objects.active = src_arm
bpy.ops.object.mode_set(mode='POSE')
for pb in src_arm.pose.bones:
    pb.rotation_mode = 'QUATERNION'


def rotate_about_head(pb, q_world):
    """Apply a world-space rotation about this bone's head, keeping the head where it is."""
    m = src_arm.matrix_world @ pb.matrix
    piv = m.to_translation()
    new = Matrix.Translation(piv) @ q_world.to_matrix().to_4x4() @ Matrix.Translation(-piv) @ m
    pb.matrix = src_arm.matrix_world.inverted() @ new
    bpy.context.view_layer.update()


print("--- joint direction alignment ---")
for sweep in (1, 2, 3):
    worst = 0.0
    worst_name = ''
    for sb, sc, tb, tc in MAP:
        cur = shead(sc) - shead(sb)
        tgt = thead(tc) - thead(tb)
        if cur.length < 1e-6 or tgt.length < 1e-6:
            continue
        ang = math.degrees(cur.angle(tgt))
        if ang > worst:
            worst, worst_name = ang, sb
        if ang > 0.01:
            rotate_about_head(src_arm.pose.bones[sb], cur.rotation_difference(tgt))
    print("  sweep %d: worst joint off by %.2f deg (%s) before correcting" % (sweep, worst, worst_name))

def posed_verts():
    bpy.context.view_layer.update()
    ev = src_mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
    m = ev.to_mesh()
    pts = [src_mesh.matrix_world @ v.co.copy() for v in m.vertices]
    ev.to_mesh_clear()
    return pts


def translate_bone(name, d):
    pb = src_arm.pose.bones[name]
    pb.matrix = src_arm.matrix_world.inverted() @ (Matrix.Translation(d) @ (src_arm.matrix_world @ pb.matrix))
    bpy.context.view_layer.update()


# Root: match the leg roots in x and y, but seat the SOLES on z = 0. Conformed V2's leg comes out 4.3 cm
# longer than V1's from hip to sole, and the game cannot have the player 4 cm through the floor - the
# component's z = -90 offset in BP_Player is tuned for feet at zero.
d = Vector((0, 0, 0))
for sb, tb in ROOT_PAIRS:
    d += thead(tb) - shead(sb)
d /= len(ROOT_PAIRS)
d.z = 0.0
translate_bone(ROOT_DRIVER, d)
sink = min(p.z for p in posed_verts())
translate_bone(ROOT_DRIVER, Vector((0, 0, -sink)))
print("  root moved %.2f cm in x/y to seat the leg roots, then %+.2f cm in z to seat the soles"
      % (d.length * 100, -sink * 100))


# --- hand roll: direction alignment cannot set it, so search it against the target's finger bones -----
def posed_cloud(group_names, nmax=200):
    want = set()
    for g in src_mesh.vertex_groups:
        if g.name in group_names:
            want.add(g.index)
    idx = [v.index for v in src_mesh.data.vertices
           if sum(g.weight for g in v.groups if g.group in want) > 0.5]
    step = max(1, len(idx) // nmax)
    return idx[::step]


for src_bone, tgt_hand in HANDS:
    segs = [(RM @ b.head_local, RM @ b.tail_local) for b in subtree(ref_arm.data.bones[tgt_hand])]
    idx = posed_cloud({src_bone, src_bone + '_End'})
    pb = src_arm.pose.bones[src_bone]
    axis = (shead(src_bone + '_End') - shead(src_bone)).normalized()
    other = axis.orthogonal().normalized()
    third = axis.cross(other).normalized()
    base = pb.matrix.copy()

    def cost():
        bpy.context.view_layer.update()
        ev = src_mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
        m = ev.to_mesh()
        tot = 0.0
        for i in idx:
            p = src_mesh.matrix_world @ m.vertices[i].co
            tot += min(seg_dist(p, a, b) for a, b in segs)
        ev.to_mesh_clear()
        return tot / len(idx)

    def place(roll, tilt, yaw):
        pb.matrix = base
        bpy.context.view_layer.update()
        if roll:
            rotate_about_head(pb, Quaternion(axis, math.radians(roll)))
        if tilt:
            rotate_about_head(pb, Quaternion(other, math.radians(tilt)))
        if yaw:
            rotate_about_head(pb, Quaternion(third, math.radians(yaw)))

    # Slide the hand onto its own finger bones before searching the roll. Seating the soles on z = 0 leaves
    # the whole body a few cm above the rig, and a rotation cannot take out a translation - but the fingers
    # are 2.5 cm apart, so a few cm of offset is enough to make the wrong finger the nearest one. A wrist
    # slide of this size only stretches forearm skin, which nothing in this game's silhouette shows.
    tgt_pts = []
    for a, b in segs:
        for f in (0.0, 0.25, 0.5, 0.75, 1.0):
            tgt_pts.append(a + (b - a) * f)
    tgt_c = sum(tgt_pts, Vector((0, 0, 0))) / len(tgt_pts)
    pv = posed_verts()
    cur_c = sum((pv[i] for i in idx), Vector((0, 0, 0))) / len(idx)
    translate_bone(src_bone, tgt_c - cur_c)
    base = pb.matrix.copy()
    axis = (shead(src_bone + '_End') - shead(src_bone)).normalized()
    other = axis.orthogonal().normalized()
    third = axis.cross(other).normalized()
    print("  %s: slid %.2f cm onto the %s finger cloud" % (src_bone, (tgt_c - cur_c).length * 100, tgt_hand))

    start = cost()
    best = (start, 0.0, 0.0, 0.0)
    print("  %s: %d sample verts; start mean distance to %s segments = %.2f cm"
          % (src_bone, len(idx), tgt_hand, start * 100))
    # Roll first and alone, over the full circle: that is the degree of freedom direction alignment left
    # undetermined. Only then allow a few degrees of tilt/yaw, so the search cannot quietly undo the joint
    # direction fit it was handed (letting it swing 28 deg made the two arms come out 4.5 cm asymmetric).
    for step, span, free in ((20.0, 180.0, False), (6.0, 24.0, False), (2.0, 7.0, True), (1.0, 2.0, True)):
        c0 = best
        n = int(span / step)
        for i in range(-n, n + 1):
            for j in ((-1, 0, 1) if free else (0,)):
                for k in ((-1, 0, 1) if free else (0,)):
                    r, t, y = c0[1] + i * step, c0[2] + j * step, c0[3] + k * step
                    place(r, t, y)
                    c = cost()
                    if c < best[0]:
                        best = (c, r, t, y)
    place(best[1], best[2], best[3])
    print("     best roll=%.1f tilt=%.1f yaw=%.1f -> mean distance %.2f cm (was %.2f)"
          % (best[1], best[2], best[3], best[0] * 100, start * 100))

# --- bake the posed mesh ------------------------------------------------------------------------------
bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.view_layer.objects.active = src_mesh
dg = bpy.context.evaluated_depsgraph_get()
ev = src_mesh.evaluated_get(dg)
baked = ev.to_mesh()
co = [src_mesh.matrix_world @ v.co.copy() for v in baked.vertices]
ev.to_mesh_clear()
inv = src_mesh.matrix_world.inverted()
for i, v in enumerate(src_mesh.data.vertices):
    v.co = inv @ co[i]
for m in list(src_mesh.modifiers):
    if m.type == 'ARMATURE':
        src_mesh.modifiers.remove(m)
src_mesh.parent = None
src_mesh.vertex_groups.clear()

pts = [src_mesh.matrix_world @ v.co for v in src_mesh.data.vertices]
print("CONFORMED verts=%d height=%.2f cm feet_z=%.2f cm x[%.1f %.1f] y[%.1f %.1f]"
      % (len(pts), (max(p.z for p in pts) - min(p.z for p in pts)) * 100, min(p.z for p in pts) * 100,
         min(p.x for p in pts) * 100, max(p.x for p in pts) * 100,
         min(p.y for p in pts) * 100, max(p.y for p in pts) * 100))
for tb in ['Bone_019', 'Bone_024', 'Bone_021', 'Bone_026', 'Bone_009', 'Bone_014',
           'Bone_029', 'Bone_049', 'Bone_036', 'Bone_056']:
    b = ref_arm.data.bones[tb]
    a, t = RM @ b.head_local, RM @ b.tail_local
    print("   nearest conformed vertex to %-10s = %5.2f cm" % (tb, min(seg_dist(p, a, t) for p in pts) * 100))

for o in list(bpy.data.objects):
    if o is not src_mesh:
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
src_mesh.select_set(True)
bpy.context.view_layer.objects.active = src_mesh
os.makedirs(os.path.dirname(OUT), exist_ok=True)
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, add_leaf_bones=False, bake_anim=False,
                         mesh_smooth_type='FACE', path_mode='COPY', embed_textures=True)
print("EXPORTED " + OUT)
