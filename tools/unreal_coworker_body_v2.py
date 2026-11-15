"""Put the remade coworker body on her EXISTING 68-bone rig, and point BP_Coworker at it.

Run through the editor console box:
    py <repo>/tools/unreal_coworker_body_v2.py [import|swap|measure]
or headless (forward slashes only - backslashes get mangled into tabs by -script=):
    UnrealEditor-Cmd.exe <uproject> -run=pythonscript -script="<repo>/tools/unreal_coworker_body_v2.py import"

Writes JumpCut/Saved/jcpy/coworker_body_v2.txt. `measure` touches nothing.

WHY THIS IS NOW POSSIBLE, WHEN #101 SAID IT WAS NOT.
The V2 body could not be reskinned onto SK_CafeCoworker_Skeleton because her A-pose was 13.5 cm per hand
away from it - posing the hand bone moved 1,384 vertices on the shipped body against 30 on the reskinned
one. That is the same fault the player had, and conform_rest_pose.py is the same fix: pose Meshy's own rig
onto the target rig's rest FIRST, bake, and only then transfer weights. After it, every mapped bone sits
0.08-1.5 cm inside her mesh and Art/Blender/rest_delta.py reads 0.0 deg against the rig her clips are keyed
to, so SK_CafeCoworkerArmature_Idle and _Walk still play with nothing retargeted.

Two post-passes matter and are in Art/Blender/collapse_hand_weights.py:
  * her hands are a FUSED MITTEN, so the rig's 41 finger bones are folded into the two palm bones. Keying
    five finger chains on one lump of geometry fans it into white shards from the first frame of Idle.
  * weights further than 12 cm from their bone are dropped. reskin_to_existing_rig.py prunes at 25 cm,
    which still lets a hip bone drive a hand vertex - and that vertex comes out as a needle spike several
    centimetres long. It is one or two vertices, invisible in any weight count, obvious in a side view.
"""
import os
import sys
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'coworker_body_v2.txt')
REPO = os.path.abspath(os.path.join(unreal.Paths.project_dir(), '..'))
ART = os.path.join(REPO, 'Art', 'Blender', 'export', 'Characters', 'CafeCoworkerV2')

FBX = os.path.join(ART, 'SK_CafeCoworkerV2_oldrig.fbx')
PNG = os.path.join(ART, 'T_CafeCoworkerV2_BaseColor.png')
DEST = '/Game/Game/Imported/CafeCoworkerV2'
TARGET = DEST + '/SK_CafeCoworkerV2'
SKEL = '/Game/Game/Imported/CafeCoworker/SK/SK_CafeCoworker_Skeleton'
TEX = DEST + '/T_CafeCoworkerV2_BaseColor'
MAT = '/Game/Game/Materials/MI_CafeCoworkerV2'
ANIME_CHAR = '/Game/Game/Materials/M_AnimeChar'
MAT_DIR = '/Game/Game/Materials'
BP_CLASS = '/Game/Game/Blueprints/BP_Coworker.BP_Coworker_C'
# BP_Coworker is NOT a Character: her body is an SCS component called CoworkerBody, and
# get_components_by_class on the CDO returns an EMPTY list for SCS components, which reads as
# "this blueprint has no mesh". The templates have to be reached through SubobjectDataSubsystem.
COMP = 'CoworkerBody'
V1 = '/Game/Game/Imported/CafeCoworker/SK/SK_CafeCoworker'

PIPE_SRC = '/Interchange/Pipelines/DefaultFBXOBJAssetsPipeline'
PIPE_TMP = DEST + '/_jc_cw_pipeline'
# Blender, from the conform+reskin run. Our FBX settings send Blender +Y to Unreal -Y, so the y pair is
# negated and swapped: Blender y[-21.2 25.0] is Unreal y[-25.0 21.2].
WANT = {'z': (0.0, 164.9)}
TOL = 3.0

ALL_COMPS = []
eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
log = []


def say(s):
    log.append(str(s))
    unreal.log('[coworker-v2] %s' % s)


def flush():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')


def path_of(o):
    try:
        return o.get_path_name()
    except Exception:
        return str(o)


def describe(tag):
    m = eal.load_asset(TARGET)
    if m is None:
        say('%s %s does not exist' % (tag, TARGET))
        return None
    sk = m.get_editor_property('skeleton')
    b = m.get_bounds()
    o, e = b.origin, b.box_extent
    say('%s %s' % (tag, TARGET))
    say('    skeleton %s' % path_of(sk))
    say('    bounds   x[%7.2f %7.2f] y[%7.2f %7.2f] z[%7.2f %7.2f]'
        % (o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y, o.z - e.z, o.z + e.z))
    say('    slots    %s' % [path_of(s.material_interface) if s.material_interface else None
                             for s in m.get_editor_property('materials')])
    return m


