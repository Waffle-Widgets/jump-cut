# Second pass on "the car is flickering badly": WHICH renderer draws the wreck, and what the
# surfaces it draws are made of.
#
# Established by pass 1 (tools/b1w_carprobe.py + Saved/b1w_carprobe.json):
#   - in the PIE world only B1_Cafe_CrashCar_GC draws the car; City_CafeCrashCar is bHidden.
#   - GC_CrashCar carries a ROOT PROXY pointing at SM_CrashCar with EMPTY override materials.
#     UE 5.8 GeometryCollectionComponent.cpp:6540 only uses the root proxy through the CUSTOM
#     renderer path, so whether that path is live decides what is on screen - and if it IS live
#     the car draws the static mesh's own MS_* grey import placeholders, not the M_City* look
#     materials the collection carries.
#
# Run: py <repo>/tools/b1w_carprobe2.py      (read-only)
import unreal, json, os, traceback

OUT = {}
P = '/Game/Game/Destruction/GC_CrashCar'


def gp(o, n):
    try:
        v = o.get_editor_property(n)
        return v.get_name() if hasattr(v, 'get_name') else v
    except Exception as e:
        return 'ERR: %s' % e


def mat_report(m):
    if m is None:
        return None
    r = {'name': m.get_name(), 'class': m.get_class().get_name(), 'path': m.get_path_name()}
    base = m
    try:
        if isinstance(m, unreal.MaterialInstance):
            r['parent'] = gp(m, 'parent')
            base = m.get_base_material()
            r['base'] = base.get_name() if base else None
    except Exception as e:
        r['parent_err'] = str(e)
    for n in ('two_sided', 'blend_mode', 'shading_model', 'dither_opacity_mask',
              'allow_negative_emissive_color', 'use_material_attributes',
              'opacity_mask_clip_value'):
        r[n] = gp(base if base else m, n)
    return r


try:
    gc = unreal.load_asset(P)
    OUT['gc'] = {'name': gc.get_name()}

    # ---- what the collection is made of -------------------------------------------------
    for n in ('materials', 'root_proxy_data', 'enable_nanite'):
        v = gp(gc, n)
        OUT['gc'][n] = str(v) if n == 'root_proxy_data' else (
            [x.get_name() if x else None for x in v] if n == 'materials' else v)
    OUT['gc']['materials_detail'] = [mat_report(m) for m in gc.get_editor_property('materials')]

    # the rest collection's own geometry, if the python bindings expose it
    counts = {}
    for n in ('number_of_elements', 'num_elements'):
        counts[n] = gp(gc, n)
    try:
        counts['geometry_group'] = gc.get_editor_property('geometry_source')
    except Exception as e:
        counts['geometry_source'] = 'ERR: %s' % e
    OUT['gc']['counts'] = {k: str(v) for k, v in counts.items()}

    # ---- which renderer path is live ----------------------------------------------------
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    w = ues.get_game_world() or ues.get_editor_world()
    OUT['world'] = w.get_path_name() if w else None
    comps = []
    for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.GeometryCollectionActor):
        c = a.get_component_by_class(unreal.GeometryCollectionComponent)
        if c is None:
            continue
        row = {'actor': a.get_actor_label(), 'rest': gp(c, 'rest_collection')}
        for n in ('custom_renderer_type', 'hidden_in_game', 'visible', 'object_type',
                  'cast_shadow', 'render_custom_depth', 'custom_depth_stencil_value',
                  'bounds_scale', 'enable_clustering', 'use_static_mesh_collision_for_traces'):
            row[n] = str(gp(c, n))
        row['num_materials'] = c.get_num_materials()
        row['materials'] = [(c.get_material(i).get_name() if c.get_material(i) else None)
                            for i in range(c.get_num_materials())]
        comps.append(row)
    OUT['gc_components'] = comps

    # the cvar that gates the custom renderer at all
    cv = {}
    for n in ('p.Chaos.GC.UseCustomRenderer', 'p.Chaos.GC.DefaultCustomRendererType',
              'p.Chaos.GC.UseRootProxyForRendering'):
        v = unreal.SystemLibrary.get_console_variable_string_value(n)
        cv[n] = v
    OUT['cvars'] = cv

    # ---- the static mesh the root proxy points at ---------------------------------------
    sm = unreal.load_asset('/Game/Game/Imported/City/SM_CrashCar')
    OUT['sm_materials_detail'] = [mat_report(s.material_interface)
                                  for s in sm.get_editor_property('static_materials')]

    # ---- does the player's look pass single the car out? --------------------------------
    OUT['anime_look'] = {}
    for p in ('/Game/Game/Materials/MI_AnimeLook_JumpCut',):
        a = unreal.load_asset(p)
        OUT['anime_look'][p] = a.get_name() if a else None
except Exception:
    OUT['error'] = traceback.format_exc()

p = os.path.join(unreal.Paths.project_saved_dir(), 'b1w_carprobe2.json')
with open(p, 'w') as fh:
    json.dump(OUT, fh, indent=1, default=str)
print('B1WCARPROBE2 wrote %s' % p)
