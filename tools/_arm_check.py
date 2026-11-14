"""Read-only. Does a retargeted clip put the arms where the mannequin's clip has them?

Evaluates the SOURCE clip on the mannequin and the retargeted clip on each Meshy character at the
same time, with AnimPoseExtensions (no actors, no PIE), then reports each arm in the character's
OWN body frame - so the comparison does not care which way the actor happens to be facing:

  * upper-arm and forearm direction as (lateral, forward, up), lateral +1 = the character's right
  * the bend at each joint, 0 = straight

The mannequin's numbers are the target. The test is whether the character's RIGHT arm matches the
mannequin's RIGHT arm. Before the side fix, the goon's right upper arm pointed backwards while the
mannequin's pointed out to the side, and the shoulder sat ~140 degrees from straight against the
mannequin's ~1.

Writes Saved/jcpy/arm_check.json.
"""
import json
import math
import os
import traceback

import unreal

TIME = 0.3
SRC_MESH = '/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple'
SRC_CLIP = '/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_01'

CASES = [
    ('Mannequin', SRC_MESH, SRC_CLIP),
    ('StreetGoon', '/Game/Game/Imported/StreetGoon/Meshy/SK_StreetGoon',
     '/Game/Game/Imported/StreetGoon/MeshyAnims/MM_Attack_01_SG'),
    ('CafeWalker', '/Game/Game/Imported/CafeWalker/Meshy/SK_CafeWalker',
     '/Game/Game/Imported/CafeWalker/MeshyAnims/MM_Attack_01_CWM'),
]

out = {}


def sub(a, b): return [a[i] - b[i] for i in range(3)]


def dot(a, b): return sum(a[i] * b[i] for i in range(3))


def ln(a): return math.sqrt(dot(a, a))


def nrm(a):
    m = ln(a)
    return [c / m for c in a] if m else list(a)


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def bend(p, q, r):
    """Degrees away from straight at q. 0 = the two segments are in line."""
    a, b = sub(p, q), sub(r, q)
    if not ln(a) or not ln(b):
        return None
    c = dot(a, b) / (ln(a) * ln(b))
    return round(180 - math.degrees(math.acos(max(-1.0, min(1.0, c)))), 1)


def hierarchy(mesh):
    """parent map + child map, from the reference pose off a throwaway actor."""
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    tmp = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, -7000),
                                     unreal.Rotator(0, 0, 0))
    tmp.set_actor_label('ZZ_ArmCheckProbe')
    c = tmp.skeletal_mesh_component
    c.set_skeletal_mesh_asset(mesh)
    names = [str(n) for n in c.get_all_socket_names()]
    par = {}
    for n in names:
        try:
            par[n] = str(c.get_parent_bone(unreal.Name(n)))
        except Exception:
            par[n] = 'None'
    eas.destroy_actor(tmp)
    kids = {}
    for n in names:
        kids.setdefault(par.get(n, 'None'), []).append(n)
    return names, par, kids


def posed(clip):
    opts = unreal.AnimPoseEvaluationOptions()
    opts.set_editor_property('extract_root_motion', True)
    pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(clip, TIME, opts)
    pos = {}
    for b in unreal.AnimPoseExtensions.get_bone_names(pose):
        t = unreal.AnimPoseExtensions.get_bone_pose(pose, b, unreal.AnimPoseSpaces.WORLD)
        v = t.translation
        pos[str(b)] = (v.x, v.y, v.z)
    return pos


