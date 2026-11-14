"""Gives a MESHY SMART RIG character Unreal's mannequin animations.

tools/unreal_retarget_mannequin.py already does this for characters built by
Art/Blender/trellis_character.py, which names its bones the way Epic's mannequin does
(root, pelvis, spine_01...). Meshy's Smart Rig names every bone `Bone_000`, so
`apply_auto_generated_retarget_definition()` finds nothing and the manual fallback in that
script - which spells mannequin bone names - adds no chains at all. That is the "nine chains
mapped by hand" the cleaver boss needed, and the warning on issues #6 and #7.

This script works the chains out instead of being told them, using the same reasoning
Art/Blender/meshy_character.py uses in Blender:
  * the root is the parentless bone, and its single child is the hip;
  * of the branches off the hip, the one whose descendants reach highest is the spine,
    and the ones that stay below a quarter of the body height are the legs;
  * follow the spine to the first bone with more than one child - that is the chest;
  * off the chest, the branch reaching highest is the neck/head and the others are the arms;
  * side is read from X: a Meshy character faces +Y in Unreal, so +X is its RIGHT.
It then names the chains exactly what Unreal's auto definition names the mannequin's, so
`auto_map_chains(FUZZY)` pairs them up.

Run it in the Unreal editor's console box (Cmd), with Play mode stopped:
    py <repo>/tools/unreal_retarget_meshy.py <target skeletal mesh> <output folder> <suffix> [arms|all|none] [clips|abp|both] [all|fight|loco]
    py .../unreal_retarget_meshy.py /Game/Game/Imported/CafeWalker/Meshy/SK_CafeWalker \
       /Game/Game/Imported/CafeWalker/MeshyAnims _CWM

Results and errors go to Saved/retarget_meshy_result.txt, and the chain table it worked out is
written to Saved/jcpy/retarget_meshy_chains.json so it can be checked before anything is trusted.
"""
import json
import math
import os
import sys
import traceback

import unreal

SRC_MESH = '/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple'
ANIMS = '/Game/Characters/Mannequins/Anims/'
# locomotion the blend space needs, then the four the fights need
LIST = ['Unarmed/BS_Idle_Walk_Run', 'Unarmed/MM_Idle',
        'Unarmed/Walk/MF_Unarmed_Walk_Fwd', 'Unarmed/Jog/MF_Unarmed_Jog_Fwd',
        'Unarmed/Jump/MM_Jump', 'Unarmed/Jump/MM_Fall_Loop', 'Unarmed/Jump/MM_Land',
        'Unarmed/Attack/MM_Attack_01', 'Unarmed/Attack/MM_Attack_02', 'Unarmed/Attack/MM_Attack_03',
        'Unarmed/Attack/MM_ChargedAttack',
        # the per-hit variety PR #47 gave the goons: without these a Meshy enemy has one hit react
        # and one death, and three of them look like one creature again
        'Rifle/HitReact/MM_HitReact_Front_Lgt_01', 'Rifle/HitReact/MM_HitReact_Front_Lgt_02',
        'Rifle/HitReact/MM_HitReact_Front_Lgt_03', 'Rifle/HitReact/MM_HitReact_Front_Lgt_04',
        'Rifle/HitReact/MM_HitReact_Front_Med_01', 'Rifle/HitReact/MM_HitReact_Front_Med_02',
        'Rifle/HitReact/MM_HitReact_Front_Hvy_01', 'Rifle/HitReact/MM_HitReact_Back_Med_01',
        'Death/MM_Death_Front_01', 'Death/MM_Death_Front_02', 'Death/MM_Death_Front_03',
        'Death/MM_Death_Back_01', 'Death/MM_Death_Left_01', 'Death/MM_Death_Right_01']

TARGET = sys.argv[1]
FOLDER = sys.argv[2]
SUFFIX = sys.argv[3] if len(sys.argv) > 3 else '_MS'
ALIGN = sys.argv[4] if len(sys.argv) > 4 else 'arms'
# ONE batch call per run. Two duplicate_and_retarget calls in a single run is the exact
# condition that made `_SGL1` copies and discarded 22 real assets (see unreal_goon_abp.py),
# so the clips and the anim blueprint are now separate runs: 'clips', 'abp', or 'both'.
ONLY = sys.argv[5] if len(sys.argv) > 5 else 'both'
# Which part of LIST to retarget. A character whose locomotion already lives in another folder
# (the street goon's is in Loco/) only wants the fight clips here, or the folder fills with a
# second unused copy of all 18 walk/jog clips.
WHICH = sys.argv[6] if len(sys.argv) > 6 else 'all'
if WHICH == 'fight':
    LIST = [n for n in LIST if '/Attack/' in n or 'HitReact' in n or 'Death/' in n]
