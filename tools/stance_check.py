"""Read-only. How far is a retargeted clip's STANCE from the mannequin's?

Issue #73: the player's walk reads as a wide, stooped, toes-out waddle. `tools/_arm_check.py`
measured the arms only, on one attack frame, which is why the ticket's leg and spine claims were
read off thumbnails instead of measured. This measures the whole stance, on any clip, and - the
part that actually tests the ticket's root cause - it measures each rig's REFERENCE POSE too.

Every number is scale-free (an angle, or a length divided by that rig's own leg length), so a
1.8 m mannequin and a Meshy character of any height compare directly.

  * stance_width   ankle-to-ankle lateral separation / leg length.
  * toe_out_deg    per foot, degrees the foot points away from the body's forward. + = outward.
  * stagger        ankle-to-ankle fore/aft separation / leg length (a staggered rest pose is > 0).
  * spine_lean_deg angle of pelvis->chest away from straight up.
  * head_drop_deg  angle of neck->head away from straight up.
  * clav_fwd       how far each shoulder leads the chest, forward component, unit. + = rolled.
  * arm_out_deg    upper arm's angle away from hanging straight down.
  * elbow_bend_deg 0 = a straight arm. The mannequin's clips keep this well off 0.

Bone roles are found by TOPOLOGY, not by name, because a Meshy Smart Rig names every bone
`Bone_000`. Limb paths follow the child with the DEEPEST subtree at each step: the mannequin's
thigh and upperarm both carry twist bones, so `straight()` (which `_arm_check.py` uses) stops one
bone in and reports the thigh itself as the ankle. That is why this script does not reuse it for
limbs - only for the spine, which has no twist branches.

Run in the editor console box (Cmd), Play stopped:
    py <repo>/tools/stance_check.py [clip_basename] [ref|posed|both] [mesh,folder,suffix,label ...]
    py <repo>/tools/stance_check.py MF_Unarmed_Walk_Fwd both

Writes Saved/jcpy/stance_check.json and Saved/stance_check_result.txt.
"""
import json
import math
import os
import sys
import traceback

import unreal

CLIP = sys.argv[1] if len(sys.argv) > 1 else 'MF_Unarmed_Walk_Fwd'
MODE = sys.argv[2] if len(sys.argv) > 2 else 'both'
SAMPLES = 12

SRC_MESH = '/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple'
SRC_DIRS = ['/Game/Characters/Mannequins/Anims/Unarmed/',
            '/Game/Characters/Mannequins/Anims/Unarmed/Walk/',
            '/Game/Characters/Mannequins/Anims/Unarmed/Jog/',
            '/Game/Characters/Mannequins/Anims/Unarmed/Jump/',
            '/Game/Characters/Mannequins/Anims/Unarmed/Attack/',
            '/Game/Characters/Mannequins/Anims/Rifle/HitReact/',
            '/Game/Characters/Mannequins/Anims/Death/']

# label, mesh, retargeted-clip folder, suffix.  folder None = this is the source rig.
CASES = [
    ('Mannequin', SRC_MESH, None, ''),
    ('CafeWalker', '/Game/Game/Imported/CafeWalker/Meshy/SK_CafeWalker',
     '/Game/Game/Imported/CafeWalker/MeshyAnims/', '_CWM'),
]
# extra cases from argv[3:], each "mesh,folder,suffix,label"
for extra in sys.argv[3:]:
    p = extra.split(',')
    if len(p) == 4:
        folder = p[1] if p[1].endswith('/') else p[1] + '/'
        CASES.append((p[3], p[0], folder, p[2]))

out = {'clip': CLIP, 'mode': MODE, 'samples': SAMPLES}
lines = []


def log(*a):
    lines.append(' '.join(str(x) for x in a))


def sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def ln(a):
    return math.sqrt(dot(a, a))


def nrm(a):
    m = ln(a)
    return [c / m for c in a] if m else list(a)


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def ang(a, b):
    c = dot(nrm(a), nrm(b))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def bend(p, q, r):
    """Degrees away from straight at q. 0 = the two segments are in line."""
    a, b = sub(p, q), sub(r, q)
    if not ln(a) or not ln(b):
        return None
    return round(180.0 - ang(a, b), 1)


