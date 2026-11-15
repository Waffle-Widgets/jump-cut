"""Beat 1, title to the street, played by a script IN REAL TIME and sampled EVERY FRAME.
Changes no assets.

    py <repo>/tools/b1u_pie.py flags on|off   editor: ShowTitleOnStart off (on) / back (off)
    py <repo>/tools/b1u_pie.py rec            PIE: play the beat and record it

WHY A TICK CALLBACK. An MCP round trip to this editor is 5-8 s; the power pickup is 2.2 s and the
hand-off after the explosion is one frame. `rec` registers a Slate post-tick callback, so the
sampling and the driving both happen inside the editor, once per frame, with the game ticking
normally in between. It walks the player through the beat with PlayerDebugTeleport (a script
cannot hold a movement key), which is the ONLY thing it fakes: every trigger after that is the
director's own range test.

It deliberately teleports the player to the coworker FACING WEST with the camera facing west too,
because that is the case the 2026-11-15 note describes: "the camera snaps to a position pointing
the other way".

Writes Saved/jcpy/b1u_pie.json (every frame) and takes `Screenshot showui` at named moments;
the json lists which shot was asked for when, in order, so the files can be matched up.
"""
import unreal, os, sys, json, math, time, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
MODE = sys.argv[1] if len(sys.argv) > 1 else 'rec'
ARG = sys.argv[2] if len(sys.argv) > 2 else 'on'

GM = '/Game/Game/Blueprints/BP_JumpCutGameMode.BP_JumpCutGameMode_C'
DIR = '/Game/Game/Blueprints/BP_OpeningDirector.BP_OpeningDirector_C'
PLY = '/Game/Game/Blueprints/BP_Player.BP_Player_C'

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)


def v3(x):
    if isinstance(x, unreal.Rotator):
        return [round(x.roll, 2), round(x.pitch, 2), round(x.yaw, 2)]
    return [round(x.x, 2), round(x.y, 2), round(x.z, 2)]


def gp(o, name, default=None):
    try:
        return o.get_editor_property(name)
    except Exception:
        return default


if MODE == 'flags':
    on = (ARG == 'on')
    cdo = unreal.get_default_object(unreal.load_class(None, GM))
    cdo.set_editor_property('ShowTitleOnStart', not on)
    msg = 'flags %s: ShowTitleOnStart=%s' % (ARG, cdo.get_editor_property('ShowTitleOnStart'))
    print(msg)
    with open(os.path.join(OUT, 'b1u_flags.txt'), 'w') as fh:
        fh.write(msg + '\n')