elif WHICH == 'loco':
    LIST = [n for n in LIST if not ('/Attack/' in n or 'HitReact' in n or 'Death/' in n)]

ABP_SRC = '/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed'

eal = unreal.EditorAssetLibrary
out = []


def save_folder(folder):
    """Save every asset in the folder BY PATH, and never call save_dirty_packages.

    Two things learned the hard way on the street goon. First, the batch operation's returned
    package names can be the pre-rename `_SG1` ones, so saving by those names saves nothing and
    the real assets are discarded later - a folder of 42 clips came back as 3. Second,
    save_dirty_packages(False, True) saves EVERY dirty package in the project, which here meant
    another lane's four read-only Blueprints: the save fails, leaves .tmp files behind, and the
    editor stops answering for ten minutes."""
    pkgs = []
    for p in eal.list_assets(folder, True, False):
        a = unreal.load_asset(p)
        if a is not None:
            pkgs.append(a.get_outermost())
    pkgs = list({p.get_name(): p for p in pkgs}.values())
    ok = unreal.EditorLoadingAndSavingUtils.save_packages(pkgs, False)
    log('saved', len(pkgs), 'packages in', folder, 'ok', ok)
    return ok


def log(*a):
    out.append(' '.join(str(x) for x in a))


def fresh(name, folder, cls, factory):
    path = folder + '/' + name
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
        if eal.does_asset_exist(path):
            # creating over a file still on disk opens a modal that freezes the MCP - reuse instead
            return unreal.load_asset(path)
    return unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, folder, cls, factory)


def read_skeleton(mesh):
    """Bone name -> (parent, world position), read off a throwaway actor. There is no Python API
    for a reference skeleton, but a placed component answers get_parent_bone / get_socket_location."""
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    tmp = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, -6000),
                                     unreal.Rotator(0, 0, 0))
    tmp.set_actor_label('ZZ_MeshyChainProbe')
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


def _sub(a, b): return [a[i] - b[i] for i in range(3)]


def _dot(a, b): return sum(a[i] * b[i] for i in range(3))


def _nrm(a):
    m = math.sqrt(_dot(a, a))
    return [c / m for c in a] if m else list(a)


def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def body_frame(pos, hip, chest, ankle, toe):
    """A rig's own up / forward / right, read off its geometry.

    forward comes from a foot (the toe is in front of the ankle), up from hip to chest, and then
    `right = up x forward` because Unreal is left-handed (+X forward, +Y right, +Z up). Verified
    against the mannequin's own _l/_r bone names by check_side_rule() on every run."""
    up = _nrm(_sub(pos[chest], pos[hip]))
    f = _nrm(_sub(pos[toe], pos[ankle]))
    fwd = _nrm([f[i] - up[i] * _dot(f, up) for i in range(3)])
    return up, fwd, _nrm(_cross(up, fwd))


def check_side_rule(mesh):
    """Prove the left/right rule on the MANNEQUIN, whose sides are known, before trusting it here.

    Getting this backwards has NO internal tell-tale. Every chain still gets a unique name, all 19
    still map, auto_align_bones still runs, the batch still retargets, and the result is simply the
    mannequin's RIGHT arm played on the character's LEFT - plus a chain-to-chain alignment that
    rotated each arm's retarget pose onto the opposite arm's. The shoulder came out 148 degrees away
    from where the source clip has it, which is the 'the main character and goons arms are mangled
    looking' report of Sat Nov 14. The old rule read the sign off X alone and had it inverted:
    a rig facing +Y has its right at -X, not +X. Both the player and the goons were built with
    swapped limbs and nothing in any log said so."""
    names, par, pos = read_skeleton(mesh)
    need = ['pelvis', 'spine_05', 'foot_r', 'ball_r',
            'hand_r', 'hand_l', 'thigh_r', 'thigh_l', 'foot_l']
    missing = [n for n in need if n not in pos]
    if missing:
        raise RuntimeError('side-rule self-check cannot run, %s has no %s' % (mesh, missing))
    _, _, right = body_frame(pos, 'pelvis', 'spine_05', 'foot_r', 'ball_r')
    bad = []
    for b in ['hand_r', 'hand_l', 'thigh_r', 'thigh_l', 'foot_r', 'foot_l']:
        d = _dot(_sub(pos[b], pos['pelvis']), right)
        want = 'Right' if b.endswith('_r') else 'Left'
        got = 'Right' if d > 0 else 'Left'
        log('  side check', b, got, round(d, 2))
        if got != want:
            bad.append('%s read as %s' % (b, got))
    if bad:
        raise RuntimeError('the left/right rule is WRONG on the mannequin (%s) - refusing to '
                           'retarget, every clip would come out with swapped limbs'
                           % '; '.join(bad))
    log('side rule verified against the mannequin bone names, 6 of 6')


