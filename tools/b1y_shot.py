"""Set up a PIE frame worth photographing, then FREEZE it so an MCP capture (5-8 s later) still
shows the moment. Run it, wait, then call CaptureEditorImage.

    py <repo>/tools/b1y_shot.py fire     the car burning: skip the cinematic, light the fire,
                                         camera on the wreck. The fire is continuous, so no freeze.
    py <repo>/tools/b1y_shot.py pop      the power-up: walk-range touch on the driver, which runs
                                         the real DriverTryTouch and spawns NS_PowerPop. Freezes
                                         0.30 s later (global time dilation 0.0001) because the
                                         burst is over in 0.75 s - far less than one round trip.
    py <repo>/tools/b1y_shot.py unfreeze put time back to 1.0

Writes Saved/jcpy/b1y_shot.json with what it found: the fire component's live state, and whether a
NiagaraComponent carrying NS_PowerPop actually exists in the world after the touch.
"""
import unreal, os, sys, math, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
MODE = sys.argv[1] if len(sys.argv) > 1 else 'fire'
res = {'mode': MODE, 'events': []}
handle = [None]
st = {'t': 0.0, 'done': False}


def ev(s):
    res['events'].append(str(s))
    print('   ' + str(s))


def allof(w, p):
    return list(unreal.GameplayStatics.get_all_actors_of_class(w, unreal.load_object(None, p)))


def niagara_report(w):
    rows = []
    for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
        for c in a.get_components_by_class(unreal.NiagaraComponent):
            asset = c.get_editor_property('asset')
            rows.append({'actor': a.get_actor_label() or a.get_name(),
                         'comp': c.get_name(),
                         'asset': asset.get_name() if asset else None,
                         'visible': c.is_visible(),
                         'active': c.is_active(),
                         'actor_hidden': bool(a.get_editor_property('hidden')),
                         'world_z': round(c.get_world_location().z, 1)})
    return rows


def aim(w, p, target, spot):
    p.set_actor_location(spot, False, True)
    d = target - spot
    yaw = math.degrees(math.atan2(d.y, d.x))
    pitch = math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    pc.set_control_rotation(unreal.Rotator(0.0, pitch, yaw))
    p.set_actor_rotation(unreal.Rotator(0.0, 0.0, yaw), False)


def freeze(w):
    unreal.GameplayStatics.set_global_time_dilation(w, 0.0001)
    ev('frozen (time dilation 0.0001)')


