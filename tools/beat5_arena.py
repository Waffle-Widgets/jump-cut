"""Beat 5: the Stunt Double boss arena, on the landing pad beat 4 ends at.

RUN THIS ON A BUILDER, in the editor with Play mode stopped:
    py <repo>/tools/beat5_arena.py            place the arena
    py <repo>/tools/beat5_arena.py clear      remove every JC_Beat5 actor, put Marker_Win back on the pad
    py <repo>/tools/beat5_arena.py report      measure what is in the level now and change nothing

It does NOT save. Saving is the builder's call - this project has lost a lane of work to a save at the
wrong moment, and gained 23 duplicate actors from an editor that died with a section dirty. Look at it
in the viewport, then save the level yourself (and `git lfs lock` the actor packages first: a committed
actor package is read-only and the save fails SILENTLY).

READ THIS BEFORE RUNNING IT - the fight does not end yet
--------------------------------------------------------
`BP_StuntDouble` is a `BP_EnemyBase` child, not a `BP_BossFreeze` child, and that difference is the whole
problem with beat 5 right now. Read out of the committed assets, not inferred:

    BP_BossFreeze.uasset   contains  BossExitGate  and  PlazaGateOpenForGood
    BP_EnemyBase.uasset    contains  neither
    BP_StuntDouble.uasset  contains  neither, and no reference to BP_PlazaGate at all

So the cleaver boss opens the plaza's exit gate when he dies (`EnemyDefeatedHook` ->
`BossExitGate.PlazaGateOpenForGood`), and the Stunt Double boss **opens nothing**. He also hands no power
over: there is no `BossHandOverPower` on him either. Beat 5 currently has no way to finish: you can kill
him and the level just stands there.

This script places `Gate_Beat5Exit` anyway, closed, and points nothing at it, because the fix is a
Blueprint change and this script only places actors. `tools/beat5_graphs.py` is that change - add the
`BossExitGate` variable and the `EnemyDefeatedHook` line, then re-run this script's `report` and it will
tell you the link is live. Until then the exit gate is a wall and the arena is a dead end.

WHAT IT TOUCHES
  * It only ever adds or removes actors tagged 'JC_Beat5'. Run it twice and you get one arena, not two.
  * `Marker_Win` is MOVED east of the exit gate. `tools/beat4_platforming.py` parked it at (14400, 0, 0),
    in the MIDDLE of the landing pad - which means the player wins the demo by walking onto the arena,
    before the boss is even awake. That is a real bug today, not a future one. `clear` puts it back at
    (14400, 0, 0), which is beat 4's home for it, NOT c1_layout's (10220, 0, 0).
  * Nothing in C1_Layout and nothing tagged JC_Beat4 is touched.
  * No .uasset is created. Every class it places already exists.

THE GEOMETRY, AND WHERE THE NUMBERS COME FROM
`tools/beat4_platforming.py` places the landing pad as six SM_RuinSlab_A at x 14000 / 14500 and
y -500 / 0 / +500. Each slab is 500 cm square with its walking surface 45 cm above its own origin, so:

    pad          x 13750 .. 14750   (10 m)        y -750 .. +750   (15 m)        top z = 0
    approach     gap 3 is x 13350 -> 13750, 400 cm wide and roofed at 215, so the player arrives
                 by blinking in along y = 0 on one 500 cm wide slab - not across the full 15 m
    void         there is nothing under the pad. Below FallLoseZ (-1000) health goes to 0, which is
                 the lose screen and a restart from Checkpoint_Beat4Entry at x 10900

    Gate_Beat5Entry  x 13800   starts OPEN, closes behind the player, wakes the boss
    Boss_StuntDouble x 14300   facing west (yaw 180), 5 m in front of the entry gate
    Gate_Beat5Exit   x 14650   starts CLOSED. Opens when the boss dies - once beat5_graphs.py is run
    Marker_Win       x 14720   east of the exit gate, 30 cm inside the pad's east lip

WHY THE ENTRY GATE IS AT THE PAD'S WEST LIP AND NOT FURTHER IN
`BP_PlazaGate`'s opening is 5 m wide (docs/FIRST_BUILD_DESIGN.md: "keep each opening 5 m wide") and the
pad is 15 m wide, so a gate anywhere on the pad can be walked around. At x 13800 that does not matter:
the only way in is gap 3's single 500 cm slab along y = 0, so a 5 m gate there seals the approach. Put it
at 14000 and the player can simply step sideways onto the pad's wide part and round it.

THE ONE THING THIS SCRIPT CANNOT SETTLE: Marker_Win's trigger radius. `BP_SceneMarker` has no
`MarkerRadius` variable - the trigger is a component, and c1_layout.py's own header records that
`Marker_FreezeFrameDoor`'s radius 200 was set per-instance by `tools/d1_editor.py`. If Marker_Win's
sphere is 200 cm, a marker at 14720 reaches back to 14520 - which is WEST of the exit gate at 14650, so
the player would win through the closed gate. `report` prints the radius it finds. Check it.
"""
import os
import sys

