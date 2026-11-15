"""Latte-art mini game, poured by a script in Play mode (a script cannot hold a mouse button). Changes no assets.

    py <repo>/tools/latte_pie.py begin            leave the title: the mini game should take the camera
    py <repo>/tools/latte_pie.py pour heart       pour that pattern through the game's own LattePour, then screenshot
    py <repo>/tools/latte_pie.py pour rosetta | tulip | blob
    py <repo>/tools/latte_pie.py state            print the game's counters
Writes Saved/jcpy/latte_pie.txt and Saved/latte_<pattern>_NN.png.

The pitcher is moved with LatteDebugMove and the milk poured with LattePour - the same function the mouse drives -
from a Slate post-tick callback, one call per frame, because an MCP round trip is far slower than a pour.
"""
import math
import os
import sys
import builtins
import unreal

SAVED = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())
OUT = os.path.join(SAVED, 'jcpy', 'latte_pie.txt')
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
GS = unreal.GameplayStatics
log = []


def say(s):
    log.append(str(s))


def latte(w):
    for a in GS.get_all_actors_of_class(w, unreal.Actor):
        if a.get_class().get_name() == 'BP_LatteGame_C':
            return a
    return None


def state(a):
    keys = ('Match', 'Shift', 'LatteActive', 'LatteDone', 'Fill', 'Pattern', 'LowTime', 'Wiggles', 'Blobs', 'CutDist', 'Ending', 'EndWin', 'PitX', 'PitY', 'PitH')
    return ' '.join('%s=%s' % (k, a.get_editor_property(k)) for k in keys)


# each plan: list of (seconds, low?, fn(u 0..1) -> (x, y)); x is up the screen, y is right, in cm from the cup's centre
def line(x0, y0, x1, y1):
    return lambda u: (x0 + (x1 - x0) * u, y0 + (y1 - y0) * u)


PLANS = {
    'blob': [(3.0, True, line(0, 0, 0, 0))],
    'right': [(2.0, True, line(2.5, 3.0, 2.5, 3.0))],          # up and to the right on screen: checks the picture is not mirrored
    'heart': [(4.0, True, line(1.0, 0, 1.0, 0)), (0.3, None, line(0, 0, 0, 0)), (0.8, False, line(4.5, 0, -3.5, 0))],
    # rosetta: a wide base at the far side, leaves that narrow as you pull back, a small heart at the near end,
    # then the cut back up through all of it (the stem)
    'rosetta': [(0.6, True, line(-2.6, 0, -2.6, 0)),
                (5.0, True, lambda u: (-2.6 + 5.4 * u, (1.3 - 0.7 * u) * math.sin(u * 2 * math.pi * 6))),
                (0.75, True, line(3.1, 0, 3.1, 0)),
                (0.25, None, line(0, 0, 0, 0)),
                (0.8, False, line(4.4, 0, -3.4, 0))],
    'topup': [(14.0, False, lambda u: (3.5 * math.cos(u * 40), 3.5 * math.sin(u * 40)))],       # high pour round the edge until the cup is full
    # tulip: each layer is poured BEHIND the last and pushed up into it, and each is smaller, so a layer dents the
    # one before it instead of swallowing it
    'tulip': [(2.2, True, line(-1.2, 0, -1.8, 0)), (0.45, None, line(0, 0, 0, 0)),
              (1.5, True, line(1.0, 0, -0.1, 0)), (0.45, None, line(0, 0, 0, 0)),
              (1.0, True, line(3.2, 0, 2.4, 0)), (0.35, None, line(0, 0, 0, 0)),
              (0.8, False, line(4.6, 0, -3.6, 0))],
}


def dump(w, a, name):
    """Read the cup's surface back out of the game as a 64 x 64 grid of foam values -> Saved/jcpy/latte_cup_<name>.txt,
    one row of digits 0-9 per line, row = v (right on screen), column = u (up the screen)."""
    try:
        latest = 'RT_LatteA' if a.get_editor_property('FlipA') else 'RT_LatteB'
        rt = unreal.load_asset('/Game/Game/Materials/Latte/' + latest)
        px = unreal.RenderingLibrary.read_render_target_raw_uv_area(w, rt, unreal.Box2D(unreal.Vector2D(0, 0), unreal.Vector2D(1, 1)), True)
        n = int(round(len(px) ** 0.5))
        rows = []
        for gv in range(64):
            row = ''
            for gu in range(64):
                c = px[int((gv + 0.5) * n / 64) * n + int((gu + 0.5) * n / 64)]
                row += str(max(0, min(9, int(c.r * 9.999))))
            rows.append(row)
        NL = chr(10)
        open(os.path.join(SAVED, 'jcpy', 'latte_cup_%s.txt' % name), 'w').write(NL.join(rows) + NL)
        open(OUT, 'a').write('DUMP %s from %s (%d px)' % (name, latest, len(px)) + NL)
    except Exception:
        import traceback
        open(OUT, 'a').write('DUMP FAILED %s' % traceback.format_exc() + chr(10))