def finger_chains(side, hand, wrist, kids, pos, straight):
    """The five branches off a hand, named the way Epic's auto definition names the mannequin's.

    Without these the target rig has no finger chains at all, every one of the source's ten is
    dropped, and the hands hold their REFERENCE pose in every retargeted clip - which on a Meshy
    body built from an A-pose reference sheet is a permanently splayed claw. That is the whole of
    the 'the arms look mangled' report of Sat Nov 14.

    Thumb is the branch that leaves the palm sideways soonest (most perpendicular offset for the
    least distance along the hand); the other four are ordered across the knuckles away from it,
    which puts the longest tip on Middle and the shortest on Pinky for every hand tested."""
    h = _nrm(_sub(pos[hand], pos[wrist]))
    br = []
    for f in kids.get(hand, []):
        ch = straight(f)
        rv = _sub(pos[f], pos[hand])
        perp = [rv[i] - h[i] * _dot(rv, h) for i in range(3)]
        br.append({'ch': ch, 'along': _dot(rv, h), 'perp': math.sqrt(_dot(perp, perp)), 'pv': perp})
    if len(br) != 5:
        return [], []
    thumb = max(br, key=lambda x: x['perp'] - x['along'])
    rest = [x for x in br if x is not thumb]
    a = _nrm(thumb['pv'])
    rest.sort(key=lambda x: -_dot(x['pv'], a))
    chains, bones = [], []
    for nm, x in zip(['Thumb', 'Index', 'Middle', 'Ring', 'Pinky'], [thumb] + rest):
        chains.append((side + nm, x['ch'][0], x['ch'][-1]))
        bones += x['ch']
    return chains, bones


