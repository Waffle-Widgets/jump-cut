"""More montages for the human enemies, so three goons stop reacting, swinging and dying as one clip.

The first fight pass (tools/unreal_fight_anims.py) made exactly one montage per job: one punch, one hit react, one
death. Every goon therefore played the same frames at the same moment. This wraps the rest of what the Third Person
template already ships - four light hit reacts, two medium, one heavy, one from behind; three front deaths and one
each from behind, left and right; three attacks and the charged one - so BP_EnemyBase can pick per goon, per hit.

Run it in the Unreal editor's console box (Cmd), with Play mode stopped:
    py <repo>/tools/unreal_goon_variety_anims.py
Results go to <project>/Saved/goon_variety_result.txt. Idempotent: an existing montage is reused, never replaced.

The source clips are Epic's (sourced, not scored). What this makes is the montage wrappers.
"""
import os
import traceback
import unreal

eal = unreal.EditorAssetLibrary
out = []
A = '/Game/Characters/Mannequins/Anims/'
FOLDER = '/Game/Game/Anims/Human'
MANN_SKEL = '/Game/Characters/Mannequins/Meshes/SK_Mannequin'

# (montage, source, hold the last pose?)
MONTAGES = [
    ('AM_Human_HitReact_Lgt02', A + 'Rifle/HitReact/MM_HitReact_Front_Lgt_02', False),
    ('AM_Human_HitReact_Lgt03', A + 'Rifle/HitReact/MM_HitReact_Front_Lgt_03', False),
    ('AM_Human_HitReact_Lgt04', A + 'Rifle/HitReact/MM_HitReact_Front_Lgt_04', False),
    ('AM_Human_HitReact_Med01', A + 'Rifle/HitReact/MM_HitReact_Front_Med_01', False),
    ('AM_Human_HitReact_Med02', A + 'Rifle/HitReact/MM_HitReact_Front_Med_02', False),
    ('AM_Human_HitReact_Hvy01', A + 'Rifle/HitReact/MM_HitReact_Front_Hvy_01', False),
    ('AM_Human_HitReact_Back',  A + 'Rifle/HitReact/MM_HitReact_Back_Med_01', False),
    ('AM_Human_Death_Front02',  A + 'Death/MM_Death_Front_02', True),
    ('AM_Human_Death_Front03',  A + 'Death/MM_Death_Front_03', True),
    ('AM_Human_Death_Back',     A + 'Death/MM_Death_Back_01', True),
    ('AM_Human_Death_Left',     A + 'Death/MM_Death_Left_01', True),
    ('AM_Human_Death_Right',    A + 'Death/MM_Death_Right_01', True),
    ('AM_Human_Charged',        A + 'Unarmed/Attack/MM_ChargedAttack', False),
]


def log(*a):
    out.append(' '.join(str(x) for x in a))


def make(name, src, hold):
    path = FOLDER + '/' + name
    if eal.does_asset_exist(path):
        log('exists', name)
        return
    anim = unreal.load_asset(src)
    if anim is None:
        log('MISSING', src)
        return
    f = unreal.AnimMontageFactory()
    f.set_editor_property('source_animation', anim)
    f.set_editor_property('target_skeleton', unreal.load_asset(MANN_SKEL))
    m = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, FOLDER, unreal.AnimMontage, f)
    if m is None:
        log('FAILED', name)
        return
    if hold:
        # a body that stands back up after dying reads as a bug: keep the last frame (same as AM_Human_Death)
        m.set_editor_property('enable_auto_blend_out', False)
    eal.save_loaded_asset(m)
    log('made', name, '%.2fs' % m.get_editor_property('sequence_length'), 'hold' if hold else '')


try:
    ref = unreal.load_asset(FOLDER + '/AM_Human_Death')
    log('reference AM_Human_Death auto blend out =', ref.get_editor_property('enable_auto_blend_out'))
    for n, s, h in MONTAGES:
        make(n, s, h)
    log('DONE')
except Exception:
    log('ERROR', traceback.format_exc())
with open(os.path.join(unreal.Paths.project_saved_dir(), 'goon_variety_result.txt'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
unreal.log('GOONVARIETY ' + ' | '.join(out)[:900])