UP = (0.0, 0.0, 1.0)


def hierarchy(mesh):
    """Parent map and REFERENCE-pose positions, read off a throwaway actor.

    There is no Python API for a reference skeleton; a placed component answers
    get_parent_bone / get_socket_location. Z is unwound from the spawn depth."""
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    tmp = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, -8000),
                                     unreal.Rotator(0, 0, 0))
    tmp.set_actor_label('ZZ_StanceProbe')
    c = tmp.skeletal_mesh_component
    c.set_skeletal_mesh_asset(mesh)
    names = [str(n) for n in c.get_all_socket_names()]
    par, pos = {}, {}
    for n in names:
        p = c.get_socket_location(unreal.Name(n))
        pos[n] = (p.x, p.y, p.z + 8000.0)
        try:
            par[n] = str(c.get_parent_bone(unreal.Name(n)))
        except Exception:
            par[n] = 'None'
    eas.destroy_actor(tmp)
    return names, par, pos


def posed(clip, t):
    opts = unreal.AnimPoseEvaluationOptions()
    opts.set_editor_property('extract_root_motion', True)
    pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(clip, t, opts)
    pos = {}
    for b in unreal.AnimPoseExtensions.get_bone_names(pose):
        v = unreal.AnimPoseExtensions.get_bone_pose(pose, b, unreal.AnimPoseSpaces.WORLD).translation
        pos[str(b)] = (v.x, v.y, v.z)
    return pos


class Rig(object):
    """Bone roles worked out from topology once, then reused for every sampled frame."""

    def __init__(self, names, par, pos):
        self.par = par
        self.kids = {}
        for n in names:
            self.kids.setdefault(par.get(n, 'None'), []).append(n)
        self._depth = {}
        roots = [n for n in names if par.get(n, 'None') in ('None', '')]
        if not roots:
            raise RuntimeError('no parentless bone')
        # NOT roots[0]. get_all_socket_names() returns sockets as well as bones and a socket's
        # parent lookup can come back empty, which makes it look parentless - the mannequin's
        # `weapon_r_muzzle` was picked as the skeleton root and the whole hierarchy vanished.
        # The real root is the parentless node carrying the biggest subtree.
        self.root = max(roots, key=self.size)
        # NOT kids[root][0]: the mannequin's root also carries ik_foot_root / interaction /
        # center_of_mass, and socket order decides which comes first. The pelvis is the big subtree.
        self.hip = max(self.kids.get(self.root, [self.root]), key=self.size)
        branches = self.kids.get(self.hip, [])
        if len(branches) < 3:
            raise RuntimeError('hip %s has %d branches, expected spine + 2 legs'
                               % (self.hip, len(branches)))
        self.spine_root = max(branches, key=lambda b: self.tipz(b, pos))
        legs = sorted([b for b in branches if b != self.spine_root],
                      key=lambda b: self.tipz(b, pos))[:2]
        if len(legs) < 2:
            raise RuntimeError('cannot find two legs off hip %s' % self.hip)
        self.spine = self.straight(self.spine_root)
        self.chest = self.spine[-1]
        off_chest = self.kids.get(self.chest, [])
        if len(off_chest) < 3:
            raise RuntimeError('chest %s has %d branches, expected head + 2 arms'
                               % (self.chest, len(off_chest)))
        self.neck_root = max(off_chest, key=lambda b: self.tipz(b, pos))
        self.head_path = self.deep(self.neck_root)
        arms = [b for b in off_chest if b != self.neck_root]
        if len(arms) != 2:
            raise RuntimeError('found %d arm branches, expected 2' % len(arms))
        self.legs = [self.deep(b) for b in legs]
        self.arms = [self.arm_path(b) for b in arms]

    def size(self, b):
        n, stack = 0, list(self.kids.get(b, []))
        while stack:
            n += 1
            stack += self.kids.get(stack.pop(), [])
        return n

    def depth(self, b):
        if b not in self._depth:
            ks = self.kids.get(b, [])
            self._depth[b] = 1 + (max(self.depth(k) for k in ks) if ks else 0)
        return self._depth[b]

    def straight(self, b):
        ch = [b]
        while len(self.kids.get(ch[-1], [])) == 1:
            ch.append(self.kids[ch[-1]][0])
        return ch

    def deep(self, b):
        """Follow the child with the DEEPEST subtree. Twist bones are shallow, so this walks the
        real limb where straight() stops at the first twist branch."""
        ch = [b]
        while self.kids.get(ch[-1], []):
            ch.append(max(self.kids[ch[-1]], key=self.depth))
        return ch

    def tipz(self, b, pos):
        """How high this branch ENDS. A thigh is high; a leg ENDS low."""
        tip = self.deep(b)[-1]
        best, stack = pos[tip][2], list(self.kids.get(tip, []))
        while stack:
            n = stack.pop()
            best = max(best, pos[n][2])
            stack += self.kids.get(n, [])
        return best

    def arm_path(self, b):
        """clavicle .. hand. The hand is the descendant with five branches (the fingers)."""
        hand, stack = None, [b]
        while stack:
            n = stack.pop()
            if len(self.kids.get(n, [])) == 5:
                hand = n
                break
            stack += self.kids.get(n, [])
        if hand is None:
            return self.deep(b)
        path = [hand]
        while path[0] != b:
            path.insert(0, self.par[path[0]])
        return path


