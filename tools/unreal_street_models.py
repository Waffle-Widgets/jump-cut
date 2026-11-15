"""Brings the Meshy street models into Unreal and puts them where the kit's placeholders stand.

Sun Nov 15: the Team Owner asked for trees, cars and bikes that "look nice, not like generic fill-ins".
The kit's own SM_StreetTree (960 triangles, a green blob), SM_KeiVan (798), SM_Bicycle (400) and
SM_Scooter (264) are flat-colour block models. These five are Gemini reference pictures -> Meshy Image
to 3D -> Art/Blender/meshy_prop_bake.py, each ONE material with ONE baked colour texture:

    Art/Meshy/SakuraTree/   SM_SakuraTree.fbx  T_SakuraTree.png     replaces SM_StreetTree  (10 placed)
    Art/Meshy/KeiVanM/      SM_KeiVanM.fbx     T_KeiVanM.png        replaces SM_KeiVan      (3 of the 5)
    Art/Meshy/Hatchback/    SM_Hatchback.fbx   T_Hatchback.png      takes 2 of the 5 van spots
    Art/Meshy/BicycleM/     SM_BicycleM.fbx    T_BicycleM.png       replaces SM_Bicycle     (5 placed)
    Art/Meshy/ScooterM/     SM_ScooterM.fbx    T_ScooterM.png       replaces SM_Scooter     (6 placed)

The "M" on three of them is only there because the kit already owns SM_KeiVan, SM_Bicycle and SM_Scooter,
and Interchange names a one-mesh FBX after its FILE: a second SM_Bicycle in another folder would work and
would be mistaken for the kit's in every log line.

WHY NEW NAMES AND NOT A RE-IMPORT OVER THE KIT MESH. Every placed City_* actor carries per-component
material overrides indexed by slot INDEX (see unreal_city_reimport_by_name.py). The kit tree has three
slots, the Meshy tree has one, so importing over SM_StreetTree would leave slot 0's override - whatever
kit material that happens to be - painted over the whole new tree, texture discarded, nothing logged.
So these are new assets under /Game/Game/Imported/Street/, and `swap` changes the mesh on each placed
actor and CLEARS its overrides. The kit assets are left alone (GC_CrashCar and the cinematic do not use
these four, but nothing here depends on that being true).

Run in the editor console box, Play mode stopped, Lvl_JumpCut open:
    py <repo>/tools/unreal_street_models.py import     meshes, textures, M_StreetProp + one MI each. Saves them.
    py <repo>/tools/unreal_street_models.py plan       lists the placed actors `swap` would change, and the
                                                        .uasset file of each one (lock those first). Changes nothing.
    py <repo>/tools/unreal_street_models.py swap       changes the mesh on those actors and saves their packages.
                                                        REFUSES if any of those files is read-only (= not locked).
    py <repo>/tools/unreal_street_models.py revert     puts the kit meshes and kit materials back on the same actors.
A SECOND BATCH (13 more models, listed in MODELS) was added at 2:20 PM the same day. `import` only brings in
models that are not in the project yet; `plan` and `swap` only ever list actors still wearing a KIT mesh, so
running them again touches the new 13 and leaves the first 26 actors alone. `swap PlanterM BenchM` does just those.
Result: Saved/jcpy/street_models.json (and the lock list in Saved/jcpy/street_models_lock.txt).

THE NEXT RUN OF jumpcut_city_place.py IN 'place' MODE WILL UNDO `swap` - it clears every City_* actor
and re-places the kit model named in city_layout.json. 'add' mode is safe (it matches by label and its
remat only touches slots whose names are kit materials). If the placer is ever re-run, run `swap` again.
"""
import json
import os
import sys
import traceback

import unreal

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', '/')
DEST = '/Game/Game/Imported/Street'
MATS = '/Game/Game/Materials/Street'
PARENT = MATS + '/M_StreetProp'
KIT = '/Game/Game/Imported/City/'

