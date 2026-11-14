"""Play-mode check for tools/goon_individual_graphs.py. Run ONCE per PIE session, as the first script:
    py <repo>/tools/goon_individual_test.py
It presses start, stands the player in front of the street goons and records, ten times a second: who is awake,
who is winding up, how far apart they keep, which montage each is playing (a feint shows as AM_Human_Charged
with 'taunt' > 0); then throws two light punches and a
finisher and records whose health moved. Result: <project>/Saved/jcpy/goon_test.json  (marker "done": true).
Nothing is saved; it only reads and calls the game's own functions.
"""
import json, math, os
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'goon_test.json')
ws = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
gm = unreal.GameplayStatics.get_game_mode(ws)
player = None
for a in unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.Actor):
    if a.get_class().get_name() == 'BP_Player_C':
        player = a
R = {'rows': [], 'events': [], 'done': False}
st = {'t': 0.0, 'phase': 0, 'next': 0.0, 'punches': 0}
handle = [None]


def goons():
    out = []
    for a in unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.Actor):
        if a.get_class().get_name() == 'BP_Goon_C':
            l = a.get_actor_location()
            if 2500 < l.x < 6200:
                out.append(a)
    out.sort(key=lambda a: a.get_name())
    return out


def gp(a, n):
    return a.get_editor_property(n)


def snap(a):
    l = a.get_actor_location()
    v = a.get_velocity()
    m = a.get_current_montage()
    return {'n': a.get_name()[-3:], 'x': round(l.x), 'y': round(l.y), 'spd': round(math.hypot(v.x, v.y)),
            'awake': gp(a, 'EnemyIsAwake'), 'wind': gp(a, 'EnemyIsWindingUp'), 'cd': round(gp(a, 'EnemyAttackCooldownLeft'), 2),
            'hp': round(gp(a, 'EnemyHealth'), 1), 'dead': gp(a, 'EnemyIsDefeated'), 'mont': m.get_name() if m else '',
            'taunt': round(gp(a, 'EnemyTauntBusyLeft'), 2)}


def ev(s):
    R['events'].append('%.2f %s' % (st['t'], s))


def face_nearest():
    pl = player.get_actor_location()
    best, bd = None, 1e9
    for g in goons():
        if gp(g, 'EnemyIsDefeated'):
            continue
        l = g.get_actor_location()
        d = math.hypot(l.x - pl.x, l.y - pl.y)
        if d < bd:
            best, bd = g, d
    if best:
        l = best.get_actor_location()
        yaw = math.degrees(math.atan2(l.y - pl.y, l.x - pl.x))
        player.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw), False)
    return best, bd


def finish():
    R['done'] = True
    with open(OUT, 'w') as fh:
        fh.write(json.dumps(R))
    unreal.unregister_slate_post_tick_callback(handle[0])


def tick(dt):
    try:
        st['t'] += dt
        t = st['t']
        p = st['phase']
        if p == 0 and t > 0.3:
            gm.call_method('JumpCutStartPlay')
            st['phase'] = 1
        elif p == 1 and t > 0.8:
            gs = goons()
            R['setup'] = [{'n': g.get_name()[-3:], 'maxhp': round(gp(g, 'EnemyMaxHealth'), 1), 'speed': round(gp(g, 'EnemyMoveSpeed')),
                           'windup': round(gp(g, 'EnemyWindup'), 2), 'aggro': round(gp(g, 'EnemyAggroRange')), 'hold': round(gp(g, 'EnemyHoldRange')),
                           'yaw': round(g.get_actor_rotation().yaw), 'vary': gp(g, 'EnemyVary'), 'scale': round(g.get_actor_scale3d().x, 3)} for g in gs]
            player.set_actor_location(unreal.Vector(3700.0, 0.0, 100.0), False, True)
            ev('player placed at x=3700; goons=%d; canact=%s' % (len(gs), player.call_method('PlayerCanAct')))
            st['phase'] = 2
            st['t0'] = t
        elif p >= 2:
            if t >= st['next']:
                st['next'] = t + 0.1
                gs = goons()
                row = {'t': round(t - st['t0'], 2), 'php': round(gp(player, 'Health'), 1), 'lost': gp(player, 'IsLost'), 'g': [snap(g) for g in gs]}
                R['rows'].append(row)
            el = t - st['t0']
            # phase 2: stand still for 12 s and let them come (long enough to see a feint). phase 3: punch.
            if p == 2 and el > 12.0:
                st['phase'] = 3
                st['pt'] = t
            elif p == 3 and t >= st['pt']:
                best, bd = face_nearest()
                if best is None or st['punches'] >= 40 or el > 40.0:
                    ev('stop: best=%s punches=%d' % (best, st['punches']))
                    st['phase'] = 4
                    st['end'] = t + 2.0
                elif bd <= 175.0:
                    before = {g.get_name()[-3:]: round(gp(g, 'EnemyHealth'), 1) for g in goons()}
                    step = gp(player, 'ComboStep')
                    player.call_method('PlayerPunch')
                    after = {g.get_name()[-3:]: round(gp(g, 'EnemyHealth'), 1) for g in goons()}
                    hit = [k for k in before if after.get(k, before[k]) != before[k]]
                    ev('punch %d (combo step was %d) at d=%.0f hit %s  %s -> %s' % (st['punches'], step, bd, hit, before, after))
                    st['punches'] += 1
                    st['pt'] = t + 0.4
                else:
                    # walk at the nearest one
                    l = best.get_actor_location(); pl = player.get_actor_location()
                    d = unreal.Vector(l.x - pl.x, l.y - pl.y, 0.0)
                    d.normalize()
                    player.add_movement_input(d, 1.0, True)
            elif p == 4 and t >= st['end']:
                finish()
    except Exception as e:
        import traceback
        R['error'] = traceback.format_exc()
        finish()


if player is None:
    R['error'] = 'no BP_Player_C in the game world (is Play mode running?)'
    R['done'] = True
    open(OUT, 'w').write(json.dumps(R))
else:
    handle[0] = unreal.register_slate_post_tick_callback(tick)