def frame(rig, pos):
    """The rig's own up / forward / right, from bones a stride does not move.

    lateral comes from the two THIGH ROOTS, which are rigid to the pelvis; ankles are not, because
    mid-stride they sit one in front of the other. forward = lateral x up with its sign fixed from
    a foot, because the toe is in front of the ankle. right = up x forward (Unreal is left-handed)."""
    up = nrm(sub(pos[rig.chest], pos[rig.hip]))
    lat = nrm(sub(pos[rig.legs[0][0]], pos[rig.legs[1][0]]))
    lat = nrm([lat[i] - up[i] * dot(lat, up) for i in range(3)])
    fwd = nrm(cross(lat, up))
    lc = rig.legs[0]
    if dot(sub(pos[lc[-1]], pos[lc[-2]]), fwd) < 0:
        fwd = [-c for c in fwd]
    return up, fwd, nrm(cross(up, fwd))


def measure(rig, pos):
    up, fwd, right = frame(rig, pos)
    hip, chest = pos[rig.hip], pos[rig.chest]

    def leglen(lc):
        return ln(sub(pos[lc[1]], pos[lc[0]])) + ln(sub(pos[lc[-2]], pos[lc[1]]))

    L = sum(leglen(lc) for lc in rig.legs) / 2.0
    if L <= 0:
        raise RuntimeError('zero leg length')

    legs = {}
    for lc in rig.legs:
        thigh, ankle, toe = lc[0], lc[-2], lc[-1]
        side = 'Right' if dot(sub(pos[thigh], hip), right) > 0 else 'Left'
        f = sub(pos[toe], pos[ankle])
        fp = [f[i] - up[i] * dot(f, up) for i in range(3)]           # onto the ground plane
        # How much of the foot survives that projection. Mid-stride the swinging foot is
        # plantar-flexed (toe pointing down), its ground-plane shadow is almost nothing, and the
        # DIRECTION of that shadow is numerical noise - which is what made toe_out_deg read 22
        # degrees on the mannequin's own walk. Only a reasonably flat foot has a toe angle.
        flat = ln(fp) / ln(f) if ln(f) else 0.0
        fg = nrm(fp)
        a = ang(fg, fwd)
        toward_right = a if dot(fg, right) > 0 else -a
        legs[side] = {'bones': len(lc), 'thigh': thigh, 'ankle': ankle, 'toe': toe,
                      'foot_flat': round(flat, 3),
                      'toe_out_deg': round(toward_right if side == 'Right' else -toward_right, 1),
                      'knee_bend_deg': bend(pos[lc[0]], pos[lc[1]], pos[lc[-2]]),
                      'ankle_lat': round(dot(sub(pos[ankle], hip), right) / L, 3),
                      'ankle_fwd': round(dot(sub(pos[ankle], hip), fwd) / L, 3)}
    if len(legs) != 2:
        raise RuntimeError('both legs read as the same side')

    arms = {}
    for ac in rig.arms:
        clav, upper, elbow, hand = ac[0], ac[1], ac[2], ac[-1]
        side = 'Right' if dot(sub(pos[upper], hip), right) > 0 else 'Left'
        ud = sub(pos[elbow], pos[upper])
        down = [-c for c in up]
        lat = dot(nrm(ud), right)
        arms[side] = {'bones': len(ac), 'clavicle': clav, 'upperarm': upper,
                      'elbow': elbow, 'hand': hand,
                      'arm_out_deg': round(ang(ud, down), 1),
                      'arm_lateral': round(lat if side == 'Right' else -lat, 3),
                      'shoulder_bend_deg': bend(pos[clav], pos[upper], pos[elbow]),
                      'elbow_bend_deg': bend(pos[upper], pos[elbow], pos[hand]),
                      'clav_fwd': round(dot(nrm(sub(pos[upper], chest)), fwd), 3)}
    if len(arms) != 2:
        raise RuntimeError('both arms read as the same side')

    head_tip = rig.head_path[-1]
    return {
        'leg_cm': round(L, 1),
        'stance_width': round(abs(legs['Right']['ankle_lat'] - legs['Left']['ankle_lat']), 3),
        'stagger': round(abs(legs['Right']['ankle_fwd'] - legs['Left']['ankle_fwd']), 3),
        'toe_out_deg': round((legs['Right']['toe_out_deg'] + legs['Left']['toe_out_deg']) / 2.0, 1),
        'toe_out_asym_deg': round(abs(legs['Right']['toe_out_deg'] - legs['Left']['toe_out_deg']), 1),
        'foot_flat': round(min(legs['Right']['foot_flat'], legs['Left']['foot_flat']), 3),
        'knee_bend_deg': round((legs['Right']['knee_bend_deg']
                                + legs['Left']['knee_bend_deg']) / 2.0, 1),
        'spine_lean_deg': round(ang(sub(chest, hip), UP), 1),
        'head_drop_deg': round(ang(sub(pos[head_tip], pos[rig.neck_root]), UP), 1),
        'arm_out_deg': round((arms['Right']['arm_out_deg'] + arms['Left']['arm_out_deg']) / 2.0, 1),
        'arm_lateral': round((arms['Right']['arm_lateral'] + arms['Left']['arm_lateral']) / 2.0, 3),
        'elbow_bend_deg': round((arms['Right']['elbow_bend_deg']
                                 + arms['Left']['elbow_bend_deg']) / 2.0, 1),
        'clav_fwd': round((arms['Right']['clav_fwd'] + arms['Left']['clav_fwd']) / 2.0, 3),
        'legs': legs, 'arms': arms}