def pour(a, name, queue=None):
    plan = PLANS[name]
    if name in ('heart', 'rosetta', 'tulip'):          # a fresh cup OF THAT PATTERN, so the guide and the meter are its own
        a.call_method('LattePick', (('heart', 'rosetta', 'tulip').index(name),))
    st = {'i': 0, 't': 0.0, 'shots': 0, 'after': 0.0, 'py': 0.0}

    def tick(dt):
        w = UES.get_game_world()
        if w is None:
            unreal.unregister_slate_post_tick_callback(builtins._latte_pour); return
        b = latte(w)
        dt = min(dt, 0.05)
        if st['i'] >= len(plan):
            st['after'] += dt
            if st['shots'] == 0 and st['after'] > 0.3:
                st['shots'] = 1
                unreal.SystemLibrary.execute_console_command(w, 'HighResShot 1280x720 filename="%slatte_%s_01.png"' % (SAVED, name))
            if st['after'] > 1.0:
                unreal.unregister_slate_post_tick_callback(builtins._latte_pour)
                open(OUT, 'a').write('POURED %s: %s\n' % (name, state(b)))
                dump(w, b, name)
                if queue:                         # the next pattern, on a fresh cup
                    pour(b, queue[0], queue[1:])
            return
        secs, low, f = plan[st['i']]
        st['t'] += dt
        u = min(1.0, st['t'] / secs)
        if st['i'] == 0 and st['t'] > 1.2 and not st.get('mid'):
            st['mid'] = True                      # one frame mid-pour, so the stream and the pitcher are in the picture
            unreal.SystemLibrary.execute_console_command(w, 'HighResShot 1280x720 filename="%slatte_%s_mid.png"' % (SAVED, name))
        if low is not None:
            x, y = f(u)
            if st.get('seg') != st['i']:
                st['seg'] = st['i']                # a new stroke: arrive first, or the jump itself counts as a drag
                b.call_method('LatteDebugMove', (x, y))
            b.call_method('LatteDebugMove', (x, y))
            b.call_method('LattePour', (dt, bool(low), (y - st['py']) / 0.012))
            st['py'] = y
        if u >= 1.0:
            st['i'] += 1; st['t'] = 0.0
    builtins._latte_pour = unreal.register_slate_post_tick_callback(tick)


