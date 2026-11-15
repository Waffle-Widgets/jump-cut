"""Beat 1 round 6: measure where the PLAYER'S OWN camera actually sits at the hand-off, so the
cinematic's last cut can end on exactly that pose instead of snapping to it.

    py <repo>/tools/b1v_cam.py prep       editor: ShowTitleOnStart off, CinePlayOpening off
    py <repo>/tools/b1v_cam.py set        PIE: point the controller at CineEndYaw
    py <repo>/tools/b1v_cam.py read       PIE: read the real camera pose (run AFTER a few ticks)
    py <repo>/tools/b1v_cam.py restore    editor: put ShowTitleOnStart / CinePlayOpening back

The pose is NOT computed from the spring arm's numbers: the arm does a collision probe and can
shorten itself, and the pawn's resting z is not floor + half-height. Measure it.

Appends to Saved/jcpy/b1v_cam.txt and rewrites b1v_cam.json.
"""
import unreal, os, sys, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
MODE = sys.argv[1] if len(sys.argv) > 1 else 'read'
L = []
def say(s):
    L.append(str(s)); print(str(s))
def v3(x):
    if isinstance(x, unreal.Rotator):
        return [round(x.roll, 3), round(x.pitch, 3), round(x.yaw, 3)]
    return [round(x.x, 3), round(x.y, 3), round(x.z, 3)]

GM = '/Game/Game/Blueprints/BP_JumpCutGameMode.BP_JumpCutGameMode_C'
DIR = '/Game/Game/Blueprints/BP_OpeningDirector.BP_OpeningDirector_C'
PLY = '/Game/Game/Blueprints/BP_Player.BP_Player_C'
res = {}

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    gw = ues.get_game_world()
    ew = ues.get_editor_world()

    if MODE in ('prep', 'restore'):
        on = (MODE == 'restore')
        gmc = unreal.load_class(None, GM)
        unreal.get_default_object(gmc).set_editor_property('ShowTitleOnStart', on)
        say('%s: ShowTitleOnStart -> %s' % (MODE, unreal.get_default_object(gmc).get_editor_property('ShowTitleOnStart')))
        dc = unreal.load_class(None, DIR)
        unreal.get_default_object(dc).set_editor_property('CinePlayOpening', on)
        say('%s: CinePlayOpening (CDO) -> %s' % (MODE, unreal.get_default_object(dc).get_editor_property('CinePlayOpening')))
        eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        for a in eas.get_all_level_actors():
            if a.get_actor_label() == 'B1_Cine_Director':
                a.set_editor_property('CinePlayOpening', on)
                say('%s: CinePlayOpening (placed) -> %s' % (MODE, a.get_editor_property('CinePlayOpening')))
                xf = a.get_actor_transform()
                a.set_actor_location_and_rotation(xf.translation, xf.rotation.rotator(), False, True)
        raise SystemExit

    if gw is None:
        raise RuntimeError('PIE is not running - StartPIE first')

    pc = unreal.GameplayStatics.get_player_controller(gw, 0)
    pawn = pc.get_controlled_pawn() if hasattr(pc, 'get_controlled_pawn') else None
    if pawn is None:
        pawns = unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.load_object(None, PLY))
        pawn = pawns[0] if pawns else None
    dirs = unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.load_object(None, DIR))
    d = dirs[0] if dirs else None
    end_yaw = d.get_editor_property('CineEndYaw') if d is not None else 172.0

    if MODE == 'set':
        pc.set_control_rotation(unreal.Rotator(0.0, 0.0, end_yaw))
        pawn.set_actor_rotation(unreal.Rotator(0.0, 0.0, end_yaw), False)
        say('set control rotation + pawn yaw -> %.2f  (pawn at %s)' % (end_yaw, v3(pawn.get_actor_location())))
        raise SystemExit

    # ---- read
    cam = None
    for c in pawn.get_components_by_class(unreal.CameraComponent):
        cam = c; break
    arm = None
    for c in pawn.get_components_by_class(unreal.SpringArmComponent):
        arm = c; break
    pcm = pc.player_camera_manager
    pov_loc = pcm.get_camera_location()
    pov_rot = pcm.get_camera_rotation()
    res = {
        'end_yaw': end_yaw,
        'pawn_loc': v3(pawn.get_actor_location()),
        'pawn_rot': v3(pawn.get_actor_rotation()),
        'control_rot': v3(pc.get_control_rotation()),
        'cam_world_loc': v3(cam.get_world_location()),
        'cam_world_rot': v3(cam.get_world_rotation()),
        'cam_fov': cam.get_editor_property('field_of_view'),
        'arm_world_loc': v3(arm.get_world_location()),
        'arm_len': arm.get_editor_property('target_arm_length'),
        'arm_socket': v3(arm.get_socket_transform(unreal.Name('SpringEndpoint')).translation)
            if hasattr(arm, 'get_socket_transform') else None,
        'camera_manager_loc': v3(pov_loc),
        'camera_manager_rot': v3(pov_rot),
        'camera_manager_fov': pcm.get_fov_angle(),
    }
    for k in ('pawn_loc', 'cam_world_loc', 'cam_world_rot', 'camera_manager_loc',
              'camera_manager_rot', 'camera_manager_fov', 'cam_fov', 'control_rot', 'pawn_rot'):
        say('%-20s %s' % (k, res[k]))
    say('full: %s' % json.dumps(res))
except SystemExit:
    pass
except Exception as e:
    say('ERROR %r' % e); say(traceback.format_exc())

with open(os.path.join(OUT, 'b1v_cam.txt'), 'a') as fh:
    fh.write('\n--- %s ---\n' % MODE)
    fh.write('\n'.join(L))
if res:
    with open(os.path.join(OUT, 'b1v_cam.json'), 'w') as fh:
        json.dump(res, fh, indent=1, default=str)
print('b1v_cam %s done' % MODE)
