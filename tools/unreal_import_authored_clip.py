"""Imports a clip AUTHORED IN BLENDER onto a character's EXISTING skeleton (issues #103, #14).

Everything in /Game/Game/Imported/<Char>/MeshyAnims/ got there by retargeting Epic's mannequin
(tools/unreal_retarget_meshy.py). This is the other route: an FBX written by
Art/Blender/death_clip.py - our own pose work on our own rig - imported as an AnimSequence
against the skeleton that is already in the game, plus a montage to play it from Blueprint.

Run it in the Unreal editor's console box (Cmd), with Play mode stopped:
    py <repo>/tools/unreal_import_authored_clip.py <fbx> <skeleton> <dest folder> <anim name> [montage|anim]
    py .../unreal_import_authored_clip.py \
       <repo>/Art/Blender/export/Characters/CafeWalker/SK_CafeWalker_Death.fbx \
       /Game/Game/Imported/CafeWalker/Meshy/SK_CafeWalker_Skeleton \
       /Game/Game/Imported/CafeWalker/Authored A_CafeWalker_Death_Authored montage

WHY IT PINS THE SKELETON, AND WHY THAT IS THE WHOLE JOB. Imported with default settings this FBX
brings its mesh with it and Interchange builds a SECOND skeleton for it. An AnimSequence on a
skeleton no character wears will never play - and it will import, save and read back perfectly
while doing so. That is exactly the class of silent failure issue #103 is about, and it is why
this script refuses to finish unless the imported clip's skeleton is the same OBJECT as the one
already in the game.

WHY INTERCHANGE AND NOT FbxImportUI. jump-cut's DefaultEngine.ini routes
InterchangeFbxTranslator -> DefaultFBXOBJAssetsPipeline, so FBX goes through Interchange here.
`unreal.AssetImportTask(options=unreal.FbxImportUI(...))` - the usual recipe, and the one the
first draft of this script used - configures the LEGACY FBX importer, which is not the importer
this project's config sends an FBX to. That was not tested to destruction: the point is that its
`skeleton` setting is not the one Interchange reads, so relying on it here is a guess, and the
failure if the guess is wrong is a silent second skeleton rather than an error.
Interchange is configured through a pipeline ASSET instead (FImportAssetParameters.OverridePipelines
is an array of FSoftObjectPath, so it cannot take a transient object), hence the duplicate-
configure-import-delete dance below.

The four settings that matter, all verified against UE 5.8's own headers:
    CommonSkeletalMeshesAndAnimationsProperties.bImportOnlyAnimations = true
    CommonSkeletalMeshesAndAnimationsProperties.Skeleton             = the existing skeleton
    MeshPipeline.bImportStaticMeshes / bImportSkeletalMeshes          = false
    AnimationPipeline.bImportAnimations                               = true

WHAT IT CHECKS AFTERWARDS, because "imported ok" is not evidence:
  * the AnimSequence exists and its skeleton is the one we asked for, BY OBJECT IDENTITY;
  * the clip has a non-zero length, and its frame count is reported so it can be read against
    the frame range Blender exported;
  * root_motion_root_lock is AnimFirstFrame, the setting commit 7ef73e1 had to apply to 44 clips
    after the player and the goons were found floating;
  * the montage sits on DefaultSlot, like AM_CafeWalker_Death and every other montage here;
  * enable_auto_blend_out is OFF, or the dead body stands back up.
Results go to Saved/jc_authored_clip.txt. Nothing is saved to disk - saving is the builder's call,
as everywhere else in tools/.
"""
import os
import sys

import unreal

PIPE_SRC = '/Interchange/Pipelines/DefaultFBXOBJAssetsPipeline'
PIPE_TMP = '/Game/Game/Imported/_jc_anim_only_pipeline'

log = []


def say(s):
    log.append(s)
    unreal.log('[authored-clip] %s' % s)


