"""Point the CafeWalker skeleton's EDITOR PREVIEW at the body the game actually runs.

    UnrealEditor-Cmd.exe <uproject> -run=pythonscript -script="<repo>/tools/unreal_fix_preview_meshes.py [save]"

WHY THIS MATTERS, and it is not cosmetic. SK_CafeWalker_Skeleton's PreviewSkeletalMesh is the body Unreal
shows you whenever you open a clip, a montage, a blend space or ABP_Unarmed_CWM. It pointed at V1 - the old
body, whose apron hangs like a skirt and whose forty finger bones all work. The game runs SK_CafeWalkerV2.
So an animator could key a hand pose, watch it read perfectly in the preview, and ship a clip that looks
nothing like that in play.

ONE ASSET, NOT FORTY-ONE, and the difference is worth writing down. 40 of the 72 animation assets under
CafeWalker do hold a soft reference to the V1 body, which looks exactly like a per-clip preview override -
and reading the .uasset name tables is how that conclusion was first reached, wrongly. Asked directly, every
one of them reports preview_pose_asset = None and exposes no preview-mesh property at all; the reference is
RETARGET_SOURCE_ASSET, the mesh whose proportions the clip was authored against. That is correct and must be
left alone: these clips were retargeted on the V1-bound rig, and repointing it would change how every one of
them is interpreted. Only USkeleton carries a preview mesh here, and every other asset inherits it.

Python exposes this as get_skeleton_preview_mesh / set_skeleton_preview_mesh on USkeleton. There is no
'preview_mesh' editor property - get_editor_property('preview_mesh') raises, which reads exactly like
"the preview is unset" and is not.
"""
import os
import sys
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'fix_preview_meshes.txt')

WANT_MESH = '/Game/Game/Imported/CafeWalkerV2/SK_CafeWalkerV2'
SKELETON = '/Game/Game/Imported/CafeWalker/Meshy/SK_CafeWalker_Skeleton'
AUDIT_ROOT = '/Game/Game/Imported/CafeWalker'

eal = unreal.EditorAssetLibrary
log = []


def say(s):
    log.append(str(s))
    unreal.log('[preview] %s' % s)


def flush():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')


def short(o):
    if o is None:
        return '(none)'
    try:
        return o.get_path_name().split('.')[0]
    except Exception:
        return str(o)


def main():
    do_save = 'save' in [a.lower() for a in sys.argv[1:]]
    say('save=%s  want=%s' % (do_save, WANT_MESH))
    if not eal.does_asset_exist(WANT_MESH):
        say('REFUSING: %s does not exist' % WANT_MESH)
        return
    mesh = eal.load_asset(WANT_MESH)
    if short(mesh.get_editor_property('skeleton')) != SKELETON:
        say('REFUSING: %s is not on %s' % (WANT_MESH, SKELETON))
        return

    sk = eal.load_asset(SKELETON)
    before = sk.get_skeleton_preview_mesh()
    say('preview mesh was: %s' % short(before))
    changed = False
    if short(before) != WANT_MESH:
        sk.set_skeleton_preview_mesh(mesh)
        now = sk.get_skeleton_preview_mesh()
        say('preview mesh now: %s' % short(now))
        if short(now) != WANT_MESH:
            say('FAILED: set_skeleton_preview_mesh did not take')
            return
        changed = True
    else:
        say('already correct')

    # Audit only - say plainly what the clips point at, and do not touch it.
    say('')
    say('retarget sources (reported, NOT changed - this is the proportions the clip was authored for):')
    counts = {}
    for p in sorted(set(x.split('.')[0] for x in eal.list_assets(AUDIT_ROOT, recursive=True))):
        a = eal.load_asset(p)
        if not isinstance(a, unreal.AnimSequence):
            continue
        try:
            rsa = a.get_editor_property('retarget_source_asset')
        except Exception:
            continue
        counts[short(rsa)] = counts.get(short(rsa), 0) + 1
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        say('   %4d clips -> %s' % (v, k))

    if changed and do_save:
        say('')
        say('saved %s -> %s' % (SKELETON, eal.save_asset(SKELETON, False)))
    elif changed:
        say('not saved (pass `save`)')


try:
    main()
finally:
    flush()
