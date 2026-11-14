"""Bring the remade CafeWalkerV2 / CafeCoworkerV2 bodies into Unreal, textured.

Run headless:
    UnrealEditor-Cmd.exe <uproject> -run=pythonscript -script="<repo>/tools/unreal_import_char_v2.py [save]"
or through the editor console box:
    py <repo>/tools/unreal_import_char_v2.py [save]

Writes JumpCut/Saved/jcpy/import_char_v2.txt. Without the `save` argument it imports into
memory and reports, and nothing reaches disk.

WHY THIS EXISTS, AND THE TRAP IT WALKS AROUND.
Meshy's remesh DISCARDS the base colour. The rigged/remeshed asset is genuinely untextured
(it renders grey in Meshy's own viewer) and its FBX embeds only a tangent-space normal map.
The colour lives on the pre-remesh 365k asset, in a DIFFERENT UV layout - dropping that
texture onto the remeshed mesh gives camouflage noise, not a barista. So the colour map
committed beside each V2 FBX was BAKED high-poly -> low-poly in Blender
(Art/Blender/bake_meshy_basecolor.py), not downloaded. Do not replace it with a Meshy
download.

THE SKELETON IS THE OTHER HALF. SK_CafeWalkerV2_oldrig.fbx is the new mesh reskinned onto
the EXISTING 69-bone armature (issue #96), so it must import against the existing
SK_CafeWalker_Skeleton or every clip, montage and anim blueprint we own stops applying to
it. Interchange reads its skeleton from a pipeline ASSET, not from FbxImportUI - see
tools/unreal_import_authored_clip.py for the same dance. SK_CafeCoworkerV2.fbx is still on
Meshy's own 28-bone rig (her reskin failed, #101), so she deliberately gets a NEW skeleton
and is art only, not animation-ready.

WHAT IT CHECKS AFTERWARDS, because "imported ok" is not evidence:
  * the SkeletalMesh exists and its skeleton is the one we asked for, BY OBJECT IDENTITY;
  * its vertex count matches what Blender measured in the FBX;
  * the material slot resolves to MI_*V2 whose parent is M_AnimeChar, not an Interchange
    import material - that mismatch is exactly what made the goons render flat (PR #105);
  * the MI's Tex parameter points at the committed texture, by object identity.
"""
import os
import sys
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'import_char_v2.txt')
REPO = os.path.abspath(os.path.join(unreal.Paths.project_dir(), '..'))
ART = os.path.join(REPO, 'Art', 'Blender', 'export', 'Characters')

PIPE_SRC = '/Interchange/Pipelines/DefaultFBXOBJAssetsPipeline'
PIPE_TMP = '/Game/Game/Imported/_jc_charv2_pipeline'
ANIME_CHAR = '/Game/Game/Materials/M_AnimeChar'
MAT_DIR = '/Game/Game/Materials'

eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary

# name, fbx, dest folder, existing skeleton (None = make a new one), expected verts
PLAN = [
    ('CafeWalkerV2',
     os.path.join(ART, 'CafeWalkerV2', 'SK_CafeWalkerV2_oldrig.fbx'),
     os.path.join(ART, 'CafeWalkerV2', 'T_CafeWalkerV2_BaseColor.png'),
     '/Game/Game/Imported/CafeWalkerV2',
     '/Game/Game/Imported/CafeWalker/Meshy/SK_CafeWalker_Skeleton',
     27976),
    ('CafeCoworkerV2',
     os.path.join(ART, 'CafeCoworkerV2', 'SK_CafeCoworkerV2.fbx'),
     os.path.join(ART, 'CafeCoworkerV2', 'T_CafeCoworkerV2_BaseColor.png'),
     '/Game/Game/Imported/CafeCoworkerV2',
     None,
     28282),
]

log = []


def say(s):
    log.append(str(s))
    unreal.log('[char-v2] %s' % s)


def flush():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')


def ensure_registry():
    """In -run=pythonscript the registry has not scanned plugin content, so
    /Interchange/Pipelines is invisible and duplicate_asset fails. Scan it by hand."""
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    ar.scan_paths_synchronous(['/Interchange/Pipelines'], True)
    ar.wait_for_completion()
    say('registry: %s exists=%s' % (PIPE_SRC, eal.does_asset_exist(PIPE_SRC)))


