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
    keys = ('Shift', 'LatteActive', 'LatteDone', 'Fill', 'Pattern', 'LowTime', 'Wiggles', 'Blobs', 'CutDist', 'Ending', 'EndWin', 'PitX', 'PitY', 'PitH')
    return ' '.join('%s=%s' % (k, a.get_editor_property(k)) for k in keys)


# each plan: list of (seconds, low?, fn(u 0..1) -> (x, y)); x is up the screen, y is right, in cm from the cup's centre
def line(x0, y0, x1, y1):
    return lambda u: (x0 + (x1 - x0) * u, y0 + (y1 - y0) * u)


PLANS = {
    'blob': [(3.0, True, line(0, 0, 0, 0))],
    'right': [(2.0, True, line(2.5, 3.0, 2.5, 3.0))],          # up and to the right on screen: checks the picture is not mirrored
    'heart': [(4.5, True, line(0.5, 0, 0.5, 0)), (0.9, False, line(4.5, 0, -4.5, 0))],
    'rosetta': [(1.2, True, line(2.5, 0, 2.5, 0)),
                (5.0, True, lambda u: (2.5 - 5.5 * u, 1.6 * math.sin(u * 2 * math.pi * 7))),
                (0.9, False, line(-4.5, 0, 4.5, 0))],
    'topup': [(14.0, False, lambda u: (3.5 * math.cos(u * 40), 3.5 * math.sin(u * 40)))],       # high pour round the edge until the cup is full
    'tulip': [(2.0, True, line(1.0, 0, 1.0, 0)), (0.5, None, line(0, 0, 0, 0)),
              (1.6, True, line(-0.8, 0, 0.6, 0)), (0.5, None, line(0, 0, 0, 0)),
              (1.3, True, line(-2.4, 0, -1.2, 0)), (0.4, None, line(0, 0, 0, 0)),
              (0.9, False, line(-4.5, 0, 4.5, 0))],
}


def pour(a, name):
    plan = PLANS[name]
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
            return
        secs, low, f = plan[st['i']]
        st['t'] += dt
        u = min(1.0, st['t'] / secs)
        if st['i'] == 0 and st['t'] > 1.2 and not st.get('mid'):
            st['mid'] = True                      # one frame mid-pour, so the stream and the pitcher are in the picture
            unreal.SystemLibrary.execute_console_command(w, 'HighResShot 1280x720 filename="%slatte_%s_mid.png"' % (SAVED, name))
        if low is not None:
            x, y = f(u)
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
