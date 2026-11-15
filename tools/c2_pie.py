"""Sun Nov 15 (afternoon): played by a script IN REAL TIME and sampled every frame. Changes no assets.

    py <repo>/tools/c2_pie.py bossff   plaza: Freeze Frame on, then the boss dies inside it.
                                       Records whether the freeze is still running through the
                                       Splice power moment and the outro, and when the boss's
                                       own clock (CustomTimeDilation) comes back.

Same method as b2_pie.py (a Slate post-tick callback; `b1u_pie.py flags on` first so the title is
skipped). Writes Saved/jcpy/c2_<mode>.json.
"""
import unreal, os, sys, json, time, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
MODE = sys.argv[1] if len(sys.argv) > 1 else 'bossff'
P = '/Game/Game/Blueprints/'
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)


def cls(n):
    return unreal.load_object(None, '%s%s.%s_C' % (P, n, n))


def v3(x):
    return [round(x.x, 1), round(x.y, 1), round(x.z, 1)]


def gp(o, name, default=None):
    try:
        return o.get_editor_property(name)
    except Exception:
        return default


S = {'phase': 0, 't0': time.time(), 'mark': 0.0, 'frames': [], 'events': [], 'handle': None, 'done': False}


def ev(s):
    S['events'].append([round(time.time() - S['t0'], 3), s])


def finish(why):
    if S['done']:
        return
    S['done'] = True
    ev('finish: ' + why)
    try:
        unreal.unregister_slate_post_tick_callback(S['handle'])
    except Exception:
        pass
    with open(os.path.join(OUT, 'c2_%s.json' % MODE), 'w') as fh:
        json.dump({'events': S['events'], 'frames': S['frames']}, fh)
    print('c2_pie %s: wrote %d frames, %s' % (MODE, len(S['frames']), why))


def actors(gw, n):
    return list(unreal.GameplayStatics.get_all_actors_of_class(gw, cls(n)))


def tp(pawn, pc, x, y, yaw, pitch=-10.0):
    pawn.call_method('PlayerDebugTeleport', (unreal.Vector(x, y, 94.15), yaw))
    pc.set_control_rotation(unreal.Rotator(roll=0.0, pitch=pitch, yaw=yaw))


