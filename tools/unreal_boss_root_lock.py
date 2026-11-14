"""The mob boss stops levitating: lock his root to the clip's first frame, not to the reference pose.

Why he floated (Nov 13). Meshy's rig keeps its root bone, Bone_000, at PELVIS height in the reference pose
(z = 87.26 cm), and the retargeted clips animate it on the FLOOR (z = 0), the way Epic's mannequin root works.
Every clip with root motion enabled (the 16 walk/jog clips and the two attacks) resets the root while it plays,
and the default "Root Motion Root Lock" is RefPose - so the root went back up to 87.26 cm and carried the whole
skeleton with it: 87.26 x his 1.2921 mesh scale = 112.7 cm. Idle, hit react and death have root motion off, which
is why he only floated "sometimes".

The player's CafeWalker clips (_CW) came through the same retarget, so they are measured in the same pass. They
read 0: his rig (our own Blender skeleton with the mannequin's bone names) keeps its root on the floor in the
reference pose, so RefPose and the first frame agree. Only clips that measure more than 5 units high are changed.

The fix is one property per clip: root_motion_root_lock = AnimFirstFrame (the first frame has the root on the
floor with its correct rotation). NOT Zero: Bone_000 carries the rig's 90-degree up-axis turn, and Zero wipes it.

Run in the editor console, Play mode stopped (lock the files with git lfs first, or the save silently fails):
    py <repo>/tools/unreal_boss_root_lock.py            measure only
    py <repo>/tools/unreal_boss_root_lock.py fix        set the lock, save, measure again
Result: <project>/Saved/jcpy/boss_root_lock.json. "lift" is the lowest bone's height with root motion extracted,
in mesh units (multiply by 1.2921 for centimetres in the level). A fixed clip reads within a few cm of 0.
"""
import json, os, sys, traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'boss_root_lock.json')
FOLDERS = [a for a in sys.argv[1:] if a.startswith('/Game')] or [
    '/Game/Game/Imported/CleaverBoss/Anims', '/Game/Game/Imported/CafeWalker/Anims',
    '/Game/Game/Imported/CafeWalker/MeshyAnims', '/Game/Game/Imported/StreetGoon/MeshyAnims']
R = {'mode': 'fix' if 'fix' in sys.argv[1:] else 'measure', 'clips': {}}


def lift(an):
    X = unreal.AnimPoseExtensions
    o = unreal.AnimPoseEvaluationOptions()
    o.set_editor_property('extract_root_motion', True)
    n = unreal.AnimationLibrary.get_num_frames(an)
    lo, hi = 1e9, -1e9
    for fr in range(0, n, max(1, n // 8)):
        pose = X.get_anim_pose_at_frame(an, fr, o)
        z = min(X.get_bone_pose(pose, b, unreal.AnimPoseSpaces.WORLD).translation.z for b in X.get_bone_names(pose))
        lo, hi = min(lo, z), max(hi, z)
    return [round(lo, 1), round(hi, 1)]


try:
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    f = unreal.ARFilter(package_paths=FOLDERS, class_paths=[unreal.TopLevelAssetPath('/Script/Engine', 'AnimSequence')])
    changed = []
    for ad in sorted(ar.get_assets(f), key=lambda a: str(a.asset_name)):
        an = ad.get_asset()
        row = {'root_motion': an.get_editor_property('enable_root_motion'), 'lock_before': str(an.get_editor_property('root_motion_root_lock')), 'lift_before': lift(an)}
        if R['mode'] == 'fix' and row['root_motion'] and row['lift_before'][1] > 5.0:  # only clips that really ride high
            an.modify()
            an.set_editor_property('root_motion_root_lock', unreal.RootMotionRootLock.ANIM_FIRST_FRAME)
            changed.append(an)
            row['lock_after'] = str(an.get_editor_property('root_motion_root_lock'))
            row['lift_after'] = lift(an)
        R['clips'][str(ad.asset_name)] = row
    if changed:
        R['saved'] = unreal.EditorLoadingAndSavingUtils.save_packages([a.get_outermost() for a in changed], False)
        R['changed'] = len(changed)
except Exception:
    R['error'] = traceback.format_exc()
open(OUT, 'w').write(json.dumps(R, indent=1))