# name -> (source folder under Art/Meshy, kit mesh it replaces or None)
MODELS = {
    'SakuraTree': ('SakuraTree', 'SM_StreetTree'),
    'KeiVanM': ('KeiVanM', 'SM_KeiVan'),
    'Hatchback': ('Hatchback', None),
    'BicycleM': ('BicycleM', 'SM_Bicycle'),
    'ScooterM': ('ScooterM', 'SM_Scooter'),
    # Second batch, Sun Nov 15 2:20 PM: the free-standing street props and six cafe pieces. Each was sized to
    # the kit model it replaces and, where the kit one stands against a wall, baked with its BACK at the kit
    # model's back (PROP_BACK), so the deeper Meshy model grows toward the street and not into the shopfront.
    'VendingMachineM': ('VendingMachineM', 'SM_VendingMachine'),
    'StreetLampM': ('StreetLampM', 'SM_StreetLamp'),
    'PlanterM': ('PlanterM', 'SM_Planter'),
    'PotRowM': ('PotRowM', 'SM_PotRow'),
    'DumpsterM': ('DumpsterM', 'SM_Dumpster'),
    'AFrameSignM': ('AFrameSignM', 'SM_AFrameSign'),
    'BenchM': ('BenchM', 'SM_Bench'),
    'CafeEspressoM': ('CafeEspressoM', 'SM_CafeEspresso'),
    'CafeRegisterM': ('CafeRegisterM', 'SM_CafeRegister'),
    'CafePastryCaseM': ('CafePastryCaseM', 'SM_CafePastryCase'),
    'CafePlantTallM': ('CafePlantTallM', 'SM_CafePlantTall'),
    'CafePlantSmallM': ('CafePlantSmallM', 'SM_CafePlantSmall'),
    'CafeStoolM': ('CafeStoolM', 'SM_CafeStool'),
}
# `import` leaves alone any model whose mesh and texture are already in the project. Re-touching the first
# five would dirty packages that are committed and therefore READ-ONLY, and a failed save of a read-only
# package is what froze the editor for ten minutes on Nov 14. `import all` forces every model (lock them first).
# `swap <Name> <Name>` / `plan <Name> ...` limits the swap to those models, so one bad model can be left out.
FORCE = 'all' in sys.argv[2:]
ONLY = {x for x in sys.argv[2:] if x in MODELS}
# The kit tree is near enough round, so two street trees were placed at yaw 270. The sakura is 4.4 m one way
# and 2.4 m the other; at yaw 270 its long side would run 1 m into the shopfronts. These two get turned so
# the long side follows the pavement. `revert` does not turn them back (the kit tree does not care).
YAW = {'City_Tree_01': 180.0, 'City_Tree_02': 180.0}
# These labels get a model other than the one their kit mesh maps to: two of the five vans become cars,
# so the street is not five copies of one vehicle.
BY_LABEL = {'City_Van_1': 'Hatchback', 'City_AvenueVan1': 'Hatchback'}
BY_KIT = {kit: n for n, (_, kit) in MODELS.items() if kit}

MODE = (sys.argv[1] if len(sys.argv) > 1 else 'plan').lower()
OUT_DIR = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT_DIR, exist_ok=True)
R = {'mode': MODE, 'log': []}
eal = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary


def say(s):
    R['log'].append(s)
    unreal.log('[street] ' + s)


def import_one(src, dest, name):
    t = unreal.AssetImportTask()
    t.set_editor_property('filename', src)
    t.set_editor_property('destination_path', dest)
    t.set_editor_property('destination_name', name)
    t.set_editor_property('replace_existing', True)
    t.set_editor_property('automated', True)
    t.set_editor_property('save', False)
    tools.import_asset_tasks([t])


def ensure_parent(default_tex):
    mat = unreal.load_asset(PARENT)
    if mat is not None:
        return mat
    mat = tools.create_asset('M_StreetProp', MATS, unreal.Material, unreal.MaterialFactoryNew())
    tex = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -500, 0)
    tex.set_editor_property('parameter_name', 'BaseTex')
    tex.set_editor_property('texture', default_tex)       # a NULL default is a compile error on every instance
    mel.connect_material_property(tex, 'RGB', unreal.MaterialProperty.MP_BASE_COLOR)
    rough = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -500, 300)
    rough.set_editor_property('r', 0.9)
    mel.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
    spec = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -500, 420)
    spec.set_editor_property('r', 0.1)                     # the cel pass bands light; a highlight would band too
    mel.connect_material_property(spec, '', unreal.MaterialProperty.MP_SPECULAR)
    mel.recompile_material(mat)
    return mat


