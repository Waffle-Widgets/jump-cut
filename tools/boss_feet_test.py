"""Is the mob boss standing on the floor? Play-mode check. Run ONCE per PIE session, as the first script:
    py <repo>/tools/boss_feet_test.py
It presses start, samples the boss as placed (asleep), then stands the player in front of him, wakes him and
samples ten times a second for 9 s while he walks, cleaves and gets punched. For every sample it reads the world
Z of all 83 bones and reports LIFT = lowest bone minus the bottom of his capsule. A boss with his feet on the
ground reads LIFT within a few cm of 0 in every state; the Nov 13 float read 107-113 while walking.
Result: <project>/Saved/jcpy/boss_feet.json ("done": true, and a per-state "summary").
Judge by LIFT, never by a montage name: a montage reports itself as playing wherever the pose is.
Nothing is saved; it only reads, moves the player and calls the game's own functions.
"""
import json, math, os
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'boss_feet.json')
ws = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
R = {'rows': [], 'events': [], 'done': False}
st = {'t': 0.0, 'phase': 0, 'next': 0.0, 'hits': 0}
handle = [None]
player = boss = None
if ws:
    for a in unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.Actor):
        n = a.get_class().get_name()
        if n == 'BP_Player_C':
            player = a
        elif n == 'BP_BossFreeze_C':
            boss = a


def sample(tag):
    mesh = boss.mesh
    loc = boss.get_actor_location()
    hh = boss.capsule_component.get_scaled_capsule_half_height()
    lo, lob = 1e9, ''
    for i in range(mesh.get_num_bones()):
        b = mesh.get_bone_name(i)
        z = mesh.get_socket_location(b).z
        if z < lo:
            lo, lob = z, str(b)
    v = boss.get_velocity()
    m = boss.get_current_montage()
    return {'t': round(st['t'], 2), 'tag': tag, 'lift': round(lo - (loc.z - hh), 1), 'bone': lob, 'actor_z': round(loc.z, 1),
            'spd': round(math.hypot(v.x, v.y)), 'vz': round(v.z), 'mode': str(boss.character_movement.movement_mode).split('.')[-1].split(':')[0],
            'mont': m.get_name() if m else '', 'awake': boss.get_editor_property('EnemyIsAwake'), 'hp': round(boss.get_editor_property('EnemyHealth'), 1)}


def finish():
    S = {}
    for r in R['rows']:
        if r['tag'] == 'asleep':
            k = 'asleep (as placed)'
        elif r['mont']:
            k = 'montage ' + r['mont']
        elif r['spd'] > 60:
            k = 'walking'
        else:
            k = 'awake, standing'
        s = S.setdefault(k, {'n': 0, 'lift_min': 1e9, 'lift_max': -1e9, 'airborne': 0})
        s['n'] += 1
        s['lift_min'] = min(s['lift_min'], r['lift'])
        s['lift_max'] = max(s['lift_max'], r['lift'])
        s['airborne'] += 0 if 'WALKING' in r['mode'].upper() else 1
    R['summary'] = S
    R['done'] = True
    with open(OUT, 'w') as fh:
        fh.write(json.dumps(R))
    if handle[0]:
        unreal.unregister_slate_post_tick_callback(handle[0])


def tick(dt):
    try:
        st['t'] += dt
        t, p = st['t'], st['phase']
        if p == 0 and t > 0.3:
            unreal.GameplayStatics.get_game_mode(ws).call_method('JumpCutStartPlay')
            st['phase'] = 1
        elif p == 1:
            if t >= st['next']:
                st['next'] = t + 0.1
                R['rows'].append(sample('asleep'))
            if t > 1.6:
                b = boss.get_actor_location()
                try:
                    player.set_editor_property('Health', 100000.0)
                except Exception as e:
                    R['events'].append('could not raise player health: %s' % e)
                player.set_actor_location(unreal.Vector(b.x - 650.0, b.y, b.z), False, True)
                boss.call_method('EnemyWake')
                R['events'].append('%.2f player placed 650 cm west of the boss, boss woken' % t)
                st['phase'] = 2
                st['t0'] = t
        elif p == 2:
            if t >= st['next']:
                st['next'] = t + 0.1
                R['rows'].append(sample('awake'))
            el = t - st['t0']
            # two light punches at 5 s and 6 s so the hit react is sampled too (no knock-up: that is a real launch)
            if st['hits'] < 2 and el > 5.0 + st['hits']:
                st['hits'] += 1
                boss.call_method('EnemyTakeHit', args=(1.0, player.get_actor_location(), 0.0, 0.0, 0.2))
                R['events'].append('%.2f light hit %d' % (t, st['hits']))
            if el > 9.0:
                finish()
    except Exception:
        import traceback
        R['error'] = traceback.format_exc()
        finish()


if player is None or boss is None:
    R['error'] = 'need Play mode with BP_Player_C and BP_BossFreeze_C in the world (player=%s boss=%s)' % (player, boss)
    R['done'] = True
    open(OUT, 'w').write(json.dumps(R))
else:
    handle[0] = unreal.register_slate_post_tick_callback(tick)
