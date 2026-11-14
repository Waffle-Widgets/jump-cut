"""Chaos for the beats 1-3 environment: things the player can smash, and things that get knocked about.

Run in the Unreal editor's console box with Play mode stopped:
    py <repo>/tools/unreal_chaos_props.py assets     cut the Geometry Collections from the city kit meshes and save them
    py <repo>/tools/unreal_chaos_props.py place      swap the placed props (idempotent; never saves - prints what to lock)
    py <repo>/tools/unreal_chaos_props.py report     what is in the level now (and which package files to git lfs lock)
    py <repo>/tools/unreal_chaos_props.py save       save exactly the actor packages this script owns (lock them first)
Result: <project>/Saved/jcpy/chaos_props.json

The Geometry Collection assets themselves are made first, by hand through the MCP (there is no Python call for it):
DataflowAgentToolset.CreateDataflowCompatibleAssetFromTemplate, className GeometryCollection, path
/Game/Game/Destruction, template /GeometryCollectionPlugin/DataflowTemplates/DF_GC_Template_StaticMesh.

BREAK: each placed static prop of these models is hidden with collision off (never deleted: the city placer owns
       it) and a GeometryCollectionActor '<label>_GC' tagged JC_Break stands in its place.
       Crate stacks also get JC_BreakSoft: the same push throws their pieces about 7x faster (measured).
KNOCK: these placed props stay what they are, but simulate physics (tag JC_Knock). Their meshes must have SIMPLE
       collision: the city kit was set to complex-as-simple, which Unreal refuses to simulate, so 'assets' switches
       these three meshes back to default and adds a box if they have none. Ejection speed is capped
       (max_depenetration_velocity) because a bag punched into a wall left at 16 m altitude without it.
       NO_KNOCK lists placed props that rest on something else and floated when simulated; they stay static.
Only props on the beats 1-3 route are touched (X_MIN..X_MAX).
"""
import json, os, sys, traceback
import unreal

MODE = sys.argv[1] if len(sys.argv) > 1 else 'report'
OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'chaos_props.json')
KIT = '/Game/Game/Imported/City/'
DEST = '/Game/Game/Destruction/'
# model -> (pieces min, pieces max)
BREAK = {'SM_CrateStack': (10, 14), 'SM_CafeTable': (8, 10), 'SM_Barrier': (10, 14)}
# model -> mass in kg
KNOCK = {'SM_CafeChair': 6.0, 'SM_TrafficCone': 3.0, 'SM_TrashBags': 8.0}
NO_KNOCK = ('City_Prop_S009_TrashBags', 'City_Prop_N046_TrashBags')
X_MIN, X_MAX = -2000.0, 9700.0
out = {'mode': MODE}
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
DBL = unreal.DataflowBlueprintLibrary


def gc_name(model):
    return 'GC_' + model[3:]


def do_assets():
    res = {}
    for model, (lo, hi) in BREAK.items():
        r = {}
        gc = unreal.load_asset(DEST + gc_name(model))
        sm = None
        for a in eas.get_all_level_actors():
            if a.get_class().get_name() == 'StaticMeshActor' and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name() == model:
                sm = a.static_mesh_component.static_mesh
                break
        r['mesh'] = sm.get_path_name() if sm else None
        r['vars'] = [str(v) for v in DBL.get_dataflow_variable_list(gc)] if hasattr(DBL, 'get_dataflow_variable_list') else None
        r['override'] = str(DBL.override_dataflow_variable_object(gc, 'SourceStaticMesh', sm))
        r['regen'] = str(DBL.regenerate_asset_from_dataflow(gc))
        r['mats'] = [m.get_name() if m else None for m in gc.get_editor_property('materials')]
        b = gc.get_editor_property('bounds') if 'bounds' in dir(gc) else None
        r['saved'] = unreal.EditorAssetLibrary.save_loaded_asset(gc)
        res[model] = r
    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    pk = []
    for model in KNOCK:
        m = unreal.load_asset(KIT + model)
        bs = m.get_editor_property('body_setup')
        if bs.get_editor_property('collision_trace_flag') != unreal.CollisionTraceFlag.CTF_USE_DEFAULT or sms.get_simple_collision_count(m) == 0:
            m.modify(); bs.modify()
            bs.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_DEFAULT)
            if sms.get_simple_collision_count(m) == 0:
                sms.add_simple_collisions(m, unreal.ScriptCollisionShapeType.BOX)
            pk.append(m.get_outermost())
        res[model] = {'simple': sms.get_simple_collision_count(m)}
    if pk:
        res['knock_meshes_saved'] = unreal.EditorLoadingAndSavingUtils.save_packages(pk, False)
    out['assets'] = res


