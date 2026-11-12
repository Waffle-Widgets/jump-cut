"""C1 Play-mode checks. Usage in the console box: py C:/Users/thecl/code/jump-cut/tools/c1_pie.py <step> [args]
steps: state | tp x y z | gate <label> open|close | spawnrest
Appends to Saved/c1_pie.txt."""
import sys
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())
argv = sys.argv[1:]
log = ['--- ' + ' '.join(argv)]


def cls(p):
    return unreal.load_class(None, '/Game/Game/Blueprints/%s.%s_C' % (p, p))


try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    w = ues.get_game_world()
    if w is None:
        raise RuntimeError('no PIE world')
    GS = unreal.GameplayStatics

    def all_of(name):
        return list(GS.get_all_actors_of_class(w, cls(name)))

    player = all_of('BP_Player')[0]
    step = argv[0]
    if step == 'tp':
        x, y, z = float(argv[1]), float(argv[2]), float(argv[3])
        player.call_method('PlayerDebugTeleport', (unreal.Vector(x, y, z), 0.0))
        log.append('teleported to %s,%s,%s' % (x, y, z))
    elif step == 'gate':
        for g in all_of('BP_PlazaGate'):
            if g.get_actor_label() == argv[1]:
                g.call_method('PlazaGateOpen' if argv[2] == 'open' else 'PlazaGateClose')
                log.append('%s called %s' % (argv[1], argv[2]))
    # always report state
    log.append('game time %.2f' % GS.get_time_seconds(w))
    loc = player.get_actor_location()
    log.append('player at (%.0f, %.0f, %.0f) health=%s HasWon=%s CheckpointLocation=%s CheckpointYaw=%s' % (
        loc.x, loc.y, loc.z, player.get_editor_property('Health'), player.get_editor_property('HasWon'),
        player.get_editor_property('CheckpointLocation'), player.get_editor_property('CheckpointYaw')))
    log.append('live BP_Player_C count %d' % len(all_of('BP_Player')))
    for g in all_of('BP_PlazaGate'):
        mesh = g.get_components_by_class(unreal.StaticMeshComponent)[0]
        log.append('gate %s GateIsOpen=%s mesh world z=%.1f (rel z=%.1f) armed=%s' % (
            g.get_actor_label(), g.get_editor_property('GateIsOpen'), mesh.get_world_location().z,
            mesh.get_editor_property('relative_location').z, g.get_editor_property('GateTriggerArmed')))
    for c in all_of('BP_Checkpoint'):
        log.append('checkpoint %s taken=%s' % (c.get_actor_label(), c.get_editor_property('CheckpointTaken')))
    goons = all_of('BP_Goon')
    log.append('goons live: %d' % len(goons))
    for g in goons:
        gl = g.get_actor_location()
        log.append('  goon at (%.0f, %.0f, %.0f) awake=%s health=%s' % (gl.x, gl.y, gl.z, g.get_editor_property('EnemyIsAwake'), g.call_method('EnemyGetHealthNow')))
except Exception as e:
    log.append('ERROR: %r' % e)
with open(ROOT + 'c1_pie.txt', 'a') as f:
    f.write('\n'.join(log) + '\n')
