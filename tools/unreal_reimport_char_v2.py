"""Re-import a V2 character body OVER the asset the game actually uses.

    UnrealEditor-Cmd.exe <uproject> -run=pythonscript -script="<repo>/tools/unreal_reimport_char_v2.py [save]"

WHY THIS EXISTS, SEPARATELY FROM unreal_import_char_v2.py. That script imports a FBX into a folder and then
renames whatever came out to SK_<Name>. That is right the FIRST time and silently wrong every time after:
Interchange names the new asset after the FBX file (SK_CafeWalkerV2_oldrig), the rename is skipped because
SK_CafeWalkerV2 already exists, and the script then validates - and reports a clean bill of health on - the
OLD asset, while the new geometry sits in a duplicate nobody references. The run looks perfect. BP_Player
keeps the body it had.

Worse, the usual sanity checks cannot see it. Re-posing a mesh does not change its vertex count, its material
slot, its skeleton or its bone count, so every check in that script passes either way. The only property that
moves is the BOUNDS, so that is what this one checks, against numbers measured in Blender.

So: delete the duplicate, re-import with reimport_asset pointed at the real asset, and prove it landed by
reading the bounds back.
"""
import os
import sys
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'reimport_char_v2.txt')
REPO = os.path.abspath(os.path.join(unreal.Paths.project_dir(), '..'))
ART = os.path.join(REPO, 'Art', 'Blender', 'export', 'Characters')

PIPE_SRC = '/Interchange/Pipelines/DefaultFBXOBJAssetsPipeline'
PIPE_TMP = '/Game/Game/Imported/_jc_reimport_pipeline'

TARGET = '/Game/Game/Imported/CafeWalkerV2/SK_CafeWalkerV2'
SKEL = '/Game/Game/Imported/CafeWalker/Meshy/SK_CafeWalker_Skeleton'
FBX = os.path.join(ART, 'CafeWalkerV2', 'SK_CafeWalkerV2_oldrig.fbx')
STRAY = [
    '/Game/Game/Imported/CafeWalkerV2/SK_CafeWalkerV2_oldrig',
    '/Game/Game/Imported/CafeWalkerV2/SK_CafeWalkerV2_oldrig_PhysicsAsset',
]
MAT = '/Game/Game/Materials/MI_CafeWalkerV2'
TEX = '/Game/Game/Imported/CafeWalkerV2/T_CafeWalkerV2_BaseColor'
TEX_SRC = os.path.join(ART, 'CafeWalkerV2', 'T_CafeWalkerV2_BaseColor.png')
# UNREAL world cm. Art/Blender/rebuild_walker_v2.py prints these in BLENDER axes; our FBX settings send
# Blender +Y to Unreal -Y, so the y pair is negated AND swapped here: Blender y[-22.31 17.88] is Unreal
# y[-17.88 22.31]. x and z carry straight across. Getting that backwards makes a good import read as a
# failure, which is how the table stays honest.
# Nov 15: model_tuneup.py lengthened the arms for one round (x -59.94..60.86) and then put the length back.
WANT = {'x': (-55.58, 56.46), 'y': (-17.88, 22.31), 'z': (0.0, 174.39)}
TOL = 2.0

eal = unreal.EditorAssetLibrary
log = []


def say(s):
    log.append(str(s))
    unreal.log('[reimport-v2] %s' % s)


def flush():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')


def bounds(mesh):
    b = mesh.get_bounds()
    o, e = b.origin, b.box_extent
    return {'x': (o.x - e.x, o.x + e.x), 'y': (o.y - e.y, o.y + e.y), 'z': (o.z - e.z, o.z + e.z)}


def show(tag, bb):
    say('%s bounds  x[%7.2f %7.2f]  y[%7.2f %7.2f]  z[%7.2f %7.2f]'
        % (tag, bb['x'][0], bb['x'][1], bb['y'][0], bb['y'][1], bb['z'][0], bb['z'][1]))


