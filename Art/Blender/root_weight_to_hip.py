"""Move every vertex weight on a Meshy Smart Rig's ROOT bone onto its hip bone. Nothing else changes.

    blender -b --factory-startup --python Art/Blender/root_weight_to_hip.py -- fix    IN.fbx OUT.fbx
    blender -b --factory-startup --python Art/Blender/root_weight_to_hip.py -- verify BEFORE.fbx AFTER.fbx

WHY (Sat Nov 14, GameStation, Blender 5.3.0). The player's new body (SK_CafeWalkerV2) showed long streaks of apron
dragged from the waist tie down to a point on the floor between his feet. Cause: on these rigs the root, Bone_000,
sits at PELVIS height in the rest pose (90.6 cm), but every retargeted clip animates it on the FLOOR, with the hip
bone Bone_001 carrying the pelvis back up. So any vertex weighted to Bone_000 is pulled toward the floor by
(its root weight) x 90 cm. The first body had the same flaw in a mild form (181 vertices, none above 0.29, a 26 cm
pull hidden inside its skirt-shaped apron). The re-skin made it loud: where the new flat apron had no matching
surface on the old body, reskin_to_existing_rig.py's fallback gives a vertex wholly to the bone it is nearest, and
at the front of the waist the nearest bone IS the root. Result: 296 vertices above 0.2, 12 above 0.8.

Bone_001 is Bone_000's only child and starts at the same place, and it is the bone that stays at the pelvis in
every clip, so handing it the root's weight keeps the rest shape exactly and removes the pull.

'verify' proves the fix changed weights and nothing else: same vertices in the same places, same UVs, same bones in
the same rest pose, same material and texture, zero weight left on the root, every vertex still summing to 1.
"""
import bpy, sys, os, json

argv = sys.argv[sys.argv.index('--') + 1:]
MODE, A, B = argv[0], argv[1], argv[2]
ROOT, HIP = 'Bone_000', 'Bone_001'


def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path)
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]
    return arm, mesh


def snapshot(path):
    arm, mesh = load(path)
    gi = {g.index: g.name for g in mesh.vertex_groups}
    root_tot, root_n, bad_sum, non_root = 0.0, 0, 0, []
    for v in mesh.data.vertices:
        ws = {gi[g.group]: g.weight for g in v.groups if g.weight > 1e-6}
        if abs(sum(ws.values()) - 1.0) > 0.02:
            bad_sum += 1
        if ws.get(ROOT, 0.0) > 1e-4:
            root_n += 1
            root_tot += ws[ROOT]
        # everything except root and hip must be untouched; root + hip together must be untouched
        rest = {k: round(w, 4) for k, w in ws.items() if k not in (ROOT, HIP)}
        non_root.append((rest, round(ws.get(ROOT, 0.0) + ws.get(HIP, 0.0), 4)))
    uv = mesh.data.uv_layers[0].data
    return {
        'verts': [tuple(mesh.matrix_world @ v.co) for v in mesh.data.vertices],
        'polys': len(mesh.data.polygons),
        'uvs': [tuple(l.uv) for l in uv],
        'bones': {b.name: [tuple(r) for r in (arm.matrix_world @ b.matrix_local)] for b in arm.data.bones},
        'parents': {b.name: (b.parent.name if b.parent else None) for b in arm.data.bones},
        'arm_name': arm.name, 'mesh_name': mesh.name,
        'mats': [s.material.name if s.material else None for s in mesh.material_slots],
        'images': sorted((i.name, tuple(i.size)) for i in bpy.data.images),
        'root_n': root_n, 'root_tot': root_tot, 'bad_sum': bad_sum, 'non_root': non_root,
    }