def do_import():
    smes = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    reg.scan_paths_synchronous([DEST, MATS], True)
    R['models'] = {}
    touched = []
    parent = None
    for name, (folder, _) in sorted(MODELS.items()):
        info = {}
        R['models'][name] = info
        src_dir = '%s/Art/Meshy/%s' % (REPO, folder)
        fbx = '%s/SM_%s.fbx' % (src_dir, folder)
        png = '%s/T_%s.png' % (src_dir, folder)
        if not (os.path.isfile(fbx) and os.path.isfile(png)):
            info['error'] = 'source missing: %s / %s' % (fbx, png)
            say('%s: %s' % (name, info['error']))
            continue
        dest = '%s/%s' % (DEST, name)
        mesh_path, tex_path = '%s/SM_%s' % (dest, name), '%s/T_%s' % (dest, name)
        if not FORCE and unreal.load_asset(mesh_path) is not None and unreal.load_asset(tex_path) is not None:
            info['skipped'] = 'already imported - left alone'
            parent = parent or unreal.load_asset(PARENT)
            continue
        if unreal.load_asset(tex_path) is None:
            import_one(png, dest, 'T_' + name)
        tex = unreal.load_asset(tex_path)
        if unreal.load_asset(mesh_path) is None:
            import_one(fbx, dest, 'SM_' + name)
        mesh = unreal.load_asset(mesh_path)
        if mesh is None:
            # Interchange names the asset itself and does not have to honour destination_name: take
            # whatever StaticMesh landed in this model's own folder rather than report a false failure.
            reg.scan_paths_synchronous([dest], True)
            for p in eal.list_assets(dest, recursive=False):
                cand = unreal.load_asset(p.split('.')[0])
                if isinstance(cand, unreal.StaticMesh):
                    mesh, mesh_path = cand, p.split('.')[0]
                    info['mesh_named_by_importer'] = cand.get_name()
                    break
        if tex is None or mesh is None or not isinstance(mesh, unreal.StaticMesh):
            info['error'] = 'import produced tex=%s mesh=%s' % (tex, mesh)
            say('%s: %s' % (name, info['error']))
            continue
        tex.set_editor_property('srgb', True)
        if parent is None:
            made_parent = unreal.load_asset(PARENT) is None
            parent = ensure_parent(tex)
            if made_parent:
                touched.append(parent)
        mi_path = '%s/MI_%s' % (MATS, name)
        mi = unreal.load_asset(mi_path)
        if mi is None:
            mi = tools.create_asset('MI_' + name, MATS, unreal.MaterialInstanceConstant,
                                    unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi, parent)
        mel.set_material_instance_texture_parameter_value(mi, 'BaseTex', tex)
        mel.update_material_instance(mi)
        # FRESH structs: get_editor_property('static_materials') hands back copies (same trap as SkeletalMaterial)
        slots = [str(m.get_editor_property('material_slot_name')) for m in mesh.get_editor_property('static_materials')]
        for i in range(len(slots)):
            mesh.set_material(i, mi)
        st = smes.get_nanite_settings(mesh)
        if st.enabled:
            st.enabled = False
            smes.set_nanite_settings(mesh, st, apply_changes=True)
        bs = mesh.get_editor_property('body_setup')
        if bs is not None:
            bs.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        b = mesh.get_bounds()
        info.update({
            'slots': slots,
            'material': [mesh.get_material(i).get_path_name() if mesh.get_material(i) else None
                         for i in range(len(slots))],
            'tris': mesh.get_num_triangles(0) if hasattr(mesh, 'get_num_triangles') else None,
            'nanite': smes.get_nanite_settings(mesh).enabled,
            'size_cm': [round(b.box_extent.x * 2, 1), round(b.box_extent.y * 2, 1), round(b.box_extent.z * 2, 1)],
            'floor_z_cm': round(b.origin.z - b.box_extent.z, 2),
            'tex': '%dx%d' % (tex.blueprint_get_size_x(), tex.blueprint_get_size_y()),
        })
        say('%s: %s' % (name, json.dumps(info)))
        touched += [mesh, tex, mi]
    pkgs = []
    for a in touched:
        p = a.get_outermost()
        if p not in pkgs:
            pkgs.append(p)
    ok = unreal.EditorLoadingAndSavingUtils.save_packages(pkgs, False) if pkgs else False
    R['saved'] = {'packages': [p.get_name() for p in pkgs], 'ok': bool(ok)}
    say('saved %d packages ok=%s' % (len(pkgs), ok))


def pkg_file(actor):
    name = actor.get_outermost().get_name()               # /Game/__ExternalActors__/...
    content = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_content_dir())
    return (content + name[len('/Game/'):] + '.uasset').replace('\\', '/')


