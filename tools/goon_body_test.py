"""Play-mode check that the street goon animates on his OWN body (#6). Run ONCE per PIE session,
as the FIRST script of that session:
    py <repo>/tools/goon_body_test.py

What it is actually proving, and why reading the Blueprint back is not enough. `BP_Goon` can carry
`SK_StreetGoon` and still not animate: the anim blueprint it pointed at until now was Epic's
`ABP_Unarmed`, whose target skeleton is the mannequin's. A mismatched anim class does not error -
the character simply stands in his reference pose, which from a script looks like a correctly
assigned mesh. So this reads the LIVE anim instance's class off a spawned goon, watches his feet
while he walks (the Meshy root sits at pelvis height, which is what made the cleaver boss float
113 cm), and throws punches to make his hit-react and death montages play.

Records, five times a second: each goon's anim instance class, the skeletal mesh he is wearing,
his speed, the lowest bone in his skeleton in world Z, and the montage playing. Then punches the
nearest one until something dies.

Result: <project>/Saved/jcpy/goon_body.json  (marker "done": true). Nothing is saved; it only
reads and calls the game's own functions. Stop PIE afterwards - a session left running blocks
every Blueprint edit.
"""
import json
import math
import os
import traceback

import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'goon_body.json')
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
            if 2500 < a.get_actor_location().x < 6200:
                out.append(a)
    out.sort(key=lambda x: x.get_name())
    return out


def ev(s):
    R['events'].append('%.2f %s' % (st['t'], s))


def body(g):
    """Everything about how this goon is being animated, read off the live component."""
    comp = g.get_component_by_class(unreal.SkeletalMeshComponent)
    row = {'n': g.get_name()[-3:]}
    if comp is None:
        row['err'] = 'no skeletal mesh component'
        return row
    mesh = comp.get_editor_property('skeletal_mesh_asset')
    inst = comp.get_anim_instance()
    row['mesh'] = mesh.get_name() if mesh else None
    row['anim_instance'] = inst.get_class().get_name() if inst else None
    names = comp.get_all_socket_names()
    row['bones'] = len(names)
    # lowest bone in WORLD space - the float shows up here and nowhere else
    lo = 1e9
    for b in ('foot_l', 'foot_r', 'Bone_010', 'Bone_015', 'Bone_006', 'Bone_011'):
        try:
            z = comp.get_socket_location(b).z
            if z != 0.0:
                lo = min(lo, z)
        except Exception:
            pass
    row['lowest_known_bone_z'] = None if lo > 1e8 else round(lo, 1)
    row['actor_z'] = round(g.get_actor_location().z, 1)
    v = g.get_velocity()
    row['spd'] = round(math.hypot(v.x, v.y))
    m = g.get_current_montage()
    row['mont'] = m.get_name() if m else ''
    row['hp'] = round(g.get_editor_property('EnemyHealth'), 1)
    row['awake'] = g.get_editor_property('EnemyIsAwake')
    row['dead'] = g.get_editor_property('EnemyIsDefeated')
    return row


def finish():
    R['done'] = True
    with open(OUT, 'w') as fh:
        fh.write(json.dumps(R, indent=1))
    unreal.unregister_slate_post_tick_callback(handle[0])


def tick(dt):
    try:
        st['t'] += dt
        t, p = st['t'], st['phase']
        if p == 0 and t > 0.3:
            gm.call_method('JumpCutStartPlay')      # the title screen locks all input
            st['phase'] = 1
        elif p == 1 and t > 0.8:
            gs = goons()
            player.set_actor_location(unreal.Vector(3700.0, 0.0, 100.0), False, True)
            ev('player at x=3700; goons=%d; canact=%s' % (len(gs), player.call_method('PlayerCanAct')))
            R['setup'] = [body(g) for g in gs]
            st['phase'] = 2
            st['t0'] = t
        elif p >= 2:
            if t >= st['next']:
                st['next'] = t + 0.2
                R['rows'].append({'t': round(t - st['t0'], 2), 'g': [body(g) for g in goons()]})
            el = t - st['t0']
            if p == 2 and el > 8.0:          # let them walk at us so the blend space has to run
                st['phase'] = 3
                st['pt'] = t
            elif p == 3:
                pl = player.get_actor_location()
                best, bd = None, 1e9
                for g in goons():
                    if g.get_editor_property('EnemyIsDefeated'):
                        continue
                    l = g.get_actor_location()
                    d = math.hypot(l.x - pl.x, l.y - pl.y)
                    if d < bd:
                        best, bd = g, d
                if best is None or st['punches'] >= 30 or el > 32.0:
                    ev('stop: punches=%d' % st['punches'])
                    st['phase'] = 4
                    st['end'] = t + 2.0
                elif t >= st['pt']:
                    l = best.get_actor_location()
                    yaw = math.degrees(math.atan2(l.y - pl.y, l.x - pl.x))
                    player.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw), False)
                    if bd <= 175.0:
                        before = {g.get_name()[-3:]: round(g.get_editor_property('EnemyHealth'), 1)
                                  for g in goons()}
                        player.call_method('PlayerPunch')
                        st['punches'] += 1
                        st['pt'] = t + 0.45
                        ev('punch %d at d=%.0f hp %s' % (st['punches'], bd, before))
                    else:
                        d = unreal.Vector(l.x - pl.x, l.y - pl.y, 0.0)
                        d.normalize()
                        player.add_movement_input(d, 1.0, True)
            elif p == 4 and t >= st['end']:
                finish()
    except Exception:
        R['error'] = traceback.format_exc()
        finish()


if player is None:
    R['error'] = 'no BP_Player_C in the game world (is Play mode running?)'
    R['done'] = True
    open(OUT, 'w').write(json.dumps(R, indent=1))
else:
    handle[0] = unreal.register_slate_post_tick_callback(tick)
