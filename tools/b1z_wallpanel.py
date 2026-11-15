"""SM_CafeWallPanel into the game: import it, cut it into Chaos pieces, stand it in the hole.

    py <repo>/tools/b1z_wallpanel.py import   import the FBX, point its slots at the kit's look
                                              materials, Nanite off, save the mesh asset
    py <repo>/tools/b1z_wallpanel.py gc       regenerate GC_CafeWallPanel from the mesh and carry
                                              the same materials onto the collection, save it
    py <repo>/tools/b1z_wallpanel.py place    stand B1_Cafe_WallPanel_GC in the hole (never saves)
    py <repo>/tools/b1z_wallpanel.py report   read everything back, change nothing

The GC ASSET ITSELF has to be created once by hand through the MCP - there is no Python call for it:
  DataflowAgentToolset.CreateDataflowCompatibleAssetFromTemplate
  className GeometryCollection, path /Game/Game/Destruction, name GC_CafeWallPanel,
  template /GeometryCollectionPlugin/DataflowTemplates/DF_GC_Template_StaticMesh
Then this script's `gc` mode fills it, exactly as tools/b1x_assets.py does for GC_CrashCar.

THREE TRAPS, all already paid for once on GC_CrashCar (CLAUDE.md):
  * a GeometryCollectionActor spawns Chaos_Object_Dynamic and a wall-sized one falls out of the
    world - it stands KINEMATIC and the director switches it before it breaks it;
  * a GC draws the materials its SOURCE FBX came in with, which are the flat grey MS_* import
    placeholders, so the collection's own materials array is set here too;
  * Chaos debris does not collide with the city kit's complex-as-simple floors - the hidden
    B1_Cafe_DebrisFloor (x -1320..280, y -600..600, top z 0) already covers this wall.

Writes Saved/jcpy/b1z_wallpanel.json.
"""
import unreal, os, sys, json, traceback

MODE = sys.argv[1] if len(sys.argv) > 1 else 'report'
OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = 'SM_CafeWallPanel'
SRC = os.path.join(REPO, 'JumpCut', 'Content', 'Game', 'Imported', 'Beat1', NAME + '.fbx')
DEST = '/Game/Game/Imported/Beat1'
SM_PATH = '%s/%s' % (DEST, NAME)
GC_PATH = '/Game/Game/Destruction/GC_CafeWallPanel'
LABEL = 'B1_Cafe_WallPanel_GC'
TAG = 'B1_Cine'
PLACE = (-622.1, -15.0, 127.3)

res = {'mode': MODE}


def kit_materials():
    """slot name -> the look material the placed City_CafeShell actually draws on that slot."""
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == 'City_CafeShell':
            smc = a.get_component_by_class(unreal.StaticMeshComponent)
            sm = smc.static_mesh
            names = [str(s.material_slot_name) for s in sm.get_editor_property('static_materials')]
            return {n: smc.get_material(i) for i, n in enumerate(names)}
    return {}


