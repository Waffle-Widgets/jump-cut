"""Smooth a skinned body's vertex weights along the surface, so neighbouring vertices follow nearly the same bones.

    blender -b --factory-startup --python Art/Blender/smooth_weights.py -- IN.fbx OUT.fbx [ITERS=12] [FACTOR=0.5] [KEEP=8]

WHY (Sun Nov 15, GameStation, Blender 5.3.0). The player's V2 body got its weights by projecting them from another
mesh. Where that body has layers of cloth a few millimetres apart (apron panel, waist tie, towel) or thin parts
(fingers, the rolled sleeve), next-door vertices came away with very different bones. In the rest pose nothing shows.
The moment he is posed like a person - arms down, feet together - the skin tears: 1,581 edges stretched to more than
2.5 times their length, the longest 31 cm, a flap of forearm left hanging at the hip, fingertips in shards.

A tear is exactly two connected vertices that disagree about who moves them. So average each vertex's weights with
its neighbours', ITERS times: weights become a smooth field over the surface and connected vertices cannot disagree
much. Geometry, UVs, rig and texture are untouched; root_weight_to_hip.py's `verify` mode checks that (its "other
weights changed" line is expected to fail here, everything else must pass).

Bone_000, the root, must stay at zero weight (see root_weight_to_hip.py): it is zero going in and an average of
zeros is zero, and this script refuses to export if that is not so.
"""
import bpy, sys, os
import numpy as np

argv = sys.argv[sys.argv.index('--') + 1:]
IN, OUT = argv[0], argv[1]
ITERS = int(argv[2]) if len(argv) > 2 else 12
FACTOR = float(argv[3]) if len(argv) > 3 else 0.5
KEEP = int(argv[4]) if len(argv) > 4 else 8

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=IN)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]
me = mesh.data
nv, ng = len(me.vertices), len(mesh.vertex_groups)
names = [g.name for g in mesh.vertex_groups]

Wt = np.zeros((nv, ng), np.float64)
for v in me.vertices:
    for g in v.groups:
        Wt[v.index, g.group] = g.weight
Wt /= np.maximum(Wt.sum(1, keepdims=True), 1e-12)
before = Wt.copy()

E = np.array([e.vertices[:] for e in me.edges], np.int64)
deg = np.bincount(E.ravel(), minlength=nv).astype(np.float64)
for _ in range(ITERS):
    acc = np.zeros_like(Wt)
    np.add.at(acc, E[:, 0], Wt[E[:, 1]])
    np.add.at(acc, E[:, 1], Wt[E[:, 0]])
    avg = acc / np.maximum(deg, 1.0)[:, None]
    has = (deg > 0)[:, None]
    Wt = np.where(has, (1.0 - FACTOR) * Wt + FACTOR * avg, Wt)

# keep each vertex's strongest KEEP bones (Unreal's default limit is 8), then renormalise
if KEEP < ng:
    cut = np.partition(Wt, ng - KEEP, axis=1)[:, ng - KEEP][:, None]
    Wt = np.where(Wt >= cut, Wt, 0.0)
Wt[Wt < 1e-4] = 0.0
Wt /= np.maximum(Wt.sum(1, keepdims=True), 1e-12)

root = names.index('Bone_000') if 'Bone_000' in names else None
root_w = float(Wt[:, root].sum()) if root is not None else 0.0
print('SMOOTH %d verts, %d groups, %d iterations at %.2f; mean |change| per vertex %.4f, max %.3f; influences per vertex max %d; root weight %.4f'
      % (nv, ng, ITERS, FACTOR, float(np.abs(Wt - before).sum(1).mean()), float(np.abs(Wt - before).sum(1).max()),
         int((Wt > 0).sum(1).max()), root_w))
if root_w > 1e-6:
    raise SystemExit('REFUSING: weight on the root bone after smoothing')

for g in mesh.vertex_groups:
    g.remove(list(range(nv)))
groups = list(mesh.vertex_groups)
nz = np.argwhere(Wt > 0)
for vi, gi in nz:
    groups[gi].add([int(vi)], float(Wt[vi, gi]), 'REPLACE')

bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, add_leaf_bones=False, bake_anim=False,
                         mesh_smooth_type='FACE', path_mode='COPY', embed_textures=True)
print('SMOOTH exported %s' % OUT)
