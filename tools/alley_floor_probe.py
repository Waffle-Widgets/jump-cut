"""#78: is the back alley a place you can stand in, or scenery you can fall out of?

Run through the editor console box:  py <repo>/tools/alley_floor_probe.py
Writes JumpCut/Saved/jcpy/alley_probe.txt

READ-ONLY. It traces and measures; it places and saves nothing.

Three questions, in the order #78 asks them:
  1. How far west does the walkable floor actually reach?
  2. Can the player get through the hole the car made in the west wall?
  3. If he can, what is out there - and where does the world end?

Trace discipline (CLAUDE.md): start a downward trace BELOW anything overhead. Tracing
from z=300 through a ceiling that occupies 215-350 begins inside the collider and
reported a floor where there was a gap. The cafe ceiling is at ~310, so the in-room
probes start at z=180, under the ceiling and over the player's head height is not
needed - we only need to be under the ceiling and above the floor.
"""
import os, sys, traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'alley_probe.txt')
out = []
def P(*a): out.append(' '.join(str(x) for x in a))

UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def flush():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


def trace_down(world, x, y, z_start, z_end=-500.0):
    """Returns (hit_z, actor_label, component_name) or None."""
    s = unreal.Vector(x, y, z_start)
    e = unreal.Vector(x, y, z_end)
    hit = unreal.SystemLibrary.line_trace_single(
        world, s, e, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [],
        unreal.DrawDebugTrace.NONE, True)
    if not hit:
        return None
    # UE 5.8 trap: every HitResult field is PROTECTED, so get_editor_property('location')
    # raises, and there is no GameplayStatics.break_hit_result in Python. to_dict() is the
    # only route that works.
    d = hit.to_dict()
    loc, a, c = d['location'], d['hit_actor'], d['hit_component']
    return (loc.z,
            str(a.get_actor_label()) if a else '?',
            str(c.get_name()) if c else '?')


def main():
    w = UES.get_editor_world()
    P('WORLD', w.get_path_name())
    actors = EAS.get_all_level_actors()
    P('ACTOR_COUNT', len(actors))

    # ---- 1. the floor actors and their real world bounds
    P('')
    P('=== FLOOR ACTORS (label contains Floor / Pave / Road / Slab) ===')
    floors = []
    for a in actors:
        lbl = str(a.get_actor_label())
        if any(k in lbl for k in ('Floor', 'Pave', 'Road', 'Slab', 'Ground', 'Plaza')):
            o, ext = a.get_actor_bounds(False)
            floors.append((lbl, o, ext))
    for lbl, o, ext in sorted(floors, key=lambda r: r[1].x - r[2].x):
        P('  %-28s x %9.1f .. %9.1f   y %9.1f .. %9.1f   top z %8.1f'
          % (lbl, o.x - ext.x, o.x + ext.x, o.y - ext.y, o.y + ext.y, o.z + ext.z))
    if floors:
        wx = min(o.x - ext.x for _, o, ext in floors)
        ex = max(o.x + ext.x for _, o, ext in floors)
        P('  FLOOR SPAN X: %.1f .. %.1f' % (wx, ex))

    # ---- 2. trace a west-going line down the alley centre
    P('')
    P('=== DOWNWARD TRACES along the alley, y = 0 (alley centre) ===')
    P('  (start z = 180: under the cafe ceiling at ~310, above any floor)')
    gaps = []
    for x in range(400, -3400, -100):
        r = trace_down(w, float(x), 0.0, 180.0)
        if r is None:
            gaps.append(x)
            P('  x %6d   NO FLOOR' % x)
        else:
            P('  x %6d   z %7.1f   %s / %s' % (x, r[0], r[1], r[2]))
    P('  GAP COUNT: %d' % len(gaps))
    if gaps:
        P('  FIRST GAP AT x = %d   LAST GAP AT x = %d' % (gaps[0], gaps[-1]))

    # ---- 3. across the alley at a few depths, to find its walkable width
    P('')
    P('=== CROSS-SECTIONS (y sweep) ===')
    for x in (-200, -700, -1400, -2200, -3000):
        row = []
        for y in range(-600, 700, 100):
            r = trace_down(w, float(x), float(y), 180.0)
            row.append('.' if r else 'X')
        P('  x %6d  y -600..+600: %s   (. = floor, X = void)' % (x, ''.join(row)))

    # ---- 4. the hole in the west wall: can a 42 cm capsule get through?
    P('')
    P('=== THE HOLE (west wall). Horizontal traces at the player capsule height ===')
    # cafe west wall is near x = -630 in level terms; sweep a band to find it
    for z in (20.0, 60.0, 100.0, 140.0, 180.0):
        row = []
        for y in range(-400, 500, 50):
            s = unreal.Vector(300.0, float(y), z)
            e = unreal.Vector(-1600.0, float(y), z)
            hit = unreal.SystemLibrary.line_trace_single(
                w, s, e, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [],
                unreal.DrawDebugTrace.NONE, True)
            if hit:
                loc = hit.to_dict()['location']
                row.append('%d' % min(9, int((300.0 - loc.x) / 200.0)))
            else:
                row.append('-')
        P('  z %5.0f  y -400..+450: %s   (- = clear all the way west)' % (z, ''.join(row)))

    # ---- 5. what actors are actually out there
    P('')
    P('=== ACTORS WEST OF x = -700 ===')
    west = []
    for a in actors:
        loc = a.get_actor_location()
        if loc.x < -700:
            west.append((loc.x, str(a.get_actor_label())))
    for x, lbl in sorted(west)[:60]:
        P('  x %8.1f  %s' % (x, lbl))
    P('  WEST ACTOR COUNT: %d' % len(west))

    # ---- 6. blocking volumes anywhere
    P('')
    P('=== BLOCKING VOLUMES ===')
    nb = 0
    for a in actors:
        if isinstance(a, unreal.BlockingVolume) or 'Blocking' in str(a.get_actor_label()):
            o, ext = a.get_actor_bounds(False)
            P('  %-28s x %9.1f .. %9.1f  y %9.1f .. %9.1f' % (
                a.get_actor_label(), o.x - ext.x, o.x + ext.x, o.y - ext.y, o.y + ext.y))
            nb += 1
    P('  BLOCKING VOLUME COUNT: %d' % nb)


try:
    main()
except Exception:
    P('EXCEPTION')
    P(traceback.format_exc())
flush()
print('wrote', OUT)