def make_pipeline(skel):
    """One-shot copy of the project's FBX pipeline, set to mesh-only on a chosen skeleton."""
    if eal.does_asset_exist(PIPE_TMP):
        eal.delete_asset(PIPE_TMP)
    if not eal.duplicate_asset(PIPE_SRC, PIPE_TMP):
        say('REFUSING: could not duplicate %s - is the Interchange plugin content mounted?'
            % PIPE_SRC)
        return None
    p = eal.load_asset(PIPE_TMP)
    common = p.get_editor_property('common_skeletal_meshes_and_animations_properties')
    common.set_editor_property('import_only_animations', False)
    if skel is not None:
        common.set_editor_property('skeleton', skel)
    mesh = p.get_editor_property('mesh_pipeline')
    mesh.set_editor_property('import_static_meshes', False)
    mesh.set_editor_property('import_skeletal_meshes', True)
    anim = p.get_editor_property('animation_pipeline')
    anim.set_editor_property('import_animations', False)
    eal.save_loaded_asset(p, False)
    return p


def import_mesh(fbx, dest, skel):
    before = set(eal.list_assets(dest, recursive=False)) \
        if eal.does_directory_exist(dest) else set()
    pipeline = make_pipeline(skel)
    if pipeline is None:
        return []
    try:
        params = unreal.ImportAssetParameters()
        params.set_editor_property('is_automated', True)
        params.set_editor_property('replace_existing', True)
        params.set_editor_property('override_pipelines', [unreal.SoftObjectPath(PIPE_TMP)])
        src = unreal.InterchangeManager.create_source_data(fbx)
        mgr = unreal.InterchangeManager.get_interchange_manager_scripted()
        mgr.import_asset(dest, src, params)
    finally:
        if eal.does_asset_exist(PIPE_TMP):
            eal.delete_asset(PIPE_TMP)
    after = set(eal.list_assets(dest, recursive=False))
    return sorted(after - before)


def import_texture(png, dest):
    task = unreal.AssetImportTask()
    task.set_editor_property('filename', png)
    task.set_editor_property('destination_path', dest)
    task.set_editor_property('automated', True)
    task.set_editor_property('replace_existing', True)
    task.set_editor_property('save', False)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    made = list(task.get_editor_property('imported_object_paths'))
    return made


def make_mi(name, tex_path):
    mi_path = '%s/MI_%s' % (MAT_DIR, name)
    if not eal.does_asset_exist(mi_path):
        unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            'MI_%s' % name, MAT_DIR,
            unreal.MaterialInstanceConstant,
            unreal.MaterialInstanceConstantFactoryNew())
    mi = eal.load_asset(mi_path)
    parent = eal.load_asset(ANIME_CHAR)
    mi.set_editor_property('parent', parent)
    tex = eal.load_asset(tex_path)
    mel.set_material_instance_texture_parameter_value(mi, 'Tex', tex)
    return mi_path, mi


