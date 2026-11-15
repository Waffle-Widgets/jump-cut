"""Drive and measure the beat-1 explosion cinematic in PIE, without a keyboard.

    py <repo>/tools/b1x_pie.py setup     put the player by the coworker, power granted, fire lit
    py <repo>/tools/b1x_pie.py rescue    call CineRescueBegin - the beat runs itself from here
    py <repo>/tools/b1x_pie.py state     one timestamped sample of everything that matters
    py <repo>/tools/b1x_pie.py street    teleport the player out past ObjStreetDoneX
    py <repo>/tools/b1x_pie.py killgoons destroy every goon on the beat-2 stretch
Appends to Saved/jcpy/b1x_pie.txt so a run of calls reads as one timeline.
"""
import unreal, os, sys, time, json

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
MODE = sys.argv[1] if len(sys.argv) > 1 else 'state'
L = []
def say(s): L.append(str(s)); print(str(s))

def allof(w, p):
    return list(unreal.GameplayStatics.get_all_actors_of_class(w, unreal.load_object(None, p)))

def v(x):
    return '(%.1f, %.1f, %.1f)' % (x.x, x.y, x.z)

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    w = ues.get_game_world()
    if w is None:
        say('NO PIE WORLD'); raise SystemExit
    B = '/Game/Game/Blueprints/'
    dirs = allof(w, B + 'BP_OpeningDirector.BP_OpeningDirector_C')
    pls = allof(w, B + 'BP_Player.BP_Player_C')
    cws = allof(w, B + 'BP_Coworker.BP_Coworker_C')
    drs = allof(w, B + 'BP_CrashDriver.BP_CrashDriver_C')
    if not (dirs and pls):
        say('director=%d player=%d - not ready' % (len(dirs), len(pls))); raise SystemExit
    d, p = dirs[0], pls[0]
    cw = cws[0] if cws else None
    dr = drs[0] if drs else None
    say('\n===== %s  @ %s =====' % (MODE, time.strftime('%H:%M:%S.')[:-1] + ('%03d' % (time.time() % 1 * 1000))))

    def tryit(label, fn):
        # several of these are not instance-editable (HasFreezeFrame is a class default), so each
        # is attempted on its own and the failure is reported rather than killing the run
        try:
            fn(); say('   ok   %s' % label)
        except Exception as ex:
            say('   SKIP %s  (%s)' % (label, str(ex)[:90]))

    if MODE == 'setup':
        tryit('grant freeze frame', lambda: p.call_method('PlayerGrantFreezeFrame', ()))
        if dr is not None:
            tryit('driver touched', lambda: dr.set_editor_property('DriverTouched', True))
        tryit('CineRunning=False', lambda: d.set_editor_property('CineRunning', False))
        tryit('CineDone=True', lambda: d.set_editor_property('CineDone', True))
        tryit('ObjectiveState=2', lambda: d.set_editor_property('ObjectiveState', 2))
        if cw is not None:
            tryit('RescueStarted=True', lambda: cw.set_editor_property('RescueStarted', True))
            tryit('CoworkerLightFire', lambda: cw.call_method('CoworkerLightFire', ()))
        tgt = cw.get_actor_location() + unreal.Vector(180.0, 60.0, 0.0)
        tgt.z = p.get_actor_location().z
        p.set_actor_location(tgt, False, False)
        say('player -> %s   fire lit=%s  fuse=%.2f' % (
            v(p.get_actor_location()), cw.get_editor_property('FireLit'),
            cw.get_editor_property('FuseLeft')))
        raise SystemExit

    if MODE == 'rescue':
        d.call_method('CineRescueBegin', ())
        say('CineRescueBegin called; RescueCine=%s RescueT=%.2f' % (
            d.get_editor_property('RescueCine'), d.get_editor_property('RescueT')))
        raise SystemExit

    if MODE == 'card':
        # Hold the fireball card open on one frame of the sheet and look straight at it, so the
        # 6x6 flipbook maths can be judged by eye instead of by the parameter read-back.
        import math
        frame = float(sys.argv[2]) if len(sys.argv) > 2 else 8.0
        card = d.get_editor_property('ExplCard')
        card.set_actor_hidden_in_game(False)
        card.set_actor_scale3d(unreal.Vector(9.0, 9.0, 9.0))
        c = card.get_component_by_class(unreal.StaticMeshComponent)
        c.set_scalar_parameter_value_on_materials('Frame', frame)
        spot = unreal.Vector(120.0, 330.0, 150.0)
        cl = card.get_actor_location()
        dv = cl - spot
        yaw = math.degrees(math.atan2(dv.y, dv.x))
        pitch = math.degrees(math.atan2(dv.z, math.hypot(dv.x, dv.y)))
        card.set_actor_rotation(unreal.Rotator(0.0, pitch + 90.0, yaw), False)
        p.set_actor_location(spot, False, False)
        pc = unreal.GameplayStatics.get_player_controller(w, 0)
        pc.set_control_rotation(unreal.Rotator(0.0, pitch, yaw))
        say('card frame=%.0f shown at %s, camera at %s (pitch %.1f yaw %.1f)'
            % (frame, v(cl), v(spot), pitch, yaw))
        raise SystemExit

    if MODE == 'look':
        # EditorActorSubsystem cannot spawn into the PIE world, so a SceneCapture2D is not an
        # option here: point the real player camera instead and use CaptureEditorImage.
        import math
        tgt = unreal.Vector(-520.0, 0.0, 60.0)
        if len(sys.argv) > 2:
            tgt = unreal.Vector(float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]))
        spot = unreal.Vector(120.0, 330.0, 94.2)
        if len(sys.argv) > 7:
            spot = unreal.Vector(float(sys.argv[5]), float(sys.argv[6]), float(sys.argv[7]))
        p.set_actor_location(spot, False, False)
        dv = tgt - spot
        yaw = math.degrees(math.atan2(dv.y, dv.x))
        pitch = math.degrees(math.atan2(dv.z + 60.0, math.hypot(dv.x, dv.y)))
        pc = unreal.GameplayStatics.get_player_controller(w, 0)
        pc.set_control_rotation(unreal.Rotator(0.0, pitch, yaw))
        say('player -> %s looking at %s  (pitch %.1f yaw %.1f)' % (v(spot), v(tgt), pitch, yaw))
        raise SystemExit

    if MODE == 'obj':
        d.set_editor_property('ObjectiveState', int(sys.argv[2]))
        say('ObjectiveState -> %d' % d.get_editor_property('ObjectiveState'))
        raise SystemExit

    if MODE == 'street':
        loc = p.get_actor_location()
        x = float(sys.argv[2]) if len(sys.argv) > 2 else 1400.0
        p.set_actor_location(unreal.Vector(x, 0.0, loc.z), False, False)
        say('player -> %s  (ObjStreetDoneX=%.0f ObjBossDoneX=%.0f)' % (
            v(p.get_actor_location()), d.get_editor_property('ObjStreetDoneX'),
            d.get_editor_property('ObjBossDoneX')))
        raise SystemExit

    if MODE == 'killgoons':
        n = 0
        for g in allof(w, B + 'BP_Goon.BP_Goon_C'):
            if g.get_actor_location().x < d.get_editor_property('GoonZoneMaxX'):
                g.destroy_actor(); n += 1
        say('destroyed %d goons inside the beat-2 zone' % n)
        raise SystemExit

    # ---------------------------------------------------------------- state
    say('directors in world: %d' % len(dirs))
    for i, dd in enumerate(dirs):
        say('  dir[%d] %s  ExplCine=%s ExplT=%.2f RescueCine=%s RescueT=%.2f obj=%d CineRunning=%s CineDone=%s'
            % (i, dd.get_name(), dd.get_editor_property('ExplCine'), dd.get_editor_property('ExplT'),
               dd.get_editor_property('RescueCine'), dd.get_editor_property('RescueT'),
               dd.get_editor_property('ObjectiveState'), dd.get_editor_property('CineRunning'),
               dd.get_editor_property('CineDone')))
    gc = d.get_editor_property('ExplCarGC')
    card = d.get_editor_property('ExplCard')
    cam = d.get_editor_property('ExplCam')
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    say('obj=%d  ExplCine=%s ExplT=%.2f ExplDone=%s ExplSaid=%s  RescueCine=%s RescueT=%.2f'
        % (d.get_editor_property('ObjectiveState'), d.get_editor_property('ExplCine'),
           d.get_editor_property('ExplT'), d.get_editor_property('ExplDone'),
           d.get_editor_property('ExplSaid'), d.get_editor_property('RescueCine'),
           d.get_editor_property('RescueT')))
    say('player %s  inputLocked=%s moveLocked=%s health=%.0f  freezeActive=%s'
        % (v(p.get_actor_location()), p.get_editor_property('InputLocked'),
           p.get_editor_property('MoveLocked'), p.get_editor_property('Health'),
           p.get_editor_property('FreezeFrameActive')))
    if cw is not None:
        say('coworker %s  blown=%s dead=%s fuse=%.2f fireLit=%s'
            % (v(cw.get_actor_location()), cw.get_editor_property('Blown'),
               cw.get_editor_property('CoworkerDead'), cw.get_editor_property('FuseLeft'),
               cw.get_editor_property('FireLit')))
    if gc is not None:
        o, e = gc.get_actor_bounds(False)
        say('wreckGC hidden=%s  bounds origin %s  extent %s' % (
            gc.get_editor_property('hidden'), v(o), v(e)))
    if card is not None:
        s = card.get_actor_scale3d()
        say('card hidden=%s scale %.2f  loc %s  rot %s' % (
            card.get_editor_property('hidden'), s.x, v(card.get_actor_location()),
            card.get_actor_rotation()))
    if cam is not None:
        say('explcam %s  %s' % (v(cam.get_actor_location()), cam.get_actor_rotation()))
    if pc is not None:
        vt = pc.get_view_target()
        say('viewTarget = %s' % (vt.get_name() if vt else 'None'))
    goons = [g for g in allof(w, B + 'BP_Goon.BP_Goon_C')]
    near = [g for g in goons if g.get_actor_location().x < d.get_editor_property('GoonZoneMaxX')]
    say('goons total=%d  inside beat-2 zone=%d  GoonsSeen=%s GoonsLeftNow=%d'
        % (len(goons), len(near), d.get_editor_property('GoonsSeen'),
           d.get_editor_property('GoonsLeftNow')))
    bk = d.get_editor_property('ObjectiveBeacon')
    if bk is not None:
        say('beacon hidden=%s at %s' % (bk.get_editor_property('hidden'), v(bk.get_actor_location())))
except SystemExit:
    pass
except Exception as e:
    import traceback
    say('ERROR %r' % e); say(traceback.format_exc())
with open(os.path.join(OUT, 'b1x_pie.txt'), 'a') as fh:
    fh.write('\n'.join(L) + '\n')
