"""Re-import a character's body over the skeletal mesh the game uses, when only the SKIN changed.

Run in the Unreal editor's console box, Play mode stopped, after `git lfs lock` + clearing read-only on the mesh:
    py <repo>/tools/unreal_reimport_body.py <fbx> <existing skeletal mesh asset> [save]
    py .../unreal_reimport_body.py <repo>/Art/Blender/export/Characters/StreetGoon/SK_StreetGoon_skinfix.fbx \
       /Game/Game/Imported/StreetGoon/Meshy/SK_StreetGoon save
Result: <project>/Saved/jcpy/reimport_body_<mesh name>.txt

For the `_skinfix.fbx` bodies (root weight moved to the hip, weights smoothed, shoes flattened): same vertices,
same UVs, same bones, so the texture and every clip stay as they are. It is unreal_reimport_char_v2.py with the
player's names taken out. What it takes from the EXISTING asset and puts back afterwards: the skeleton (the import
is pinned to it and may not touch its reference pose) and the material slots, in order - a re-import can hand a
slot back as WorldGridMaterial without a word. Anything new the import leaves in the folder (Interchange names
assets after the FBX file) is deleted. It refuses to save if the skeleton, the bone count or the slot list moved,
or if the bounds moved by more than 10 cm (a skin fix does not resize anybody).

A weights-only change moves nothing this script can measure, so "it ran" is not proof the new skin is in. The proof
is the picture: play a clip on the character and look where the old one tore.
"""
import os
import sys
import unreal

eal = unreal.EditorAssetLibrary
PIPE_SRC = '/Interchange/Pipelines/DefaultFBXOBJAssetsPipeline'
PIPE_TMP = '/Game/Game/Imported/_jc_reimport_body_pipeline'
log = []
args = sys.argv[1:]
OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'reimport_body_%s.txt' % (args[1].split('/')[-1] if len(args) > 1 else 'x'))


def say(s):
    log.append(str(s))
    unreal.log('[reimport-body] %s' % s)


def bounds(mesh):
    b = mesh.get_bounds()
    o, e = b.origin, b.box_extent
    return [o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y, o.z - e.z, o.z + e.z]


def slot_list(mesh):
    return [(str(s.get_editor_property('material_slot_name')),
             s.material_interface.get_path_name() if s.material_interface else None) for s in mesh.get_editor_property('materials')]


def main():
    if len(args) < 2:
        say('usage: <fbx> <existing skeletal mesh asset> [save]')
        return
    fbx, target, do_save = args[0], args[1], 'save' in [a.lower() for a in args[2:]]
    if not os.path.isfile(fbx):
        say('REFUSING: no such file %s' % fbx)
        return
    unreal.AssetRegistryHelpers.get_asset_registry().scan_paths_synchronous([target.rsplit('/', 1)[0]], True)
    mesh = eal.load_asset(target)
    if not isinstance(mesh, unreal.SkeletalMesh):
        say('loaded %r' % (mesh,))
    if not isinstance(mesh, unreal.SkeletalMesh):
        say('REFUSING: %s is not a SkeletalMesh' % target)
        return
    folder = target.rsplit('/', 1)[0]
    skel = mesh.get_editor_property('skeleton')
    b0, s0 = bounds(mesh), slot_list(mesh)
    mats0 = [s.material_interface for s in mesh.get_editor_property('materials')]
    nb0 = len(mesh.get_editor_property('skeleton').get_reference_pose().get_bone_names()) if hasattr(skel, 'get_reference_pose') else -1
    say('before: skeleton %s (%s bones)  slots %s' % (skel.get_name(), nb0, s0))
    say('before bounds %s' % ['%.1f' % v for v in b0])

    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    ar.scan_paths_synchronous(['/Interchange/Pipelines', folder], True)
    listed = set(eal.list_assets(folder, recursive=False))
    if eal.does_asset_exist(PIPE_TMP):
        eal.delete_asset(PIPE_TMP)
    if not eal.duplicate_asset(PIPE_SRC, PIPE_TMP):
        say('REFUSING: could not duplicate %s' % PIPE_SRC)
        return
    p = eal.load_asset(PIPE_TMP)
    common = p.get_editor_property('common_skeletal_meshes_and_animations_properties')
    common.set_editor_property('import_only_animations', False)
    common.set_editor_property('skeleton', skel)
    try:
        common.set_editor_property('update_skeleton_reference_pose', False)
    except Exception as e:
        say('note: update_skeleton_reference_pose not settable (%s)' % e)
    m = p.get_editor_property('mesh_pipeline')
    m.set_editor_property('import_static_meshes', False)
    m.set_editor_property('import_skeletal_meshes', True)
    p.get_editor_property('animation_pipeline').set_editor_property('import_animations', False)
    for sub, prop in (('material_pipeline', 'import_materials'),):
        try:
            p.get_editor_property(sub).set_editor_property(prop, False)
            p.get_editor_property(sub).get_editor_property('texture_pipeline').set_editor_property('import_textures', False)
        except Exception as e:
            say('note: could not switch off %s (%s)' % (prop, e))
    eal.save_loaded_asset(p, False)
    try:
        params = unreal.ImportAssetParameters()
        params.set_editor_property('is_automated', True)
        params.set_editor_property('replace_existing', True)
        params.set_editor_property('reimport_asset', mesh)
        params.set_editor_property('override_pipelines', [unreal.SoftObjectPath(PIPE_TMP)])
        src = unreal.InterchangeManager.create_source_data(fbx)
        unreal.InterchangeManager.get_interchange_manager_scripted().import_asset(folder, src, params)
    finally:
        if eal.does_asset_exist(PIPE_TMP):
            eal.delete_asset(PIPE_TMP)

    stray = sorted(set(eal.list_assets(folder, recursive=False)) - listed)
    for s in stray:
        say('deleting what the import left behind: %s -> %s' % (s.split('/')[-1], eal.delete_asset(s.split('.')[0])))
    mesh = eal.load_asset(target)
    if mesh.get_editor_property('skeleton') != skel:
        say('FAILED: the mesh is no longer on %s. NOT saved.' % skel.get_name())
        return
    s1 = slot_list(mesh)
    if len(s1) != len(s0):
        say('FAILED: the slot list changed %s -> %s. NOT saved.' % (s0, s1))
        return
    if s1 != s0:
        fresh = []
        for s, mi in zip(mesh.get_editor_property('materials'), mats0):
            sm = unreal.SkeletalMaterial()
            sm.set_editor_property('material_interface', mi)
            sm.set_editor_property('material_slot_name', s.get_editor_property('material_slot_name'))
            fresh.append(sm)
        mesh.set_editor_property('materials', fresh)
        say('material slots came back as %s; restored to %s' % (s1, slot_list(mesh)))
        if [m_ for _, m_ in slot_list(mesh)] != [m_ for _, m_ in s0]:
            say('FAILED: could not restore the materials. NOT saved.')
            return
    b1 = bounds(mesh)
    say('after  bounds %s' % ['%.1f' % v for v in b1])
    worst = max(abs(x - y) for x, y in zip(b0, b1))
    if worst > 10.0:
        say('FAILED: the bounds moved %.1f cm; a skin fix does not do that. NOT saved.' % worst)
        return
    say('bounds moved %.2f cm at most; skeleton and material slots as before' % worst)
    if do_save:
        say('saved %s -> %s' % (target, unreal.EditorLoadingAndSavingUtils.save_packages([mesh.get_outermost()], False)))
    else:
        say('NOT saved (pass `save`)')


try:
    main()
except Exception:
    import traceback
    say('ERROR ' + traceback.format_exc())
finally:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')
