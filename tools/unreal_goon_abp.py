"""The street goon gets an anim blueprint of his own, and BP_Goon is pointed at it (#6).

What was wrong (Nov 14). `tools/unreal_retarget_meshy.py` put the goon's 20 fight clips in
`MeshyLoco` and reported `saved 43 packages ok True`, but only **21** assets exist in that folder:
every `MF_*` locomotion clip, `BS_Idle_Walk_Run_SGL`, `MM_Idle_SGL` and - the one that matters -
`ABP_Unarmed_SGL` were discarded. That is the trap already written into CLAUDE.md: the second
`duplicate_and_retarget` call of the run made `_SGL1` copies and renamed them, the names it handed
back were the pre-rename ones, and the real assets went away. So `BP_Goon` was left pointing at
**Epic's `ABP_Unarmed`**, whose target skeleton is the mannequin - it cannot drive a 76-bone Meshy
skeleton, and the goon stands in his reference pose instead of walking.

Why this script is separate rather than a re-run. Retargeting into a folder that already holds
`_SG*` assets is what triggers the rename collision, so this goes into a FRESH folder with a FRESH
suffix and makes exactly ONE batch call: the anim blueprint. Its locomotion state machine drags its
own dependencies across with it (the blend space, the idle, all 16 walk/jog clips), which is the
whole set `BP_Goon` needs, and it carries Epic's `Slot 'DefaultSlot'` node so the 19 `AM_Goon_*`
montages already on the Blueprint keep playing with no graph work.

It reuses the IK retargeter the earlier run already built and saved
(`MeshyLoco/RTG_Mannequin_to_SK_StreetGoon`, 9 of 9 chains mapped), so no chain work is repeated.

Run in the editor console box with Play mode stopped:
    py <repo>/tools/unreal_goon_abp.py              make the assets, report what really landed
    py <repo>/tools/unreal_goon_abp.py wire         also point BP_Goon's mesh at the new ABP
Result: Saved/jcpy/goon_abp.json. Never trust the batch call's return value - this reads the
folder back off the asset registry afterwards and that is the number to believe.
"""
import json
import os
import sys
import traceback

import unreal

SRC_MESH = '/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple'
ABP_SRC = '/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed'
TGT_MESH = '/Game/Game/Imported/StreetGoon/Meshy/SK_StreetGoon'
RTG = '/Game/Game/Imported/StreetGoon/MeshyLoco/RTG_Mannequin_to_SK_StreetGoon'
FOLDER = '/Game/Game/Imported/StreetGoon/Loco'
SUFFIX = '_SGN'
GOON = '/Game/Game/Blueprints/BP_Goon'
OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'goon_abp.json')

R = {'folder': FOLDER, 'suffix': SUFFIX, 'wire': 'wire' in sys.argv[1:]}
eal = unreal.EditorAssetLibrary


def folder_assets():
    """What is REALLY in the folder, off the asset registry - not what the batch call returned.

    The synchronous scan is not optional. A folder that `duplicate_and_retarget` created in an
    EARLIER editor session is on disk but is NOT in the registry's path index when a new script
    starts, so both this function and `does_asset_exist` answer "empty" for 22 assets that are
    plainly there - which silently defeated the idempotence guard below and re-ran the batch."""
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    if eal.does_directory_exist(FOLDER):
        ar.scan_paths_synchronous([FOLDER], True)
    got = {}
    for ad in ar.get_assets(unreal.ARFilter(package_paths=[FOLDER], recursive_paths=True)):
        got.setdefault(str(ad.asset_class_path.asset_name), []).append(str(ad.asset_name))
    return {k: sorted(v) for k, v in sorted(got.items())}


def save_folder():
    """Save by PATH. Never save_dirty_packages: another lane has read-only Blueprints dirty in
    this editor (BP_BossFreeze, BP_GoonSpawner, BP_StuntDouble, BP_StuntStandIn) and a project-wide
    save fails on them, leaves .tmp files behind and stops the editor answering for ten minutes."""
    pkgs = {}
    for p in eal.list_assets(FOLDER, True, False):
        a = unreal.load_asset(p)
        if a is not None:
            pkgs[a.get_outermost().get_name()] = a.get_outermost()
    ok = unreal.EditorLoadingAndSavingUtils.save_packages(list(pkgs.values()), False)
    return {'packages': len(pkgs), 'ok': bool(ok)}


try:
    src_mesh = unreal.load_asset(SRC_MESH)
    tgt_mesh = unreal.load_asset(TGT_MESH)
    rtg = unreal.load_asset(RTG)
    for nm, obj, path in (('source mesh', src_mesh, SRC_MESH), ('target mesh', tgt_mesh, TGT_MESH),
                          ('retargeter', rtg, RTG)):
        if obj is None:
            raise RuntimeError('%s not found: %s' % (nm, path))

    R['before'] = folder_assets()   # also forces the registry scan the guard below depends on

    want = FOLDER + '/ABP_Unarmed' + SUFFIX
    # IDEMPOTENT ON PURPOSE. Retargeting into a folder that already holds `<SUFFIX>` assets is the
    # exact condition that makes duplicate_and_retarget produce `<SUFFIX>1` copies, rename them,
    # and hand back the pre-rename names - which is how 22 assets were lost the first time. So if
    # the anim blueprint is already there, skip the batch entirely and go straight to the wiring.
    if eal.does_asset_exist(want):
        R['batch'] = 'skipped - %s already exists' % want
    else:
        ar = unreal.AssetRegistryHelpers.get_asset_registry()
        abp = ar.get_asset_by_object_path(ABP_SRC + '.' + ABP_SRC.split('/')[-1])
        if not abp.is_valid():
            raise RuntimeError('anim blueprint source not found: %s' % ABP_SRC)
        res = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
            [abp], src_mesh, tgt_mesh, rtg, '', '', '', SUFFIX, FOLDER, False, True, True)
        R['batch_claimed'] = [str(ad.package_name) for ad in res]
        R['save'] = save_folder()
    R['after'] = folder_assets()

    R['abp_path'] = want
    R['abp_exists'] = bool(eal.does_asset_exist(want))

    if R['wire'] and R['abp_exists']:
        bp = unreal.load_asset(GOON)
        gc = bp.generated_class()
        cdo = unreal.get_default_object(gc)
        abp_asset = unreal.load_asset(want)
        new_class = abp_asset.generated_class()
        rows = []
        for c in cdo.get_components_by_class(unreal.SkeletalMeshComponent):
            was = c.get_editor_property('anim_class')
            c.modify()
            c.set_editor_property('anim_class', new_class)
            now = c.get_editor_property('anim_class')
            rows.append({'component': c.get_name(),
                         'was': was.get_path_name() if was else None,
                         'now': now.get_path_name() if now else None})
        R['goon_anim_class'] = rows
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        R['goon_saved'] = bool(unreal.EditorLoadingAndSavingUtils.save_packages(
            [bp.get_outermost()], False))
        # read it back from the recompiled CDO rather than from what we just set
        cdo2 = unreal.get_default_object(bp.generated_class())
        R['goon_readback'] = [
            (c.get_editor_property('anim_class').get_path_name()
             if c.get_editor_property('anim_class') else None)
            for c in cdo2.get_components_by_class(unreal.SkeletalMeshComponent)]
except Exception:
    R['error'] = traceback.format_exc()

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w').write(json.dumps(R, indent=1))
unreal.log('GOON ABP done -> ' + OUT)
