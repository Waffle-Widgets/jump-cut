"""Why does the player levitate at the start of the opening cinematic? Measure it, don't guess.

Run this FIRST (it waits for the PIE world), then start Play:
    py <repo>/tools/b1y_float.py
It waits up to 30 s for a game world, calls JumpCutStartPlay the moment it appears (that is what
begins the cinematic), then samples the player every 0.05 s for 6 s:

  actor_z  the capsule centre
  bottom   capsule bottom
  gap      capsule bottom above the floor under it (trace ignores characters). >1 cm = the CAPSULE floats.
  root     bone 0 above the mesh component's own origin. The Meshy REFERENCE POSE puts it at pelvis
           height (~90 cm), so a big root with a grounded capsule = the MESH floats, not the pawn.
  low      lowest bone above the capsule bottom
  mode     movement mode. NONE = DisableMovement ran (PlayerRefreshMoveLock does this whenever
           InputLocked is true) and gravity is off, so nothing can settle him.
  mont/abp what is actually animating him

Writes Saved/jcpy/b1y_float.json and prints a table. Reads only - sets nothing, saves nothing.
"""
import unreal, os, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
DUR = 6.0
STEP = 0.05
WAIT = 30.0

R = {'rows': [], 'events': [], 'done': False, 'start': None}
st = {'t': -1.0, 'next': 0.0, 'waited': 0.0, 'started': False}
handle = [None]


def ev(s):
    R['events'].append('%.2f %s' % (st['t'], s))
    print('   ' + str(s))


def game():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def allof(w, p):
    return list(unreal.GameplayStatics.get_all_actors_of_class(w, unreal.load_object(None, p)))


def sample(w, a, d):
    mesh = a.mesh
    loc = a.get_actor_location()
    hh = a.capsule_component.get_scaled_capsule_half_height()
    bottom = loc.z - hh
    lo, hi = 1e9, -1e9
    for i in range(mesh.get_num_bones()):
        z = mesh.get_socket_location(mesh.get_bone_name(i)).z
        lo, hi = min(lo, z), max(hi, z)
    root = mesh.get_socket_location(mesh.get_bone_name(0)).z - mesh.get_world_location().z
    hit = unreal.SystemLibrary.line_trace_single(
        w, unreal.Vector(loc.x, loc.y, bottom + 5.0), unreal.Vector(loc.x, loc.y, bottom - 3000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [a], unreal.DrawDebugTrace.NONE, True)
    fz = None
    if hit is not None:
        hd = hit.to_dict()
        if hd.get('blocking_hit'):
            fz = hd['location'].z
    m = a.get_current_montage()
    ai = mesh.get_anim_instance()

    def gp(o, n, dv=None):
        try:
            return o.get_editor_property(n)
        except Exception:
            return dv
    return {'t': round(st['t'], 2),
            'actor_z': round(loc.z, 1), 'bottom': round(bottom, 1),
            'floor': None if fz is None else round(fz, 1),
            'gap': None if fz is None else round(bottom - fz, 1),
            'root': round(root, 1), 'low': round(lo - bottom, 1),
            'mesh_z': round(mesh.get_world_location().z, 1),
            'vz': round(a.get_velocity().z, 1),
            'mode': str(a.character_movement.movement_mode).split('.')[-1].split(':')[0],
            'mont': m.get_name() if m else '',
            'abp': ai.get_class().get_name() if ai else '',
            'inlock': gp(a, 'InputLocked'), 'movelock': gp(a, 'MoveLocked'),
            'cine_run': gp(d, 'CineRunning'), 'cine_t': round(gp(d, 'CineTime', 0.0) or 0.0, 2),
            'cine_done': gp(d, 'CineDone')}


def finish():
    R['done'] = True
    with open(os.path.join(OUT, 'b1y_float.json'), 'w') as f:
        json.dump(R, f, indent=1)
    if handle[0] is not None:
        unreal.unregister_slate_post_tick_callback(handle[0])
        handle[0] = None
    print('B1Y_FLOAT_DONE rows=%d -> %s' % (len(R['rows']), os.path.join(OUT, 'b1y_float.json')))


def tick(dt):
    try:
        w = game()
        if w is None:
            st['waited'] += dt
            if st['waited'] > WAIT:
                ev('no PIE world after %.0f s - giving up' % WAIT)
                finish()
            return
        B = '/Game/Game/Blueprints/'
        pls = allof(w, B + 'BP_Player.BP_Player_C')
        dirs = allof(w, B + 'BP_OpeningDirector.BP_OpeningDirector_C')
        if not pls or not dirs:
            st['waited'] += dt
            if st['waited'] > WAIT:
                ev('player=%d director=%d after %.0f s' % (len(pls), len(dirs), WAIT))
                finish()
            return
        p, d = pls[0], dirs[0]
        if not st['started']:
            st['started'] = True
            st['t'] = 0.0
            gm = unreal.GameplayStatics.get_game_mode(w)
            R['start'] = {'gm': gm.get_class().get_name() if gm else None,
                          'player': p.get_name(), 'director': d.get_actor_label()}
            try:
                gm.call_method('JumpCutStartPlay')
                ev('JumpCutStartPlay called')
            except Exception as e:
                ev('JumpCutStartPlay failed: %s' % e)
        else:
            st['t'] += dt
        if st['t'] >= st['next']:
            st['next'] += STEP
            R['rows'].append(sample(w, p, d))
        if st['t'] >= DUR:
            finish()
    except Exception:
        R['events'].append(traceback.format_exc())
        finish()


handle[0] = unreal.register_slate_post_tick_callback(tick)
print('B1Y_FLOAT_ARMED - now press Play (waiting up to %.0f s)' % WAIT)