def find_src_clip(base):
    for d in SRC_DIRS:
        p = d + base
        if unreal.EditorAssetLibrary.does_asset_exist(p):
            return p
    return None


KEYS = ['stance_width', 'stagger', 'toe_out_deg', 'toe_out_asym_deg', 'knee_bend_deg',
        'spine_lean_deg', 'head_drop_deg', 'arm_out_deg', 'arm_lateral', 'elbow_bend_deg',
        'clav_fwd']
# a toe angle is only meaningful on a foot that is roughly flat to the ground - see foot_flat
FLAT_ONLY = ('toe_out_deg', 'toe_out_asym_deg')
FLAT_MIN = 0.6


def mean_of(rows):
    flat = [r for r in rows if r.get('foot_flat', 1.0) >= FLAT_MIN]
    m = {'flat_samples': len(flat)}
    for k in KEYS:
        src = flat if k in FLAT_ONLY else rows
        v = [r[k] for r in src if r.get(k) is not None]
        m[k] = round(sum(v) / len(v), 3) if v else None
    return m


def one_case(label, meshp, folder, suffix):
    mesh = unreal.load_asset(meshp)
    rec = {'mesh': meshp}
    if mesh is None:
        rec['error'] = 'mesh not found'
        return rec
    names, par, refpos = hierarchy(mesh)
    clipp = find_src_clip(CLIP) if folder is None else folder + CLIP + suffix
    clip = unreal.load_asset(clipp) if clipp else None
    # get_all_socket_names() returns SOCKETS as well as bones. A socket is always a leaf, so one
    # attached to a hand makes it a six-branch node and the finger test stops finding the hand;
    # and a socket whose parent lookup comes back empty looks like a second skeleton root. An
    # AnimPose carries BONES only, so use a clip's own bone list as the filter.
    p0 = posed(clip, 0.0) if clip is not None else None
    if p0 is not None:
        rec['sockets_dropped'] = len([n for n in names if n not in p0])
        names = [n for n in names if n in p0]
    rig = Rig(names, par, refpos)
    rec['bones'] = len(names)
    rec['roles'] = {'root': rig.root, 'hip': rig.hip, 'chest': rig.chest,
                    'neck': rig.neck_root, 'head_tip': rig.head_path[-1],
                    'legs': [lc[0] + '..' + lc[-1] for lc in rig.legs],
                    'arms': [ac[0] + '..' + ac[-1] for ac in rig.arms]}
    if MODE in ('ref', 'both'):
        rec['reference_pose'] = measure(rig, refpos)
    if MODE in ('posed', 'both'):
        if clip is None:
            rec['posed_error'] = 'clip not found: %s' % clipp
        else:
            dur = clip.get_play_length()
            # Roles come from the REFERENCE pose and are reused for every frame. Re-deriving them
            # from a posed frame is unsafe: topology picks the spine as the branch off the hip that
            # reaches highest, and a badly aligned retarget (GLOBAL_ROTATION_AXES) put a leg above
            # the spine, so a toe bone was identified as the chest and the run died.
            rows = [measure(rig, posed(clip, dur * i / float(SAMPLES))) for i in range(SAMPLES)]
            rec['posed'] = {'clip': clipp, 'length_s': round(dur, 3),
                            'mean': mean_of(rows),
                            'per_sample': [dict((k, r[k]) for k in KEYS + ['foot_flat'])
                                           for r in rows]}
    return rec