def do_import():
    if not os.path.isfile(FBX):
        say('REFUSING: no such file %s' % FBX)
        return False
    skel = eal.load_asset(SKEL)
    if skel is None:
        say('REFUSING: %s is missing - that is the rig her clips are keyed to' % SKEL)
        return False

    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    ar.scan_paths_synchronous(['/Interchange/Pipelines'], True)
    ar.wait_for_completion()

    describe('BEFORE')
    # The shipped V2 sits on a 28-bone skeleton of its own. A re-import cannot move an asset to a different
    # skeleton, and Interchange would quietly make a SECOND asset named after the FBX instead - the PR #112
    # trap. So delete the old set first and import fresh.
    for p in (TARGET, TARGET + '_PhysicsAsset', TARGET + '_Skeleton'):
        if eal.does_asset_exist(p):
            say('deleting %s (28-bone set being replaced)' % p)
            eal.delete_asset(p)
    # A deleted asset the editor still has loaded keeps answering load_asset() with the TRASHED object -
    # old bounds, skeleton None - so the verification below reads the corpse instead of the new import and
    # reports a perfectly good import as a failure. Collect first.
    unreal.SystemLibrary.collect_garbage()

    if eal.does_asset_exist(PIPE_TMP):
        eal.delete_asset(PIPE_TMP)
    if not eal.duplicate_asset(PIPE_SRC, PIPE_TMP):
        say('REFUSING: could not duplicate %s' % PIPE_SRC)
        return False
    p = eal.load_asset(PIPE_TMP)
    common = p.get_editor_property('common_skeletal_meshes_and_animations_properties')
    common.set_editor_property('import_only_animations', False)
    common.set_editor_property('skeleton', skel)
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
        params.set_editor_property('override_pipelines', [unreal.SoftObjectPath(PIPE_TMP)])
        src = unreal.InterchangeManager.create_source_data(FBX)
        unreal.InterchangeManager.get_interchange_manager_scripted().import_asset(DEST, src, params)
    finally:
        if eal.does_asset_exist(PIPE_TMP):
            eal.delete_asset(PIPE_TMP)

    ar.scan_paths_synchronous([DEST], True)
    ar.wait_for_completion()
    unreal.SystemLibrary.collect_garbage()

    # Interchange names the asset after the FBX file. Ours is SK_CafeCoworkerV2_oldrig. Rename it
    # unconditionally: gating on "TARGET does not exist" is wrong, because a just-deleted TARGET can still
    # answer does_asset_exist until the registry catches up, and then the rename is skipped silently.
    stray = DEST + '/SK_CafeCoworkerV2_oldrig'
    if eal.does_asset_exist(stray):
        if eal.does_asset_exist(TARGET):
            say('deleting the stale %s so the new import can take its name' % TARGET)
            eal.delete_asset(TARGET)
            unreal.SystemLibrary.collect_garbage()
        say('renaming %s -> %s' % (stray, TARGET))
        eal.rename_asset(stray, TARGET)
        for suf in ('_PhysicsAsset',):
            if eal.does_asset_exist(stray + suf):
                if eal.does_asset_exist(TARGET + suf):
                    eal.delete_asset(TARGET + suf)
                eal.rename_asset(stray + suf, TARGET + suf)
    ar.scan_paths_synchronous([DEST], True)
    ar.wait_for_completion()

    task = unreal.AssetImportTask()
    task.set_editor_property('filename', PNG)
    task.set_editor_property('destination_path', DEST)
    task.set_editor_property('automated', True)
    task.set_editor_property('replace_existing', True)
    task.set_editor_property('save', False)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    say('texture imported: %s' % list(task.get_editor_property('imported_object_paths')))

    if not eal.does_asset_exist(MAT):
        unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            MAT.rsplit('/', 1)[1], MAT_DIR, unreal.MaterialInstanceConstant,
            unreal.MaterialInstanceConstantFactoryNew())
    mi = eal.load_asset(MAT)
    mi.set_editor_property('parent', eal.load_asset(ANIME_CHAR))
    tex = eal.load_asset(TEX)
    if tex is None:
        say('REFUSING: %s did not import' % TEX)
        return False
    mel.set_material_instance_texture_parameter_value(mi, 'Tex', tex)

    mesh = eal.load_asset(TARGET)
    if mesh is None:
        say('REFUSING: %s was not created' % TARGET)
        return False
    # get_editor_property('materials') hands back COPIES; mutate them and the write is silently discarded.
    fresh = []
    for s in mesh.get_editor_property('materials'):
        sm = unreal.SkeletalMaterial()
        sm.set_editor_property('material_interface', mi)
        sm.set_editor_property('material_slot_name', s.get_editor_property('material_slot_name'))
        fresh.append(sm)
    mesh.set_editor_property('materials', fresh)

    m = describe('AFTER ')
    if m is None:
        return False
    if m.get_editor_property('skeleton') is not eal.load_asset(SKEL):
        say('FAILED: she is not on %s - her clips would not apply' % SKEL)
        return False
    b = m.get_bounds()
    zlo, zhi = b.origin.z - b.box_extent.z, b.origin.z + b.box_extent.z
    if abs(zlo - WANT['z'][0]) > TOL or abs(zhi - WANT['z'][1]) > TOL:
        say('FAILED: height z[%.2f %.2f] is not the %.1f cm Blender measured' % (zlo, zhi, WANT['z'][1]))
        return False
    slots = [path_of(s.material_interface) if s.material_interface else None
             for s in m.get_editor_property('materials')]
    if any(s is None or s.split('.')[0] != MAT for s in slots):
        say('FAILED: material slot is %s, not %s' % (slots, MAT))
        return False

    for p in (TARGET, TARGET + '_PhysicsAsset', TEX, MAT):
        if eal.does_asset_exist(p):
            say('saved %s -> %s' % (p, eal.save_asset(p, False)))
    return True


