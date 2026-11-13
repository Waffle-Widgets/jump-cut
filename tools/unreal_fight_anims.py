"""Gives the fight animation the first build never had: montage assets for the punches, hit reacts and deaths, for
the mannequin skeleton (the player and the goons) and for our own CleaverBoss skeleton (retargeted from the
mannequin's motion capture first).

Why montages at all: BP_Player.PlayerPunch and BP_EnemyBase only ever did damage - nothing in the project played an
animation, and the project had no AnimMontage asset outside Epic's pistol one. ABP_Unarmed already carries a
"DefaultSlot" Slot node (AnimGraph.AnimGraphNode_Slot_0), so Play Anim Montage works on anything using it with no
change to the anim blueprint at all.

Run it in the Unreal editor's console box (Cmd), with Play mode stopped:
    py <repo>/tools/unreal_fight_anims.py
Results and errors go to Saved/fight_anims_result.txt.

The source animations ship with Unreal's Third Person template (MM_Attack_01..03, MM_HitReact_*, MM_Death_*), so
they are sourced, not scored. What this script makes is the montage wrapper and the retargeted copies.
"""
import os
import traceback
import unreal

eal = unreal.EditorAssetLibrary
out = []


def log(*a):
    out.append(' '.join(str(x) for x in a))


MANN_MESH = '/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple'
MANN_SKEL = '/Game/Characters/Mannequins/Meshes/SK_Mannequin'

# (montage name, source animation)
HUMAN = [
    ('AM_Human_Punch_01', '/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_01'),
    ('AM_Human_Punch_02', '/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_02'),
    ('AM_Human_Punch_03', '/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_03'),
    ('AM_Human_HitReact', '/Game/Characters/Mannequins/Anims/Rifle/HitReact/MM_HitReact_Front_Lgt_01'),
    ('AM_Human_Death',    '/Game/Characters/Mannequins/Anims/Death/MM_Death_Front_01'),
]
HUMAN_FOLDER = '/Game/Game/Anims/Human'

# the same motion, retargeted onto the boss's own skeleton, then wrapped
BOSS_SRC = ['Unarmed/Attack/MM_Attack_01', 'Unarmed/Attack/MM_Attack_03',
            'Rifle/HitReact/MM_HitReact_Front_Med_01', 'Death/MM_Death_Front_01']
BOSS_FOLDER = '/Game/Game/Imported/CleaverBoss/Anims'
BOSS_RTG = BOSS_FOLDER + '/RTG_Mannequin_to_SK_CleaverBoss'
BOSS_MESH = '/Game/Game/Imported/CleaverBoss/SK/SK_CleaverBoss'
BOSS_SUFFIX = '_CB'
BOSS_MONTAGES = [
    ('AM_CleaverBoss_Punch',    BOSS_FOLDER + '/MM_Attack_01' + BOSS_SUFFIX),
    ('AM_CleaverBoss_Cleave',   BOSS_FOLDER + '/MM_Attack_03' + BOSS_SUFFIX),
    ('AM_CleaverBoss_HitReact', BOSS_FOLDER + '/MM_HitReact_Front_Med_01' + BOSS_SUFFIX),
    ('AM_CleaverBoss_Death',    BOSS_FOLDER + '/MM_Death_Front_01' + BOSS_SUFFIX),
]


def fresh(name, folder, cls, factory):
    """Create an asset, reusing any asset already at that path. Never let a modal overwrite box appear: it freezes
    the MCP until a person clicks it."""
    path = folder + '/' + name
    if eal.does_asset_exist(path):
        log('exists, reusing', path)
        return unreal.load_asset(path)
    return unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, folder, cls, factory)


def make_montage(name, folder, anim_path, skeleton):
    anim = unreal.load_asset(anim_path)
    if anim is None:
        log('MISSING source animation', anim_path)
        return None
    f = unreal.AnimMontageFactory()
    f.set_editor_property('source_animation', anim)
    f.set_editor_property('target_skeleton', skeleton)
    m = fresh(name, folder, unreal.AnimMontage, f)
    if m is None:
        log('FAILED montage', name)
        return None
    slots = 'unread'
    for prop in ('slot_anim_tracks', 'slot_animations'):
        try:
            slots = [str(t.slot_name) for t in m.get_editor_property(prop)]
            break
        except Exception:
            continue
    log('made', name, 'len %.2fs' % m.get_editor_property('sequence_length'), 'slots', slots)
    eal.save_loaded_asset(m)
    return m


def retarget_boss():
    rtg = unreal.load_asset(BOSS_RTG)
    if rtg is None:
        log('NO retargeter at', BOSS_RTG)
        return
    src_mesh, tgt_mesh = unreal.load_asset(MANN_MESH), unreal.load_asset(BOSS_MESH)
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = []
    for n in BOSS_SRC:
        leaf = n.split('/')[-1]
        p = '/Game/Characters/Mannequins/Anims/' + n
        if eal.does_asset_exist(BOSS_FOLDER + '/' + leaf + BOSS_SUFFIX):
            log('already retargeted', leaf + BOSS_SUFFIX)
            continue
        ad = reg.get_asset_by_object_path(p + '.' + leaf)
        log('source', n, ad.is_valid())
        if ad.is_valid():
            assets.append(ad)
    if not assets:
        log('nothing to retarget')
        return
    res = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
        assets, src_mesh, tgt_mesh, rtg, '', '', '', BOSS_SUFFIX, BOSS_FOLDER, False, True, True)
    for ad in res:
        log('retargeted ->', ad.package_name)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(False, True)
    for ad in res:
        eal.save_asset(str(ad.package_name), only_if_is_dirty=False)


def run():
    mann_skel = unreal.load_asset(MANN_SKEL)
    log('mannequin skeleton', mann_skel)
    for name, src in HUMAN:
        make_montage(name, HUMAN_FOLDER, src, mann_skel)
    retarget_boss()
    boss_skel = unreal.load_asset('/Game/Game/Imported/CleaverBoss/SK/SK_CleaverBoss_Skeleton')
    log('boss skeleton', boss_skel)
    for name, src in BOSS_MONTAGES:
        make_montage(name, BOSS_FOLDER, src, boss_skel)


try:
    run()
    log('DONE')
except Exception:
    log('ERROR', traceback.format_exc())
with open(os.path.join(r'C:\Users\thecl\code\jump-cut\JumpCut\Saved', 'fight_anims_result.txt'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
unreal.log('FIGHTANIMS ' + ' | '.join(out)[:900])