def analyse(names, par, kids, pos):
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

    def subtree(b):
        n, stack = 0, list(kids.get(b, []))
        while stack:
            n += 1
            stack += kids.get(stack.pop(), [])
        return n

    # NOT kids[root][0]: the mannequin's root also carries ik_foot_root / interaction /
    # center_of_mass, and socket order decides which comes first. The pelvis is the big subtree.
    hip = max(kids.get(root, [root]), key=subtree)
    branches = kids.get(hip, [])
    height = max(p[2] for p in pos.values())
    spine_root = max(branches, key=tipz)
    # the two lowest-reaching branches off the hip are the legs. A height fraction is not safe
    # here: this is a POSED skeleton, and a clip that lifts a foot moves the threshold.
    legs = sorted([b for b in branches if b != spine_root], key=tipz)[:2]
    if len(legs) < 2:
        raise RuntimeError('hip %s has branches %s - cannot find two legs' % (hip, branches))
    spine = straight(spine_root)
    chest = spine[-1]
    off_chest = kids.get(chest, [])
    head_root = max(off_chest, key=tipz)
    arms = [b for b in off_chest if b != head_root]

    # body frame from the REFERENCE-pose facing is not available here (the clip has turned the
    # character), so take forward from the pelvis->chest up axis crossed with the hip line, which
    # a punch does not move: lateral = left leg -> right leg is unreliable mid-stride, but the two
    # leg ROOTS (the thighs) are rigid to the pelvis.
    up = nrm(sub(pos[chest], pos[hip]))
    thighs = [straight(b)[0] for b in legs]
    lat = nrm(sub(pos[thighs[0]], pos[thighs[1]]))
    lat = nrm([lat[i] - up[i] * dot(lat, up) for i in range(3)])
    fwd = nrm(cross(lat, up))
    # orient: the toe is in front of the ankle, so fix fwd's sign from a foot
    lc = straight(legs[0])
    ankle, toe = lc[max(0, len(lc) - 3)], lc[-1]
    if dot(sub(pos[toe], pos[ankle]), fwd) < 0:
        fwd = [-c for c in fwd]
    right = nrm(cross(up, fwd))

    def loc(a, b2):
        v = nrm(sub(pos[b2], pos[a]))
        return [round(dot(v, right), 2), round(dot(v, fwd), 2), round(dot(v, up), 2)]

    def find_hand(b):
        """The hand is the descendant with five branches (the fingers). Do NOT use straight():
        the mannequin's upperarm carries twist bones, so it stops two bones in."""
        stack = [b]
        while stack:
            n = stack.pop()
            if len(kids.get(n, [])) == 5:
                return n
            stack += kids.get(n, [])
        return None

    rows = []
    for b in arms:
        hand = find_hand(b)
        if hand is None:
            rows.append({'side': '?', 'error': 'no five-branch hand under ' + b})
            continue
        path = [hand]
        while path[0] != b:
            path.insert(0, par[path[0]])
        if len(path) < 4:
            rows.append({'side': '?', 'error': 'arm path too short: %s' % path})
            continue
        clav, upper, elbow = path[0], path[1], path[2]
        # Side from the UPPER ARM, not the hand: at t=0.3 of a punch the hand has crossed the
        # midline and both hands read as the same side.
        s = 'Right' if dot(sub(pos[upper], pos[hip]), right) > 0 else 'Left'
        rows.append({'side': s, 'path': path, 'bones': len(path),
                     'clavicle': clav, 'upperarm': upper, 'elbow': elbow, 'hand': hand,
                     'upperarm_dir': loc(upper, elbow),
                     'forearm_dir': loc(elbow, hand),
                     'shoulder_bend': bend(pos[clav], pos[upper], pos[elbow]),
                     'elbow_bend': bend(pos[upper], pos[elbow], pos[hand]),
                     'upperarm_cm': round(ln(sub(pos[elbow], pos[upper])), 1),
                     'forearm_cm': round(ln(sub(pos[hand], pos[elbow])), 1)})
    rows.sort(key=lambda r: r['side'])
    return rows


try:
    for label, meshp, clipp in CASES:
        mesh, clip = unreal.load_asset(meshp), unreal.load_asset(clipp)
        if mesh is None or clip is None:
            out[label] = {'error': 'missing mesh=%s clip=%s' % (mesh is None, clip is None)}
            continue
        names, par, kids = hierarchy(mesh)
        pos = posed(clip)
        # get_all_socket_names() returns sockets as well as bones; the pose only has bones, so
        # drop anything the pose does not carry or every lookup below is a KeyError.
        missing = [n for n in names if n not in pos]
        names = [n for n in names if n in pos]
        kids = {k: [c for c in v if c in pos] for k, v in kids.items() if k in pos or k == 'None'}
        out[label] = {'clip': clipp, 'time': TIME, 'bones_posed': len(pos),
                      'bones_missing_from_pose': len(missing), 'arms': analyse(names, par, kids, pos)}
except Exception:
    out['ERROR'] = traceback.format_exc()

d = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy')
if not os.path.isdir(d):
    os.makedirs(d)
with open(os.path.join(d, 'arm_check.json'), 'w') as fh:
    json.dump(out, fh, indent=1)
unreal.log('ARM-CHECK wrote arm_check.json')
