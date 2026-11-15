"""Bring a batch of the player's authored clips into Unreal in one go and save them.

Run in the Unreal editor's console box, Play mode stopped:
    py <repo>/tools/unreal_import_player_clips.py Jump Fall Land
Result: <project>/Saved/jcpy/import_player_clips.txt

For each name it takes Art/Blender/export/Characters/CafeWalkerV2/SK_CafeWalkerV2_<Name>.fbx and makes (or, if it is
already there, re-imports over) /Game/Game/Imported/CafeWalker/Authored/A_CafeWalker_<Name>_Authored, by running
the two single-clip tools - unreal_import_authored_clip.py the first time, unreal_reimport_authored_clip.py after
that - so their checks (same skeleton object, root lock AnimFirstFrame) all still apply. Then it reads each clip
back: length, skeleton, root motion and root lock, and where the root and hip sit at the first frame, and saves the
new clip's own package.
"""
import os
import runpy
import sys
import unreal

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'import_player_clips.txt')
SKEL = '/Game/Game/Imported/CafeWalker/Meshy/SK_CafeWalker_Skeleton'
DEST = '/Game/Game/Imported/CafeWalker/Authored'
eal = unreal.EditorAssetLibrary
E = unreal.AnimPoseExtensions
log = []
names = sys.argv[1:]
try:
    unreal.AssetRegistryHelpers.get_asset_registry().scan_paths_synchronous([DEST], True)
    for n in names:
        fbx = os.path.join(REPO, 'Art', 'Blender', 'export', 'Characters', 'CafeWalkerV2', 'SK_CafeWalkerV2_%s.fbx' % n).replace('\\', '/')
        asset = 'A_CafeWalker_%s_Authored' % n
        path = '%s/%s' % (DEST, asset)
        if not os.path.isfile(fbx):
            log.append('%s: NO FBX at %s' % (n, fbx))
            continue
        first = eal.load_asset(path) is None
        if first:
            sys.argv = ['x', fbx, SKEL, DEST, asset, 'anim']
            runpy.run_path(os.path.join(HERE, 'unreal_import_authored_clip.py'), run_name='__main__')
        else:
            sys.argv = ['x', fbx, path]
            runpy.run_path(os.path.join(HERE, 'unreal_reimport_authored_clip.py'), run_name='__main__')
        a = eal.load_asset(path)
        if not isinstance(a, unreal.AnimSequence):
            log.append('%s: FAILED, no AnimSequence at %s after %s' % (n, path, 'import' if first else 're-import'))
            continue
        a.set_editor_property('enable_root_motion', False)
        a.set_editor_property('root_motion_root_lock', unreal.RootMotionRootLock.ANIM_FIRST_FRAME)
        o = unreal.AnimPoseEvaluationOptions()
        o.set_editor_property('extract_root_motion', False)
        pose = E.get_anim_pose_at_time(a, 0.0, o)
        r = E.get_bone_pose(pose, 'Bone_000', unreal.AnimPoseSpaces.WORLD).translation
        h = E.get_bone_pose(pose, 'Bone_001', unreal.AnimPoseSpaces.WORLD).translation
        ok = unreal.EditorLoadingAndSavingUtils.save_packages([a.get_outermost()], False)
        log.append('%s: %s  %.3f s  skeleton %s  root motion %s  lock %s  root (%.1f %.1f %.1f) hip z %.1f  saved %s' % (
            n, 'imported' if first else 're-imported', a.get_play_length(), a.get_editor_property('skeleton').get_name(),
            a.get_editor_property('enable_root_motion'), a.get_editor_property('root_motion_root_lock'), r.x, r.y, r.z, h.z, ok))
except Exception:
    import traceback
    log.append('ERROR ' + traceback.format_exc())
finally:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')
