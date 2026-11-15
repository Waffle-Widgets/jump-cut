"""How far is each rig's REST pose from the 69-bone rig the 48 clips are keyed against?

    blender -b -noaudio --python rest_delta.py -- ORIG69.fbx A.fbx B.fbx ...

Unreal's anim tracks are absolute-local: playback puts the bone where the clip says, whatever the mesh was
bound in. So the deformation a clip applies to a mesh is (clip pose) * (bind)^-1. If the bind rest differs
from the rest the clip was authored against, every frame carries that difference as extra twist.
"""
import bpy, sys, os, math

argv = sys.argv[sys.argv.index("--") + 1:]
REF, TESTS = argv[0], argv[1:]


def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path)
    arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    out = {}
    for b in arm.data.bones:
        out[b.name] = b.matrix_local.copy()   # armature-space rest
    return out


ref = load(REF)
print('REF %s bones=%d' % (os.path.basename(REF), len(ref)))
for t in TESTS:
    cur = load(t)
    rows = []
    for n, m in cur.items():
        if n not in ref:
            continue
        d = (ref[n].to_quaternion().inverted() @ m.to_quaternion())
        ang = math.degrees(d.angle)
        if ang > 180:
            ang = 360 - ang
        pos = (ref[n].to_translation() - m.to_translation()).length
        rows.append((ang, pos * 100.0, n))
    rows.sort(reverse=True)
    angs = [r[0] for r in rows]
    print('\n== %s : %d shared bones' % (os.path.basename(t), len(rows)))
    print('   rest ROTATION vs the clip rig:  mean %.1f deg   max %.1f deg   over 20deg: %d'
          % (sum(angs) / len(angs), max(angs), sum(1 for a in angs if a > 20)))
    print('   worst: ' + ', '.join('%s %.0fdeg/%.1fcm' % (n, a, p) for a, p, n in rows[:8]))