def make_pipeline(skel):
    """A one-shot copy of the project's FBX pipeline, set to animation-only on OUR skeleton."""
    if unreal.EditorAssetLibrary.does_asset_exist(PIPE_TMP):
        unreal.EditorAssetLibrary.delete_asset(PIPE_TMP)
    if not unreal.EditorAssetLibrary.duplicate_asset(PIPE_SRC, PIPE_TMP):
        say('REFUSING: could not duplicate %s - is the Interchange plugin content mounted?' % PIPE_SRC)
        return None
    p = unreal.EditorAssetLibrary.load_asset(PIPE_TMP)
    common = p.get_editor_property('common_skeletal_meshes_and_animations_properties')
    common.set_editor_property('import_only_animations', True)
    common.set_editor_property('skeleton', skel)
    mesh = p.get_editor_property('mesh_pipeline')
    mesh.set_editor_property('import_static_meshes', False)
    mesh.set_editor_property('import_skeletal_meshes', False)
    anim = p.get_editor_property('animation_pipeline')
    anim.set_editor_property('import_animations', True)
    anim.set_editor_property('import_bone_tracks', True)
    unreal.EditorAssetLibrary.save_loaded_asset(p, False)
    say('pipeline %s: import_only_animations=%s skeleton=%s import_skeletal_meshes=%s'
        % (PIPE_TMP, common.get_editor_property('import_only_animations'),
           skel.get_name(), mesh.get_editor_property('import_skeletal_meshes')))
    return p