import unreal

TAG = 'JC_Beat5'
BP = '/Game/Game/Blueprints/'

GATE_H = 400.0                 # BP_PlazaGate's mesh height; c1_layout.py places gates at H / 2
PAD_W, PAD_E = 13750.0, 14750.0
WIN_BEAT4 = unreal.Vector(14400.0, 0.0, 0.0)     # where beat4_platforming.py parks Marker_Win
WIN_BEAT5 = unreal.Vector(14720.0, 0.0, 0.0)     # east of the exit gate

# (label, blueprint, x, y, z, yaw, {variable: value})
ACTORS = [
    # The entry gate is the wake trigger, exactly as Gate_PlazaEntry is for the cleaver boss: it starts
    # open, shuts behind the player, and its tick calls GateEnemyToWake.EnemyWake when it shuts.
    # GateEnemyToWake is a level reference, so it is wired below, after both actors exist.
    ('Gate_Beat5Entry', 'BP_PlazaGate', 13800.0, 0.0, GATE_H / 2.0,   0.0,
     {'GateStartsOpen': True, 'GateClosesBehindPlayer': True}),

    # Facing west down the pad. 300 health, 0.40 s windup, 1.0 s cooldown are his class defaults - this
    # script does not re-state them, so tuning stays in one place (the Blueprint).
    ('Boss_StuntDouble', 'BP_StuntDouble', 14300.0, 0.0, 200.0, 180.0, {}),

    # Closed, and nothing points at it yet. See the header.
    ('Gate_Beat5Exit', 'BP_PlazaGate', 14650.0, 0.0, GATE_H / 2.0,   0.0,
     {'GateStartsOpen': False, 'GateClosesBehindPlayer': False}),
]

log = []


def say(msg):
    log.append(msg)
    unreal.log('B5: ' + msg)
    print(msg)


def write_log():
    out = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())
    with open(os.path.join(out, 'jc_beat5.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')


def by_label(eas, label):
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == label:
            return a
    return None


def clear(eas):
    n = 0
    for a in list(eas.get_all_level_actors()):
        if unreal.Name(TAG) in a.get_editor_property('tags'):
            eas.destroy_actor(a)
            n += 1
    say('removed %d earlier %s actors' % (n, TAG))
    return n


def move_win(eas, where):
    a = by_label(eas, 'Marker_Win')
    if a is None:
        say('Marker_Win not found - not moved. Has beat 4 been placed?')
        return
    a.modify()
    a.set_actor_location_and_rotation(where, unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0), False, True)
    say('Marker_Win -> %s' % a.get_actor_location())


def win_radius(eas):
    """Marker_Win's trigger radius, or None. See the header: this is the number that can let the player
    win through a closed gate, and it lives on a component, not on a Blueprint variable."""
    a = by_label(eas, 'Marker_Win')
    if a is None:
        return None
    for comp in a.get_components_by_class(unreal.SphereComponent):
        return comp.get_unscaled_sphere_radius() * comp.get_component_scale().x
    return None


