"""Put a NEW mesh onto an EXISTING character's skeleton, keeping every clip that skeleton already drives.

    blender --background --python Art/Blender/reskin_to_existing_rig.py -- OLD.fbx NEW.fbx OUT.fbx

WHY THIS EXISTS. Meshy's current Humanoid rig is 28 bones with no finger chains (jump-cut #96), while our
shipped characters are on 69-bone rigs with a 21-bone five-finger subtree per hand - and every clip, montage,
blend space and ABP_Unarmed_CWM in the game is built against those. Re-rigging a remade character would mean
re-retargeting all of it, which is exactly what #69 and #71 have only just finished stabilising. So instead:
keep the old skeleton, move the new mesh onto it.

It only works when the two meshes are the same character in the same pose at the same scale. Check that first
(both CafeWalker meshes: 1.750 m tall, feet at z=0, A-pose, arm span within 3 cm) - this is not a retargeter
and it will happily produce nonsense from two different poses.

THREE PASSES, because no single one of them is enough:

  1. POLYINTERP_VNORPROJ. Projects along vertex normals, so it follows the surface and keeps fine structure -
     18 of 20 finger bones survive it. But it misses wherever the two silhouettes differ (the new apron is a
     front panel where the old one wrapped the legs), leaving ~2,700 vertices with no weight at all.
     The plain proximity modes are the opposite trade: NEAREST, POLYINTERP_NEAREST and EDGEINTERP_NEAREST each
     cover every vertex and each collapse the fingers to 4 bones, because the two A-poses put the hands a few
     centimetres apart and a finger is about one centimetre thick. Measured, all three, same answer.

  2. KD-tree fallback. Fill every vertex pass 1 missed from its nearest source vertex.

  3. Prune by distance. Pass 2 copies a source vertex's WHOLE weight set, so a target vertex can inherit a
     weight to a bone nowhere near it. One vertex at shoe height came out driven by a hand bone 82 cm above
     it and swung 83 cm when that hand turned - one vertex, and it would have been a visible spike. So drop
     any weight whose bone segment is more than MAXD from the vertex's rest position, and for a vertex whose
     weights are ALL distant, give it wholly to the bone it is actually nearest.

HOW TO KNOW IT WORKED. Do not trust "it exported". Pose one hand bone 60 degrees and measure how far the mesh
moves, against the same test on the model you are replacing:

                              shipped      naive NEAREST    this script
    max displacement          15.5 cm      83.3 cm          14.1 cm
    verts moving > 20 cm      0            1                0
    unweighted vertices       -            0                0
    finger bones with weights 21 + 21      4 + 4            13 + 13

Thirteen of twenty-one is worse than the twenty-one we had: the hand is coarser than the shipped one and some
finger joints carry no vertices. That is a real cost and it is the honest reason this is a trade, not a win.
"""

import bpy, sys, os, mathutils
from mathutils.kdtree import KDTree

argv = sys.argv[sys.argv.index("--")+1:]
OLD, NEW, OUT = argv[0], argv[1], argv[2]
bpy.ops.wm.read_factory_settings(use_empty=True)

def imp(path, tag):
    before=set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=path)
    added=[o for o in bpy.data.objects if o not in before]
    for o in added: o.name = tag+'_'+o.name
    return added

old=imp(OLD,'OLD'); new=imp(NEW,'NEW')
old_mesh=next(o for o in old if o.type=='MESH'); old_arm=next(o for o in old if o.type=='ARMATURE')
new_mesh=next(o for o in new if o.type=='MESH')
for a in [o for o in new if o.type=='ARMATURE']: bpy.data.objects.remove(a, do_unlink=True)
for m in list(new_mesh.modifiers):
    if m.type=='ARMATURE': new_mesh.modifiers.remove(m)
new_mesh.vertex_groups.clear(); new_mesh.parent=None

bpy.ops.object.select_all(action='DESELECT')
new_mesh.select_set(True); old_mesh.select_set(True)
bpy.context.view_layer.objects.active = old_mesh
bpy.ops.object.data_transfer(use_reverse_transfer=False, data_type='VGROUP_WEIGHTS', use_create=True,
                             vert_mapping='POLYINTERP_VNORPROJ', layers_select_src='ALL',
                             layers_select_dst='NAME', mix_mode='REPLACE', ray_radius=0.05)

missing=[v.index for v in new_mesh.data.vertices if not any(g.weight>1e-5 for g in v.groups)]
print(f"after projection: groups={len(new_mesh.vertex_groups)} unweighted={len(missing)}")

