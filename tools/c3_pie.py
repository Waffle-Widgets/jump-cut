"""Sun Nov 15, 2 PM: the boss intro's camera hand-off, played IN REAL TIME and sampled every frame.
Changes no assets.

    py <repo>/tools/c3_pie.py boss     PIE running: put the player in the plaza facing NORTH, start the
                                       boss intro through the director's own CineBossBegin, and push
                                       the look input DOWN and sideways every frame of the speech, the
                                       way a player's mouse does (BP_Player's InputLocked does not
                                       stop the template's look input). Records the hand-off.
    py <repo>/tools/c3_pie.py music    PIE running from the TITLE: which music track is playing, and
                                       how loud, at the title, in the latte shift, at the wall break,
                                       after the opening, and after a whole-level restart.

Writes Saved/jcpy/c3_<mode>.json with every frame and a summary.
"""
import unreal, os, sys, json, math, time, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
MODE = sys.argv[1] if len(sys.argv) > 1 else 'boss'
P = '/Game/Game/Blueprints/'
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
GS = unreal.GameplayStatics


def cls(n):
    return unreal.load_object(None, '%s%s.%s_C' % (P, n, n))


def v3(x):
    if isinstance(x, unreal.Rotator):
        return [round(x.roll, 2), round(x.pitch, 2), round(x.yaw, 2)]
    return [round(x.x, 2), round(x.y, 2), round(x.z, 2)]


def gp(o, name, default=None):
    try:
        return o.get_editor_property(name)
    except Exception:
        return default


def wrap(a):
    return (a + 180.0) % 360.0 - 180.0


S = {'phase': -2 if MODE == 'boss' else 0, 't0': time.time(), 'mark': 0.0, 'frames': [], 'events': [], 'handle': None, 'done': False}


def ev(s):
    S['events'].append([round(time.time() - S['t0'], 3), s])


def finish(why, summary=None):
    if S['done']:
        return
    S['done'] = True
    ev('finish: ' + why)
    try:
        unreal.unregister_slate_post_tick_callback(S['handle'])
    except Exception:
        pass
    with open(os.path.join(OUT, 'c3_%s.json' % MODE), 'w') as fh:
        json.dump({'summary': summary, 'events': S['events'], 'frames': S['frames']}, fh)
    print('c3_pie %s: %d frames, %s' % (MODE, len(S['frames']), why))


def boss_summary(frames, boss_loc):
    # hand-off window: from the start of the return leg (bossT 7.6) to 1.0 s after the cine ends
    idx = [i for i, f in enumerate(frames) if f.get('bossT', 0) >= 7.6 or f.get('after', -1) >= 0]
    jumps = []
    for a, b in zip(idx, idx[1:]):
        fa, fb = frames[a], frames[b]
        dp = math.dist(fa['cam'], fb['cam'])
        dr = max(abs(wrap(fb['camrot'][k] - fa['camrot'][k])) for k in (1, 2))
        df = abs(fb['fov'] - fa['fov'])
        jumps.append((dp, dr, df, fb['t']))
    last = frames[-1]
    bear = math.degrees(math.atan2(boss_loc[1] - last['ploc'][1], boss_loc[0] - last['ploc'][0]))
    return {'frames_in_window': len(idx),
            'max_step_cm': round(max(j[0] for j in jumps), 2) if jumps else None,
            'max_step_deg': round(max(j[1] for j in jumps), 2) if jumps else None,
            'max_step_fov': round(max(j[2] for j in jumps), 2) if jumps else None,
            'final_cam': last['cam'], 'final_camrot': last['camrot'], 'final_fov': last['fov'],
            'final_ctrl': last['ctrl'], 'boss': boss_loc, 'player': last['ploc'],
            'bearing_player_to_boss': round(bear, 2),
            'final_yaw_error': round(wrap(last['camrot'][2] - bear), 2),
            'final_pitch': last['camrot'][1],
            'cam_height_over_player': round(last['cam'][2] - last['ploc'][2], 2),
            'view_target': last['vt']}