def get_comp():
    bp = eal.load_asset(BP_CLASS.split('.')[0])
    if bp is None:
        say('REFUSING: could not load %s' % BP_CLASS)
        return None, None
    sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    found = []
    seen = []
    for h in sub.k2_gather_subobject_data_for_blueprint(bp):
        d = sub.k2_find_subobject_data_from_handle(h)
        o = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(d)
        n = str(unreal.SubobjectDataBlueprintFunctionLibrary.get_variable_name(d))
        seen.append('%s:%s' % (n, o.get_class().get_name() if o else '?'))
        if n == COMP and isinstance(o, unreal.SkeletalMeshComponent):
            found.append(o)
    if not found:
        say('REFUSING: no SkeletalMeshComponent named %s; present: %s' % (COMP, seen))
        return bp, None
    # the subsystem lists each SCS node twice (the node and its template). Write to EVERY one of them -
    # if they are distinct objects, setting only the first leaves the other holding V1 and the read-back
    # still says V2.
    say('found %d handle(s) for %s' % (len(found), COMP))
    global ALL_COMPS
    ALL_COMPS = found
    return bp, found[0]


def snap(c, tag):
    d = {k: c.get_editor_property(k) for k in
         ('skeletal_mesh_asset', 'anim_class', 'override_materials',
          'relative_location', 'relative_rotation', 'relative_scale3d')}
    say('%s BP_Coworker.%s' % (tag, COMP))
    say('    mesh   %s' % path_of(d['skeletal_mesh_asset']))
    say('    anim   %s' % path_of(d['anim_class']))
    say('    ovr    %s' % [path_of(m) for m in d['override_materials']])
    say('    xform  %s %s %s' % (d['relative_location'], d['relative_rotation'], d['relative_scale3d']))
    return d


def do_swap():
    bp, c = get_comp()
    if c is None:
        return False
    before = snap(c, 'BEFORE')
    v2 = eal.load_asset(TARGET)
    if v2 is None:
        say('REFUSING: %s is missing - run `import` first' % TARGET)
        return False
    if v2.get_editor_property('skeleton') is not eal.load_asset(SKEL):
        say('REFUSING: V2 is not on %s - swapping would break her clips' % SKEL)
        return False
    if before['skeletal_mesh_asset'] is v2:
        say('ALREADY on V2 - nothing to do')
        return True
    if path_of(before['skeletal_mesh_asset']).split('.')[0] != V1:
        say('note: she was on %s, not the expected V1' % path_of(before['skeletal_mesh_asset']))

    for comp in ALL_COMPS:
        comp.set_editor_property('skeletal_mesh_asset', v2)
    after = snap(c, 'AFTER ')
    for i, comp in enumerate(ALL_COMPS):
        got = comp.get_editor_property('skeletal_mesh_asset')
        say('    handle %d -> %s' % (i, path_of(got)))
    ok = after['skeletal_mesh_asset'] is v2
    if not ok:
        say('FAIL: the property did not take')
    if path_of(after['anim_class']) != path_of(before['anim_class']):
        say('FAIL: anim_class changed'); ok = False
    if len(after['override_materials']) != 0:
        say('FAIL: override_materials is not empty - it would beat the mesh slot (PR #105)'); ok = False
    for k in ('relative_location', 'relative_rotation', 'relative_scale3d'):
        if str(before[k]) != str(after[k]):
            say('FAIL: %s changed %s -> %s' % (k, before[k], after[k])); ok = False
    if not ok:
        say('NOT SAVING - a check failed above')
        return False
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    saved = unreal.EditorLoadingAndSavingUtils.save_packages([bp.get_outermost()], False)
    say('SAVED %s ok=%s' % (bp.get_outermost().get_name(), saved))
    return True


def main():
    mode = (sys.argv[1].lower() if len(sys.argv) > 1 else 'measure')
    say('repo=%s mode=%s' % (REPO, mode))
    if mode == 'import':
        say('IMPORT %s' % ('OK' if do_import() else 'FAILED'))
    elif mode == 'swap':
        say('SWAP %s' % ('OK' if do_swap() else 'FAILED'))
    else:
        describe('NOW   ')
        bp, c = get_comp()
        if c is not None:
            snap(c, 'NOW   ')


try:
    main()
except Exception:
    import traceback
    say(traceback.format_exc())
finally:
    flush()
