"""Is there ever more than ONE car on screen during the opening? Count them, frame by frame.

The cinematic car is a Sequencer SPAWNABLE built from SM_CrashCar; the real wreck is the geometry
collection B1_Cafe_CrashCar_GC; the old static City_CafeCrashCar is hidden for good. This samples
every 0.1 s from JumpCutStartPlay for 10 s and records, per sample, every one of those that is
actually DRAWN (not hidden in game, component visible).

    py <repo>/tools/b1y_cars.py        (run first, then press Play)
Writes Saved/jcpy/b1y_cars.json. Reads only.
"""
import unreal, os, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
R = {'rows': [], 'events': [], 'done': False}
st = {'t': -1.0, 'next': 0.0, 'waited': 0.0, 'started': False}
handle = [None]


def ev(s):
    R['events'].append('%.2f %s' % (max(st['t'], 0.0), s))
    print('   ' + str(s))


def drawn_cars(w):
    out = []
    for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
        if bool(a.get_editor_property('hidden')):
            continue
        name = None
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            m = c.get_editor_property('static_mesh')
            if m is not None and 'CrashCar' in m.get_name() and c.is_visible():
                name = m.get_name()
        for c in a.get_components_by_class(unreal.GeometryCollectionComponent):
            rc = c.get_editor_property('rest_collection')
            if rc is not None and 'CrashCar' in rc.get_name() and c.is_visible():
                name = rc.get_name()
        if name:
            lab = a.get_actor_label() or a.get_name()
            out.append('%s[%s]' % (lab, name))
    return sorted(out)


def finish():
    R['done'] = True
    worst = 0
    for r in R['rows']:
        worst = max(worst, len(r['cars']))
    R['max_cars_at_once'] = worst
    R['verdict'] = 'PASS - never more than one car drawn' if worst <= 1 else 'FAIL - %d at once' % worst
    with open(os.path.join(OUT, 'b1y_cars.json'), 'w') as f:
        json.dump(R, f, indent=1)
    if handle[0] is not None:
        unreal.unregister_slate_post_tick_callback(handle[0])
        handle[0] = None
    print('B1Y_CARS_DONE %s' % R['verdict'])


def tick(dt):
    try:
        w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if w is None:
            st['waited'] += dt
            if st['waited'] > 30.0:
                ev('no PIE')
                finish()
            return
        if not st['started']:
            st['started'] = True
            st['t'] = 0.0
            gm = unreal.GameplayStatics.get_game_mode(w)
            try:
                gm.call_method('JumpCutStartPlay')
                ev('JumpCutStartPlay')
            except Exception as e:
                ev('start failed %s' % e)
        else:
            st['t'] += dt
        if st['t'] >= st['next']:
            st['next'] += 0.1
            R['rows'].append({'t': round(st['t'], 2), 'cars': drawn_cars(w)})
        if st['t'] >= 10.0:
            finish()
    except Exception:
        R['events'].append(traceback.format_exc())
        finish()


handle[0] = unreal.register_slate_post_tick_callback(tick)
print('B1Y_CARS_ARMED - press Play')
