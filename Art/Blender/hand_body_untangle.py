"""Untangle a hand from the hip it was skinned next to: every vertex follows the hand OR the body, never both.

    blender -b --factory-startup --python Art/Blender/hand_body_untangle.py -- IN.fbx OUT.fbx

WHY (Sun Nov 15, GameStation, Blender 5.3.0). The coworker's hands "look all twisted up" in her idle. On her rig
the rest pose hangs the forearms down beside the hips, so a hand is within centimetres of the trousers when the
skin is bound. Two tools then made each other's mistake permanent: the proximity weight transfer gave some hand
vertices a hip bone and some trouser vertices a hand bone, and collapse_hand_weights.py's prune pass hands any
vertex that lost everything to the NEAREST bone - which for a fingertip beside a hip is the hip. Nothing shows
while she holds the pose she was sculpted in. Lower the arm and a piece of the hand stays behind with the leg, and
a bite of the trousers leaves with the hand.

HOW. Near a hand, distance alone cannot say what a vertex is - but a hand is thin and a hip is thick. Each vertex in
reach of a hand gets two distances: to the hand's own line (wrist to fingertip), measured in hand radii (5 cm), and
to the nearest body bone that is not part of an arm, measured in body radii (10 cm). The smaller wins.
  hand -> the whole weight goes to the palm bone (she has a mitten: no fingers to bend; see collapse_hand_weights)
  body -> every weight on that arm's forearm, hand and finger bones is removed and the rest renormalised
Vertices at the wrist itself are left alone so the cuff still blends.
"""
import bpy, sys, os
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
IN, OUT = argv[0], argv[1]
HAND_R, BODY_R, REACH = 5.0, 10.0, 9.0          # centimetres
HAND_REACH = 18.0                               # a splayed fingertip is a long way from the hand's centre line; nothing else skin-coloured is this near

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=IN)
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
mesh = max([o for o in bpy.data.objects if o.type == 'MESH'], key=lambda o: len(o.data.vertices))
AW, MW = arm.matrix_world, mesh.matrix_world
B = arm.data.bones
zs = [(MW @ v.co).z for v in mesh.data.vertices]
CM = (max(zs) - min(zs)) / 164.4                # scene units per centimetre, from her height
seg = {b.name: (AW @ b.head_local, AW @ b.tail_local) for b in B}


def sd(p, a, b):
    ab = b - a
    L2 = ab.dot(ab)
    if L2 < 1e-12:
        return (p - a).length, 0.0
    t = (p - a).dot(ab) / L2
    tc = max(0.0, min(1.0, t))
    return (p - (a + ab * tc)).length, t


def tree(b):
    out = [b.name]
    for c in b.children:
        out += tree(c)
    return out


ups = [B[n] for n in ('Bone_022', 'Bone_027') if n in B]
if len(ups) != 2:
    raise SystemExit('REFUSING: expected upper arms Bone_022 and Bone_027')
sides = []
arm_bones = set()
for up in ups:
    arm_bones |= set(tree(up.parent))                             # collarbone and everything under it
    fo = up.children[0]; wr = fo.children[0]
    palm = wr
    while len(palm.children) < 3 and palm.children:
        palm = palm.children[0]
    w = AW @ wr.head_local
    tip = max((AW @ B[n].tail_local for n in tree(wr)), key=lambda p: (p - w).length)
    sides.append({'fo': fo.name, 'wr': wr.name, 'palm': palm.name, 'w': w, 'tip': tip, 'chain': set(tree(fo))})
body = [n for n in seg if n not in arm_bones]
gi = {g.name: g.index for g in mesh.vertex_groups}
name_of = {g.index: g.name for g in mesh.vertex_groups}

# WHAT A VERTEX IS, BY ITS COLOUR. The first version of this asked "is it nearer the hand's line or a body bone",
# and shattered the hands: a splayed fingertip is as far from the hand's line as the trouser cloth is from the thigh
# bone. Her hands are bare skin and everything they lie against is navy trousers or a teal apron, so the painted
# colour under each vertex says which it is, and says it for certain.
import numpy as np
img = max(bpy.data.images, key=lambda i: i.size[0] * i.size[1])
iw, ih = img.size
px = np.empty(iw * ih * 4, dtype=np.float32); img.pixels.foreach_get(px); px = px.reshape(ih, iw, 4)
uvl = mesh.data.uv_layers.active.data
vuv = {}
for l in mesh.data.loops:
    vuv.setdefault(l.vertex_index, uvl[l.index].uv)