def main():
    do_save = 'save' in [a.lower() for a in sys.argv[1:]]
    say('repo=%s save=%s' % (REPO, do_save))
    if not os.path.isfile(FBX):
        say('REFUSING: no such file %s' % FBX)
        return
    if not eal.does_asset_exist(TARGET):
        say('REFUSING: %s does not exist - use unreal_import_char_v2.py for a first import' % TARGET)
        return

    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    ar.scan_paths_synchronous(['/Interchange/Pipelines'], True)
    ar.wait_for_completion()

    for s in STRAY:
        if eal.does_asset_exist(s):
            say('deleting duplicate left by the import path: %s' % s)
            eal.delete_asset(s)

    mesh = eal.load_asset(TARGET)
    before = bounds(mesh)
    show('before', before)

    if eal.does_asset_exist(PIPE_TMP):
        eal.delete_asset(PIPE_TMP)
    if not eal.duplicate_asset(PIPE_SRC, PIPE_TMP):
        say('REFUSING: could not duplicate %s' % PIPE_SRC)
        return
    p = eal.load_asset(PIPE_TMP)
    common = p.get_editor_property('common_skeletal_meshes_and_animations_properties')
    common.set_editor_property('import_only_animations', False)
    common.set_editor_property('skeleton', eal.load_asset(SKEL))
    # The rest pose is the skeleton's, and 48 clips are keyed against it. Never let an import move it.
    try:
        common.set_editor_property('update_skeleton_reference_pose', False)
    except Exception as e:
        say('note: update_skeleton_reference_pose not settable (%s)' % e)
    m = p.get_editor_property('mesh_pipeline')
    m.set_editor_property('import_static_meshes', False)
    m.set_editor_property('import_skeletal_meshes', True)
    a = p.get_editor_property('animation_pipeline')
    a.set_editor_property('import_animations', False)
    eal.save_loaded_asset(p, False)

    try:
        params = unreal.ImportAssetParameters()
        params.set_editor_property('is_automated', True)
        params.set_editor_property('replace_existing', True)
        params.set_editor_property('reimport_asset', mesh)
        params.set_editor_property('override_pipelines', [unreal.SoftObjectPath(PIPE_TMP)])
        src = unreal.InterchangeManager.create_source_data(FBX)
        mgr = unreal.InterchangeManager.get_interchange_manager_scripted()
        mgr.import_asset('/Game/Game/Imported/CafeWalkerV2', src, params)
    finally:
        if eal.does_asset_exist(PIPE_TMP):
            eal.delete_asset(PIPE_TMP)

    mesh = eal.load_asset(TARGET)
    after = bounds(mesh)
    show('after ', after)
    say('want   x[%7.2f %7.2f]  y[%7.2f %7.2f]  z[%7.2f %7.2f]  (Blender, +-%.1f cm)'
        % (WANT['x'][0], WANT['x'][1], WANT['y'][0], WANT['y'][1], WANT['z'][0], WANT['z'][1], TOL))

    bad = []
    for ax in 'xyz':
        for i in (0, 1):
            if abs(after[ax][i] - WANT[ax][i]) > TOL:
                bad.append('%s[%d] %.2f vs %.2f' % (ax, i, after[ax][i], WANT[ax][i]))
    if bad:
        if after == before:
            say('FAILED: bounds did not move at all - the re-import was a no-op')
        else:
            say('FAILED: bounds do not match the FBX Blender measured: %s' % '; '.join(bad))
        return
    if after == before:
        say('note: bounds already matched WANT before this run - this is a re-run, geometry unchanged')
    say('bounds match the FBX Blender measured - the new geometry is in the asset the game uses')

    skel = mesh.get_editor_property('skeleton')
    say('skeleton: %s' % (skel.get_path_name() if skel else '(none)'))
    if skel is None or skel.get_path_name().split('.')[0] != SKEL:
        say('FAILED: skeleton is not %s' % SKEL)
        return
    # A re-import can hand the slot back as WorldGridMaterial - Interchange matches slots by the FBX's own
    # material name, and a rebuilt FBX need not use the same one. It does not error. The character simply
    # renders as grey checkerboard. So put MI_CafeWalkerV2 back, and say so.
    # get_editor_property('materials') returns COPIES of the slot structs: mutating them in place is
    # silently discarded. The whole array has to be set back.
    mi = eal.load_asset(MAT)
    slots = mesh.get_editor_property('materials')
    names = [str(s.material_interface.get_path_name()) if s.material_interface else None for s in slots]
    say('material slots after import: %s' % names)
    if mi is None:
        say('WARNING: %s missing - cannot restore the material slot' % MAT)
    elif any(n is None or n.split('.')[0] != MAT for n in names):
        # Fresh structs, not the copies get_editor_property handed back - mutating those is discarded
        # silently (the lesson from unreal_import_char_v2.py, and it caught this script out once).
        fresh = []
        for s in slots:
            sm = unreal.SkeletalMaterial()
            sm.set_editor_property('material_interface', mi)
            sm.set_editor_property('material_slot_name', s.get_editor_property('material_slot_name'))
            fresh.append(sm)
        mesh.set_editor_property('materials', fresh)
        names = [str(s.material_interface.get_path_name()) if s.material_interface else None
                 for s in mesh.get_editor_property('materials')]
        say('material slots restored: %s' % names)
        if any(n is None or n.split('.')[0] != MAT for n in names):
            say('FAILED: could not restore the material slot')
            return

    # The base colour and the mesh share ONE UV space. Replacing the mesh without replacing the texture
    # (or the reverse) does not error - it renders as camouflage noise. So they go together, in one run.
    tex_ok = reimport_texture()

    if do_save:
        for path in [TARGET, TARGET + '_PhysicsAsset'] + ([TEX] if tex_ok else []):
            if eal.does_asset_exist(path):
                say('saved %s -> %s' % (path, eal.save_asset(path, False)))
        if not tex_ok:
            say('WARNING: texture NOT saved - mesh and base colour are now out of step')
    else:
        say('not saved (pass `save`)')


def reimport_texture():
    if not os.path.isfile(TEX_SRC):
        say('REFUSING texture: no such file %s' % TEX_SRC)
        return False
    if not eal.does_asset_exist(TEX):
        say('REFUSING texture: %s does not exist' % TEX)
        return False
    tex = eal.load_asset(TEX)
    try:
        params = unreal.ImportAssetParameters()
        params.set_editor_property('is_automated', True)
        params.set_editor_property('replace_existing', True)
        params.set_editor_property('reimport_asset', tex)
        src = unreal.InterchangeManager.create_source_data(TEX_SRC)
        mgr = unreal.InterchangeManager.get_interchange_manager_scripted()
        mgr.import_asset('/Game/Game/Imported/CafeWalkerV2', src, params)
    except Exception as e:
        say('texture re-import raised: %s' % e)
        return False
    tex = eal.load_asset(TEX)
    say('texture %s imported_size=%sx%s' % (TEX, tex.blueprint_get_size_x(), tex.blueprint_get_size_y()))
    return True


try:
    main()
finally:
    flush()
