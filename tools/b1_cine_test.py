"""Drive and measure the beat-1 opening cinematic.

    py <repo>/tools/b1_cine_test.py titleoff   ShowTitleOnStart = false on the game mode CDO
    py <repo>/tools/b1_cine_test.py titleon    put it back (ALWAYS do this when finished)
    py <repo>/tools/b1_cine_test.py state      read the LIVE PIE actors - appends to b1_cine_state.txt

A simulated key press cannot drive the title screen (the game polls IsInputKeyDown once a tick and
SlateInspector.PressKey presses and releases inside one call), so `titleoff` is the only way a
script gets into play. See CLAUDE.md.
"""
import unreal, os, sys, time

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
GM = '/Game/Game/Blueprints/BP_JumpCutGameMode.BP_JumpCutGameMode'
MODE = sys.argv[1] if len(sys.argv) > 1 else 'state'
lines = []
def say(s):
    lines.append(str(s)); print(str(s))

try:
    if MODE in ('titleoff', 'titleon'):
        cls = unreal.load_class(None, GM + '_C')
        cdo = unreal.get_default_object(cls)
        want = (MODE == 'titleon')
        cdo.set_editor_property('ShowTitleOnStart', want)
        say('ShowTitleOnStart = %s (read back %s)' % (want, cdo.get_editor_property('ShowTitleOnStart')))
    else:
        ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        gw = ues.get_game_world()
        if gw is None:
            say('NO PIE WORLD')
        else:
            t = unreal.GameplayStatics.get_time_seconds(gw)
            say('--- t=%.2f  world=%s' % (t, gw.get_name()))
            for a in unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.Actor):
                lab = a.get_actor_label()
                cn = a.get_class().get_name()
                if cn == 'BP_OpeningDirector_C':
                    say('  director  running=%s done=%s time=%.2f objState=%s' % (
                        a.get_editor_property('CineRunning'), a.get_editor_property('CineDone'),
                        a.get_editor_property('CineTime'), a.get_editor_property('ObjectiveState')))
                elif cn == 'BP_Player_C':
                    say('  player    loc=%s inputLocked=%s moveLocked=%s hasFF=%s' % (
                        a.get_actor_location(), a.get_editor_property('InputLocked'),
                        a.get_editor_property('MoveLocked'), a.get_editor_property('HasFreezeFrame')))
                elif cn == 'LevelSequenceActor':
                    p = None
                    for acc in ('sequence_player',):
                        try:
                            p = a.get_editor_property(acc)
                        except Exception:
                            pass
                    if p is None:
                        try:
                            p = a.get_sequence_player()
                        except Exception as e:
                            say('  sequence  <no player accessor: %s>' % type(e).__name__)
                    if p:
                        try:
                            say('  sequence  playing=%s current=%s' % (p.is_playing(), p.get_current_time().time.frame_number.value))
                        except Exception as e:
                            say('  sequence  playing=%s (time unread: %s)' % (p.is_playing(), e))
                elif lab.startswith('City_CafeCrashCar') or lab.startswith('C1_Cafe_CrashDriver') \
                        or lab.startswith('B1_Cine_WallPatch') or lab.startswith('B1_Objective_Beacon'):
                    say('  %-24s hidden=%-6s loc=%s' % (lab, a.get_editor_property('hidden'),
                                                        a.get_actor_location()))
            # what the sequence spawned
            n = 0
            for a in unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.Actor):
                nm = a.get_name()
                if 'CineCar' in nm or 'CineDriver' in nm or 'CineCam' in nm:
                    say('  spawned   %-26s loc=%s' % (nm, a.get_actor_location()))
                    n += 1
            say('  (%d sequence spawnables alive)' % n)
            pc = unreal.GameplayStatics.get_player_controller(gw, 0)
            if pc:
                vt = pc.get_view_target()
                say('  view target: %s' % (vt.get_name() if vt else None))
except Exception as e:
    import traceback
    say('ERROR %r' % e); say(traceback.format_exc())

path = os.path.join(OUT, 'b1_cine_state.txt')
mode = 'a' if MODE == 'state' else 'w'
with open(path, mode) as fh:
    fh.write('\n'.join(lines) + '\n')
