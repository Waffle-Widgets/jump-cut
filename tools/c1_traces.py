"""C1: line + sphere traces along the route at chest height. Works in the editor world or the PIE world (PIE if running).
    py C:/Users/thecl/code/jump-cut/tools/c1_traces.py
Writes Saved/c1_traces.txt (appends). 'hit' lines name what blocked."""
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())
log = []
try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = ues.get_game_world() or ues.get_editor_world()
    log.append('--- world %s (%s)' % (world.get_name(), 'PIE' if ues.get_game_world() else 'editor'))
    SL = unreal.SystemLibrary

    def trace(name, x0, x1, y=0.0, z=130.0, sphere=0.0, y1=None):
        a, b = unreal.Vector(x0, y, z), unreal.Vector(x1, y if y1 is None else y1, z)
        if sphere:
            hit = SL.sphere_trace_single(world, a, b, sphere, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [],
                                         unreal.DrawDebugTrace.NONE, True)
        else:
            hit = SL.line_trace_single(world, a, b, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [],
                                       unreal.DrawDebugTrace.NONE, True)
        # hit is (bool, HitResult)? depending on binding
        res = hit
        try:
            ok = bool(res[0]) if isinstance(res, tuple) else bool(res)
            hr = res[1] if isinstance(res, tuple) else None
        except Exception:
            ok, hr = False, None
        who = ''
        if ok and hr is not None:
            d = hr.to_tuple()
            who = ' by %s at x=%.0f' % (hr.get_editor_property('hit_object_handle').fetch_actor().get_actor_label()
                                        if hasattr(hr.get_editor_property('hit_object_handle'), 'fetch_actor') else '?',
                                        hr.get_editor_property('location').x)
        log.append('%s%s: %s%s' % (name, ' (sphere r=%d)' % sphere if sphere else '', 'HIT' if ok else 'clear', who))

    for sph in (0.0, 34.0):
        zz = 130.0 if not sph else 100.0
        trace('cafe -> door', 0, 700, z=zz, sphere=sph)
        trace('door -> street end (before gate)', 700, 6500, z=zz, sphere=sph)
        trace('entry gate segment 6500->6740', 6500, 6740, z=zz, sphere=sph)
        trace('plaza 6740 -> 9500', 6740, 9500, z=zz, sphere=sph)
        trace('exit gate segment 9500->9740', 9500, 9740, z=zz, sphere=sph)
        trace('exit run 9740 -> Marker_Win 10220 -> end 10600', 9740, 10600, z=zz, sphere=sph)
    # sanity: walls really block sideways
    trace('across street y 0 -> 1200 at x=3000 (must HIT)', 3000, 3000, y=0.0, y1=1200.0)
    trace('through cafe wall y 0 -> 800 at x=-300 (must HIT)', -300, -300, y=0.0, y1=800.0)
except Exception as e:
    log.append('ERROR: %r' % e)
with open(ROOT + 'c1_traces.txt', 'a') as f:
    f.write('\n'.join(log) + '\n')
