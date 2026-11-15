"""Beat 1 round 6 in PIE, IN REAL TIME. Changes no assets.

    py <repo>/tools/b1v_pie.py flags on|off   ShowTitleOnStart off + CinePlayOpening on (or back)
    py <repo>/tools/b1v_pie.py sample         one sample of everything this round changed

WHY NOT STEP THE CLOCK. tools/b1z_pie.py drives CineDirectorStep by hand, which is the only way
to measure an 11 s cinematic across 5-8 s MCP round trips - but it works precisely BECAUSE no
ticks happen, and the player's turn is driven through AddMovementInput, which needs the character
movement component to tick to move or rotate at all. So this one lets the opening run in real
time (StartPIE's warmupSeconds does the waiting) and samples the end state.

Appends to Saved/jcpy/b1v_pie.txt, rewrites b1v_pie.json.
"""
import unreal, os, sys, json, math, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
MODE = sys.argv[1] if len(sys.argv) > 1 else 'sample'
ARG = sys.argv[2] if len(sys.argv) > 2 else 'on'
L = []; res = {}
def say(s):
    L.append(str(s)); print(str(s))
def v3(x):
    if isinstance(x, unreal.Rotator):
        return [round(x.roll, 2), round(x.pitch, 2), round(x.yaw, 2)]
    return [round(x.x, 2), round(x.y, 2), round(x.z, 2)]

