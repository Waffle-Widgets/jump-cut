"""Look at NS_CarFire in the EDITOR viewport, where the camera is mine to place.

An instance NiagaraComponent added in the editor does not auto-activate outside play, and the two
red `C1_Layout` placeholder cubes (hidden in game, visible in the editor) sit exactly over the
wreck - so the editor shows neither the car nor the fire until both are dealt with.

    py <repo>/tools/b1y_firelook.py on     activate the fire, hide the placeholder cubes
    py <repo>/tools/b1y_firelook.py off    put both back
The hide is `set_is_temporarily_hidden_in_editor`, which is transient and never saved.
"""
import unreal, os, sys, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
MODE = sys.argv[1] if len(sys.argv) > 1 else 'on'
HIDE = ('C1_Cafe_Car', 'C1_Cafe_CarCab')
res = {'mode': MODE}
try:
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    by = {}
    for a in eas.get_all_level_actors():
        by.setdefault(a.get_actor_label(), a)
    fire = by.get('B1_Cafe_Fire')
    assert fire is not None, 'no B1_Cafe_Fire'
    comps = fire.get_components_by_class(unreal.NiagaraComponent)
    assert comps, 'no NiagaraComponent on B1_Cafe_Fire'
    c = comps[0]
    if MODE == 'on':
        c.activate(True)
        for n in HIDE:
            if by.get(n):
                by[n].set_is_temporarily_hidden_in_editor(True)
        res['hidden'] = list(HIDE)
    else:
        c.deactivate()
        for n in HIDE:
            if by.get(n):
                by[n].set_is_temporarily_hidden_in_editor(False)
        res['shown'] = list(HIDE)
    res['fire'] = {'active': c.is_active(), 'visible': c.is_visible(),
                   'world': [round(v, 1) for v in c.get_world_location().to_tuple()]}
    gc = by.get('B1_Cafe_CrashCar_GC')
    if gc:
        res['wreck_hidden_in_game'] = bool(gc.get_editor_property('hidden'))
except Exception:
    res['error'] = traceback.format_exc()
with open(os.path.join(OUT, 'b1y_firelook.json'), 'w') as f:
    json.dump(res, f, indent=1, default=str)
print('B1Y_FIRELOOK_%s %s' % (MODE.upper(), json.dumps(res.get('fire'))))
