"""Why does the exploding car have no textures? Compare the materials the GEOMETRY COLLECTION draws
with (MS_* from Imported/City, the import-time ones) against the ones the placed static wreck
overrides to (M_* from Materials/City, the real look).

    py <repo>/tools/b1y_mats.py
Reads only. Writes Saved/jcpy/b1y_mats.json.
"""
import unreal, os, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
res = {}
NAMES = ['CityAccent', 'CityTrim', 'CityGlass', 'CityMetal', 'CitySignA', 'CityWall', 'CityCloth']


def describe(p):
    a = unreal.load_asset(p)
    if a is None:
        return {'path': p, 'exists': False}
    d = {'path': p, 'exists': True, 'class': a.get_class().get_name()}
    try:
        par = a.get_editor_property('parent')
        d['parent'] = par.get_path_name() if par else None
    except Exception:
        d['parent'] = 'n/a'
    # scalar / vector / texture parameter overrides actually set on an instance
    for key, prop in (('vectors', 'vector_parameter_values'),
                      ('scalars', 'scalar_parameter_values'),
                      ('textures', 'texture_parameter_values')):
        try:
            vals = a.get_editor_property(prop)
            out = []
            for v in vals:
                nm = str(v.get_editor_property('parameter_info').get_editor_property('name'))
                pv = v.get_editor_property('parameter_value')
                if hasattr(pv, 'get_path_name'):
                    pv = pv.get_path_name()
                elif hasattr(pv, 'r'):
                    pv = [round(pv.r, 3), round(pv.g, 3), round(pv.b, 3)]
                out.append({nm: pv})
            d[key] = out
        except Exception:
            pass
    try:
        d['base'] = str(a.get_base_material().get_path_name())
    except Exception:
        pass
    return d


try:
    rows = {}
    for n in NAMES:
        rows['MS_' + n] = describe('/Game/Game/Imported/City/MS_' + n)
        rows['M_' + n] = describe('/Game/Game/Materials/City/M_' + n)
    res['materials'] = rows
    # does any other City_* actor rely on MS_* with no override? (i.e. would changing MS_* matter)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    no_override = []
    for a in eas.get_all_level_actors():
        c = a.get_component_by_class(unreal.StaticMeshComponent)
        if c is None:
            continue
        try:
            ovs = list(c.get_editor_property('override_materials'))
        except Exception:
            ovs = []
        n = c.get_num_materials()
        if n and (not ovs or all(o is None for o in ovs)):
            m0 = c.get_material(0)
            if m0 and '/Imported/City/MS_' in m0.get_path_name():
                no_override.append(a.get_actor_label())
    res['actors_drawing_MS_directly'] = sorted(no_override)[:40]
    res['actors_drawing_MS_directly_count'] = len(no_override)
except Exception:
    res['error'] = traceback.format_exc()

with open(os.path.join(OUT, 'b1y_mats.json'), 'w') as f:
    json.dump(res, f, indent=1)
print('B1Y_MATS_DONE')
