"""Latte shift: look at the cafe before changing it. Changes nothing.   py <repo>/tools/latte_scout.py
Writes Saved/jcpy/latte_scout.txt: what stands near the counter, and capsule sweeps along the barista's route.
"""
import os
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'latte_scout.txt')
log = []
say = lambda s: log.append(str(s))
try:
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    W = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for a in sub.get_all_level_actors():
        l = a.get_actor_location()
        if -760 < l.x < 160 and -560 < l.y < -120:
            o, e = a.get_actor_bounds(True)
            if e.x > 600 or e.y > 600:
                continue
            say('%-34s loc (%5.0f %5.0f %4.0f) yaw %4.0f box x %5.0f..%5.0f y %5.0f..%5.0f z %4.0f..%4.0f coll %s hidden %s' % (
                a.get_actor_label()[:34], l.x, l.y, l.z, a.get_actor_rotation().yaw, o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y,
                o.z - e.z, o.z + e.z, a.get_actor_enable_collision(), a.is_hidden_ed()))

    def sweep(a, b):
        h = unreal.SystemLibrary.capsule_trace_single(W, unreal.Vector(a[0], a[1], 96), unreal.Vector(b[0], b[1], 96), 34.0, 90.0,
                                                      unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        if h is None:
            return 'clear'
        d = h.to_dict()
        act = d.get('hit_actor')
        return 'BLOCKED at (%.0f %.0f) by %s initial_overlap %s' % (d['location'].x, d['location'].y, act.get_actor_label() if act else None, d.get('initial_overlap'))

    def floor(x, y):
        h = unreal.SystemLibrary.line_trace_single(W, unreal.Vector(x, y, 200), unreal.Vector(x, y, -100), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                   False, [], unreal.DrawDebugTrace.NONE, True)
        if h is None:
            return 'none'
        d = h.to_dict()
        return '%.0f (%s)' % (d['location'].z, d['hit_actor'].get_actor_label() if d.get('hit_actor') else None)

    for y in (-320, -340, -360, -380, -400, -440):
        say('floor at x -300 y %d: %s | x -540: %s | x -40: %s | x 40: %s' % (y, floor(-300, y), floor(-540, y), floor(-40, y), floor(40, y)))
    for name, a, b in (('start -> right end, customer side', (0, 0), (0, -150)),
                       ('round the right end', (0, -150), (0, -340)),
                       ('round the right end, wider', (40, -150), (40, -340)),
                       ('behind the counter to the register y -340', (0, -340), (-540, -340)),
                       ('behind the counter to the register y -360', (0, -360), (-540, -360)),
                       ('behind the counter to the register y -320', (0, -320), (-540, -320)),
                       ('left end round', (-640, -150), (-640, -340)),
                       ('left end in', (-640, -340), (-540, -340))):
        say('%-46s %s' % (name, sweep(a, b)))
except Exception:
    import traceback
    say(traceback.format_exc())
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write('\n'.join(log) + '\n')