try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    w = ues.get_game_world()
    assert w is not None, 'NO PIE WORLD - press Play first'
    B = '/Game/Game/Blueprints/'
    p = allof(w, B + 'BP_Player.BP_Player_C')[0]
    d = allof(w, B + 'BP_OpeningDirector.BP_OpeningDirector_C')[0]
    cws = allof(w, B + 'BP_Coworker.BP_Coworker_C')
    drs = allof(w, B + 'BP_CrashDriver.BP_CrashDriver_C')
    gm = unreal.GameplayStatics.get_game_mode(w)

    if MODE == 'unfreeze':
        unreal.GameplayStatics.set_global_time_dilation(w, 1.0)
        ev('time dilation 1.0')
        raise SystemExit

    def try_(label, fn):
        try:
            fn()
            ev('ok   ' + label)
        except Exception as e:
            ev('SKIP %s (%s)' % (label, str(e)[:90]))

    try_('JumpCutStartPlay', lambda: gm.call_method('JumpCutStartPlay'))
    # skip the 11 s opening - we are photographing what comes after it
    try_('CineRunning=False', lambda: d.set_editor_property('CineRunning', False))
    try_('CineDone=True', lambda: d.set_editor_property('CineDone', True))

    if MODE == 'fire':
        try_('ObjectiveState=2', lambda: d.set_editor_property('ObjectiveState', 2))
        try_('grant freeze frame', lambda: p.call_method('PlayerGrantFreezeFrame', ()))
        if drs:
            try_('DriverTouched=True', lambda: drs[0].set_editor_property('DriverTouched', True))
        if cws:
            try_('RescueStarted=True', lambda: cws[0].set_editor_property('RescueStarted', True))
            try_('CoworkerLightFire', lambda: cws[0].call_method('CoworkerLightFire', ()))
        spot = unreal.Vector(150.0, -60.0, 94.0)
        if len(sys.argv) > 4:
            spot = unreal.Vector(float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]))
        aim(w, p, unreal.Vector(-500.0, 0.0, 150.0), spot)
        pc = unreal.GameplayStatics.get_player_controller(w, 0)
        cam = pc.player_camera_manager
        res['camera'] = {'loc': [round(v, 1) for v in cam.get_camera_location().to_tuple()],
                         'rot': [round(v, 1) for v in cam.get_camera_rotation().to_tuple()],
                         'player': [round(v, 1) for v in p.get_actor_location().to_tuple()]}
        ev('camera on the wreck from %s' % res['camera'])
        # where IS everything, and is the fire even in front of the camera?
        rows = {}
        for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
            lab = a.get_actor_label()
            if lab in ('B1_Cafe_CrashCar_GC', 'B1_Cafe_Fire', 'City_CafeCrashCar',
                       'C1_Cafe_CrashDriver', 'Coworker_Cafe'):
                rows[lab] = {'loc': [round(v, 1) for v in a.get_actor_location().to_tuple()],
                             'hidden': bool(a.get_editor_property('hidden'))}
        res['landmarks'] = rows
        try:
            sp = pc.project_world_location_to_screen(unreal.Vector(-500.0, 0.0, 130.0), False)
            res['fire_on_screen'] = [round(sp.x, 1), round(sp.y, 1)] if sp else None
        except Exception as e:
            res['fire_on_screen'] = 'ERR ' + str(e)[:80]
        res['niagara'] = niagara_report(w)

    elif MODE == 'pop':
        try_('ObjectiveState=1', lambda: d.set_editor_property('ObjectiveState', 1))
        assert drs, 'no BP_CrashDriver in the world'
        dr = drs[0]
        dl = dr.get_actor_location()
        res['driver_loc'] = [round(v, 1) for v in dl.to_tuple()]
        # stand him in range and let the REAL gated function decide, exactly as walking there would
        p.set_actor_location(unreal.Vector(dl.x + 90.0, dl.y + 90.0, p.get_actor_location().z), False, True)
        res['before'] = niagara_report(w)
        try_('DriverTryTouch', lambda: dr.call_method('DriverTryTouch', ()))
        res['driver_touched'] = bool(dr.get_editor_property('DriverTouched'))
        aim(w, p, unreal.Vector(dl.x, dl.y, dl.z + 60.0), unreal.Vector(dl.x + 300.0, dl.y + 240.0, 150.0))
        ev('camera on the driver; freezing in 0.30 s')

        def tick(dt):
            st['t'] += dt
            if st['t'] >= 0.30 and not st['done']:
                st['done'] = True
                res['after'] = niagara_report(w)
                freeze(w)
                with open(os.path.join(OUT, 'b1y_shot.json'), 'w') as fh:
                    json.dump(res, fh, indent=1, default=str)
                if handle[0] is not None:
                    unreal.unregister_slate_post_tick_callback(handle[0])
                    handle[0] = None
                print('B1Y_SHOT_POP_FROZEN')
        handle[0] = unreal.register_slate_post_tick_callback(tick)
except SystemExit:
    pass
except Exception:
    res['error'] = traceback.format_exc()

if MODE != 'pop' or 'error' in res:
    with open(os.path.join(OUT, 'b1y_shot.json'), 'w') as f:
        json.dump(res, f, indent=1, default=str)
print('B1Y_SHOT_%s err=%s' % (MODE.upper(), 'error' in res))