def placed():
    rows = []
    for a in eas.get_all_level_actors():
        cn = a.get_class().get_name()
        l = a.get_actor_location()
        if cn == 'StaticMeshActor':
            sm = a.static_mesh_component.static_mesh
            n = sm.get_name() if sm else ''
            if (n in BREAK or n in KNOCK) and X_MIN <= l.x <= X_MAX and a.get_actor_label() not in NO_KNOCK:
                rows.append((a, n))
    return rows


def full_transform_touch(a):
    # re-setting the whole transform is what dirties a one-file-per-actor package
    a.modify()
    a.set_actor_transform(a.get_actor_transform(), False, True)


def do_place():
    made, knocked, touched = [], [], []
    labels = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
    for a, model in placed():
        lab = a.get_actor_label()
        if model in BREAK:
            if lab + '_GC' in labels:
                continue
            gc = unreal.load_asset(DEST + gc_name(model))
            g = eas.spawn_actor_from_class(unreal.GeometryCollectionActor, a.get_actor_location(), a.get_actor_rotation())
            g.set_actor_label(lab + '_GC')
            g.set_actor_scale3d(a.get_actor_scale3d())
            g.tags = [unreal.Name('JC_Break'), unreal.Name('JC_Chaos')] + ([unreal.Name('JC_BreakSoft')] if model == 'SM_CrateStack' else [])
            c = g.get_component_by_class(unreal.GeometryCollectionComponent)
            c.set_rest_collection(gc)
            c.set_editor_property('damage_threshold', [5000.0, 2000.0, 500.0])
            g.set_folder_path('Chaos')
            a.set_actor_hidden_in_game(True)
            a.set_is_temporarily_hidden_in_editor(True)
            a.set_actor_enable_collision(False)
            full_transform_touch(a)
            made.append(lab + '_GC')
            touched.append(a.get_outermost().get_name())
        else:
            c = a.static_mesh_component
            c.modify()
            c.set_editor_property('mobility', unreal.ComponentMobility.MOVABLE)
            # set_simulate_physics() alone does not persist on a placed actor: write the body instance itself
            bi = c.get_editor_property('body_instance')
            bi.set_editor_property('simulate_physics', True)
            bi.set_editor_property('override_max_depenetration_velocity', True)
            bi.set_editor_property('max_depenetration_velocity', 120.0)
            bi.set_editor_property('use_ccd', True)
            bi.set_editor_property('linear_damping', 0.4)
            bi.set_editor_property('angular_damping', 0.8)
            c.set_editor_property('body_instance', bi)
            c.set_mass_override_in_kg('None', KNOCK[model], True)
            c.set_collision_profile_name('PhysicsActor')
            a.tags = [t for t in a.tags if str(t) not in ('JC_Knock',)] + [unreal.Name('JC_Knock')]
            full_transform_touch(a)
            knocked.append(lab)
            touched.append(a.get_outermost().get_name())
    out['made'] = made
    out['knocked'] = knocked
    out['lock_these'] = sorted(set(touched))


def do_report():
    rows = []
    for a in eas.get_all_level_actors():
        tags = [str(t) for t in a.tags]
        if 'JC_Break' in tags or 'JC_Knock' in tags:
            l = a.get_actor_location()
            r = {'label': a.get_actor_label(), 'class': a.get_class().get_name(), 'x': round(l.x), 'y': round(l.y), 'tags': tags, 'pkg': a.get_outermost().get_name()}
            if 'JC_Knock' in tags:
                c = a.static_mesh_component
                r['sim'] = c.get_editor_property('body_instance').get_editor_property('simulate_physics')
                r['mob'] = str(c.get_editor_property('mobility'))
            else:
                c = a.get_component_by_class(unreal.GeometryCollectionComponent)
                rc = c.get_editor_property('rest_collection')
                r['gc'] = rc.get_name() if rc else None
            rows.append(r)
    out['actors'] = rows
    out['hidden_originals'] = [{'label': a.get_actor_label(), 'hidden': a.get_editor_property('hidden'), 'coll': a.get_actor_enable_collision(), 'pkg': a.get_outermost().get_name()} for a, m in placed() if m in BREAK]


def do_save():
    pk = []
    for a in eas.get_all_level_actors():
        tags = [str(t) for t in a.tags]
        if 'JC_Break' in tags or 'JC_Knock' in tags:
            pk.append(a.get_outermost())
    for a, m in placed():
        if m in BREAK:
            pk.append(a.get_outermost())
    out['saving'] = len(pk)
    out['ok'] = unreal.EditorLoadingAndSavingUtils.save_packages(pk, False)


try:
    {'assets': do_assets, 'place': do_place, 'report': do_report, 'save': do_save}[MODE]()
    out['dirty'] = [q.get_name() for q in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())]
except Exception:
    out['error'] = traceback.format_exc()
with open(OUT, 'w') as fh:
    fh.write(json.dumps(out, indent=1))