def targets(eas, revert):
    """(actor, model name, kit mesh name) for every placed actor this tool owns."""
    out = []
    new_to_kit = {'SM_' + n: kit for n, (_, kit) in MODELS.items() if kit}
    new_to_kit['SM_Hatchback'] = 'SM_KeiVan'
    for a in eas.get_all_level_actors():
        if not isinstance(a, unreal.StaticMeshActor):
            continue
        mesh = a.static_mesh_component.get_editor_property('static_mesh')
        if mesh is None:
            continue
        mn, label = mesh.get_name(), a.get_actor_label()
        if revert:
            if mn in new_to_kit and mesh.get_path_name().startswith(DEST) and (not ONLY or mn[3:] in ONLY):
                out.append((a, None, new_to_kit[mn]))
        elif mn in BY_KIT and mesh.get_path_name().startswith(KIT):
            name = BY_LABEL.get(label, BY_KIT[mn])
            if not ONLY or name in ONLY:
                out.append((a, name, mn))
    return sorted(out, key=lambda t: t[0].get_actor_label())


def do_swap(plan_only, revert=False):
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = ues.get_editor_world()
    if world.get_name() != 'Lvl_JumpCut' or ues.get_game_world() is not None:
        raise RuntimeError('wrong world (%s) or PIE is running - stop Play first' % world.get_name())
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    tg = targets(eas, revert)
    files = [pkg_file(a) for a, _, _ in tg]
    with open(os.path.join(OUT_DIR, 'street_models_lock.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(files) + '\n')
    R['actors'] = [{'label': a.get_actor_label(), 'to': n or k, 'from': k if n else 'street model', 'file': fl}
                   for (a, n, k), fl in zip(tg, files)]
    say('%d placed actors %s' % (len(tg), 'would change' if plan_only else 'to change'))
    if plan_only or not tg:
        return
    locked = [fl for fl in files if os.path.isfile(fl) and not os.access(fl, os.W_OK)]
    if locked:
        R['refused'] = locked
        raise RuntimeError('%d actor files are read-only - git lfs lock them first (list in '
                           'Saved/jcpy/street_models_lock.txt). Nothing was changed.' % len(locked))
    meshes, kit_mats = {}, {}
    if revert:
        for a in unreal.EditorAssetLibrary.list_assets('/Game/Game/Materials/City', recursive=False):
            m = unreal.load_asset(a.split('.')[0])
            if m is not None:
                kit_mats[m.get_name().replace('M_', 'MS_', 1)] = m
    pkgs, rows = [], []
    for a, name, kit in tg:
        path = (KIT + kit) if revert else '%s/%s/SM_%s' % (DEST, name, name)
        mesh = meshes.get(path) or unreal.load_asset(path)
        if mesh is None:
            raise RuntimeError('mesh not found: %s - run `import` first. Stopped before saving anything.' % path)
        meshes[path] = mesh
        comp = a.static_mesh_component
        comp.modify()
        comp.set_static_mesh(mesh)
        comp.set_editor_property('override_materials', [])
        if revert:
            for i, sm in enumerate(mesh.get_editor_property('static_materials')):
                m = kit_mats.get(str(sm.get_editor_property('material_slot_name')))
                if m is not None:
                    comp.set_material(i, m)
        xf = a.get_actor_transform()
        if not revert and a.get_actor_label() in YAW:
            xf = unreal.Transform(xf.translation, unreal.Rotator(roll=0.0, pitch=0.0, yaw=YAW[a.get_actor_label()]),
                                  xf.scale3d)
        a.set_actor_transform(xf, False, False)                           # also dirties the actor's own package
        got = comp.get_editor_property('static_mesh')
        rows.append({'label': a.get_actor_label(), 'mesh': got.get_name() if got else None,
                     'overrides': len(comp.get_editor_property('override_materials')),
                     'material0': comp.get_material(0).get_name() if comp.get_material(0) else None})
        pkgs.append(a.get_outermost())
    ok = unreal.EditorLoadingAndSavingUtils.save_packages(pkgs, False)
    R['changed'] = rows
    R['saved'] = {'count': len(pkgs), 'ok': bool(ok)}
    say('changed %d actors, save ok=%s' % (len(rows), ok))


try:
    if MODE == 'import':
        do_import()
    elif MODE in ('plan', 'swap', 'revert'):
        do_swap(MODE == 'plan', revert=(MODE == 'revert'))
    else:
        raise RuntimeError('unknown mode %r - import | plan | swap | revert' % MODE)
    R['ok'] = True
except Exception as e:                                     # noqa: BLE001 - the report is the point
    R['ok'] = False
    R['error'] = '%s: %s' % (type(e).__name__, e)
    R['traceback'] = traceback.format_exc()
    unreal.log_error('[street] ' + R['error'])
finally:
    with open(os.path.join(OUT_DIR, 'street_models.json'), 'w', encoding='utf-8') as f:
        json.dump(R, f, indent=1)
