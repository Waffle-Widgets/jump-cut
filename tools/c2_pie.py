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


def tick(dt):
    try:
        now = time.time() - S['t0']
        gw = ues.get_game_world()
        if gw is None:
            if now > 5.0:
                finish('PIE not running')
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
             'won': bool(gp(pawn, 'HasWon', False)), 'splice': bool(gp(pawn, 'HasSplice', False))}
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
        if ph == 0 and obj == 1:
            pawn.call_method('PlayerGrantFreezeFrame')
            for g in actors(gw, 'BP_EnemyBase'):
                if g.get_actor_location().x < 6500.0:
                    g.call_method('EnemyTakeHit', (9999.0, pawn.get_actor_location(), 300.0, 100.0, 0.5))
            d.set_editor_property('ObjectiveState', 5)
            tp(pawn, pc, 7050.0, 0.0, 0.0)
            S['phase'] = 1; S['mark'] = now; ev('teleported into the plaza')
        elif ph == 1:
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
            for key in ('power', 'outro', 'won', 'ff', 'bstop'):
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