GM = '/Game/Game/Blueprints/BP_JumpCutGameMode.BP_JumpCutGameMode_C'
DIR = '/Game/Game/Blueprints/BP_OpeningDirector.BP_OpeningDirector_C'
PLY = '/Game/Game/Blueprints/BP_Player.BP_Player_C'
DRV = '/Game/Game/Blueprints/BP_CrashDriver.BP_CrashDriver_C'

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

    if MODE == 'flags':
        on = (ARG == 'on')
        unreal.get_default_object(unreal.load_class(None, GM)).set_editor_property(
            'ShowTitleOnStart', not on)
        dc = unreal.get_default_object(unreal.load_class(None, DIR))
        dc.set_editor_property('CinePlayOpening', True)
        eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        for a in eas.get_all_level_actors():
            if a.get_actor_label() == 'B1_Cine_Director':
                a.set_editor_property('CinePlayOpening', True)
                xf = a.get_actor_transform()
                a.set_actor_location_and_rotation(xf.translation, xf.rotation.rotator(), False, True)
        say('flags %s: ShowTitleOnStart=%s CinePlayOpening=%s' % (
            ARG,
            unreal.get_default_object(unreal.load_class(None, GM)).get_editor_property('ShowTitleOnStart'),
            dc.get_editor_property('CinePlayOpening')))
        raise SystemExit

    gw = ues.get_game_world()
    if gw is None:
        raise RuntimeError('PIE is not running')
    pc = unreal.GameplayStatics.get_player_controller(gw, 0)
    pawns = unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.load_object(None, PLY))
    pawn = pawns[0] if pawns else None
    dirs = unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.load_object(None, DIR))
    d = dirs[0] if dirs else None

    # ---- how many bodies, how many cars, in the RUNNING world
    bodies = []
    for a in unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.SkeletalMeshActor):
        sk = a.get_component_by_class(unreal.SkeletalMeshComponent)
        m = sk.get_skeletal_mesh_asset() if sk else None
        bodies.append({'label': a.get_actor_label(), 'cls': 'SkeletalMeshActor',
                       'mesh': (m.get_name() if m else None), 'loc': v3(a.get_actor_location()),
                       'hidden': a.get_editor_property('hidden')})
    for a in unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.load_object(None, DRV)):
        bodies.append({'label': a.get_actor_label(), 'cls': 'BP_CrashDriver',
                       'loc': v3(a.get_actor_location()), 'hidden': a.get_editor_property('hidden')})
    res['bodies'] = bodies
    say('bodies drawn (not hidden): %s' % json.dumps([b for b in bodies if not b['hidden']]))
    say('bodies hidden            : %s' % json.dumps([b['label'] for b in bodies if b['hidden']]))

    cars = []
    for a in unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.StaticMeshActor):
        smc = a.get_component_by_class(unreal.StaticMeshComponent)
        m = smc.static_mesh if smc else None
        if m is None or 'CrashCar' not in m.get_name():
            continue
        cars.append({'label': a.get_actor_label(), 'mesh': m.get_name(),
                     'loc': v3(a.get_actor_location()), 'hidden': a.get_editor_property('hidden')})
    for a in unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.GeometryCollectionActor):
        if 'CrashCar' not in a.get_actor_label():
            continue
        cars.append({'label': a.get_actor_label(), 'mesh': 'GC',
                     'loc': v3(a.get_actor_location()), 'hidden': a.get_editor_property('hidden')})
    res['cars'] = cars
    say('cars: %s' % json.dumps(cars))

    # ---- the hand-off
    cam = None
    for c in (pawn.get_components_by_class(unreal.CameraComponent) if pawn else []):
        cam = c; break
    pcm = pc.player_camera_manager
    res['handoff'] = {
        'pawn_loc': v3(pawn.get_actor_location()),
        'pawn_yaw': round(pawn.get_actor_rotation().yaw, 2),
        'control_yaw': round(pc.get_control_rotation().yaw, 2),
        'view_target': pc.get_view_target().get_actor_label() if pc.get_view_target() else None,
        'camera_loc': v3(pcm.get_camera_location()),
        'camera_rot': v3(pcm.get_camera_rotation()),
        'camera_fov': round(pcm.get_fov_angle(), 2),
        'player_cam_loc': v3(cam.get_world_location()) if cam else None,
        'speed': round(pawn.get_velocity().length(), 2),
    }
    say('hand-off: %s' % json.dumps(res['handoff']))
    say('  drift from the origin: %.1f cm' % math.hypot(
        pawn.get_actor_location().x, pawn.get_actor_location().y))

    # ---- the director's own state
    dd = {}
    for k in ('CineRunning', 'CineDone', 'CineTime', 'CineTurnOn', 'CineTurnDone',
              'CineTurnFromYaw', 'ObjectiveState', 'CineFireLit', 'RagdollOn', 'RagdollDone'):
        try:
            dd[k] = d.get_editor_property(k)
        except Exception as e:
            dd[k] = '<%s>' % type(e).__name__
    res['director'] = dd
    say('director: %s' % json.dumps(dd, default=str))

    # ---- is the sequence stopped?
    sas = unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.LevelSequenceActor)
    sq = []
    for a in sas:
        # UE 5.8: ALevelSequenceActor has no get_sequence_player() in Python - the obvious name
        # raises AttributeError. It is the 'sequence_player' editor property.
        try:
            p = a.get_editor_property('sequence_player')
        except Exception:
            p = None
        sq.append({'label': a.get_actor_label(),
                   'playing': (p.is_playing() if p else None),
                   'time': (str(p.get_current_time().time) if p else None),
                   'cuts_disabled': (p.get_disable_camera_cuts() if p else None)})
    res['sequences'] = sq
    say('sequences: %s' % json.dumps(sq, default=str))

    # ---- the beacon: is it over her?
    bc = None
    for a in unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.StaticMeshActor):
        if a.get_actor_label().startswith('B1_Objective_Beacon'):
            bc = a; break
    if bc is not None:
        res['beacon'] = {'loc': v3(bc.get_actor_location()),
                         'hidden': bc.get_editor_property('hidden')}
        say('beacon: %s' % json.dumps(res['beacon']))
except SystemExit:
    pass
except Exception as e:
    say('ERROR %r' % e); say(traceback.format_exc()); res['error'] = repr(e)

with open(os.path.join(OUT, 'b1v_pie.txt'), 'a') as fh:
    fh.write('\n--- %s %s ---\n' % (MODE, ARG))
    fh.write('\n'.join(L))
if res:
    with open(os.path.join(OUT, 'b1v_pie.json'), 'w') as fh:
        json.dump(res, fh, indent=1, default=str)
print('b1v_pie %s done' % MODE)