def main():
    do_save = 'save' in [a.lower() for a in sys.argv[1:]]
    say('repo=%s  save=%s' % (REPO, do_save))
    ensure_registry()
    results = []

    for name, fbx, png, dest, skel_path, want_verts in PLAN:
        say('')
        say('=== %s ===' % name)
        if not os.path.isfile(fbx):
            say('REFUSING: no such file %s' % fbx)
            continue
        if not os.path.isfile(png):
            say('REFUSING: no such texture %s' % png)
            continue

        skel = None
        if skel_path:
            if not eal.does_asset_exist(skel_path):
                say('REFUSING: skeleton %s does not exist - importing would build a second '
                    'one, and a mesh on a skeleton nobody animates never moves' % skel_path)
                continue
            skel = eal.load_asset(skel_path)
            say('binding to existing skeleton %s' % skel_path)
        else:
            say('no existing skeleton asked for - Interchange will build a new one')

        new_mesh = import_mesh(fbx, dest, skel)
        say('new assets in %s: %s'
            % (dest, ', '.join(n.split('/')[-1] for n in new_mesh) or '(none)'))
        meshes = [p for p in new_mesh
                  if isinstance(eal.load_asset(p), unreal.SkeletalMesh)]
        if not meshes:
            existing = [p for p in eal.list_assets(dest, recursive=False)
                        if isinstance(eal.load_asset(p), unreal.SkeletalMesh)] \
                if eal.does_directory_exist(dest) else []
            if existing:
                meshes = existing
                say('no NEW SkeletalMesh - reusing existing %s (re-import)' % meshes)
            else:
                say('FAILED: no SkeletalMesh came out of %s' % fbx)
                continue
        mesh_path = meshes[0]
        # The FBX is called *_oldrig because of how it was built (new mesh reskinned onto
        # the old armature). That is build provenance, not a name the game should carry.
        want_path = '%s/SK_%s' % (dest, name)
        if mesh_path != want_path and not eal.does_asset_exist(want_path):
            if eal.rename_asset(mesh_path, want_path):
                say('renamed %s -> %s' % (mesh_path.split('/')[-1], want_path.split('/')[-1]))
                mesh_path = want_path
                phys_old = '%s_PhysicsAsset' % (meshes[0])
                phys_new = '%s_PhysicsAsset' % want_path
                if eal.does_asset_exist(phys_old) and not eal.does_asset_exist(phys_new):
                    eal.rename_asset(phys_old, phys_new)
                    say('renamed physics asset -> %s' % phys_new.split('/')[-1])
        elif eal.does_asset_exist(want_path):
            mesh_path = want_path
            say('using existing %s' % want_path)
        mesh = eal.load_asset(mesh_path)

        got = mesh.get_editor_property('skeleton')
        if skel is not None and got != skel:
            say('REFUSING to go further: %s is on %s, not %s. Every clip we own would '
                'stop applying to it.'
                % (mesh_path, got.get_path_name() if got else '(none)', skel_path))
            continue
        say('skeleton: %s' % (got.get_path_name() if got else '(none)'))
        say('bones: %d' % len(got.get_editor_property('bone_tree')) if got else 'bones: ?')
        try:
            # Unreal splits a vertex at every UV/normal/tangent seam, so this is ALWAYS
            # higher than Blender's unique-vertex count. It is a non-empty / right-order
            # check, not an equality one - treating a legitimate split as a MISMATCH is how
            # a good import gets thrown away.
            n = unreal.get_editor_subsystem(
                unreal.SkeletalMeshEditorSubsystem).get_num_verts(mesh, 0)
            ratio = float(n) / want_verts if want_verts else 0.0
            say('verts lod0: %d render verts (Blender: %d unique in the FBX, ratio %.2f) %s'
                % (n, want_verts, ratio,
                   'OK - seam splitting' if 1.0 <= ratio <= 1.6 else 'LOOK AT THIS'))
        except Exception as e:
            say('vert count unavailable: %s' % e)

        tex_made = import_texture(png, dest)
        tex_path = '%s/%s' % (dest, os.path.splitext(os.path.basename(png))[0])
        say('texture: %s (import returned %s)' % (tex_path, tex_made))
        if not eal.does_asset_exist(tex_path):
            say('FAILED: texture did not land at %s' % tex_path)
            continue
        tex = eal.load_asset(tex_path)
        say('texture size: %sx%s' % (tex.blueprint_get_size_x(), tex.blueprint_get_size_y()))

        mi_path, mi = make_mi(name, tex_path)
        back = mel.get_material_instance_texture_parameter_value(mi, 'Tex')
        say('%s parent=%s Tex=%s %s'
            % (mi_path,
               mi.get_editor_property('parent').get_path_name(),
               back.get_path_name() if back else '(none)',
               'OK' if back == tex else 'MISMATCH'))

        # get_editor_property('materials') hands back COPIES of the structs, so mutating
        # them in place is silently discarded - the slot keeps the Interchange import
        # material and the character renders untextured. Build fresh entries instead.
        old = mesh.get_editor_property('materials')
        new_mats = []
        for m in old:
            sm = unreal.SkeletalMaterial()
            sm.set_editor_property('material_interface', mi)
            sm.set_editor_property('material_slot_name',
                                   m.get_editor_property('material_slot_name'))
            new_mats.append(sm)
        mesh.set_editor_property('materials', new_mats)
        mats2 = mesh.get_editor_property('materials')
        got_slots = [m.get_editor_property('material_interface').get_path_name()
                     for m in mats2]
        say('mesh slots now: %s %s'
            % (got_slots,
               'OK' if all(s.startswith(mi_path) for s in got_slots) else 'DID NOT TAKE'))

        results.append((mesh_path, tex_path, mi_path))

    if do_save:
        say('')
        for mesh_path, tex_path, mi_path in results:
            for p in (mesh_path, tex_path, mi_path):
                ok = eal.save_asset(p, only_if_is_dirty=False)
                say('saved %s -> %s' % (p, ok))
            # the skeleton/physics asset the mesh brought with it
            for p in eal.list_assets(os.path.dirname(mesh_path), recursive=False):
                ok = eal.save_asset(p, only_if_is_dirty=True)
                say('saved %s -> %s' % (p, ok))
    else:
        say('')
        say('NOT SAVED - pass `save` to write these to disk.')


try:
    main()
except Exception:
    import traceback
    say(traceback.format_exc())
finally:
    flush()
    print('\n'.join(log))