try:
    for case in CASES:
        # One case per try: a variant that retargets to a broken pose must not take the whole
        # comparison down with it - that is the point of running variants side by side.
        try:
            out[case[0]] = one_case(*case)
        except Exception:
            out[case[0]] = {'mesh': case[1], 'error': traceback.format_exc().strip().split('\n')[-1]}

    base = out.get('Mannequin', {})
    for part in ('reference_pose', 'posed'):
        bm = base.get(part) or {}
        bm = bm.get('mean', bm) if part == 'posed' else bm
        if not bm:
            continue
        log('')
        log('=== %s%s ===' % (part, (' ' + CLIP) if part == 'posed' else ''))
        for label in [k for k in out if k not in ('Mannequin', 'clip', 'mode', 'samples', 'table')]:
            rec = out[label]
            if not isinstance(rec, dict):
                continue
            cm = rec.get(part) or {}
            cm = cm.get('mean', cm) if part == 'posed' else cm
            if not cm:
                log('  %s: %s' % (label, rec.get('posed_error', rec.get('error', 'no data'))))
                continue
            log('-- %s vs Mannequin' % label)
            if 'flat_samples' in cm:
                log('   toe angles averaged over %s/%s flat-footed samples (ref %s/%s)'
                    % (cm.get('flat_samples'), SAMPLES, bm.get('flat_samples'), SAMPLES))
            log('   %-16s %10s %10s %10s' % ('metric', 'Mannequin', label[:10], 'delta'))
            for k in KEYS:
                a, b = bm.get(k), cm.get(k)
                if a is None or b is None:
                    continue
                log('   %-16s %10.3f %10.3f %+10.3f' % (k, a, b, b - a))
    out['table'] = lines
except Exception:
    out['ERROR'] = traceback.format_exc()
    log('ERROR ' + traceback.format_exc())

d = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy')
if not os.path.isdir(d):
    os.makedirs(d)
with open(os.path.join(d, 'stance_check.json'), 'w') as fh:
    json.dump(out, fh, indent=1, default=str)
with open(os.path.join(unreal.Paths.project_saved_dir(), 'stance_check_result.txt'), 'w') as fh:
    fh.write('\n'.join(lines) + '\n')
unreal.log('STANCE-CHECK ' + ' | '.join(lines)[:900])