try:
    W = UES.get_game_world()
    mode = sys.argv[1] if len(sys.argv) > 1 else 'state'
    if W is None:
        say('NO GAME WORLD')
    else:
        a = latte(W)
        if a is None:
            say('NO BP_LatteGame in the game world')
        elif mode == 'begin':
            gm = GS.get_game_mode(W)
            gm.call_method('JumpCutStartPlay')
            p = GS.get_player_character(W, 0)
            say('BEGIN FlowState %s  player InputLocked %s  view target %s' % (
                gm.get_editor_property('FlowState'), p.get_editor_property('InputLocked'),
                GS.get_player_controller(W, 0).get_view_target().get_name()))
            say(state(a))
        elif mode == 'call':                      # call <function>: LatteStartPour, LatteClockOut (a script cannot press E)
            a.call_method(sys.argv[2]); say('CALL %s: %s' % (sys.argv[2], state(a)))
        elif mode == 'tp':                        # tp <x> <y> [yaw]: stand the player there
            p = GS.get_player_character(W, 0)
            p.set_actor_location(unreal.Vector(float(sys.argv[2]), float(sys.argv[3]), p.get_actor_location().z), False, True)
            if len(sys.argv) > 4:
                GS.get_player_controller(W, 0).set_control_rotation(unreal.Rotator(roll=0, pitch=-5, yaw=float(sys.argv[4])))
            say('TP %s' % p.get_actor_location())
        elif mode == 'shot':                      # shot <name>: the game view to Saved/latte_<name>.png
            unreal.SystemLibrary.execute_console_command(W, 'HighResShot 1280x720 filename="%slatte_%s.png"' % (SAVED, sys.argv[2]))
            say('SHOT %s' % sys.argv[2])
        elif mode == 'auto':                      # auto <pattern>: leave the title, start the pour and pour it, in one go
            GS.get_game_mode(W).call_method('JumpCutStartPlay')
            a.call_method('LatteStartPour')
            say('AUTO %s start: %s' % (sys.argv[2], state(a)))
            pour(a, sys.argv[2])
        elif mode == 'pattern':                   # pattern <0|1|2>: fresh cups until that pattern comes up, then a screenshot
            want = int(sys.argv[2])
            for _ in range(60):
                if a.get_editor_property('Pattern') == want:
                    break
                a.call_method('LatteReset')
            say('PATTERN %s: %s' % (want, state(a)))
            unreal.SystemLibrary.execute_console_command(W, 'HighResShot 1280x720 filename="%slatte_pattern_%d.png"' % (SAVED, want))
        elif mode == 'all':                       # leave the title and pour heart, rosetta and tulip, reading each cup back
            GS.get_game_mode(W).call_method('JumpCutStartPlay')
            a.call_method('LatteStartPour')
            pour(a, 'heart', ['rosetta', 'tulip'])
            say('ALL started')
        elif mode == 'near':                      # near <x> <y> <radius>: what is VISIBLE in the running game round that spot
            cx, cy, rad = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
            rows = []
            for o in GS.get_all_actors_of_class(W, unreal.Actor):
                l = o.get_actor_location()
                if (l.x - cx) ** 2 + (l.y - cy) ** 2 > rad * rad or o.get_editor_property('hidden'):
                    continue
                prims = [c for c in o.get_components_by_class(unreal.PrimitiveComponent) if c.is_visible()]
                if not prims:
                    continue
                try: lab = o.get_actor_label()
                except Exception: lab = o.get_name()
                rows.append('%-34s %-30s (%.0f %.0f %.0f) tags %s' % (lab[:34], o.get_class().get_name()[:30], l.x, l.y, l.z, [str(t) for t in o.tags]))
            say('NEAR (%s, %s) r %s: %d visible' % (cx, cy, rad, len(rows)))
            for r_ in sorted(rows): say('  ' + r_)
        elif mode == 'wall':                      # the breakable wall and car: where their pieces are right now
            for o in GS.get_all_actors_of_class(W, unreal.Actor):
                if o.get_class().get_name() == 'GeometryCollectionActor' and (len(sys.argv) > 2 or 'B1_Cine' in [str(t) for t in o.tags]):
                    c = o.get_components_by_class(unreal.PrimitiveComponent)[0]
                    org, ext = o.get_actor_bounds(False)
                    try: ot = c.get_editor_property('object_type')
                    except Exception: ot = '?'
                    say('WALL %-26s tags %s hidden %s type %s box x %.0f..%.0f y %.0f..%.0f z %.0f..%.0f' % (o.get_actor_label(), [str(t) for t in o.tags], o.get_editor_property('hidden'), ot,
                        org.x - ext.x, org.x + ext.x, org.y - ext.y, org.y + ext.y, org.z - ext.z, org.z + ext.z))
        elif mode == 'small':                     # small <x0> <x1> <y0> <y1>: small visible things on the floor in that box, by BOUNDS
            x0, x1, y0, y1 = [float(v) for v in sys.argv[2:6]]
            n = 0
            for o in GS.get_all_actors_of_class(W, unreal.Actor):
                if o.get_editor_property('hidden'):
                    continue
                for c in o.get_components_by_class(unreal.PrimitiveComponent):
                    if not c.is_visible():
                        continue
                    b = c.get_editor_property('bounds') if False else None
                    org, ext, rad = unreal.SystemLibrary.get_component_bounds(c)
                    if x0 <= org.x <= x1 and y0 <= org.y <= y1 and org.z < 45 and ext.z < 30 and max(ext.x, ext.y) < 90:
                        try: lab = o.get_actor_label()
                        except Exception: lab = o.get_name()
                        say('SMALL %-30s %-26s %-22s at (%.0f %.0f %.0f) half (%.0f %.0f %.0f) tags %s' % (lab[:30], o.get_class().get_name()[:26], c.get_name()[:22],
                            org.x, org.y, org.z, ext.x, ext.y, ext.z, [str(t) for t in o.tags]))
                        n += 1
            say('SMALL total %d' % n)
        elif mode == 'who':                       # who <x> <y> <z>: every component whose bounds reach that point, hidden or not
            px, py, pz = [float(v) for v in sys.argv[2:5]]
            for o in GS.get_all_actors_of_class(W, unreal.Actor):
                for c in o.get_components_by_class(unreal.PrimitiveComponent):
                    org, ext, rad = unreal.SystemLibrary.get_component_bounds(c)
                    if max(ext.x, ext.y) > 600:
                        continue
                    if abs(org.x - px) <= ext.x + 60 and abs(org.y - py) <= ext.y + 60 and abs(org.z - pz) <= ext.z + 60:
                        try: lab = o.get_actor_label()
                        except Exception: lab = o.get_name()
                        say('WHO %-28s %-24s %-26s half (%.0f %.0f %.0f) actorHidden %s compVisible %s' % (lab[:28], o.get_class().get_name()[:24], c.get_class().get_name()[:26],
                            ext.x, ext.y, ext.z, o.get_editor_property('hidden'), c.is_visible()))
            say('WHO end')
        elif mode == 'hide':                      # hide <label>: hide that actor in the running game (to see what a thing is made of)
            for o in GS.get_all_actors_of_class(W, unreal.Actor):
                try: lab = o.get_actor_label()
                except Exception: lab = ''
                if lab == sys.argv[2]:
                    o.set_actor_hidden_in_game(True); say('HID %s' % lab)
        elif mode == 'fx':                        # fx: every Niagara component, and anything named like debris
            for o in GS.get_all_actors_of_class(W, unreal.Actor):
                try: lab = o.get_actor_label()
                except Exception: lab = o.get_name()
                l = o.get_actor_location()
                for c in o.get_components_by_class(unreal.ActorComponent):
                    cn = c.get_class().get_name()
                    if 'Niagara' in cn or 'Particle' in cn or 'Instanced' in cn:
                        extra = ''
                        try: extra = 'active %s asset %s' % (c.is_active(), c.get_editor_property('asset').get_name() if cn.startswith('Niagara') and c.get_editor_property('asset') else '')
                        except Exception as e: extra = str(e)[:40]
                        say('FX %-28s %-22s %-24s at (%.0f %.0f %.0f) hidden %s %s' % (lab[:28], o.get_class().get_name()[:22], cn[:24], l.x, l.y, l.z, o.get_editor_property('hidden'), extra))
                if any(w in (lab + o.get_class().get_name()).lower() for w in ('shrap', 'debris', 'rubble', 'brick', 'chunk')):
                    say('FX-NAME %-28s %-22s at (%.0f %.0f %.0f) hidden %s comps %s' % (lab[:28], o.get_class().get_name()[:22], l.x, l.y, l.z, o.get_editor_property('hidden'),
                        [c.get_class().get_name() for c in o.get_components_by_class(unreal.PrimitiveComponent)][:4]))
            say('FX end')
        elif mode == 'shotui':                    # the game view WITH its on-screen text (HighResShot leaves UMG out)
            unreal.SystemLibrary.execute_console_command(W, 'Screenshot showui')
            say('SHOTUI')
        elif mode == 'pour':
            say('POUR %s start: %s' % (sys.argv[2], state(a)))
            pour(a, sys.argv[2])
        else:
            p = GS.get_player_character(W, 0)
            for d in GS.get_all_actors_of_class(W, unreal.Actor):
                if d.get_class().get_name() == 'BP_OpeningDirector_C':
                    say('DIRECTOR ' + ' '.join('%s=%s' % (k, d.get_editor_property(k)) for k in ('CinePlayOpening', 'CineRunning', 'CineDone', 'CineTime', 'ObjectiveState')))
            cm = GS.get_player_camera_manager(W, 0)
            say('CAMERA at %s rot %s' % (cm.get_camera_location(), cm.get_camera_rotation()))
            say('LATTE actor at %s  FlowState %s' % (a.get_actor_location(), GS.get_game_mode(W).get_editor_property('FlowState')))
            say('STATE %s | player InputLocked %s | view %s' % (state(a), p.get_editor_property('InputLocked'), GS.get_player_controller(W, 0).get_view_target().get_name()))
except Exception:
    import traceback
    say(traceback.format_exc())
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'a', encoding='utf-8').write('\n'.join(log) + '\n')
