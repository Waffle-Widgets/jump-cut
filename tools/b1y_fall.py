"""Is the 90.6 cm levitation the FALLING state? Force it and watch, then jump and watch.

    py <repo>/tools/b1y_fall.py       (run first, then press Play)
Timeline: t=0 JumpCutStartPlay, t=2.0 force MOVE_Falling by hand, t=4.0 call Jump.
If root goes to ~90 in either, the jump/fall state is what lifts him and the start-of-game
levitation is the same defect as #69/#71. Writes Saved/jcpy/b1y_fall.json. Sets nothing persistent.
"""
import unreal, os, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
R = {'rows': [], 'events': [], 'done': False}
st = {'t': -1.0, 'next': 0.0, 'waited': 0.0, 'started': False, 'fell': False, 'jumped': False}
handle = [None]


def ev(s):
    R['events'].append('%.2f %s' % (st['t'], s)); print('   ' + str(s))


def allof(w, p):
    return list(unreal.GameplayStatics.get_all_actors_of_class(w, unreal.load_object(None, p)))


def sample(a):
    mesh = a.mesh
    loc = a.get_actor_location()
    hh = a.capsule_component.get_scaled_capsule_half_height()
    bottom = loc.z - hh
    lo, hi = 1e9, -1e9
    for i in range(mesh.get_num_bones()):
        z = mesh.get_socket_location(mesh.get_bone_name(i)).z
        lo, hi = min(lo, z), max(hi, z)
    root = mesh.get_socket_location(mesh.get_bone_name(0)).z - mesh.get_world_location().z
    m = a.get_current_montage()
    return {'t': round(st['t'], 2), 'actor_z': round(loc.z, 1), 'root': round(root, 1),
            'low': round(lo - bottom, 1), 'spread': round(hi - lo, 1),
            'vz': round(a.get_velocity().z, 1),
            'mode': str(a.character_movement.movement_mode).split('.')[-1].split(':')[0],
            'mont': m.get_name() if m else ''}


def finish():
    R['done'] = True
    with open(os.path.join(OUT, 'b1y_fall.json'), 'w') as f:
        json.dump(R, f, indent=1)
    if handle[0] is not None:
        unreal.unregister_slate_post_tick_callback(handle[0]); handle[0] = None
    print('B1Y_FALL_DONE rows=%d' % len(R['rows']))


def tick(dt):
    try:
        w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if w is None:
            st['waited'] += dt
            if st['waited'] > 30.0:
                ev('no PIE'); finish()
            return
        pls = allof(w, '/Game/Game/Blueprints/BP_Player.BP_Player_C')
        if not pls:
            st['waited'] += dt
            if st['waited'] > 30.0:
                ev('no player'); finish()
            return
        p = pls[0]
        if not st['started']:
            st['started'] = True; st['t'] = 0.0
            gm = unreal.GameplayStatics.get_game_mode(w)
            try:
                gm.call_method('JumpCutStartPlay'); ev('JumpCutStartPlay')
            except Exception as e:
                ev('start failed %s' % e)
        else:
            st['t'] += dt
        if st['t'] >= 2.0 and not st['fell']:
            st['fell'] = True
            try:
                p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FALLING, 0)
                ev('forced MOVE_Falling')
            except Exception as e:
                ev('force failed %s' % e)
        if st['t'] >= 4.0 and not st['jumped']:
            st['jumped'] = True
            try:
                p.jump(); ev('jump() called')
            except Exception as e:
                ev('jump failed %s' % e)
        if st['t'] >= st['next']:
            st['next'] += 0.05
            R['rows'].append(sample(p))
        if st['t'] >= 7.0:
            finish()
    except Exception:
        R['events'].append(traceback.format_exc()); finish()


handle[0] = unreal.register_slate_post_tick_callback(tick)
print('B1Y_FALL_ARMED - press Play')