else:
    S = {'phase': 0, 't0': time.time(), 'mark': None, 'frames': [], 'events': [], 'shots': [],
         'handle': None, 'done': False, 'shot_done': set()}

    def ev(s):
        S['events'].append([round(time.time() - S['t0'], 3), s])

    def shot(gw, tag):
        if tag in S['shot_done']:
            return
        S['shot_done'].add(tag)
        unreal.SystemLibrary.execute_console_command(gw, 'Screenshot showui')
        S['shots'].append([round(time.time() - S['t0'], 3), tag])

    def finish(why):
        if S['done']:
            return
        S['done'] = True
        ev('finish: ' + why)
        try:
            unreal.unregister_slate_post_tick_callback(S['handle'])
        except Exception:
            pass
        with open(os.path.join(OUT, 'b1u_pie.json'), 'w') as fh:
            json.dump({'events': S['events'], 'shots': S['shots'], 'frames': S['frames']}, fh)
        print('b1u_pie: wrote %d frames, %s' % (len(S['frames']), why))

    def tick(dt):
        try:
            now = time.time() - S['t0']
            gw = ues.get_game_world()
            if gw is None:
                if now > 5.0:
                    finish('PIE not running')
                return
            pc = unreal.GameplayStatics.get_player_controller(gw, 0)
            pawns = unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.load_object(None, PLY))
            dirs = unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.load_object(None, DIR))
            if not pawns or not dirs or pc is None:
                return
            pawn, d = pawns[0], dirs[0]
            cm = pc.player_camera_manager
            ov = gp(d, 'OverlayRef')
            bk = gp(d, 'ObjectiveBeacon')
            xc = gp(d, 'ExplCam')
            obj = gp(d, 'ObjectiveState', -1)
            f = {'t': round(now, 3), 'obj': obj,
                 'dil': round(unreal.GameplayStatics.get_global_time_dilation(gw), 3),
                 'power': bool(gp(d, 'PowerCine', False)), 'powerT': round(gp(d, 'PowerT', 0.0), 3),
                 'flash': round(gp(d, 'FlashAlpha', 0.0), 3),
                 'resc': bool(gp(d, 'RescueCine', False)),
                 'expl': bool(gp(d, 'ExplCine', False)), 'explT': round(gp(d, 'ExplT', 0.0), 3),
                 'explDone': bool(gp(d, 'ExplDone', False)),
                 'bars': round(gp(d, 'BarAlpha', 0.0), 3),
                 'ploc': v3(pawn.get_actor_location()), 'pyaw': round(pawn.get_actor_rotation().yaw, 2),
                 'cyaw': round(pc.get_control_rotation().yaw, 2),
                 'cam': v3(cm.get_camera_location()), 'camrot': v3(cm.get_camera_rotation()),
                 'fov': round(cm.get_fov_angle(), 2),
                 'vt': pc.get_view_target().get_name()[:24],
                 'locked': bool(gp(pawn, 'InputLocked', False)),
                 'hp': round(gp(pawn, 'Health', -1.0), 1)}
            if xc is not None:
                f['xcam'] = v3(xc.get_actor_location())
                f['xrot'] = v3(xc.get_actor_rotation())
            if bk is not None:
                f['bk'] = v3(bk.get_actor_location())
                f['bks'] = v3(bk.get_actor_scale3d())
                f['bkh'] = bool(gp(bk, 'hidden', False))
                if 'bkmat' not in S:
                    try:
                        smc = bk.get_component_by_class(unreal.StaticMeshComponent)
                        S['bkmat'] = smc.get_material(0).get_name()
                    except Exception as e:
                        S['bkmat'] = 'ERR %s' % e
                f['bkmat'] = S['bkmat']
            if ov is not None:
                try:
                    cb = ov.get_editor_property('CapBox')
                    f['capvis'] = str(cb.get_visibility()).split('.')[-1][:18]
                    f['capscale'] = round(cb.get_editor_property('render_transform').scale.x, 4)
                    f['cap'] = str(ov.get_editor_property('CapText').get_text())[:60]
                    f['flashw'] = round(ov.get_editor_property('FlashBox').get_render_opacity(), 3)
                except Exception as e:
                    f['overr'] = str(e)[:80]
            S['frames'].append(f)

            ph = S['phase']
            if ph == 0 and obj == 1:
                S['phase'] = 1; S['mark'] = now; ev('opening over, objective 1')
            elif ph == 1:
                if now - S['mark'] > 1.0:
                    shot(gw, 'obj1_marker')
                if now - S['mark'] > 1.6:
                    pawn.call_method('PlayerDebugTeleport', (unreal.Vector(-215.0, -40.0, 94.15), 190.0))
                    pc.set_control_rotation(unreal.Rotator(roll=0.0, pitch=-12.0, yaw=190.0))
                    S['phase'] = 2; ev('teleported to the driver')
            elif ph == 2:
                if f['power']:
                    if f['powerT'] > 0.10: shot(gw, 'power_flash')
                    if f['powerT'] > 1.20: shot(gw, 'power_hold')
                elif obj == 2:
                    S['phase'] = 3; S['mark'] = now; ev('power moment over, objective 2')
                    pc.set_control_rotation(unreal.Rotator(roll=0.0, pitch=-8.0, yaw=133.0))
            elif ph == 3:
                if now - S['mark'] > 0.7: shot(gw, 'after_power')
                if now - S['mark'] > 3.2: shot(gw, 'get_her_out')
                if now - S['mark'] > 3.8:
                    pawn.call_method('PlayerDebugTeleport', (unreal.Vector(-330.0, 60.0, 94.15), 128.0))
                    pc.set_control_rotation(unreal.Rotator(roll=0.0, pitch=-8.0, yaw=128.0))
                    S['phase'] = 4; ev('teleported to the coworker, facing WEST')
            elif ph == 4:
                if f['resc']:
                    shot(gw, 'rescue')
                if f['expl']:
                    S['phase'] = 5; ev('explosion cinematic began')
            elif ph == 5:
                if f['explT'] > 0.5: shot(gw, 'expl_a')
                if f['explT'] > 3.0: shot(gw, 'expl_pan')
                if f['explT'] > 4.9: shot(gw, 'expl_last')
                if f['explDone']:
                    S['phase'] = 6; S['mark'] = now; ev('explosion over, control handed back')
            elif ph == 6:
                if now - S['mark'] > 0.03: shot(gw, 'handoff_0')
                if now - S['mark'] > 0.6: shot(gw, 'handoff_1')
                if now - S['mark'] > 2.5:
                    finish('ran to the end')
            if now > 110.0:
                finish('timeout in phase %d' % S['phase'])
        except Exception:
            ev('EXC ' + traceback.format_exc()[-600:])
            finish('exception')

    S['handle'] = unreal.register_slate_post_tick_callback(tick)
    print('b1u_pie: recording')