def work_out_chains(names, par, pos):
    kids = {}
    for n in names:
        kids.setdefault(par.get(n, 'None'), []).append(n)
    height = max(p[2] for p in pos.values())
    roots = [n for n in names if par.get(n, 'None') in ('None', '')]
    if not roots:
        raise RuntimeError('no parentless bone')
    root = roots[0]

    def straight(b):
        ch = [b]
        while len(kids.get(ch[-1], [])) == 1:
            ch.append(kids[ch[-1]][0])
        return ch

    def tipz(b):
        """How high the END of this branch reaches. Follow the branch to where it splits, then take
        the highest bone below that - a leg's thigh is high, but a leg ENDS low, which is the
        difference between a leg and the spine."""
        tip = straight(b)[-1]
        best, stack = pos[tip][2], list(kids.get(tip, []))
        while stack:
            n = stack.pop()
            best = max(best, pos[n][2])
            stack += kids.get(n, [])
        return best

    hip = kids.get(root, [root])[0]
    branches = kids.get(hip, [])
    if len(branches) < 3:
        raise RuntimeError('hip %s has %d branches, expected spine + two legs' % (hip, len(branches)))
    spine_root = max(branches, key=tipz)
    legs = [b for b in branches if b != spine_root and tipz(b) < 0.25 * height]
    if len(legs) != 2:
        raise RuntimeError('found %d leg branches, expected 2' % len(legs))
    spine = straight(spine_root)
    chest = spine[-1]
    off_chest = kids.get(chest, [])
    if len(off_chest) < 3:
        raise RuntimeError('chest %s has %d branches, expected head + two arms' % (chest, len(off_chest)))
    head_root = max(off_chest, key=tipz)
    arms = [b for b in off_chest if b != head_root]
    if len(arms) != 2:
        raise RuntimeError('found %d arm branches, expected 2' % len(arms))
    head_chain = straight(head_root)

    # Which way does this rig face? Read it off a foot: the toe is in front of the ankle. Then the
    # character's right is up x forward. Do NOT read side from a clavicle's own X - the street goon's
    # two clavicles sit at x = +3.9 and +0.4, both on the same side of zero, which made both arms
    # "Right" and silently cost him one of them. The END of the chain (a hand, a toe) is unambiguous.
    #
    # And do not shortcut this to the sign of X. It used to read `right_sign = +1 if faces_plus_y`
    # and compare tip X against the hip's, which is inverted: a rig facing +Y has its right hand at
    # NEGATIVE X. Both Meshy characters were built with every arm and leg labelled the wrong way
    # round - see check_side_rule(), which now proves the rule on the mannequin before each run.
    leg_chain = straight(legs[0])
    ankle, toe = leg_chain[max(0, len(leg_chain) - 3)], leg_chain[-1]
    faces_plus_y = (pos[toe][1] - pos[ankle][1]) > 0
    up, fwd, right = body_frame(pos, hip, chest, ankle, toe)

    def side(chain):
        return 'Right' if _dot(_sub(pos[chain[-1]], pos[hip]), right) > 0 else 'Left'

    chains, arm_bones = [], []
    chains.append(('Spine', spine[0], spine[-1]))
    if len(head_chain) >= 2:
        chains.append(('Neck', head_chain[0], head_chain[0]))
        chains.append(('Head', head_chain[1], head_chain[-1]))
    else:
        chains.append(('Head', head_chain[0], head_chain[-1]))
    for b in arms:
        ch = straight(b)                      # clavicle, upperarm, lowerarm, hand...
        s = side(ch)
        chains.append((s + 'Clavicle', ch[0], ch[0]))
        chains.append((s + 'Arm', ch[1], ch[-1]))
        arm_bones += ch
        fc, fb = finger_chains(s, ch[-1], ch[-2], kids, pos, straight)
        if fc:
            chains += fc
            arm_bones += fb
        else:
            log('WARN hand', ch[-1], 'is not a five-branch hand - no finger chains, hands will'
                ' hold the reference pose in every clip')
    for b in legs:
        ch = straight(b)
        chains.append((side(ch) + 'Leg', ch[0], ch[-1]))
    names_used = [c[0] for c in chains]
    dupes = sorted({n for n in names_used if names_used.count(n) > 1})
    if dupes:
        raise RuntimeError('two chains got the same name (%s) - the side test failed, and a duplicate '
                           'name silently replaces the first chain' % ', '.join(dupes))
    return {'root': root, 'hip': hip, 'height': round(height, 2), 'faces_plus_y': faces_plus_y,
            'axis_up': [round(c, 3) for c in up], 'axis_fwd': [round(c, 3) for c in fwd],
            'axis_right': [round(c, 3) for c in right],
            'chains': chains, 'arm_bones': arm_bones}