if MODE == 'fix':
    arm, mesh = load(A)
    root_g, hip_g = mesh.vertex_groups.get(ROOT), mesh.vertex_groups.get(HIP)
    if root_g is None or hip_g is None:
        raise SystemExit('REFUSING: %s or %s is not a vertex group on this mesh' % (ROOT, HIP))
    b0, b1 = arm.data.bones[ROOT], arm.data.bones[HIP]
    if b1.parent != b0 or len(b0.children) != 1 or (b1.head_local - b0.head_local).length > 0.05 / arm.scale.x:
        raise SystemExit('REFUSING: %s is not the single child of %s starting near it' % (HIP, ROOT))
    moved, total = 0, 0.0
    for v in mesh.data.vertices:
        w0 = next((g.weight for g in v.groups if g.group == root_g.index), 0.0)
        if w0 <= 0.0:
            continue
        hip_g.add([v.index], w0, 'ADD')
        root_g.remove([v.index])
        moved += 1
        total += w0
    print('FIX moved root weight on %d vertices (total %.1f) from %s to %s' % (moved, total, ROOT, HIP))
    # Same export call as rebuild_walker_v2.py, which made the file this reads. The armature and mesh keep the
    # names they were imported with: Unreal takes the armature OBJECT's name as the root bone (PR #112).
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.export_scene.fbx(filepath=B, use_selection=True, add_leaf_bones=False, bake_anim=False,
                             mesh_smooth_type='FACE', path_mode='COPY', embed_textures=True)
    print('FIX exported %s  (armature "%s", mesh "%s")' % (B, arm.name, mesh.name))

elif MODE == 'verify':
    a, b = snapshot(A), snapshot(B)
    R = {'blender': bpy.app.version_string}
    R['verts'] = [len(a['verts']), len(b['verts'])]
    R['polys'] = [a['polys'], b['polys']]
    same_n = len(a['verts']) == len(b['verts'])
    R['max_vertex_move_cm'] = max(sum((p - q) ** 2 for p, q in zip(x, y)) ** 0.5 for x, y in zip(a['verts'], b['verts'])) * 100 if same_n else None
    R['max_uv_move'] = max(max(abs(p - q) for p, q in zip(x, y)) for x, y in zip(a['uvs'], b['uvs'])) if len(a['uvs']) == len(b['uvs']) else None
    R['bones'] = [len(a['bones']), len(b['bones'])]
    R['bone_names_and_parents_same'] = a['parents'] == b['parents']
    R['max_rest_matrix_diff'] = max(max(abs(p - q) for ra, rb in zip(a['bones'][n], b['bones'][n]) for p, q in zip(ra, rb)) for n in a['bones']) if a['parents'] == b['parents'] else None
    R['names'] = [[a['arm_name'], a['mesh_name']], [b['arm_name'], b['mesh_name']]]
    R['materials'] = [a['mats'], b['mats']]
    R['images'] = [a['images'], b['images']]
    R['root_weighted_verts'] = [a['root_n'], b['root_n']]
    R['root_weight_total'] = [round(a['root_tot'], 2), round(b['root_tot'], 2)]
    R['verts_not_summing_to_1'] = [a['bad_sum'], b['bad_sum']]
    R['verts_whose_other_weights_changed'] = sum(1 for x, y in zip(a['non_root'], b['non_root'])
                                                 if x[0] != y[0] or abs(x[1] - y[1]) > 0.002) if same_n else None
    ok = (same_n and R['polys'][0] == R['polys'][1] and R['max_vertex_move_cm'] < 0.01 and R['max_uv_move'] is not None
          and R['max_uv_move'] < 1e-5 and R['bone_names_and_parents_same'] and R['max_rest_matrix_diff'] < 1e-4
          and R['names'][0] == R['names'][1] and R['materials'][0] == R['materials'][1] and R['images'][0] == R['images'][1]
          and b['root_n'] == 0 and b['bad_sum'] == 0 and R['verts_whose_other_weights_changed'] == 0)
    R['ok'] = ok
    print('VERIFY ' + json.dumps(R, indent=1))
    if not ok:
        raise SystemExit('VERIFY FAILED')
else:
    raise SystemExit('mode must be fix or verify')