# --- KD-tree fallback: fill each missed vertex from its nearest SOURCE vertex -------------------------
kd=KDTree(len(old_mesh.data.vertices))
for i,v in enumerate(old_mesh.data.vertices):
    kd.insert(old_mesh.matrix_world @ v.co, i)
kd.balance()
src_names={g.index:g.name for g in old_mesh.vertex_groups}
dst={g.name:g for g in new_mesh.vertex_groups}
filled=0
for vi in missing:
    co = new_mesh.matrix_world @ new_mesh.data.vertices[vi].co
    _,si,_ = kd.find(co)
    for g in old_mesh.data.vertices[si].groups:
        if g.weight<=1e-5: continue
        nm=src_names[g.group]
        grp = dst.get(nm) or new_mesh.vertex_groups.new(name=nm)
        dst[nm]=grp
        grp.add([vi], g.weight, 'REPLACE')
    filled+=1
print(f"fallback filled {filled} vertices from nearest source vertex")

# --- prune implausible weights ------------------------------------------------------------------------
# The KD-tree fallback copies a source vertex's WHOLE weight set, so a target vertex can inherit a weight to a
# bone nowhere near it. One vertex at shoe height came out weighted to a hand bone 82 cm above it and swung
# 83 cm when the hand turned. A vertex can only sensibly be driven by a bone it is near, so: drop any weight
# whose bone segment is further than MAXD from the vertex's REST position, and never leave a vertex with none.
MAXD = 0.25
def seg_dist(p, a, b):
    ab = b - a
    L2 = ab.dot(ab)
    if L2 < 1e-12: return (p - a).length
    t = max(0.0, min(1.0, (p - a).dot(ab) / L2))
    return (p - (a + ab * t)).length

bone_seg = {}
for bn in old_arm.data.bones:
    bone_seg[bn.name] = (old_arm.matrix_world @ bn.head_local, old_arm.matrix_world @ bn.tail_local)
gname = {g.index: g.name for g in new_mesh.vertex_groups}
pruned = 0
reseated = 0
for v in new_mesh.data.vertices:
    co = new_mesh.matrix_world @ v.co
    ws = [(g.group, g.weight) for g in v.groups if g.weight > 1e-5]
    if not ws: continue
    keep, drop = [], []
    for gi, w in ws:
        seg = bone_seg.get(gname.get(gi))
        if seg and seg_dist(co, seg[0], seg[1]) > MAXD: drop.append((gi, w))
        else: keep.append((gi, w))
    if drop and keep:
        for gi, _ in drop:
            new_mesh.vertex_groups[gname[gi]].remove([v.index]); pruned += 1
    elif drop and not keep:
        # EVERY weight this vertex has is to a distant bone - the fallback copied a whole weight set from a
        # source vertex somewhere else entirely. Give it wholly to the bone it is actually nearest.
        best = min(bone_seg.items(), key=lambda kv: seg_dist(co, kv[1][0], kv[1][1]))[0]
        for gi, _ in drop:
            new_mesh.vertex_groups[gname[gi]].remove([v.index]); pruned += 1
        grp = new_mesh.vertex_groups.get(best) or new_mesh.vertex_groups.new(name=best)
        grp.add([v.index], 1.0, 'REPLACE')
        reseated += 1
print(f"pruned {pruned} weights further than {MAXD*100:.0f} cm from their bone; "
      f"reseated {reseated} vertices that had no nearby bone at all")

mod=new_mesh.modifiers.new(name='Armature', type='ARMATURE'); mod.object=old_arm
new_mesh.parent=old_arm; new_mesh.matrix_parent_inverse=old_arm.matrix_world.inverted()
bpy.ops.object.select_all(action='DESELECT'); new_mesh.select_set(True)
bpy.context.view_layer.objects.active=new_mesh
bpy.ops.object.vertex_group_normalize_all(lock_active=False)

unw=sum(1 for v in new_mesh.data.vertices if not any(g.weight>1e-5 for g in v.groups))
nonempty=sum(1 for g in new_mesh.vertex_groups
             if any(gg.group==g.index and gg.weight>1e-5 for v in new_mesh.data.vertices for gg in v.groups))
print(f"VERIFY groups={len(new_mesh.vertex_groups)} unweighted_verts={unw}")

bpy.data.objects.remove(old_mesh, do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
old_arm.select_set(True); new_mesh.select_set(True)
bpy.context.view_layer.objects.active=old_arm
os.makedirs(os.path.dirname(OUT), exist_ok=True)
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, add_leaf_bones=False, bake_anim=False,
                         mesh_smooth_type='FACE', path_mode='COPY', embed_textures=True)
print("EXPORTED "+OUT)
