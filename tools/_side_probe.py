"""Read-only. Does unreal_retarget_meshy.py's side() label the Meshy rigs' limbs correctly?

Rebuilds the chains the same way the tool does, off the REFERENCE pose (a posed skeleton
cannot answer this - at t=0.3 of a punch both hands are on the same side of the midline).
Then works the true side out independently:

    forward = toe - ankle           (the tool's own facing rule)
    up      = spine - hip
    right   = up x forward          (validated 6/6 against the mannequin's own _l/_r bone
                                     names in Saved/jcpy/arm_probe.json)

and prints the tool's label beside the truth for every arm and leg chain.

Writes Saved/jcpy/side_probe.json. Touches nothing.
"""
import json
import math
import os
import traceback

import unreal

MESHES = [
    ('CafeWalker', '/Game/Game/Imported/CafeWalker/Meshy/SK_CafeWalker'),
    ('StreetGoon', '/Game/Game/Imported/StreetGoon/Meshy/SK_StreetGoon'),
]

out = {}


def sub(a, b): return [a[i] - b[i] for i in range(3)]


def dot(a, b): return sum(a[i] * b[i] for i in range(3))


def nrm(a):
    m = math.sqrt(dot(a, a))
    return [c / m for c in a] if m else list(a)


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def read_skeleton(mesh):
    """Same helper the tool uses: reference pose read off a throwaway unrotated actor."""
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    tmp = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, -6000),
                                     unreal.Rotator(0, 0, 0))
    tmp.set_actor_label('ZZ_SideProbe')
    c = tmp.skeletal_mesh_component
    c.set_skeletal_mesh_asset(mesh)
    names = [str(n) for n in c.get_all_socket_names()]
    pos, par = {}, {}
    for n in names:
        p = c.get_socket_location(unreal.Name(n))
        pos[n] = (p.x, p.y, p.z + 6000.0)
        try:
            par[n] = str(c.get_parent_bone(unreal.Name(n)))
        except Exception:
            par[n] = 'None'
    eas.destroy_actor(tmp)
    return names, par, pos


def analyse(names, par, pos):
    kids = {}
    for n in names:
        kids.setdefault(par.get(n, 'None'), []).append(n)
    height = max(p[2] for p in pos.values())
    root = [n for n in names if par.get(n, 'None') in ('None', '')][0]

    def straight(b):
        ch = [b]
        while len(kids.get(ch[-1], [])) == 1:
            ch.append(kids[ch[-1]][0])
        return ch

    def tipz(b):
        tip = straight(b)[-1]
        best, stack = pos[tip][2], list(kids.get(tip, []))
        while stack:
            n = stack.pop()
            best = max(best, pos[n][2])
            stack += kids.get(n, [])
        return best

    hip = kids.get(root, [root])[0]
    branches = kids.get(hip, [])
    spine_root = max(branches, key=tipz)
    legs = [b for b in branches if b != spine_root and tipz(b) < 0.25 * height]
    spine = straight(spine_root)
    chest = spine[-1]
    off_chest = kids.get(chest, [])
    head_root = max(off_chest, key=tipz)
    arms = [b for b in off_chest if b != head_root]

    # --- the tool's rule, copied verbatim -------------------------------------------------
    leg_chain = straight(legs[0])
    ankle, toe = leg_chain[max(0, len(leg_chain) - 3)], leg_chain[-1]
    faces_plus_y = (pos[toe][1] - pos[ankle][1]) > 0
    right_sign = 1.0 if faces_plus_y else -1.0
    hip_x = pos[hip][0]

    def tool_side(chain):
        return 'Right' if (pos[chain[-1]][0] - hip_x) * right_sign > 0 else 'Left'

    # --- the independent answer ------------------------------------------------------------
    UP = nrm(sub(pos[spine[-1]], pos[hip]))
    f = nrm(sub(pos[toe], pos[ankle]))
    FWD = nrm([f[i] - UP[i] * dot(f, UP) for i in range(3)])
    RIGHT = nrm(cross(UP, FWD))

    def truth(chain):
        d = dot(sub(pos[chain[-1]], pos[hip]), RIGHT)
        return ('Right' if d > 0 else 'Left'), round(d, 2)

    rows = []
    for kind, starts in (('arm', arms), ('leg', legs)):
        for b in starts:
            ch = straight(b)
            t, d = truth(ch)
            rows.append({'kind': kind, 'start': ch[0], 'tip': ch[-1], 'len': len(ch),
                         'tool': tool_side(ch), 'truth': t, 'dot_right': d,
                         'tip_dx': round(pos[ch[-1]][0] - hip_x, 2),
                         'chain': ch})
    return {'root': root, 'hip': hip, 'height': round(height, 2),
            'faces_plus_y': faces_plus_y, 'right_sign': right_sign,
            'ankle': ankle, 'toe': toe,
            'axis_up': [round(c, 3) for c in UP], 'axis_fwd': [round(c, 3) for c in FWD],
            'axis_right': [round(c, 3) for c in RIGHT],
            'rows': rows,
            'agree': all(r['tool'] == r['truth'] for r in rows),
            'all_flipped': all(r['tool'] != r['truth'] for r in rows)}


def rig_chains(path):
    """What the IK rig asset on disk actually declares, and the mannequin's source chain sizes."""
    rig = unreal.load_asset(path)
    if rig is None:
        return {'missing': path}
    c = unreal.IKRigController.get_controller(rig)
    res = []
    for ch in c.get_retarget_chains():
        res.append({'name': str(ch.chain_name), 'start': str(ch.start_bone.bone_name),
                    'end': str(ch.end_bone.bone_name)})
    return res


try:
    for label, path in MESHES:
        mesh = unreal.load_asset(path)
        if mesh is None:
            out[label] = {'error': 'mesh not found: ' + path}
            continue
        names, par, pos = read_skeleton(mesh)
        out[label] = analyse(names, par, pos)
        out[label]['bones'] = len(names)
    out['ik_SK_CafeWalker'] = rig_chains('/Game/Game/Imported/CafeWalker/MeshyAnims/IK_SK_CafeWalker')
    out['ik_SK_StreetGoon'] = rig_chains('/Game/Game/Imported/StreetGoon/MeshyAnims/IK_SK_StreetGoon')
    out['ik_Mannequin_Src'] = rig_chains('/Game/Game/Imported/StreetGoon/MeshyAnims/IK_Mannequin_Src')
except Exception:
    out['ERROR'] = traceback.format_exc()

d = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy')
if not os.path.isdir(d):
    os.makedirs(d)
with open(os.path.join(d, 'side_probe.json'), 'w') as fh:
    json.dump(out, fh, indent=1)
unreal.log('SIDE-PROBE wrote side_probe.json')