try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    assert ues.get_editor_world().get_name() == 'Lvl_JumpCut', 'wrong world'
    assert ues.get_game_world() is None, 'PIE is running - stop it first'
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)

    if MODE == 'import':
        assert os.path.exists(SRC), 'no FBX at %s' % SRC
        existed = unreal.EditorAssetLibrary.does_asset_exist(SM_PATH)
        p = os.path.join(os.path.dirname(SRC), NAME + '.uasset')
        if existed and os.path.exists(p) and not os.access(p, os.W_OK):
            os.chmod(p, 0o666)      # or re-import raises the modal Check Out Assets dialog
        t = unreal.AssetImportTask()
        t.set_editor_property('filename', SRC)
        t.set_editor_property('destination_path', DEST)
        t.set_editor_property('destination_name', NAME)
        t.set_editor_property('replace_existing', True)
        t.set_editor_property('automated', True)
        t.set_editor_property('save', False)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
        sm = unreal.load_asset(SM_PATH)
        res['imported'] = sm is not None
        assert sm is not None, 'import produced nothing'
        # Interchange turns Nanite ON and its fallback mesh drops thin parts (the dado rail here)
        ns = sms.get_nanite_settings(sm)
        if ns.enabled:
            ns.enabled = False
            sms.set_nanite_settings(sm, ns, apply_changes=True)
        km = kit_materials()
        rows = []
        slots = [str(s.material_slot_name) for s in sm.get_editor_property('static_materials')]
        mats = sm.get_editor_property('static_materials')
        for i, n in enumerate(slots):
            want = km.get(n)
            had = mats[i].material_interface
            if want is not None:
                mats[i].material_interface = want
            rows.append({'slot': n, 'was': had.get_name() if had else None,
                         'now': want.get_name() if want else 'UNCHANGED (no kit match)'})
        sm.set_editor_property('static_materials', mats)
        res['slots'] = rows
        res['nanite'] = bool(sm.get_editor_property('nanite_settings').enabled)
        b = sm.get_bounds()
        res['bounds'] = {'origin': [round(b.origin.x, 2), round(b.origin.y, 2), round(b.origin.z, 2)],
                         'extent': [round(b.box_extent.x, 2), round(b.box_extent.y, 2), round(b.box_extent.z, 2)]}
        res['saved'] = unreal.EditorAssetLibrary.save_loaded_asset(sm)

    elif MODE == 'gc':
        gc = unreal.load_asset(GC_PATH)
        sm = unreal.load_asset(SM_PATH)
        assert gc is not None, 'make GC_CafeWallPanel from the Dataflow template first (see docstring)'
        assert sm is not None, 'no %s - run import first' % SM_PATH
        DBL = unreal.DataflowBlueprintLibrary
        res['vars'] = [str(v) for v in DBL.get_dataflow_variable_list(gc)]
        res['override'] = str(DBL.override_dataflow_variable_object(gc, 'SourceStaticMesh', sm))
        res['regen'] = str(DBL.regenerate_asset_from_dataflow(gc))
        # the collection came in with the FBX's own placeholder materials; carry the look ones over
        km = kit_materials()
        slots = [str(s.material_slot_name) for s in sm.get_editor_property('static_materials')]
        before = [m.get_name() if m else None for m in gc.get_editor_property('materials')]
        want = [km.get(n) for n in slots]
        cur = list(gc.get_editor_property('materials'))
        for i, w in enumerate(want):
            if w is not None and i < len(cur):
                cur[i] = w
        gc.set_editor_property('materials', cur)
        res['mats_before'] = before
        res['mats_after'] = [m.get_name() if m else None for m in gc.get_editor_property('materials')]
        try:
            res['pieces'] = gc.get_editor_property('geometry_collection').num_elements('Transform')
        except Exception as e:
            res['pieces'] = 'n/a %s' % e
        res['saved'] = unreal.EditorAssetLibrary.save_loaded_asset(gc)

    elif MODE == 'place':
        gc = unreal.load_asset(GC_PATH)
        assert gc is not None, 'no GC asset'
        old = [a for a in eas.get_all_level_actors() if a.get_actor_label() == LABEL]
        for a in old:
            eas.destroy_actor(a)
        res['removed_old'] = len(old)
        a = eas.spawn_actor_from_class(unreal.GeometryCollectionActor,
                                       unreal.Vector(*PLACE), unreal.Rotator())
        a.set_actor_label(LABEL)
        a.set_editor_property('tags', [unreal.Name(TAG)])
        comp = a.get_component_by_class(unreal.GeometryCollectionComponent)
        comp.set_rest_collection(gc)
        # a punch must NOT take the wall apart - only the car does, through ApplyExternalStrain
        comp.set_editor_property('damage_threshold', [500000.0, 500000.0, 500000.0])
        # KINEMATIC: a dynamic wall-sized collection falls out of the world at BeginPlay.
        comp.set_editor_property('object_type', unreal.ObjectStateTypeEnum.CHAOS_OBJECT_KINEMATIC)
        comp.set_editor_property('enable_clustering', True)
        comp.set_editor_property('notify_breaks', True)
        a.set_folder_path('Chaos')
        # hidden until the opening shows it, exactly like the grey patch it replaces
        a.set_actor_hidden_in_game(True)
        a.set_actor_location_and_rotation(unreal.Vector(*PLACE), unreal.Rotator(), False, True)
        res['placed'] = {'label': a.get_actor_label(),
                         'loc': [round(a.get_actor_location().x, 2), round(a.get_actor_location().y, 2),
                                 round(a.get_actor_location().z, 2)],
                         'object_type': str(comp.get_editor_property('object_type')),
                         'rest': comp.get_editor_property('rest_collection').get_name(),
                         'hidden': bool(a.get_editor_property('hidden'))}
        o = a.get_actor_bounds(False)
        res['placed']['bounds_origin'] = [round(o[0].x, 2), round(o[0].y, 2), round(o[0].z, 2)]
        res['placed']['bounds_extent'] = [round(o[1].x, 2), round(o[1].y, 2), round(o[1].z, 2)]
        res['package'] = a.get_outermost().get_name()

    else:   # report
        sm = unreal.load_asset(SM_PATH)
        gc = unreal.load_asset(GC_PATH)
        res['sm'] = None if sm is None else {
            'slots': [str(s.material_slot_name) for s in sm.get_editor_property('static_materials')],
            'mats': [s.material_interface.get_name() if s.material_interface else None
                     for s in sm.get_editor_property('static_materials')],
            'nanite': bool(sm.get_editor_property('nanite_settings').enabled)}
        res['gc'] = None if gc is None else {
            'mats': [m.get_name() if m else None for m in gc.get_editor_property('materials')]}
        for a in eas.get_all_level_actors():
            if a.get_actor_label() == LABEL:
                comp = a.get_component_by_class(unreal.GeometryCollectionComponent)
                o = a.get_actor_bounds(False)
                res['actor'] = {'loc': [round(a.get_actor_location().x, 2), round(a.get_actor_location().y, 2),
                                        round(a.get_actor_location().z, 2)],
                                'hidden': bool(a.get_editor_property('hidden')),
                                'object_type': str(comp.get_editor_property('object_type')),
                                'bounds_origin': [round(o[0].x, 2), round(o[0].y, 2), round(o[0].z, 2)],
                                'bounds_extent': [round(o[1].x, 2), round(o[1].y, 2), round(o[1].z, 2)]}
except Exception as e:
    res['error'] = repr(e)
    res['tb'] = traceback.format_exc()

with open(os.path.join(OUT, 'b1z_wallpanel.json'), 'w') as fh:
    json.dump(res, fh, indent=1, default=str)
print('b1z_wallpanel %s done' % MODE)