SHOTS = [float(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else [0.5, 1.2, 2.0, 2.45, 3.0, 4.5]
W_KEYS = ['TitleBarista', 'TitleDirector', 'TitleClapOpen', 'TitleClapShut', 'TitleArt', 'ScreenTitle', 'ScreenKey', 'KeyBox']


def title_tick(now, gw):
    """`title`: the title screen as the player sees it. Needs ShowTitleOnStart TRUE (b1u_pie.py flags off)."""
    gms = actors(gw, 'BP_JumpCutGameMode')
    if not gms:
        return
    gm = gms[0]
    w = gp(gm, 'TitleWidget', None)
    if w is None:
        return
    vis = str(w.get_visibility()).split('.')[-1]
    if 'tw0' not in S and 'COLLAPSED' not in vis.upper():
        S['tw0'] = now; ev('title widget visible (%s)' % vis)
    if 'tw0' not in S:
        return
    t = now - S['tw0']
    f = {'t': round(t, 3), 'vis': vis, 'flow': gp(gm, 'FlowState', -1),
         'dil': round(unreal.GameplayStatics.get_global_time_dilation(gw), 3),
         'animT': round(gp(w, 'TitleT', -1.0), 3), 'snapped': gp(w, 'TitleSnapped', None)}
    for k in W_KEYS:
        c = gp(w, k, None)
        if c is not None:
            f[k] = [round(c.get_render_opacity(), 3), str(c.get_visibility()).split('.')[-1]]
    S['frames'].append(f)
    for s in SHOTS:
        tag = 'title_%.2f' % s
        if t >= s and tag not in S.get('shot', set()):
            S.setdefault('shot', set()).add(tag)
            unreal.SystemLibrary.execute_console_command(gw, 'Screenshot showui')
            ev('screenshot %s at t=%.3f' % (tag, t))
            break
    if t > max(SHOTS) + 1.0:
        finish('title sampled')


def tick(dt):
    try:
        now = time.time() - S['t0']
        gw = ues.get_game_world()
        if gw is None:
            if now > 5.0:
                finish('PIE not running')
            return
        if MODE == 'music':
            # title (2 s) -> R -> opening (music silent) -> play (music up) -> whole-level restart
            gms, dirs = actors(gw, 'BP_JumpCutGameMode'), actors(gw, 'BP_OpeningDirector')
            if not gms or not dirs:
                return
            gm, d = gms[0], dirs[0]
            comp = gp(d, 'MusicComp', None)
            mus = 0
            for a in unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.Actor):
                for c in a.get_components_by_class(unreal.AudioComponent):
                    s = c.get_editor_property('sound')
                    if s is not None and s.get_name().startswith('MUS_') and c.is_playing():
                        mus += 1
            st = {'t': round(now, 3), 'ph': S['phase'], 'flow': gp(gm, 'FlowState', -1),
                  'have': gp(d, 'MusicHave', None), 'level': gp(d, 'MusicLevel', None),
                  'sound': comp.get_editor_property('sound').get_name() if comp and comp.get_editor_property('sound') else None,
                  'playing': comp.is_playing() if comp else None, 'mus_playing': mus,
                  'opening': bool(gp(d, 'CineRunning', False)), 'world': gw.get_name()}
            S['frames'].append(st)
            key = (st['flow'], st['have'], st['level'], st['sound'], st['playing'], st['mus_playing'], st['opening'])
            if key != S.get('lastkey'):
                ev('state %s' % st); S['lastkey'] = key
            ph = S['phase']
            if ph == 0 and st['flow'] == 0 and now > 2.5:
                gm.call_method('JumpCutStartPlay'); S['phase'] = 1; S['mark'] = now; ev('called JumpCutStartPlay')
            elif ph == 1 and S['mark'] and not st['opening'] and now - S['mark'] > 3.0 and st['level'] == 1.0:
                S['phase'] = 2; S['mark'] = now; ev('opening over, music up')
            elif ph == 2 and now - S['mark'] > 2.0:
                gm.call_method('JumpCutRestartWholeLevel'); S['phase'] = 3; S['mark'] = now; ev('called JumpCutRestartWholeLevel')
            elif ph == 3 and now - S['mark'] > 4.0:
                finish('music checked through a restart')
            if now > 60.0:
                finish('timeout in phase %d' % ph)
            return
        if MODE == 'titleskip':
            # start play 1 s into the animation (what R does), then restart the whole level (what R
            # does on the win screen) and check the new title widget starts its animation from 0
            gms = actors(gw, 'BP_JumpCutGameMode')
            if not gms:
                return
            gm = gms[0]
            w = gp(gm, 'TitleWidget', None)
            ph = S['phase']
            st = {'flow': gp(gm, 'FlowState', -1), 'vis': str(w.get_visibility()).split('.')[-1] if w else None,
                  'animT': round(gp(w, 'TitleT', -1.0), 3) if w else None,
                  'dil': round(unreal.GameplayStatics.get_global_time_dilation(gw), 3),
                  'world': gw.get_name(), 'wid': w.get_name() if w else None}
            S['frames'].append(dict(st, t=round(now, 3), ph=ph))
            if ph == 0 and st['animT'] is not None and st['animT'] > 1.0:
                ev('before start: %s' % st)
                gm.call_method('JumpCutStartPlay')
                S['phase'] = 1; S['mark'] = now
            elif ph == 1 and now - S['mark'] > 0.5:
                pawn = actors(gw, 'BP_Player')[0]
                ev('0.5 s after start: %s inputLocked=%s' % (st, gp(pawn, 'InputLocked', None)))
                S['wid0'] = st['wid']
                gm.call_method('JumpCutRestartWholeLevel')
                S['phase'] = 2; S['mark'] = now
            elif ph == 2 and st['wid'] != S.get('wid0') and st['animT'] is not None and st['animT'] > 0.0:
                ev('after restart, first frame of new title: %s' % st)
                S['phase'] = 3; S['mark'] = now
            elif ph == 3 and now - S['mark'] > 3.0:
                ev('3 s into the replayed title: %s' % st)
                finish('skip and replay checked')
            if now > 60.0:
                finish('timeout in phase %d' % ph)
            return
        if MODE == 'title':
            title_tick(now, gw)
            if now > 40.0:
                finish('timeout')
            return
        pc = unreal.GameplayStatics.get_player_controller(gw, 0)
        pawns, dirs = actors(gw, 'BP_Player'), actors(gw, 'BP_OpeningDirector')
        if not pawns or not dirs or pc is None:
            return
        pawn, d = pawns[0], dirs[0]
        obj = gp(d, 'ObjectiveState', -1)
        f = {'t': round(now, 3), 'ph': S['phase'], 'obj': obj,
             'dil': round(unreal.GameplayStatics.get_global_time_dilation(gw), 3),
             'power': bool(gp(d, 'PowerCine', False)), 'powerT': round(gp(d, 'PowerT', 0.0), 3),
             'outro': bool(gp(d, 'OutroCine', False)), 'outroT': round(gp(d, 'OutroT', 0.0), 3),
             'boss': bool(gp(d, 'BossCine', False)),
             'ff': bool(gp(pawn, 'FreezeFrameActive', False)),
             'ffLeft': round(gp(pawn, 'FreezeFrameTimeLeft', -1.0), 3),
             'won': bool(gp(pawn, 'HasWon', False)), 'splice': bool(gp(pawn, 'HasSplice', False)),
             'mlevel': gp(d, 'MusicLevel', None),
             'msound': (lambda c: c.get_editor_property('sound').get_name() if c and c.get_editor_property('sound') else None)(gp(d, 'MusicComp', None))}
        bs = actors(gw, 'BP_BossFreeze')
        if bs:
            b = bs[0]
            f['bhp'] = round(gp(b, 'EnemyHealth', -1.0), 1)
            f['bdef'] = bool(gp(b, 'EnemyIsDefeated', False))
            f['bstop'] = bool(gp(b, 'EnemyTimeStopped', False))
            f['bctd'] = round(b.get_editor_property('custom_time_dilation'), 3)
            f['bloc'] = v3(b.get_actor_location())
            f['blinger'] = round(gp(b, 'EnemyDefeatLingerLeft', -1.0), 3)
        else:
            f['boss_gone'] = True
        S['frames'].append(f)
        ph = S['phase']
        if MODE == 'crash':
            # the opening plays by itself; log the director clock on the frame each event fires
            f['cine'] = round(gp(d, 'CineTime', -1.0), 3)
            sa = gp(d, 'CineSeqActor', None)
            try:
                f['seq'] = round(sa.get_editor_property('sequence_player').get_current_time().time.frame_number.value / 30.0, 3)
            except Exception:
                f['seq'] = None
            for key in ('CineCrashSounded', 'CineWallDone', 'CineFireDone', 'RagdollOn'):
                v = bool(gp(d, key, False))
                if S.get('p_' + key) is not None and S['p_' + key] != v:
                    ev('%s -> %s at CineTime %s (sequence %s)' % (key, v, f['cine'], f['seq']))
                S['p_' + key] = v
            if f['cine'] > 8.0 or now > 60.0:
                finish('opening sampled')
            return
        if ph == 0 and obj == 1:
            pawn.call_method('PlayerGrantFreezeFrame')
            for g in actors(gw, 'BP_EnemyBase'):
                if g.get_actor_location().x < 6500.0:
                    g.call_method('EnemyTakeHit', (9999.0, pawn.get_actor_location(), 300.0, 100.0, 0.5))
            d.set_editor_property('ObjectiveState', 5)
            tp(pawn, pc, 7050.0, 0.0, 0.0)
            S['phase'] = 1; S['mark'] = now; ev('teleported into the plaza')
        elif ph == 1:
            if f['boss'] and not S.get('saw'):
                ev('boss intro started; music %s level %s' % (f['msound'], f['mlevel']))
            if f['boss']:
                S['saw'] = True
            elif S.get('saw') and not f['power']:
                S['phase'] = 2; S['mark'] = now; ev('boss intro over')
            elif now - S['mark'] > 12.0:
                finish('boss intro never started (obj=%s)' % obj)
        elif ph == 2 and now - S['mark'] > 0.8:
            pawn.call_method('FreezeFrameStart')
            S['phase'] = 3; S['mark'] = now; ev('FreezeFrameStart; ff=%s' % gp(pawn, 'FreezeFrameActive', None))
        elif ph == 3 and now - S['mark'] > 0.5 and bs:
            b = bs[0]
            ev('before kill: boss stopped=%s ctd=%s ffLeft=%s' % (f.get('bstop'), f.get('bctd'), f['ffLeft']))
            b.call_method('EnemyTakeHit', (9999.0, pawn.get_actor_location(), 300.0, 100.0, 0.5))
            S['phase'] = 4; S['mark'] = now; ev('boss killed inside Freeze Frame')
        elif ph == 4:
            for key in ('power', 'outro', 'won', 'ff', 'bstop', 'mlevel', 'msound'):
                prev = S.get('prev_' + key)
                if prev is not None and prev != f.get(key):
                    ev('%s -> %s (powerT %s outroT %s dil %s bctd %s)' % (key, f.get(key), f['powerT'], f['outroT'], f['dil'], f.get('bctd')))
                S['prev_' + key] = f.get(key)
            if now - S['mark'] > 14.0:
                finish('watched 14 s after the kill')
        if now > 90.0:
            finish('timeout in phase %d' % ph)
    except Exception:
        ev('EXC ' + traceback.format_exc()[-700:])
        finish('exception')


S['handle'] = unreal.register_slate_post_tick_callback(tick)
print('c2_pie %s: recording' % MODE)
