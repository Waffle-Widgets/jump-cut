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
    py <repo>/tools/unreal_retarget_meshy.py <target skeletal mesh> <output folder> <suffix> [arms|all|none]
    py .../unreal_retarget_meshy.py /Game/Game/Imported/CafeWalker/Meshy/SK_CafeWalker \
       /Game/Game/Imported/CafeWalker/MeshyAnims _CWM

Results and errors go to Saved/retarget_meshy_result.txt, and the chain table it worked out is
written to Saved/jcpy/retarget_meshy_chains.json so it can be checked before anything is trusted.
"""
import json
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
    # character's right is forward x up. Do NOT read side from a clavicle's own X - the street goon's
    # two clavicles sit at x = +3.9 and +0.4, both on the same side of zero, which made both arms
    # "Right" and silently cost him one of them. The END of the chain (a hand, a toe) is unambiguous.
    leg_chain = straight(legs[0])
    ankle, toe = leg_chain[max(0, len(leg_chain) - 3)], leg_chain[-1]
    faces_plus_y = (pos[toe][1] - pos[ankle][1]) > 0
    right_sign = 1.0 if faces_plus_y else -1.0
    hip_x = pos[hip][0]

    def side(chain):
        return 'Right' if (pos[chain[-1]][0] - hip_x) * right_sign > 0 else 'Left'

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
    for b in legs:
        ch = straight(b)
        chains.append((side(ch) + 'Leg', ch[0], ch[-1]))
    names_used = [c[0] for c in chains]
    dupes = sorted({n for n in names_used if names_used.count(n) > 1})
    if dupes:
        raise RuntimeError('two chains got the same name (%s) - the side test failed, and a duplicate '
                           'name silently replaces the first chain' % ', '.join(dupes))
    return {'root': root, 'hip': hip, 'height': round(height, 2), 'faces_plus_y': faces_plus_y,
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
    res = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
        assets, src_mesh, tgt_mesh, rtg, '', '', '', SUFFIX, FOLDER, False, True, True)
    for ad in res:
        log('made', ad.asset_class_path.asset_name, ad.package_name)
    log('retargeted', len(res), 'assets into', FOLDER)

    # The template's anim blueprint goes through the same operation, which brings its locomotion
    # state machine AND its DefaultSlot (what makes montages play) across with every animation
    # reference remapped. Doing it in the same run matters: see save_folder below.
    abp = reg.get_asset_by_object_path(ABP_SRC + '.' + ABP_SRC.split('/')[-1])
    if abp.is_valid():
        ares = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
            [abp], src_mesh, tgt_mesh, rtg, '', '', '', SUFFIX, FOLDER, False, True, True)
        for ad in ares:
            log('made', ad.asset_class_path.asset_name, ad.package_name)
    else:
        log('ABP source missing', ABP_SRC)

    save_folder(FOLDER)


try:
    run()
    log('DONE')
except Exception:
    log('ERROR', traceback.format_exc())
with open(os.path.join(unreal.Paths.project_saved_dir(), 'retarget_meshy_result.txt'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
unreal.log('RETARGET-MESHY ' + ' | '.join(out)[:900])