def is_skin(vi):
    u, v_ = vuv[vi]
    c = px[min(ih - 1, max(0, int(v_ * ih))), min(iw - 1, max(0, int(u * iw)))]
    return c[0] > 0.5 and c[0] >= c[1] * 0.97 and c[0] >= c[2] * 0.97     # light and not blue or green: navy is dark, the apron is teal


# The grooves between her fingers are PAINTED as dark lines, and a vertex on one reads as cloth. A groove is a thin
# line with skin either side; trousers are dark all round. So each vertex takes the majority of its neighbours, a few
# times over (the first try without this tore a shard off the hand along every groove).
SKIN = [is_skin(v.index) for v in mesh.data.vertices]
nb = [[] for _ in mesh.data.vertices]
for e in mesh.data.edges:
    a_, b_ = e.vertices
    nb[a_].append(b_); nb[b_].append(a_)
for _ in range(4):                                  # ONE WAY ONLY: dark becomes skin, never the reverse. Skin is never
    nxt = list(SKIN)                                # misread (trousers and apron are nowhere near it), and voting both
    for i, ns in enumerate(nb):                     # ways ate a small patch of hand that touches the hip.
        if ns and not SKIN[i]:
            nxt[i] = sum(SKIN[j] for j in ns) * 2 >= len(ns)
    SKIN = nxt
to_hand = to_body = to_arm = 0
for v in mesh.data.vertices:
    p = MW @ v.co
    wts = {name_of[g.group]: g.weight for g in v.groups if g.weight > 1e-5}
    for s in sides:
        dh, t = sd(p, s['w'], s['tip'])
        df, tf = sd(p, seg[s['fo']][0], s['w'])
        has = any(n in s['chain'] for n in wts)
        skin = SKIN[v.index]
        if min(dh, df) > (HAND_REACH if skin else REACH) * CM and not has:
            continue
        if skin and dh <= HAND_REACH * CM and t > 0.12:
            if set(wts) == {s['palm']}:
                break
            new = {s['palm']: 1.0}; to_hand += 1                    # hand: one rigid piece on the palm bone
        elif skin and min(dh, df) <= REACH * CM:
            new = {n: w for n, w in wts.items() if n in arm_bones}  # wrist or forearm skin: arm bones only
            if len(new) == len(wts):
                break
            if not new:
                new = {s['fo']: 1.0}
            to_arm += 1
        elif not skin and has:
            new = {n: w for n, w in wts.items() if n not in s['chain']}   # cloth: nothing from this forearm or hand
            if not new:
                new = {min(body, key=lambda n: sd(p, *seg[n])[0]): 1.0}
            to_body += 1
        else:
            continue
        tot = sum(new.values())
        for g in list(v.groups):
            mesh.vertex_groups[g.group].remove([v.index])
        for n, w in new.items():
            if n not in gi:
                gi[n] = mesh.vertex_groups.new(name=n).index; name_of[gi[n]] = n
            mesh.vertex_groups[gi[n]].add([v.index], w / tot, 'REPLACE')
        break
import collections
hist = collections.Counter()
for v in mesh.data.vertices:
    p = MW @ v.co
    for s_ in sides:
        if sd(p, s_['w'], s_['tip'])[0] < 6 * CM:
            u, v_ = vuv[v.index]; c = px[min(ih - 1, max(0, int(v_ * ih))), min(iw - 1, max(0, int(u * iw)))]
            hist[(round(float(c[0]), 1), round(float(c[1]), 1), round(float(c[2]), 1))] += 1
print('UNTANGLE colours within 6 cm of a hand line: %s' % hist.most_common(8))
print('UNTANGLE colour from %s %dx%d: %d hand vertices put wholly on a palm bone, %d arm-skin vertices freed from body bones, %d cloth vertices freed from an arm' % (img.name, iw, ih, to_hand, to_arm, to_body))
if any(sum(g.weight for g in v.groups) < 1e-4 for v in mesh.data.vertices):
    raise SystemExit('REFUSING: a vertex lost all weight')
arm.name = 'Armature'; arm.data.name = 'Armature'
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True); arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, add_leaf_bones=False, bake_anim=False,
                         mesh_smooth_type='FACE', path_mode='COPY', embed_textures=True)
print('UNTANGLE exported ' + OUT)
