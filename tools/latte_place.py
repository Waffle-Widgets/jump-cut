"""Latte shift: the level changes.   py <repo>/tools/latte_place.py [report|apply]     (Play mode stopped)
Writes Saved/jcpy/latte_place.txt.

  * Latte_Game faces the STAFF side of the counter (yaw 90): the barista pours from behind it.
  * City_Cafe_01_CafeRegister is turned round (yaw 180 -> 0) so it is worked from behind the counter.
    NOTE: jumpcut_city_place.py would turn it back - the layout row must change with it.
  * C1_Cafe_Counter is the hidden grey-box counter from Thursday. It still collides, and it walls off the only way
    round the end of the real counter (measured: a capsule from (0,-150) to (0,-340) stops at y -306). Collision off.
`report` prints each actor's package: `git lfs lock` those files and make them writable BEFORE `apply`.
"""
import os
import sys
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'latte_place.txt')
log = []
say = lambda s: log.append(str(s))
ROUTE = (('start to the end of the counter', (0, 0), (20, -150)), ('round the end', (20, -150), (20, -350)),
         ('behind the counter to the cup', (20, -350), (-285, -350)), ('on to the register', (-285, -350), (-540, -350)),
         ('up to the register', (-540, -350), (-540, -325)), ('up to the cup', (-285, -350), (-285, -325)))
try:
    mode = sys.argv[1] if len(sys.argv) > 1 else 'report'
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    W = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    by = {a.get_actor_label(): a for a in sub.get_all_level_actors()}
    todo = []
    for lab in ('Latte_Game', 'City_Cafe_01_CafeRegister', 'C1_Cafe_Counter'):
        a = by[lab]
        say('%-28s yaw %.0f collides %s hidden_in_game %s package %s' % (lab, a.get_actor_rotation().yaw, a.get_actor_enable_collision(),
                                                                         a.get_editor_property('hidden'), a.get_outermost().get_name()))
        if mode != 'apply':
            continue
        t = a.get_actor_transform()
        loc, rot = t.translation, t.rotation.rotator()
        if lab == 'Latte_Game':
            rot = unreal.Rotator(roll=0.0, pitch=0.0, yaw=90.0)
        elif lab == 'City_Cafe_01_CafeRegister':
            rot = unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0)
        else:
            if not a.get_editor_property('hidden'):
                say('   VISIBLE in game: leaving its collision alone'); continue
            a.set_actor_enable_collision(False)
        a.set_actor_transform(unreal.Transform(loc, rot, t.scale3d), False, False)        # full transform: dirties the package
        todo.append(a)
        say('   now yaw %.0f collides %s' % (a.get_actor_rotation().yaw, a.get_actor_enable_collision()))
    if todo:
        say('SAVED %s' % unreal.EditorLoadingAndSavingUtils.save_packages([a.get_outermost() for a in todo], False))
    for name, a, b in ROUTE:
        h = unreal.SystemLibrary.capsule_trace_single(W, unreal.Vector(a[0], a[1], 96), unreal.Vector(b[0], b[1], 96), 34.0, 90.0,
                                                      unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        if h is None:
            say('%-34s clear' % name)
        else:
            d = h.to_dict()
            say('%-34s BLOCKED at (%.0f %.0f) by %s initial_overlap %s' % (name, d['location'].x, d['location'].y,
                d['hit_actor'].get_actor_label() if d.get('hit_actor') else None, d.get('initial_overlap')))
except Exception:
    import traceback
    say(traceback.format_exc())
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write('\n'.join(log) + '\n')