def tick(dt):
    try:
        now = time.time() - S['t0']
        gw = ues.get_game_world()
        if gw is None:
            if now > 5.0:
                finish('PIE not running')
            return
        pc = GS.get_player_controller(gw, 0)
        pawns = GS.get_all_actors_of_class(gw, cls('BP_Player'))
        dirs = GS.get_all_actors_of_class(gw, cls('BP_OpeningDirector'))
        if not pawns or not dirs or pc is None:
            return
        pawn, d = pawns[0], dirs[0]
        cm = pc.player_camera_manager
        f = {'t': round(now, 3), 'cam': v3(cm.get_camera_location()), 'camrot': v3(cm.get_camera_rotation()),
             'fov': round(cm.get_fov_angle(), 2), 'ctrl': v3(pc.get_control_rotation()),
             'ploc': v3(pawn.get_actor_location()), 'vt': pc.get_view_target().get_name()[:28]}
        if MODE == 'boss':
            f['boss'] = bool(gp(d, 'BossCine', False))
            f['bossT'] = round(gp(d, 'BossT', 0.0), 3)
            ph = S['phase']
            if ph == -2:
                # the real flow first: clock out of the latte shift, let the opening run to the end
                lat = [a for a in GS.get_all_actors_of_class(gw, unreal.Actor) if a.get_class().get_name() == 'BP_LatteGame_C']
                if now > 1.0 and lat:
                    lat[0].call_method('LatteClockOut')
                    S['phase'] = -1; ev('clocked out of the latte shift')
                return
            if ph == -1:
                if gp(d, 'ObjectiveState', -1) == 1:
                    S['phase'] = 0; ev('opening over')
                return
            if ph == 0:
                pawn.call_method('PlayerDebugTeleport', (unreal.Vector(7050.0, 0.0, 94.15), 90.0))
                pc.set_control_rotation(unreal.Rotator(roll=0.0, pitch=-8.0, yaw=90.0))
                S['phase'] = 1; S['mark'] = now
                ev('teleported into the plaza facing north')
            elif ph == 1 and now - S['mark'] > 0.5:
                d.call_method('CineBossBegin')
                b = gp(d, 'BossRef')
                S['bossloc'] = v3(b.get_actor_location()) if b else None
                ev('CineBossBegin; ObjBossLoc=%s boss actor=%s' % (v3(gp(d, 'ObjBossLoc')), S['bossloc']))
                S['phase'] = 2
            elif ph == 2:
                if f['boss']:
                    # a player's mouse during the speech: down and to the right, every frame
                    if 1.0 < f['bossT'] < 8.6:
                        pc.add_pitch_input(0.8)
                        pc.add_yaw_input(0.6)
                    if f['bossT'] > 4.0 and 'mid' not in S:
                        S['mid'] = 1; ev('mid-speech control rotation %s' % f['ctrl'])
                else:
                    S['phase'] = 3; S['mark'] = now; ev('boss cine ended')
            elif ph == 3:
                f['after'] = round(now - S['mark'], 3)
                if now - S['mark'] > 0.7 and 'shot' not in S:
                    S['shot'] = 1
                    unreal.SystemLibrary.execute_console_command(gw, 'Screenshot showui')
                    ev('screenshot of the final framing')
                if now - S['mark'] > 1.2:
                    S['frames'].append(f)
                    b = gp(d, 'BossRef')
                    bl = v3(b.get_actor_location()) if b else S.get('bossloc')
                    finish('hand-off measured', boss_summary(S['frames'], bl))
                    return
            S['frames'].append(f)
            if now > 70.0:
                finish('timeout in phase %d' % S['phase'])
        elif MODE == 'music':
            comp = gp(d, 'MusicComp', None)
            snd = None
            vol = None
            playing = None
            if comp is not None:
                s = comp.get_editor_property('sound')
                snd = s.get_name() if s else None
                vol = round(comp.get_editor_property('volume_multiplier'), 3)
                playing = comp.is_playing()
            gm = GS.get_game_mode(gw)
            lat = [a for a in GS.get_all_actors_of_class(gw, unreal.Actor) if a.get_class().get_name() == 'BP_LatteGame_C']
            f.update({'snd': snd, 'vol': vol, 'playing': playing,
                      'mlevel': gp(d, 'MusicLevel', None), 'mhave': gp(d, 'MusicHave', None),
                      'flow': gp(gm, 'FlowState', None),
                      'shift': gp(lat[0], 'Shift', None) if lat else None,
                      'cine': bool(gp(d, 'CineRunning', False)), 'cineT': round(gp(d, 'CineTime', 0.0), 3),
                      'wall': bool(gp(d, 'CineWallDone', False)), 'obj': gp(d, 'ObjectiveState', -1)})
            S['frames'].append(f)
            key = (snd, playing, f['mlevel'])
            if key != S.get('lastkey'):
                S['lastkey'] = key
                ev('MUSIC -> %s playing=%s level=%s | shift=%s cine=%s cineT=%s wall=%s obj=%s flow=%s' % (
                    snd, playing, f['mlevel'], f['shift'], f['cine'], f['cineT'], f['wall'], f['obj'], f['flow']))
            ph = S['phase']
            if ph == 0 and now > 2.0:
                ev('title: %s vol %s playing %s flow %s' % (snd, vol, playing, f['flow']))
                gm.call_method('JumpCutStartPlay')
                S['phase'] = 1; S['mark'] = now
            elif ph == 1 and now - S['mark'] > 2.0:
                ev('latte shift %s: %s vol %s playing %s' % (f['shift'], snd, vol, playing))
                lat[0].call_method('LatteClockOut')
                S['phase'] = 2; S['mark'] = now; ev('clocked out (LatteClockOut)')
            elif ph == 2:
                if f['cine'] and f['cineT'] > 1.0 and 'c1' not in S:
                    S['c1'] = 1; ev('opening t=%s (before the wall): %s vol %s playing %s' % (f['cineT'], snd, vol, playing))
                if f['wall'] and 'w' not in S:
                    S['w'] = 1; ev('wall break t=%s: %s vol %s playing %s' % (f['cineT'], snd, vol, playing))
                if f['wall'] and f['cineT'] > 6.0 and 'w2' not in S:
                    S['w2'] = 1; ev('opening t=%s: %s vol %s playing %s' % (f['cineT'], snd, vol, playing))
                if f['obj'] == 1:
                    S['phase'] = 3; S['mark'] = now; ev('opening over: %s vol %s playing %s' % (snd, vol, playing))
            elif ph == 3 and now - S['mark'] > 1.5:
                ev('in play: %s vol %s playing %s' % (snd, vol, playing))
                # UseGeneratedMusic: flip it on the live director and replay the gameplay track
                try:
                    d.set_editor_property('UseGeneratedMusic', True)
                    d.call_method('CineMusicPlay', (2,))
                    ev('UseGeneratedMusic on, track 2 -> %s' % comp.get_editor_property('sound').get_name())
                    d.call_method('CineMusicPlay', (4,))
                    ev('UseGeneratedMusic on, track 4 -> %s' % comp.get_editor_property('sound').get_name())
                    d.set_editor_property('UseGeneratedMusic', False)
                    d.call_method('CineMusicPlay', (2,))
                    ev('UseGeneratedMusic off, track 2 -> %s' % comp.get_editor_property('sound').get_name())
                except Exception as e:
                    ev('UseGeneratedMusic check failed: %s' % e)
                S['phase'] = 35; S['mark'] = now
            elif ph == 35 and now - S['mark'] > 0.5:
                unreal.SystemLibrary.execute_console_command(gw, 'RestartLevel')
                S['phase'] = 4; S['mark'] = now
            elif ph == 4 and now - S['mark'] > 3.0:
                ev('after restart: %s vol %s playing %s flow %s shift %s' % (snd, vol, playing, f['flow'], f['shift']))
                finish('music checked')
                return
            if now > 60.0:
                finish('timeout in phase %d' % ph)
    except Exception:
        ev('EXC ' + traceback.format_exc()[-700:])
        finish('exception')


S['handle'] = unreal.register_slate_post_tick_callback(tick)
print('c3_pie %s: recording' % MODE)
