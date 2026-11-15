"""Make a mitten hand move as one piece: fold every finger bone's weight into the palm bone.

    blender -b -noaudio --python collapse_hand_weights.py -- IN.fbx OUT.fbx [HAND_BONES]

WHY. jump-cut #101. `CafeCoworkerV2` has no fingers - Meshy generated a fused mitten with shallow grooves
and a stub thumb. The 68-bone rig she has to bind to (so her existing Idle and Walk still play) carries a
20-bone finger chain per hand, authored against V1's body, which DOES have separated fingers. Transfer those
weights onto a mitten and the clip's finger keys fan one lump of geometry in five directions at once: the
hands come out as long white shards from the very first frame of Idle.

Collapsing the chains costs nothing she has. She cannot articulate fingers she was not given, and a hand
that moves rigidly at the wrist reads correctly at the distance she is ever seen from. It is strictly better
than a hand that shatters.

This is NOT the right move for a character whose fingers actually exist - the player's hands separate, and
PR #117/#123 went to some trouble to keep 32 of his 40 finger bones working. Only reach for it when the
geometry has no fingers to drive.
"""
import bpy, sys, os

argv = sys.argv[sys.argv.index("--") + 1:]
IN, OUT = argv[0], argv[1]
HANDS = argv[2].split(',') if len(argv) > 2 else ['Bone_020', 'Bone_025']

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=IN)
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
mesh = next(o for o in bpy.data.objects if o.type == 'MESH')


def subtree(b):
    out = []
    for c in b.children:
        out.append(c.name)
        out += subtree(c)
    return out


plan = {}
for h in HANDS:
    if h not in arm.data.bones:
        raise SystemExit('REFUSING: no bone %s in %s' % (h, IN))
    for n in subtree(arm.data.bones[h]):
        plan[n] = h
print('folding %d finger bones into %s' % (len(plan), HANDS))

gi = {g.name: g.index for g in mesh.vertex_groups}
missing = [n for n in plan if n not in gi]
if missing:
    print('note: %d finger bones have no vertex group (nothing to fold): %s' % (len(missing), missing[:6]))

moved_verts = 0
moved_weight = 0.0
for v in mesh.data.vertices:
    acc = {}
    for g in v.groups:
        acc[g.group] = acc.get(g.group, 0.0) + g.weight
    folded = {}
    touched = False
    for idx, w in acc.items():
        name = mesh.vertex_groups[idx].name
        tgt = plan.get(name)
        if tgt is not None:
            touched = True
            moved_weight += w
            folded[gi[tgt]] = folded.get(gi[tgt], 0.0) + w
        else:
            folded[idx] = folded.get(idx, 0.0) + w
    if not touched:
        continue
    moved_verts += 1
    tot = sum(folded.values())
    for idx in acc:
        mesh.vertex_groups[idx].remove([v.index])
    for idx, w in folded.items():
        if w > 1e-5:
            mesh.vertex_groups[idx].add([v.index], w / tot, 'REPLACE')

print('FOLDED %d vertices, %.1f weight units' % (moved_verts, moved_weight))

# Second pass: drop any weight whose bone is a long way from the vertex it is driving. reskin_to_existing_rig
# prunes at 25 cm, which is generous enough to leave a hand vertex following a hip bone - and a hip bone
# swinging 25 cm away from a hand drags that vertex into a needle spike several centimetres long. It is one
# or two vertices, it never shows in a weight count, and it is plainly visible in a side view.
PRUNE = float(os.environ.get('JC_PRUNE_M', '0.12'))


def seg_dist(p, a, b):
    ab = b - a
    L2 = ab.dot(ab)
    if L2 < 1e-12:
        return (p - a).length
    t = max(0.0, min(1.0, (p - a).dot(ab) / L2))
    return (p - (a + ab * t)).length


segs = {}
for b in arm.data.bones:
    segs[b.name] = (arm.matrix_world @ b.head_local, arm.matrix_world @ b.tail_local)
name_of = {g.index: g.name for g in mesh.vertex_groups}
pruned = 0
pruned_verts = 0
for v in mesh.data.vertices:
    p = mesh.matrix_world @ v.co
    keep = {}
    for g in v.groups:
        n = name_of[g.group]
        if n not in segs:
            continue
        if seg_dist(p, *segs[n]) <= PRUNE:
            keep[g.group] = keep.get(g.group, 0.0) + g.weight
        else:
            pruned += 1
    if len(keep) == len({g.group for g in v.groups}):
        continue
    pruned_verts += 1
    if not keep:
        near = min(segs, key=lambda n: seg_dist(p, *segs[n]))
        keep = {gi[near]: 1.0}
    tot = sum(keep.values())
    for idx in {g.group for g in v.groups}:
        mesh.vertex_groups[idx].remove([v.index])
    for idx, w in keep.items():
        if w > 1e-5:
            mesh.vertex_groups[idx].add([v.index], w / tot, 'REPLACE')
print('PRUNED %d weights over %.0f cm from their bone, on %d vertices' % (pruned, PRUNE * 100, pruned_verts))

# the finger groups are now empty; leave them in place so the bone list still matches the skeleton
unweighted = 0
for v in mesh.data.vertices:
    if sum(g.weight for g in v.groups) < 1e-4:
        unweighted += 1
print('VERIFY unweighted_verts=%d  groups=%d' % (unweighted, len(mesh.vertex_groups)))
if unweighted:
    raise SystemExit('REFUSING: %d vertices lost all weight' % unweighted)

arm.name = 'Armature'
arm.data.name = 'Armature'
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, add_leaf_bones=False, bake_anim=False,
                         mesh_smooth_type='FACE', path_mode='COPY', embed_textures=True)
print('EXPORTED ' + OUT)