def place(eas):
    for label, bpname, x, y, z, yaw, vars_ in ACTORS:
        cls = unreal.load_class(None, '%s%s.%s_C' % (BP, bpname, bpname))
        if cls is None:
            raise RuntimeError('%s does not exist - is this branch up to date?' % bpname)
        a = eas.spawn_actor_from_class(cls, unreal.Vector(x, y, z),
                                       unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
        a.set_actor_label(label)
        a.set_editor_property('tags', [unreal.Name(TAG)])
        for k, v in vars_.items():
            a.set_editor_property(k, v)
            # Never assume a set took: an exposed variable can accept a write with no error at all and
            # still read back unchanged (BP_Player.InputLocked did exactly that).
            got = a.get_editor_property(k)
            if got != v:
                raise RuntimeError('%s.%s read back %r, not %r' % (label, k, got, v))
        # A property written on a placed actor does not dirty its package; re-setting the transform does.
        a.set_actor_location_and_rotation(unreal.Vector(x, y, z),
                                         unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw), False, True)
        say('%s at %s yaw %.0f %s' % (label, a.get_actor_location(), yaw, vars_ or ''))

    # The level references, after both ends exist.
    boss = by_label(eas, 'Boss_StuntDouble')
    entry = by_label(eas, 'Gate_Beat5Entry')
    exit_ = by_label(eas, 'Gate_Beat5Exit')

    entry.set_editor_property('GateEnemyToWake', boss)
    if entry.get_editor_property('GateEnemyToWake') != boss:
        raise RuntimeError('GateEnemyToWake did not take')
    entry.set_actor_transform(entry.get_actor_transform(), False, True)
    say('Gate_Beat5Entry.GateEnemyToWake -> Boss_StuntDouble')

    # BossExitGate only exists on BP_BossFreeze. Try it anyway and say plainly which world we are in,
    # rather than leaving a silently dead exit gate behind.
    try:
        boss.set_editor_property('BossExitGate', exit_)
        ok = boss.get_editor_property('BossExitGate') == exit_
    except Exception:                                              # noqa: BLE001
        ok = False
    if ok:
        boss.set_actor_transform(boss.get_actor_transform(), False, True)
        say('Boss_StuntDouble.BossExitGate -> Gate_Beat5Exit  (beat5_graphs.py has been run)')
    else:
        say('!! Boss_StuntDouble has NO BossExitGate, so Gate_Beat5Exit will never open and beat 5')
        say('!! has no ending. Run tools/beat5_graphs.py, then re-run this script. See the header.')


def report(eas):
    """Measure the arena that is actually in the level, and say whether the fight can end."""
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

    mine = [a for a in eas.get_all_level_actors()
            if unreal.Name(TAG) in a.get_editor_property('tags')]
    say('%d %s actors: %s' % (len(mine), TAG, sorted(a.get_actor_label() for a in mine)))

    # Ground under the pad: the arena is useless if the boss is standing over a hole.
    for px in (13800.0, 14300.0, 14650.0, 14720.0):
        for py in (-600.0, 0.0, 600.0):
            hit = unreal.SystemLibrary.line_trace_single(
                world, unreal.Vector(px, py, 200.0), unreal.Vector(px, py, -600.0),
                unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
            if hit is None:
                say('   NO GROUND at (%.0f, %.0f) - the pad does not reach here' % (px, py))
    say('ground probed across the pad at x 13800/14300/14650/14720, y -600/0/+600')

    boss = by_label(eas, 'Boss_StuntDouble')
    entry = by_label(eas, 'Gate_Beat5Entry')
    exit_ = by_label(eas, 'Gate_Beat5Exit')
    if boss is not None:
        say('Boss_StuntDouble at %s, health %s' % (boss.get_actor_location(),
                                                   boss.get_editor_property('EnemyMaxHealth')))
    if entry is not None:
        w = entry.get_editor_property('GateEnemyToWake')
        say('Gate_Beat5Entry.GateEnemyToWake = %s' % (w.get_actor_label() if w else 'NONE - the boss never wakes'))
    if exit_ is not None:
        say('Gate_Beat5Exit starts open = %s' % exit_.get_editor_property('GateStartsOpen'))
    if boss is not None:
        try:
            g = boss.get_editor_property('BossExitGate')
            say('Boss_StuntDouble.BossExitGate = %s' % (g.get_actor_label() if g else 'NONE'))
        except Exception:                                          # noqa: BLE001
            say('Boss_StuntDouble has NO BossExitGate variable -> killing him opens nothing.')
            say('   Beat 5 cannot be finished. Run tools/beat5_graphs.py.')

    r = win_radius(eas)
    a = by_label(eas, 'Marker_Win')
    if a is not None:
        say('Marker_Win at %s, trigger radius %s' % (a.get_actor_location(), r))
        if r is not None and a.get_actor_location().x - r < 14650.0:
            say('   !! that radius reaches WEST of Gate_Beat5Exit (14650): the player can win through')
            say('   !! the closed gate. Shrink the sphere or move the marker east.')


def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else 'place').lower()
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = ues.get_editor_world()
    if world.get_name() != 'Lvl_JumpCut' or ues.get_game_world() is not None:
        raise RuntimeError('wrong world (%s) or PIE is running - stop Play first' % world.get_name())
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    if mode == 'report':
        report(eas)
        return
    if mode == 'clear':
        clear(eas)
        move_win(eas, WIN_BEAT4)
        say('done. NOT SAVED.')
        return

    clear(eas)
    place(eas)
    move_win(eas, WIN_BEAT5)
    report(eas)
    say('NOT SAVED. Look at it in the viewport, then save the level yourself.')


try:
    main()
except Exception as e:                                             # noqa: BLE001 - the log is the result
    say('ERROR: %r' % e)
    raise
finally:
    write_log()
