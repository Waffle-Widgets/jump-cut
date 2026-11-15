"""Blur the skin weights over the hands only, to take the spikes out of a curled fist.

    blender --background --python Art/Blender/smooth_hand_weights.py -- IN.fbx OUT.fbx [factor] [passes]

After conform_rest_pose.py + reskin_to_existing_rig.py the hand reads correctly at rest and 33 of 40 finger
bones drive real geometry - but curling every finger 55 degrees still threw a shard off the palm. That is the
signature of ISOLATED vertices: a weight transfer assigns per-vertex, so one vertex can come out bound hard to
a bone none of its neighbours touch, and it then flies off on its own when that bone turns. Nothing about the
weight table looks wrong; the vertex has a plausible weight to a plausible bone.

The fix is the oldest one in skinning: average each vertex's weights with its neighbours'. Restricted to the
hands, because the body was never the problem and blurring it would only soften joints that currently work.

Run reweight_verify.py afterwards. Smoothing trades a little articulation for smoothness, so if a finger bone
drops out of 'ok' this pass went too far - lower the factor rather than keeping it.
"""
import bpy, sys, os
from collections import defaultdict

argv = sys.argv[sys.argv.index("--") + 1:]
IN, OUT = argv[0], argv[1]
FACTOR = float(argv[2]) if len(argv) > 2 else 0.5
PASSES = int(argv[3]) if len(argv) > 3 else 3
WRIST = 0.10   # only vertices this far into the hand subtree are touched

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=IN)
mesh = next(o for o in bpy.data.objects if o.type == 'MESH')
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
arm.name = arm.data.name = 'Armature'      # see reskin_to_existing_rig.py - Unreal names the root bone after
mesh.name = 'Mesh0'                        # the armature OBJECT, and gets it wrong non-fatally.


def subtree(b):
    out = [b]
    for c in b.children:
        out += subtree(c)
    return out


hands = [b for b in arm.data.bones if len(b.children) == 5]
if len(hands) != 2:
    raise SystemExit("expected 2 bones with five children (the hands), found %d" % len(hands))
fam = set()
for h in hands:
    fam |= set(b.name for b in subtree(h))

idx2name = {g.index: g.name for g in mesh.vertex_groups}
name2grp = {g.name: g for g in mesh.vertex_groups}

W = [dict() for _ in mesh.data.vertices]
for v in mesh.data.vertices:
    for g in v.groups:
        if g.weight > 1e-6 and g.group in idx2name:
            W[v.index][idx2name[g.group]] = g.weight

region = [i for i, w in enumerate(W) if sum(x for n, x in w.items() if n in fam) > WRIST]
print("smoothing %d hand vertices, factor=%.2f passes=%d" % (len(region), FACTOR, PASSES))

adj = defaultdict(set)
for e in mesh.data.edges:
    a, b = e.vertices
    adj[a].add(b)
    adj[b].add(a)

inreg = set(region)
for p in range(PASSES):
    new = {}
    for i in region:
        nb = [j for j in adj[i] if j in inreg]
        if not nb:
            continue
        acc = defaultdict(float)
        for j in nb:
            for n, x in W[j].items():
                acc[n] += x
        blended = defaultdict(float)
        for n, x in W[i].items():
            blended[n] += (1 - FACTOR) * x
        for n, x in acc.items():
            blended[n] += FACTOR * x / len(nb)
        s = sum(blended.values())
        new[i] = {n: x / s for n, x in blended.items() if x / s > 1e-4}
    for i, w in new.items():
        W[i] = w

for i in region:
    for n in set(list(W[i].keys()) + [idx2name[g.group] for g in mesh.data.vertices[i].groups
                                      if g.group in idx2name]):
        g = name2grp.get(n) or mesh.vertex_groups.new(name=n)
        name2grp[n] = g
        if n in W[i]:
            g.add([i], W[i][n], 'REPLACE')
        else:
            g.remove([i])

unw = sum(1 for v in mesh.data.vertices if not any(g.weight > 1e-5 for g in v.groups))
print("VERIFY verts=%d groups=%d unweighted=%d" % (len(mesh.data.vertices), len(mesh.vertex_groups), unw))
if unw:
    raise SystemExit("refusing to export: %d vertices follow no bone" % unw)

bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
mesh.select_set(True)
bpy.context.view_layer.objects.active = arm
os.makedirs(os.path.dirname(OUT), exist_ok=True)
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, add_leaf_bones=False, bake_anim=False,
                         mesh_smooth_type='FACE', path_mode='COPY', embed_textures=True)
print("EXPORTED " + OUT)
