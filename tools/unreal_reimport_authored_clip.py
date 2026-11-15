"""Re-import a clip authored in Blender OVER the AnimSequence the game already plays.

Run in the Unreal editor's console box, Play mode stopped, after `git lfs lock` on the asset:
    py <repo>/tools/unreal_reimport_authored_clip.py <fbx> <existing anim asset> [save]
    py .../unreal_reimport_authored_clip.py <repo>/Art/Blender/export/Characters/CafeWalkerV2/SK_CafeWalkerV2_Idle.fbx \
       /Game/Game/Imported/CafeWalker/Authored/A_CafeWalker_Idle_Authored save
Result: <project>/Saved/jcpy/reimport_authored_clip.txt

WHY NOT unreal_import_authored_clip.py AGAIN. That script imports under the FBX's own name and renames the result,
which is right the first time and cannot work the second: the name is taken, and the asset that holds it is the one
the anim blueprint points at. Deleting it first would null that pointer in the running editor (the stale-session
trap, Nov 14). So this one hands Interchange the existing asset as `reimport_asset`, the same way
unreal_reimport_char_v2.py does for a body, and the anim blueprint never loses its reference.

A re-import that silently did nothing reads back as a perfectly healthy clip, so this proves the content changed:
it records where six bones are at the first frame before and after, and reports the largest move. It also puts back
the two settings an authored clip on a Meshy rig needs (root motion off, root lock AnimFirstFrame), because a fresh
import resets them and RefPose is the float bug.
"""
import os
import sys
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'reimport_authored_clip.txt')
PIPE_SRC = '/Interchange/Pipelines/DefaultFBXOBJAssetsPipeline'
PIPE_TMP = '/Game/Game/Imported/_jc_reimport_clip_pipeline'
PROBE = ['Bone_000', 'Bone_001', 'Bone_008', 'Bone_013', 'Bone_020', 'Bone_025']
eal = unreal.EditorAssetLibrary
E = unreal.AnimPoseExtensions
log = []


def say(s):
    log.append(str(s))
    unreal.log('[reimport-clip] %s' % s)


def probe(anim):
    o = unreal.AnimPoseEvaluationOptions()
    o.set_editor_property('extract_root_motion', False)
    pose = E.get_anim_pose_at_time(anim, 0.0, o)
    have = set(str(b) for b in E.get_bone_names(pose))
    return {b: E.get_bone_pose(pose, b, unreal.AnimPoseSpaces.WORLD).translation for b in PROBE if b in have}


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        say('usage: <fbx> <existing anim asset> [save]')
        return
    fbx, target, do_save = args[0], args[1], 'save' in [a.lower() for a in args[2:]]
    if not os.path.isfile(fbx):
        say('REFUSING: no such file %s' % fbx)
        return
    anim = eal.load_asset(target)
    if not isinstance(anim, unreal.AnimSequence):
        say('REFUSING: %s is not an AnimSequence' % target)
        return
    skel = anim.get_editor_property('skeleton')
    before = probe(anim)
    len_before = anim.get_play_length()
    say('before: %s  length %.3f s  skeleton %s' % (anim.get_name(), len_before, skel.get_name()))

    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    ar.scan_paths_synchronous(['/Interchange/Pipelines'], True)
    if eal.does_asset_exist(PIPE_TMP):
        eal.delete_asset(PIPE_TMP)
    if not eal.duplicate_asset(PIPE_SRC, PIPE_TMP):
        say('REFUSING: could not duplicate %s' % PIPE_SRC)
        return
    p = eal.load_asset(PIPE_TMP)
    common = p.get_editor_property('common_skeletal_meshes_and_animations_properties')
    common.set_editor_property('import_only_animations', True)
    common.set_editor_property('skeleton', skel)
    m = p.get_editor_property('mesh_pipeline')
    m.set_editor_property('import_static_meshes', False)
    m.set_editor_property('import_skeletal_meshes', False)
    p.get_editor_property('animation_pipeline').set_editor_property('import_animations', True)
    eal.save_loaded_asset(p, False)
    folder = target.rsplit('/', 1)[0]
    listed = set(eal.list_assets(folder, recursive=False))
    try:
        params = unreal.ImportAssetParameters()
        params.set_editor_property('is_automated', True)
        params.set_editor_property('replace_existing', True)
        params.set_editor_property('reimport_asset', anim)
        params.set_editor_property('override_pipelines', [unreal.SoftObjectPath(PIPE_TMP)])
        src = unreal.InterchangeManager.create_source_data(fbx)
        unreal.InterchangeManager.get_interchange_manager_scripted().import_asset(folder, src, params)
    finally:
        if eal.does_asset_exist(PIPE_TMP):
            eal.delete_asset(PIPE_TMP)

    stray = sorted(set(eal.list_assets(folder, recursive=False)) - listed)
    if stray:
        say('WARNING: the import made NEW assets instead of replacing: %s' % ', '.join(s.split('/')[-1] for s in stray))
    anim = eal.load_asset(target)
    if anim.get_editor_property('skeleton') != skel:
        say('FAILED: the clip is no longer on %s' % skel.get_name())
        return
    after = probe(anim)
    moved = max((after[b] - before[b]).length() for b in before if b in after) if before else -1.0
    say('after:  length %.3f s; largest move of a probed bone at the first frame %.2f cm' % (anim.get_play_length(), moved))
    for b in sorted(after):
        say('    %s  (%.1f %.1f %.1f) -> (%.1f %.1f %.1f)' % (b, before[b].x, before[b].y, before[b].z, after[b].x, after[b].y, after[b].z))
    if moved < 0.01 and abs(anim.get_play_length() - len_before) < 1e-4:
        say('NOTE: nothing measurable changed. Either the FBX is the clip that was already there, or the re-import was a no-op.')
    anim.set_editor_property('enable_root_motion', False)
    anim.set_editor_property('root_motion_root_lock', unreal.RootMotionRootLock.ANIM_FIRST_FRAME)
    say('enable_root_motion %s, root lock %s' % (anim.get_editor_property('enable_root_motion'), anim.get_editor_property('root_motion_root_lock')))
    if do_save and not stray:
        say('saved %s -> %s' % (target, unreal.EditorLoadingAndSavingUtils.save_packages([anim.get_outermost()], False)))
    else:
        say('NOT saved' + (' (stray assets: sort those out first)' if stray else ' (pass `save`)'))


try:
    main()
except Exception:
    import traceback
    say('ERROR ' + traceback.format_exc())
finally:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')
