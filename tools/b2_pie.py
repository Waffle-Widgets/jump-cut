"""Sun Nov 15 polish, played by a script IN REAL TIME and sampled every frame. Changes no assets.

    py <repo>/tools/b2_pie.py rescue   beat 1 up to the rescue: do both of them RUN, facing the way they go
    py <repo>/tools/b2_pie.py clap     the power pickup, then a Freeze Frame the player triggers himself
    py <repo>/tools/b2_pie.py boss     straight to the plaza: the intro, then the boss's own Splice

Same method as b1u_pie.py (a Slate post-tick callback; `b1u_pie.py flags on` first so the title is
skipped). The player is walked with PlayerDebugTeleport because a script cannot hold a key; every
trigger after that is the game's own. Writes Saved/jcpy/b2_<mode>.json and `Screenshot showui`s.
"""
import unreal, os, sys, json, time, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
MODE = sys.argv[1] if len(sys.argv) > 1 else 'rescue'
P = '/Game/Game/Blueprints/'
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)


def cls(n):
    return unreal.load_object(None, '%s%s.%s_C' % (P, n, n))


def v3(x):
    if isinstance(x, unreal.Rotator):
        return [round(x.roll, 1), round(x.pitch, 1), round(x.yaw, 1)]
    return [round(x.x, 1), round(x.y, 1), round(x.z, 1)]


def gp(o, name, default=None):
    try:
        return o.get_editor_property(name)
    except Exception:
        return default


