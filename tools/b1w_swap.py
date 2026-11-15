"""Prove the car swap at the moment of the blast: the static wreck goes, the geometry collection
appears and comes apart. Run with PIE up.

    py <repo>/tools/b1w_swap.py
Writes Saved/jcpy/b1w_swap.json.
"""
import unreal, os, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
res = {}
try:
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    assert w is not None, 'no PIE world'

    def cars():
        out = {}
        for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
            l = a.get_actor_label()
            if l in ('City_CafeCrashCar', 'B1_Cafe_CrashCar_GC'):
                o, e = a.get_actor_bounds(False)
                row = {'hidden': bool(a.get_editor_property('hidden')),
                       'extent': [round(e.x, 1), round(e.y, 1), round(e.z, 1)],
                       'origin': [round(o.x, 1), round(o.y, 1), round(o.z, 1)]}
                c = a.get_component_by_class(unreal.GeometryCollectionComponent)
                if c is not None:
                    row['object_type'] = str(c.get_editor_property('object_type'))
                out[l] = row
        return out

    res['before'] = cars()
    d = unreal.GameplayStatics.get_all_actors_of_class(
        w, unreal.load_object(None, '/Game/Game/Blueprints/BP_OpeningDirector.BP_OpeningDirector_C'))[0]
    d.call_method('CineExplFire')
    res['after_call'] = cars()
except Exception:
    res['error'] = traceback.format_exc()
with open(os.path.join(OUT, 'b1w_swap.json'), 'w') as f:
    json.dump(res, f, indent=1, default=str)
print('B1W_SWAP done')
