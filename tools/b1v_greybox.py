"""The hidden grey-box crash-car placeholders still COLLIDE, and they wall off the cafe floor.

    py <repo>/tools/b1v_greybox.py           report only
    py <repo>/tools/b1v_greybox.py apply     switch collision off on the hidden ones

C1_Cafe_Car (200 x 100 x 75 at (-520, 0, 75)) and C1_Cafe_CarCab are the grey boxes from the
Thursday grey-box build. They are hidden in game, the REAL wreck (City_CafeCrashCar) carries
complex-as-simple collision of its own, and these boxes stick out past it - so all they do is
put an invisible wall across the cafe. Measured 2026-11-15: a player capsule sweep from past the
driver's body to the coworker's new spot on the car's +Y side is stopped by C1_Cafe_Car, and
every spot deeper than x = -460 on that side is unreachable.

Per CLAUDE.md: it must be the ACTOR property (component collision does not serialize), and the
full transform has to be re-set afterwards or the package is not dirtied and the change lives
only in memory. Save with tools/jc_save_actors.py, after git lfs lock.
"""
import unreal, os, sys, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
MODE = sys.argv[1] if len(sys.argv) > 1 else 'report'
WANT = ('C1_Cafe_Car', 'C1_Cafe_CarCab')
L = []; res = {}
def say(s):
    L.append(str(s)); print(str(s))

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    if ues.get_game_world() is not None:
        raise RuntimeError('PIE is running - stop it first')
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    by = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
    for lab in WANT:
        a = by.get(lab)
        if a is None:
            say('%-18s MISSING' % lab); continue
        o, e = a.get_actor_bounds(False)
        d = {'hidden_in_game': a.get_editor_property('hidden'),
             'collides': a.get_actor_enable_collision(),
             'origin': [round(o.x, 1), round(o.y, 1), round(o.z, 1)],
             'extent': [round(e.x, 1), round(e.y, 1), round(e.z, 1)],
             'package': a.get_outermost().get_name()}
        if MODE == 'apply':
            if not d['hidden_in_game']:
                say('%-18s is VISIBLE in game - refusing to touch its collision' % lab)
                res[lab] = d
                continue
            a.set_actor_enable_collision(False)
            xf = a.get_actor_transform()
            a.set_actor_location_and_rotation(xf.translation, xf.rotation.rotator(), False, True)
            a.set_actor_scale3d(xf.scale3d)
            d['collides_after'] = a.get_actor_enable_collision()
        res[lab] = d
        say('%-18s %s' % (lab, json.dumps(d)))

    # prove it: the sweep that was blocked
    w = ues.get_editor_world()
    HH, RR = 90.0, 35.0
    hit = unreal.SystemLibrary.capsule_trace_single(
        w, unreal.Vector(-240.0, -40.0, 94.0), unreal.Vector(-440.0, 200.0, 94.0), RR, HH,
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [by['C1_Cafe_CrashDriver']],
        unreal.DrawDebugTrace.NONE, True)
    if hit is None:
        res['sweep_past_body_to_coworker'] = 'CLEAR'
    else:
        ha = hit.to_dict().get('hit_actor')
        res['sweep_past_body_to_coworker'] = 'blocked by %s' % (ha.get_actor_label() if ha else '?')
    say('sweep past the body -> the coworker: %s' % res['sweep_past_body_to_coworker'])
except Exception as e:
    say('ERROR %r' % e); say(traceback.format_exc()); res['error'] = repr(e)

with open(os.path.join(OUT, 'b1v_greybox.txt'), 'w') as fh:
    fh.write('\n'.join(L))
with open(os.path.join(OUT, 'b1v_greybox.json'), 'w') as fh:
    json.dump(res, fh, indent=1, default=str)
print('b1v_greybox %s done' % MODE)
