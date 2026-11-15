# "The car is flickering badly" (Team Owner, 2026-11-15). Read-only probe: what actually draws
# where the wreck stands, in BOTH worlds, plus everything the geometry collection carries.
#
# Run through the editor's status-bar console box:  py <repo>/tools/b1w_carprobe.py
# Writes JumpCut/Saved/b1w_carprobe.json (and prints the same).
#
# Why both worlds: a viewport capture can be of a different world than Python is editing, and
# #109 was chased for a day because CaptureViewport during PIE renders the EDITOR world. So every
# actor below is reported with the world its path lives in.
import unreal, json, os

CAR_BOX = (unreal.Vector(-900.0, -400.0, -50.0), unreal.Vector(-150.0, 400.0, 350.0))
OUT = {}


def vec(v):
    return [round(v.x, 2), round(v.y, 2), round(v.z, 2)]


def gp(o, name, default='<err>'):
    try:
        return o.get_editor_property(name)
    except Exception as e:
        return '%s: %s' % (default, e)


def describe_actor(a):
    d = {'label': a.get_actor_label(), 'name': a.get_name(),
         'class': a.get_class().get_name(), 'path': a.get_path_name()}
    try:
        d['loc'] = vec(a.get_actor_location())
        r = a.get_actor_rotation()
        d['rot'] = [round(r.roll, 2), round(r.pitch, 2), round(r.yaw, 2)]
        d['scale'] = vec(a.get_actor_scale3d())
    except Exception as e:
        d['xform_err'] = str(e)
    for p in ('hidden', 'is_temporarily_hidden_in_editor'):
        d[p] = gp(a, p)
    try:
        o, e = a.get_actor_bounds(False)
        d['bounds_origin'] = vec(o)
        d['bounds_extent'] = vec(e)
    except Exception as ex:
        d['bounds_err'] = str(ex)
    comps = []
    for c in a.get_components_by_class(unreal.PrimitiveComponent):
        cd = {'comp': c.get_name(), 'class': c.get_class().get_name(),
              'visible': gp(c, 'visible'), 'hidden_in_game': gp(c, 'hidden_in_game')}
        try:
            cd['num_materials'] = c.get_num_materials()
            cd['materials'] = [(m.get_name() if m else None) for m in c.get_materials()]
        except Exception as e:
            cd['mat_err'] = str(e)
        if isinstance(c, unreal.StaticMeshComponent):
            sm = gp(c, 'static_mesh')
            cd['static_mesh'] = sm.get_name() if hasattr(sm, 'get_name') else str(sm)
            try:
                cd['tris'] = sum(sm.get_num_triangles(i) for i in range(sm.get_num_lods()))
                cd['lods'] = sm.get_num_lods()
                cd['nanite'] = sm.get_editor_property('nanite_settings').enabled
            except Exception as e:
                cd['sm_err'] = str(e)
        if 'GeometryCollection' in c.get_class().get_name():
            for p in ('object_type', 'enable_clustering', 'cluster_group_index',
                      'damage_propagation_data', 'rest_collection', 'cache_parameters',
                      'notify_breaks', 'notify_removals', 'enable_nanite',
                      'cast_shadow', 'bounds_scale'):
                v = gp(c, p)
                cd[p] = v.get_name() if hasattr(v, 'get_name') else str(v)
        comps.append(cd)
    d['components'] = comps
    return d


def world_report(world, tag):
    acts = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    hits = []
    for a in acts:
        try:
            o, e = a.get_actor_bounds(False)
        except Exception:
            continue
        lo = unreal.Vector(o.x - e.x, o.y - e.y, o.z - e.z)
        hi = unreal.Vector(o.x + e.x, o.y + e.y, o.z + e.z)
        if (lo.x <= CAR_BOX[1].x and hi.x >= CAR_BOX[0].x and
                lo.y <= CAR_BOX[1].y and hi.y >= CAR_BOX[0].y and
                lo.z <= CAR_BOX[1].z and hi.z >= CAR_BOX[0].z):
            if e.x < 1.0 and e.y < 1.0 and e.z < 1.0:
                continue                      # skip point actors (lights, notes, markers)
            hits.append(describe_actor(a))
    return {'tag': tag, 'world': world.get_path_name(), 'total_actors': len(acts),
            'overlapping_car_box': len(hits), 'actors': hits}


def gc_asset_report():
    r = {}
    gc = unreal.load_asset('/Game/Game/Destruction/GC_CrashCar')
    if gc is None:
        return {'error': 'GC_CrashCar not found'}
    r['class'] = gc.get_class().get_name()
    mats = gp(gc, 'materials')
    try:
        r['materials'] = [(m.get_name() if m else None) for m in mats]
        r['material_parents'] = []
        for m in mats:
            p = None
            try:
                p = m.get_editor_property('parent')
            except Exception:
                pass
            r['material_parents'].append(p.get_name() if p else None)
    except Exception as e:
        r['materials_err'] = str(e)
    for p in ('enable_nanite', 'collision_type', 'implicit_type', 'collision_object_reduction_percentage',
              'density', 'minimum_mass_clamp', 'root_proxy_data', 'asset_import_data'):
        v = gp(gc, p)
        r[p] = v.get_name() if hasattr(v, 'get_name') else str(v)
    return r


def sm_asset_report(path):
    sm = unreal.load_asset(path)
    if sm is None:
        return {'error': path + ' not found'}
    r = {'name': sm.get_name()}
    try:
        r['lods'] = sm.get_num_lods()
        r['tris'] = [sm.get_num_triangles(i) for i in range(sm.get_num_lods())]
        r['verts'] = [sm.get_num_vertices(i) for i in range(sm.get_num_lods())]
        r['materials'] = [(m.material_interface.get_name() if m.material_interface else None)
                          for m in sm.get_editor_property('static_materials')]
        b = sm.get_bounding_box()
        r['bounds_min'] = vec(b.min)
        r['bounds_max'] = vec(b.max)
        r['nanite'] = sm.get_editor_property('nanite_settings').enabled
    except Exception as e:
        r['err'] = str(e)
    return r


def main():
    # get_editor_world() on EditorLevelLibrary returns None while PIE is up ("The Editor is
    # currently in a play mode") - the UnrealEditorSubsystem answers in both states.
    sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    ed = sub.get_editor_world()
    g = sub.get_game_world()
    OUT['pie_running'] = bool(g)
    for w, tag in ((ed, 'editor'), (g, 'pie')):
        if w is None:
            OUT[tag] = {'tag': tag, 'world': None}
            continue
        try:
            OUT[tag] = world_report(w, tag)
        except Exception as e:
            OUT[tag] = {'tag': tag, 'err': str(e)}
    OUT['gc_asset'] = gc_asset_report()
    OUT['sm_crashcar'] = sm_asset_report('/Game/Game/Imported/City/SM_CrashCar')
    p = os.path.join(unreal.Paths.project_saved_dir(), 'b1w_carprobe.json')
    with open(p, 'w') as fh:
        json.dump(OUT, fh, indent=1)
    unreal.log('B1WCARPROBE wrote %s' % p)
    print('B1WCARPROBE wrote %s' % p)


main()
