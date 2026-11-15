"""Drive beat 1's fire hazard in a live PIE session by writing the state a key press would set.

    py <repo>/tools/b1_fire_test.py state       report everything
    py <repo>/tools/b1_fire_test.py move <x> [y]   teleport the player
    py <repo>/tools/b1_fire_test.py touch       BP_CrashDriver.DriverTryTouch  (what F does)
    py <repo>/tools/b1_fire_test.py freeze      BP_Player.FreezeFrameStart     (what E does)
    py <repo>/tools/b1_fire_test.py unfreeze    BP_Player.PlayerFreezeFrameEnd
    py <repo>/tools/b1_fire_test.py rescue      BP_Coworker.CoworkerTryRescue  (what F on her does)
    py <repo>/tools/b1_fire_test.py burn        BP_Coworker.CoworkerBlastNow   (end the fuse now)

A simulated key press cannot drive anything we poll (CLAUDE.md), so this calls the very functions
the key polls would have called - `Object.call_method` reaches a BlueprintCallable UFunction, which
is better than writing state, because most of these variables are not instance-editable and the
write is REFUSED (HasFreezeFrame does exactly that). It proves the logic and the gates,
NOT the key bindings and NOT the feel. Appends to Saved/jcpy/b1_fire_test.txt.
"""
import unreal, os, sys

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
MODE = sys.argv[1] if len(sys.argv) > 1 else 'state'
ARG = sys.argv[2] if len(sys.argv) > 2 else None
lines = []
def say(s): lines.append(str(s)); print(str(s))