S = {'phase': 0, 't0': time.time(), 'mark': 0.0, 'frames': [], 'events': [], 'shots': [],
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
    with open(os.path.join(OUT, 'b2_%s.json' % MODE), 'w') as fh:
        json.dump({'events': S['events'], 'shots': S['shots'], 'frames': S['frames']}, fh)
    print('b2_pie %s: wrote %d frames, %s' % (MODE, len(S['frames']), why))


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
             'resc': bool(gp(d, 'RescueCine', False)), 'rescT': round(gp(d, 'RescueT', 0.0), 3),
             'expl': bool(gp(d, 'ExplCine', False)),
             'boss': bool(gp(d, 'BossCine', False)), 'bossT': round(gp(d, 'BossT', 0.0), 3),
             'ploc': v3(pawn.get_actor_location()), 'pyaw': round(pawn.get_actor_rotation().yaw, 1),
             'pvel': round(pawn.get_velocity().length(), 1),
             'locked': bool(gp(pawn, 'InputLocked', False)), 'hp': round(gp(pawn, 'Health', -1.0), 1),
             'ff': bool(gp(pawn, 'FreezeFrameActive', False)),
             'clapT': round(gp(d, 'ClapT', -1.0), 3) if gp(d, 'ClapOn', False) else -1.0}
        if MODE == 'rescue':
            cws = actors(gw, 'BP_Coworker')
            if cws:
                cw = cws[0]
                f['cw'] = v3(cw.get_actor_location()); f['cwyaw'] = round(cw.get_actor_rotation().yaw, 1)
                f['cwrun'] = bool(gp(cw, 'HoldMoving', False))
        if MODE == 'boss':
            bs = actors(gw, 'BP_BossFreeze')
            if bs:
                b = bs[0]
                f['bloc'] = v3(b.get_actor_location()); f['bhp'] = round(gp(b, 'EnemyHealth', -1.0), 1)
                f['bsplT'] = round(gp(b, 'BossSpliceT', -1.0), 3) if gp(b, 'BossSpliceOn', False) else -1.0
                f['bcd'] = round(gp(b, 'BossSpliceCooldownLeft', -9.0), 2)
                f['buse'] = gp(b, 'BossSpliceArmed', None); f['bstate'] = gp(b, 'BossState', None)
                f['bstun'] = round(gp(b, 'EnemyStunLeft', -9.0), 2); f['bwind'] = gp(b, 'EnemyIsWindingUp', None)
                m = b.get_component_by_class(unreal.SkeletalMeshComponent)
                f['bscale'] = v3(m.get_editor_property('relative_scale3d'))
                # a Screenshot hitches the game ~0.3 s, longer than the whole 0.4 s blink: slow the
                # world while he is mid-blink so the frames can be told apart. Test only.
                if not f['power']:
                    unreal.GameplayStatics.set_global_time_dilation(gw, 0.12 if f['bsplT'] >= 0.0 else 1.0)
        S['frames'].append(f)
        ph = S['phase']

        if MODE == 'boss':
            if ph == 0 and obj == 1:
                # skip beat 1 and 2: hand the powers over and clear the street
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
                    for tt, tag in ((5.6, 'boss_line3'), (7.3, 'boss_cut_after')):
                        if f['bossT'] > tt: shot(gw, tag)
                    for tt, tag in ((0.08, 'cut_008'), (0.17, 'cut_017'), (0.24, 'cut_024'), (0.33, 'cut_033')):
                        if f.get('bsplT', -1.0) > tt: shot(gw, tag)
                elif S.get('saw'):
                    S['phase'] = 2; S['mark'] = now; ev('intro over; boss at %s player at %s' % (f.get('bloc'), f['ploc']))
                elif now - S['mark'] > 8.0:
                    finish('boss intro never started (obj=%s)' % obj)
            elif ph == 2:
                # stand still and let him come: every Splice he does is his own decision
                if f.get('bsplT', -1.0) > 0.0 and 'spl' not in S:
                    S['spl'] = now; ev('boss Splice began; boss at %s' % f.get('bloc'))
                for tt, tag in ((0.08, 'spl_008'), (0.17, 'spl_017'), (0.24, 'spl_024'), (0.33, 'spl_033')):
                    if f.get('bsplT', -1.0) > tt: shot(gw, tag)
                if 'spl' in S:
                    if now - S['spl'] > 4.0: shot(gw, 'spl_after')
                    if now - S['spl'] > 4.2 and 'spl2' not in S:
                        S['spl2'] = 1; ev('after Splice: boss at %s scale %s player hp %s' % (f.get('bloc'), f.get('bscale'), f['hp']))
                if now - S['mark'] > 16.0:
                    finish('watched the fight for 16 s')
            if now > 60.0:
                finish('timeout in phase %d' % ph)
            return

        # ---- rescue / clap share beat 1's run-up
        if ph == 0 and obj == 1:
            S['phase'] = 1; S['mark'] = now; ev('opening over, objective 1')
        elif ph == 1 and now - S['mark'] > 1.0:
            tp(pawn, pc, -215.0, -40.0, 190.0)
            S['phase'] = 2; ev('teleported to the driver')
        elif ph == 2:
            if f['power']:
                for tt, tag in ((0.06, 'pw_open'), (0.17, 'pw_snap'), (0.5, 'pw_hold'), (0.9, 'pw_fade')):
                    if MODE == 'clap' and f['clapT'] > tt and tag not in S['shot_done']:
                        shot(gw, tag); break
            elif obj == 2:
                S['phase'] = 3; S['mark'] = now; ev('power moment over, objective 2')
        elif ph == 3:
            if MODE == 'clap':
                if now - S['mark'] > 1.0 and 'ffs' not in S:
                    S['ffs'] = now; pawn.call_method('FreezeFrameStart'); ev('called FreezeFrameStart')
                if 'ffs' in S:
                    for tt, tag in ((0.06, 'ff_open'), (0.17, 'ff_snap'), (0.5, 'ff_hold')):
                        if f['clapT'] > tt and now - S['ffs'] > 0.02 and tag not in S['shot_done']:
                            shot(gw, tag); break
                    if now - S['ffs'] > 2.0:
                        finish('clap watched twice')
            elif now - S['mark'] > 1.0:
                tp(pawn, pc, -330.0, 60.0, 128.0)
                S['phase'] = 4; ev('teleported to the coworker')
        elif ph == 4:
            if f['resc']:
                for tt, tag in ((0.25, 'run_025'), (0.6, 'run_060'), (1.0, 'run_100'), (1.4, 'run_140'), (2.2, 'run_220')):
                    if f['rescT'] > tt: shot(gw, tag)
            if f['expl']:
                finish('explosion began')
        if now > 80.0:
            finish('timeout in phase %d' % ph)
    except Exception:
        ev('EXC ' + traceback.format_exc()[-700:])
        finish('exception')


S['handle'] = unreal.register_slate_post_tick_callback(tick)
print('b2_pie %s: recording' % MODE)