def main():
    a = sys.argv[1:]
    if len(a) < 4:
        say('usage: <fbx> <skeleton> <dest folder> <anim name> [montage|anim]')
        return
    fbx, skel_path, dest, name = a[0], a[1], a[2], a[3]
    want_montage = (a[4] if len(a) > 4 else 'montage') == 'montage'

    if not os.path.isfile(fbx):
        say('REFUSING: no such file %s' % fbx)
        return
    if not unreal.EditorAssetLibrary.does_asset_exist(skel_path):
        say('REFUSING: skeleton %s does not exist - importing would build a second one, '
            'and a clip on a skeleton nobody wears never plays' % skel_path)
        return
    skel = unreal.EditorAssetLibrary.load_asset(skel_path)
    before = set(unreal.EditorAssetLibrary.list_assets(dest, recursive=False)) \
        if unreal.EditorAssetLibrary.does_directory_exist(dest) else set()

    pipeline = make_pipeline(skel)
    if pipeline is None:
        return
    try:
        params = unreal.ImportAssetParameters()
        params.set_editor_property('is_automated', True)
        params.set_editor_property('replace_existing', True)
        params.set_editor_property('override_pipelines', [unreal.SoftObjectPath(PIPE_TMP)])
        src = unreal.InterchangeManager.create_source_data(fbx)
        mgr = unreal.InterchangeManager.get_interchange_manager_scripted()
        mgr.import_asset(dest, src, params)
    finally:
        if unreal.EditorAssetLibrary.does_asset_exist(PIPE_TMP):
            unreal.EditorAssetLibrary.delete_asset(PIPE_TMP)

    after = set(unreal.EditorAssetLibrary.list_assets(dest, recursive=False))
    new = sorted(after - before)
    anims = [p for p in new
             if isinstance(unreal.EditorAssetLibrary.load_asset(p), unreal.AnimSequence)]
    say('new assets in %s: %s' % (dest, ', '.join(n.split('/')[-1] for n in new) or '(none)'))
    if not anims:
        say('FAILED: no AnimSequence was created. If a SkeletalMesh appeared instead, the '
            'pipeline override did not take.')
        return
    if len(anims) > 1:
        say('NOTE: %d AnimSequences came out of one FBX - the file holds more than one action.'
            % len(anims))
    anim_path = anims[0]
    anim = unreal.EditorAssetLibrary.load_asset(anim_path)

    got = anim.get_editor_property('skeleton')
    if got != skel:
        say('REFUSING to go further: %s is on %s, not %s. This clip would never play.'
            % (anim_path, got.get_path_name() if got else '(none)', skel_path))
        return
    say('skeleton matches the one in the game, by object identity: %s' % skel_path)

    want = '%s/%s' % (dest.rstrip('/'), name)
    if anim_path != want:
        unreal.EditorAssetLibrary.rename_asset(anim_path, want)
        anim_path = want
        anim = unreal.EditorAssetLibrary.load_asset(anim_path)
    say('imported %s' % anim_path)
    say('  length %.3f s, %d sampled keys, rate %s'
        % (anim.get_play_length(), anim.get_number_of_sampled_keys(), anim.get_sampling_frame_rate()))

    # ROOT MOTION MUST BE OFF on an authored clip from this rig, and getting it wrong is the
    # float defect all over again. A Meshy Smart Rig's root (Bone_000) sits at PELVIS height and
    # carries skin weight, so Art/Blender/death_clip.py keys the whole fall on it. Extract that as
    # root motion and AnimFirstFrame pins the pelvis at standing height - the body falls out from
    # under itself and the character hangs in the air. Keyed-in-place is what we want.
    anim.set_editor_property('enable_root_motion', False)
    # 7ef73e1 found 44 clips still on RefPose, which is what made the player and the goons float.
    # Harmless while root motion is off, but match the project rather than inherit a default.
    anim.set_editor_property('root_motion_root_lock', unreal.RootMotionRootLock.ANIM_FIRST_FRAME)
    say('  enable_root_motion: %s   root_motion_root_lock: %s'
        % (anim.get_editor_property('enable_root_motion'),
           anim.get_editor_property('root_motion_root_lock')))

    if not want_montage:
        say('NOTHING WAS SAVED. Save %s before committing.' % anim_path)
        return

    mont_name = ('AM_' + name[2:]) if name.startswith('A_') else ('AM_' + name)
    mont_path = '%s/%s' % (dest.rstrip('/'), mont_name)
    if unreal.EditorAssetLibrary.does_asset_exist(mont_path):
        unreal.EditorAssetLibrary.delete_asset(mont_path)
    factory = unreal.AnimMontageFactory()
    factory.set_editor_property('target_skeleton', skel)
    mont = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        mont_name, dest.rstrip('/'), unreal.AnimMontage, factory)
    if mont is None:
        say('FAILED: could not create %s' % mont_path)
        return

    seg = unreal.AnimSegment()
    seg.set_editor_property('anim_reference', anim)
    seg.set_editor_property('start_pos', 0.0)
    seg.set_editor_property('anim_start_time', 0.0)
    seg.set_editor_property('anim_end_time', anim.get_play_length())
    seg.set_editor_property('anim_play_rate', 1.0)
    seg.set_editor_property('loop_count', 1)
    track = unreal.AnimTrack()
    track.set_editor_property('anim_segments', [seg])
    slot = unreal.SlotAnimationTrack()
    slot.set_editor_property('slot_name', 'DefaultSlot')
    slot.set_editor_property('anim_track', track)
    mont.set_editor_property('slot_anim_tracks', [slot])
    mont.set_editor_property('enable_auto_blend_out', False)   # a death montage holds its last pose

    read = mont.get_editor_property('slot_anim_tracks')
    say('made %s  slot=%s  segments=%d  auto_blend_out=%s'
        % (mont_path, read[0].get_editor_property('slot_name'),
           len(read[0].get_editor_property('anim_track').get_editor_property('anim_segments')),
           mont.get_editor_property('enable_auto_blend_out')))
    say('NOTHING WAS SAVED. Save %s and %s in the editor before committing.'
        % (anim_path, mont_path))


try:
    main()
except Exception:
    import traceback
    say('EXCEPTION:\n' + traceback.format_exc())

out = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())
with open(os.path.join(out, 'jc_authored_clip.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(log) + '\n')