def find(gw):
    out = {}
    for a in unreal.GameplayStatics.get_all_actors_of_class(gw, unreal.Actor):
        cn = a.get_class().get_name()
        if cn == 'BP_Player_C': out['player'] = a
        elif cn == 'BP_Coworker_C': out['cw'] = a
        elif cn == 'BP_CrashDriver_C': out['drv'] = a
        elif cn == 'BP_OpeningDirector_C': out['dir'] = a
        else:
            lab = a.get_actor_label()
            if lab in ('B1_Cafe_Fire', 'B1_Cafe_FireLight', 'B1_Cafe_BlastRing',
                       'B1_Objective_Beacon'):
                out[lab] = a
    return out

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    gw = ues.get_game_world()
    if gw is None:
        say('NO PIE WORLD'); raise SystemExit
    A = find(gw)
    t = unreal.GameplayStatics.get_time_seconds(gw)
    p, cw, drv, dr = A.get('player'), A.get('cw'), A.get('drv'), A.get('dir')

    if MODE == 'win':
        # The whole run-up in ONE frame. MCP round trips here are 5-8 s and the fuse is 9 s, so
        # doing this as separate calls burns the fuse before the rescue and always ends in the
        # failure path - which is a measurement artefact, not the game being unwinnable.
        p.set_actor_location(unreal.Vector(-300.0, 180.0, p.get_actor_location().z), False, True)
        say('DriverTryTouch -> %s  hasFF=%s'
            % (drv.call_method('DriverTryTouch'), p.get_editor_property('HasFreezeFrame')))
        cw.call_method('CoworkerStartStep')
        cw.call_method('CoworkerLightFire')
        say('CoworkerLightFire -> fireLit=%s fuse=%.2f armed=%s'
            % (cw.get_editor_property('FireLit'), cw.get_editor_property('FuseLeft'),
               cw.get_editor_property('RescueArmed')))
        p.call_method('FreezeFrameStart')
        say('FreezeFrameStart -> ffActive=%s' % p.get_editor_property('FreezeFrameActive'))
        p.set_actor_location(unreal.Vector(-450.0, -140.0, p.get_actor_location().z), False, True)
        say('CoworkerTryRescue -> %s  holding=%s'
            % (cw.call_method('CoworkerTryRescue'), cw.get_editor_property('Holding')))
        p.set_actor_location(unreal.Vector(430.0, -40.0, p.get_actor_location().z), False, True)
        say('player teleported to the safe spot; she should now walk after him')
    elif MODE == 'setup':
        # The whole run-up in ONE frame, so no MCP latency can burn the fuse between steps:
        # stand by the driver, take the power, cross to her, stop time, take her hand.
        p.set_actor_location(unreal.Vector(-300.0, 180.0, p.get_actor_location().z), False, True)
        say('DriverTryTouch -> %s' % drv.call_method('DriverTryTouch'))
        say('  hasFF now %s' % p.get_editor_property('HasFreezeFrame'))
        # the fire needs ExplosionDelay to pass, so light it by hand for this test and say so
        cw.call_method('CoworkerStartStep')
        cw.set_editor_property('ExplosionTimeLeft', 0.0)
        say('  (test) ExplosionTimeLeft forced to 0 so the fire lights this frame')
        p.set_actor_location(unreal.Vector(-450.0, -140.0, p.get_actor_location().z), False, True)
        say('FreezeFrameStart -> %s' % p.call_method('FreezeFrameStart'))
        say('  ffActive now %s' % p.get_editor_property('FreezeFrameActive'))
    elif MODE == 'move':
        x = float(ARG)
        y = float(sys.argv[3]) if len(sys.argv) > 3 else p.get_actor_location().y
        p.set_actor_location(unreal.Vector(x, y, p.get_actor_location().z), False, True)
        say('player moved to %s' % p.get_actor_location())
    elif MODE == 'touch':
        # the REAL path: BP_CrashDriver.DriverTryTouch, which gates on DriverCanTouch (range 220)
        say('DriverTryTouch -> %s' % drv.call_method('DriverTryTouch'))
    elif MODE == 'freeze':
        say('FreezeFrameStart -> %s' % p.call_method('FreezeFrameStart'))
    elif MODE == 'unfreeze':
        say('PlayerFreezeFrameEnd -> %s' % p.call_method('PlayerFreezeFrameEnd'))
    elif MODE == 'rescue':
        say('CoworkerTryRescue -> %s' % cw.call_method('CoworkerTryRescue'))
    elif MODE == 'burn':
        say('CoworkerBlastNow -> %s' % cw.call_method('CoworkerBlastNow'))

    # always report
    say('--- t=%.2f  mode=%s' % (t, MODE))
    if dr:
        say('  director  running=%s done=%s time=%.2f objState=%s'
            % (dr.get_editor_property('CineRunning'), dr.get_editor_property('CineDone'),
               dr.get_editor_property('CineTime'), dr.get_editor_property('ObjectiveState')))
    if p:
        say('  player    x=%.0f y=%.0f  hasFF=%s ffActive=%s health=%.0f lost=%s'
            % (p.get_actor_location().x, p.get_actor_location().y,
               p.get_editor_property('HasFreezeFrame'), p.get_editor_property('FreezeFrameActive'),
               p.get_editor_property('Health'), p.get_editor_property('IsLost')))
    if cw:
        L = cw.get_actor_location()
        say('  coworker  x=%.0f y=%.0f  started=%s fireLit=%s fuse=%.2f holding=%s blown=%s dead=%s rescueDone=%s armed=%s'
            % (L.x, L.y, cw.get_editor_property('RescueStarted'), cw.get_editor_property('FireLit'),
               cw.get_editor_property('FuseLeft'), cw.get_editor_property('Holding'),
               cw.get_editor_property('Blown'), cw.get_editor_property('CoworkerDead'),
               cw.get_editor_property('RescueDone'), cw.get_editor_property('RescueArmed')))
        say('            dist to blast origin = %.0f cm (radius %.0f)'
            % (unreal.Vector(L.x - (-520.0), L.y, 0.0).length(), cw.get_editor_property('BlastRadius')))
    for lab in ('B1_Cafe_Fire', 'B1_Cafe_FireLight', 'B1_Cafe_BlastRing', 'B1_Objective_Beacon'):
        a = A.get(lab)
        if a:
            say('  %-20s hidden=%-6s loc=%s scale=%s'
                % (lab, a.get_editor_property('hidden'),
                   '%.0f %.0f %.0f' % (a.get_actor_location().x, a.get_actor_location().y,
                                       a.get_actor_location().z),
                   '%.2f %.2f %.2f' % (a.get_actor_scale3d().x, a.get_actor_scale3d().y,
                                       a.get_actor_scale3d().z)))
except SystemExit:
    pass
except Exception as e:
    import traceback
    say('ERROR %r' % e); say(traceback.format_exc())
with open(os.path.join(OUT, 'b1_fire_test.txt'), 'a') as fh:
    fh.write('\n'.join(lines) + '\n')