def make_src_rig(folder, mesh):
    rig = fresh('IK_Mannequin_Src', folder, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
    c = unreal.IKRigController.get_controller(rig)
    c.set_skeletal_mesh(mesh)
    log('src auto definition', c.apply_auto_generated_retarget_definition())
    log('src chains', [str(ch.chain_name) for ch in c.get_retarget_chains()])
    eal.save_loaded_asset(rig)
    return rig


def make_target_rig(name, folder, mesh, plan):
    rig = fresh(name, folder, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
    c = unreal.IKRigController.get_controller(rig)
    c.set_skeletal_mesh(mesh)
    c.set_retarget_root(plan['hip'])
    for cn, a, b in plan['chains']:
        c.add_retarget_chain(cn, a, b, '')
    log(name, 'root', c.get_retarget_root(), 'chains',
        [(str(ch.chain_name), str(c.get_retarget_chain_start_bone(ch.chain_name)),
          str(c.get_retarget_chain_end_bone(ch.chain_name))) for ch in c.get_retarget_chains()])
    eal.save_loaded_asset(rig)
    return rig


def run():
    src_mesh, tgt_mesh = unreal.load_asset(SRC_MESH), unreal.load_asset(TARGET)
    if tgt_mesh is None:
        raise RuntimeError('target not found: %s' % TARGET)
    if src_mesh is None:
        raise RuntimeError('source mannequin not found: %s' % SRC_MESH)
    check_side_rule(src_mesh)
    names, par, pos = read_skeleton(tgt_mesh)
    plan = work_out_chains(names, par, pos)
    plan['bones'] = len(names)
    json.dump(plan, open(os.path.join(unreal.Paths.project_saved_dir(), 'jcpy',
                                      'retarget_meshy_chains.json'), 'w'), indent=1, default=str)
    log('bones', len(names), 'root', plan['root'], 'hip', plan['hip'], 'height', plan['height'])
    for cn, a, b in plan['chains']:
        log('  chain', cn, a, '->', b)

    src = make_src_rig(FOLDER, src_mesh)
    tgt = make_target_rig('IK_' + TARGET.split('/')[-1], FOLDER, tgt_mesh, plan)

    rtg = fresh('RTG_Mannequin_to_' + TARGET.split('/')[-1], FOLDER,
                unreal.IKRetargeter, unreal.IKRetargetFactory())
    c = unreal.IKRetargeterController.get_controller(rtg)
    S, T = unreal.RetargetSourceOrTarget.SOURCE, unreal.RetargetSourceOrTarget.TARGET
    c.set_ik_rig(S, src)
    c.set_ik_rig(T, tgt)
    c.add_default_ops()
    try:
        c.assign_ik_rig_to_all_ops(S, src)
        c.assign_ik_rig_to_all_ops(T, tgt)
    except Exception as e:
        log('assign_ik_rig_to_all_ops:', str(e)[:200])
    c.auto_map_chains(unreal.AutoMapChainType.FUZZY, True)
    c.reset_retarget_pose(c.get_current_retarget_pose_name(T), [], T)
    if ALIGN == 'all':
        c.auto_align_all_bones(T)
    elif ALIGN == 'arms':
        c.auto_align_bones([unreal.Name(b) for b in plan['arm_bones']],
                           unreal.RetargetAutoAlignMethod.CHAIN_TO_CHAIN, T)
    # joint rotations only: the IK pass drags hands and feet onto the mannequin's and bows the knees
    for i in range(c.get_num_retarget_ops()):
        if 'IK' in str(c.get_op_name(i)):
            c.set_retarget_op_enabled(i, False)
    mapped = 0
    for cn, _, _ in plan['chains']:
        try:
            s = str(c.get_source_chain(cn))
            log('map', cn, '<-', s)
            if s and s != 'None':
                mapped += 1
        except Exception as e:
            log('map', cn, 'ERR', str(e)[:120])
    log('mapped', mapped, 'of', len(plan['chains']))
    eal.save_loaded_asset(rtg)

    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = []
    for n in LIST:
        ad = reg.get_asset_by_object_path(ANIMS + n + '.' + n.split('/')[-1])
        if ad.is_valid():
            assets.append(ad)
        else:
            log('source MISSING', n)
    if ONLY in ('clips', 'both'):
        res = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
            assets, src_mesh, tgt_mesh, rtg, '', '', '', SUFFIX, FOLDER, False, True, True)
        for ad in res:
            log('made', ad.asset_class_path.asset_name, ad.package_name)
        log('retargeted', len(res), 'assets into', FOLDER)
    else:
        log('skipped the clip batch (ONLY=%s)' % ONLY)

    # The template's anim blueprint goes through the same operation, which brings its locomotion
    # state machine AND its DefaultSlot (what makes montages play) across with every animation
    # reference remapped. Doing it in the same run matters: see save_folder below.
    abp = reg.get_asset_by_object_path(ABP_SRC + '.' + ABP_SRC.split('/')[-1])
    if ONLY not in ('abp', 'both'):
        log('skipped the anim blueprint batch (ONLY=%s)' % ONLY)
    elif abp.is_valid():
        ares = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
            [abp], src_mesh, tgt_mesh, rtg, '', '', '', SUFFIX, FOLDER, False, True, True)
        for ad in ares:
            log('made', ad.asset_class_path.asset_name, ad.package_name)
    else:
        log('ABP source missing', ABP_SRC)

    save_folder(FOLDER)

    # Never trust the batch call's return: it hands back PRE-RENAME names. Read the folder back.
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    if eal.does_directory_exist(FOLDER):
        ar.scan_paths_synchronous([FOLDER], True)
    got = sorted(str(a.asset_name) for a in
                 ar.get_assets(unreal.ARFilter(package_paths=[FOLDER], recursive_paths=True)))
    log('folder now holds', len(got), 'assets')
    strays = [g for g in got if g.endswith(SUFFIX + '1') or (SUFFIX + '1') in g]
    log('STRAY RENAME COPIES', strays) if strays else log('no stray rename copies')


try:
    run()
    log('DONE')
except Exception:
    log('ERROR', traceback.format_exc())
with open(os.path.join(unreal.Paths.project_saved_dir(), 'retarget_meshy_result.txt'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
unreal.log('RETARGET-MESHY ' + ' | '.join(out)[:900])
