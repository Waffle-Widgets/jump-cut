"""Pose every finger bone on its own and measure how far the mesh ACTUALLY moves.

    blender --background --python Art/Blender/reweight_verify.py -- A.fbx [B.fbx ...]

A weight table can say a bone has vertices and the bone can still move nothing visible. jump-cut #96 was
reported as "18 of 21 finger bones carry weight", which was true and useless: most of those carried a handful
of vertices. So this measures displacement, in centimetres, from the evaluated (skinned) mesh - the only
number that answers "can an animator see this bone move".
"""
import bpy, sys, math
from mathutils import Euler

argv = sys.argv[sys.argv.index("--")+1:]

def subtree(b):
    out=[b]
    for c in b.children: out+=subtree(c)
    return out

def evaluated(mesh):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh.evaluated_get(dg)
    m  = ev.to_mesh()
    pts = [mesh.matrix_world @ v.co.copy() for v in m.vertices]
    ev.to_mesh_clear()
    return pts

for path in argv:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path)
    mesh = next(o for o in bpy.data.objects if o.type=='MESH')
    arm  = next(o for o in bpy.data.objects if o.type=='ARMATURE')
    bones = arm.data.bones
    hands = [b for b in bones if len(b.children)==5]

    idx2name = {g.index: g.name for g in mesh.vertex_groups}
    counts = {}
    for v in mesh.data.vertices:
        for g in v.groups:
            if g.weight > 1e-6:
                n = idx2name.get(g.group)
                if n: counts[n] = counts.get(n,0)+1

    base = evaluated(mesh)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='POSE')

    print("\n################ %s ################" % path)
    dead=[]; weak=[]; ok=[]
    for hand in hands:
        fingers = [b for b in subtree(hand) if b is not hand]
        print("-- hand %s (%d finger bones)" % (hand.name, len(fingers)))
        for b in fingers:
            pb = arm.pose.bones[b.name]
            pb.rotation_mode='XYZ'
            pb.rotation_euler = Euler((math.radians(60),0,0),'XYZ')
            bpy.context.view_layer.update()
            pts = evaluated(mesh)
            d = [ (pts[i]-base[i]).length*100 for i in range(len(base)) ]
            mx = max(d); moved = sum(1 for x in d if x > 0.1)
            pb.rotation_euler = Euler((0,0,0),'XYZ')
            bpy.context.view_layer.update()
            tag = "DEAD" if mx < 0.1 else ("weak" if mx < 1.0 else "ok")
            (dead if tag=="DEAD" else weak if tag=="weak" else ok).append(b.name)
            print("   %-12s verts=%-6s max_move=%7.2f cm  verts_moved=%-6d %s"
                  % (b.name, counts.get(b.name,0), mx, moved, tag))
    # whole-hand regression guard
    for hand in hands:
        pb = arm.pose.bones[hand.name]; pb.rotation_mode='XYZ'
        pb.rotation_euler = Euler((math.radians(60),0,0),'XYZ')
        bpy.context.view_layer.update()
        pts = evaluated(mesh)
        d = [(pts[i]-base[i]).length*100 for i in range(len(base))]
        print("   WHOLE HAND %-10s max_move=%7.2f cm  verts>20cm=%d" % (hand.name, max(d), sum(1 for x in d if x>20)))
        pb.rotation_euler = Euler((0,0,0),'XYZ'); bpy.context.view_layer.update()
    bpy.ops.object.mode_set(mode='OBJECT')
    print("SUMMARY %s : finger bones  ok(>1cm)=%d  weak(0.1-1cm)=%d  DEAD(<0.1cm)=%d" % (path, len(ok), len(weak), len(dead)))
    if dead: print("  DEAD: %s" % ", ".join(dead))
