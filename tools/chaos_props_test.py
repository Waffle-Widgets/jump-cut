"""Play-mode check for the breakable and knockable props. Run ONCE per PIE session, as the first script:
    py <repo>/tools/chaos_props_test.py
It presses start, checks every knockable prop came to rest on the floor where it was placed, then stands the player
in front of a plaza crate stack (far from any goon) and throws a full combo at it, and one punch at a bag of
trash. It records the size of the breakable's bounds and the prop's position either side of each punch.
Result: <project>/Saved/jcpy/chaos_test.json (marker "done": true). Nothing is saved.
"""
import json, math, os
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'chaos_test.json')
ws = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
gm = unreal.GameplayStatics.get_game_mode(ws)
R = {'events': [], 'done': False}
st = {'t': 0.0, 'phase': 0}
handle = [None]
allactors = unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.Actor)
player = [a for a in allactors if a.get_class().get_name() == 'BP_Player_C']
player = player[0] if player else None
knock = [a for a in allactors if 'JC_Knock' in [str(t) for t in a.tags]]
brk = [a for a in allactors if 'JC_Break' in [str(t) for t in a.tags]]
start = {a.get_name(): a.get_actor_location() for a in knock}


def near(lst, x, y):
    return min(lst, key=lambda a: math.hypot(a.get_actor_location().x - x, a.get_actor_location().y - y))


crate = near(brk, 6900, -1350) if brk else None
bags = near(knock, 9400, -1340) if knock else None


def ext(a):
    o, e = a.get_actor_bounds(False)
    return [round(o.x), round(o.y), round(o.z), round(e.x), round(e.y), round(e.z)]


def ev(s):
    R['events'].append('%.2f %s' % (st['t'], s))


def me():
    return 'hp=%.0f lost=%s canact=%s' % (player.get_editor_property('Health'), player.get_editor_property('IsLost'), player.call_method('PlayerCanAct'))


def stand(x, y, yaw):
    player.set_actor_location(unreal.Vector(x, y, 100.0), False, True)
    player.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw), False)


def finish():
    R['done'] = True
    with open(OUT, 'w') as fh:
        fh.write(json.dumps(R, indent=1))
    unreal.unregister_slate_post_tick_callback(handle[0])


STEPS = [
    (0.3, lambda: gm.call_method('JumpCutStartPlay')),
    (2.5, lambda: R.update(settle=[{'n': a.get_actor_label() if hasattr(a, 'get_actor_label') else a.get_name(), 'moved': round((a.get_actor_location() - start[a.get_name()]).length(), 1),
                                    'z': round(a.get_actor_location().z, 1), 'spd': round(a.get_velocity().length(), 1)} for a in knock],
                           counts={'knock': len(knock), 'break': len(brk)})),
    (2.6, lambda: (stand(crate.get_actor_location().x, crate.get_actor_location().y + 125.0, -90.0), ev('at crate %s ext=%s %s' % (crate.get_name(), ext(crate), me())))),
    (3.0, lambda: (player.call_method('PlayerPunch'), ev('punch 1 (light)'))),
    (3.05, lambda: ev('crate ext=%s' % ext(crate))),
    (3.35, lambda: ev('crate ext=%s' % ext(crate))),
    (3.4, lambda: (player.call_method('PlayerPunch'), ev('punch 2 (light)'))),
    (3.75, lambda: ev('crate ext=%s' % ext(crate))),
    (3.8, lambda: (player.call_method('PlayerPunch'), ev('punch 3 (finisher)'))),
    (4.3, lambda: ev('crate ext=%s' % ext(crate))),
    (4.7, lambda: ev('crate ext=%s' % ext(crate))),
    (5.1, lambda: ev('crate ext=%s' % ext(crate))),
    (5.5, lambda: ev('crate ext=%s %s' % (ext(crate), me()))),
    (5.6, lambda: (stand(bags.get_actor_location().x, bags.get_actor_location().y + 120.0, -90.0), ev('at bags %s loc=%s' % (bags.get_name(), bags.get_actor_location())))),
    (6.2, lambda: (ev('bags before loc=%s' % bags.get_actor_location()), player.call_method('PlayerPunch'), ev('punch at bags'))),
    (6.4, lambda: ev('bags spd=%.0f' % bags.get_velocity().length())),
    (7.0, lambda: ev('bags loc=%s spd=%.0f' % (bags.get_actor_location(), bags.get_velocity().length()))),
    (8.5, lambda: ev('bags after loc=%s spd=%.0f %s' % (bags.get_actor_location(), bags.get_velocity().length(), me()))),
    (8.6, finish),
]


def tick(dt):
    try:
        st['t'] += dt
        while st['phase'] < len(STEPS) and st['t'] >= STEPS[st['phase']][0]:
            f = STEPS[st['phase']][1]
            st['phase'] += 1
            f()
    except Exception:
        import traceback
        R['error'] = traceback.format_exc()
        finish()


if player is None or crate is None or bags is None:
    R['error'] = 'missing: player=%s crate=%s bags=%s (is Play mode running?)' % (player, crate, bags)
    R['done'] = True
    open(OUT, 'w').write(json.dumps(R))
else:
    handle[0] = unreal.register_slate_post_tick_callback(tick)
