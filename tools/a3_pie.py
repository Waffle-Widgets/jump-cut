# One-off editor step from the first build (Nov 12), copied from the ignored JumpCut/Saved/ so the level set-up can be traced.
# Run with `py <path> <step>` in the Unreal editor console (a3_pie.py: during Play mode; the others: Play mode stopped).
# Read it before re-running: steps change placed actors in Lvl_JumpCut and some save the level.
"""A3 Play-mode steps.  py a3_pie.py <mode> [args]  -> appends to Saved/a3_pie.txt
  state                 characters (live, with Render CustomDepth), spawners, volume, flow
  play                  JumpCutStartPlay (leave the title)
  look on|off           enable / disable PP_AnimeLook in the PIE world
  spot <name>           teleport the player + camera to a capture spot, then freeze time (dilation 0.0001)
  wake                  EnemyWake on every enemy
  ff                    PlayerGrantFreezeFrame + FreezeFrameStart, freeze time shortly after
  lose                  PlayerTakeHit 999, freeze time
  win                   PlayerReachWin (after the boss is beaten by EnemyTakeHit), freeze time
  warn                  a goon's punch warning up (EnemyStartPunchWindup if it exists), freeze
  dil <x>
"""
import sys, math, builtins
import unreal

SAVED = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())
LOG = SAVED + 'a3_pie.txt'
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
GS = unreal.GameplayStatics
BPP = '/Game/Game/Blueprints/'


def say(s):
    with open(LOG, 'a') as f:
        f.write(s + '\n')


def W():
    return UES.get_game_world()


def cls(n):
    return unreal.load_class(None, '%s%s.%s_C' % (BPP, n, n))


def of(n):
    return list(GS.get_all_actors_of_class(W(), cls(n)))


def P():
    return of('BP_Player')[0]


def GM():
    return GS.get_game_mode(W())


def vt(v):
    return '(%.0f,%.0f,%.0f)' % (v.x, v.y, v.z)


def ppv():
    for a in GS.get_all_actors_of_class(W(), unreal.PostProcessVolume):
        if a.get_actor_label() == 'PP_AnimeLook':
            return a
    return None


def state():
    say('--- state t=%.2f dil=%.4f' % (GS.get_time_seconds(W()), GS.get_global_time_dilation(W())))
    for a in GS.get_all_actors_of_class(W(), unreal.Character):
        m = a.mesh
        mats = [x.get_name() if x else None for x in m.get_materials()]
        say('  CHAR %s %s %s rcd=%s mats=%s' % (a.get_actor_label(), a.get_class().get_name(), vt(a.get_actor_location()),
                                               m.get_editor_property('render_custom_depth'), mats))
    for a in of('BP_GoonSpawner'):
        say('  SPAWNER %s %s' % (a.get_actor_label(), vt(a.get_actor_location())))
    v = ppv()
    say('  PPV %s enabled=%s unbound=%s' % (v.get_actor_label() if v else None, v.get_editor_property('enabled') if v else None,
                                            v.get_editor_property('unbound') if v else None))
    try:
        say('  FlowState=%s' % GM().get_editor_property('FlowState'))
    except Exception as e:
        say('  flow err %s' % e)
    p = P()
    say('  player hp=%.0f HasFF=%s lost=%s' % (p.get_editor_property('Health'), p.get_editor_property('HasFreezeFrame'), p.get_editor_property('IsLost')))


def play():
    GS.set_global_time_dilation(W(), 1.0)
    GM().call_method('JumpCutStartPlay')
    say('play called')


def look(on):
    v = ppv()
    v.set_editor_property('enabled', on == 'on')
    say('look %s -> enabled=%s' % (on, v.get_editor_property('enabled')))


# name: (player x, y, yaw, control yaw, control pitch)
SPOTS = {
    'cafe': (150, 0, 150, 150, -12),
    'street': (None, None, 0, 0, -12),
    'plaza': (7350, 0, 0, 0, -10),
}


def spot(name, *args):
    GS.set_global_time_dilation(W(), 1.0)
    p = P()
    x, y, yaw, cy, cp = SPOTS[name]
    if args:
        x, y = float(args[0]), float(args[1])
        if len(args) > 2:
            yaw = cy = float(args[2])
    p.call_method('PlayerDebugTeleport', (unreal.Vector(x, y, 100.0), float(yaw)))
    GS.get_player_controller(W(), 0).set_control_rotation(unreal.Rotator(roll=0.0, pitch=cp, yaw=cy))
    say('spot %s player %s' % (name, vt(p.get_actor_location())))


def dil(x):
    GS.set_global_time_dilation(W(), float(x))
    say('dil %s' % x)


def wake():
    for e in of('BP_EnemyBase'):
        e.call_method('EnemyWake')
    say('woke %d' % len(of('BP_EnemyBase')))


def ff():
    p = P()
    p.call_method('PlayerGrantFreezeFrame')
    p.call_method('FreezeFrameStart')
    say('ff: HasFF=%s FFActive=%s' % (p.get_editor_property('HasFreezeFrame'), p.get_editor_property('FreezeFrameActive')))


def lose():
    GS.set_global_time_dilation(W(), 1.0)
    P().call_method('PlayerTakeHit', (999.0,))
    say('lose: IsLost=%s FlowState=%s' % (P().get_editor_property('IsLost'), GM().get_editor_property('FlowState')))


def funcs(n):
    c = cls(n)
    names = [f for f in dir(unreal.get_default_object(c)) if f[0].isupper()]
    say('%s: %s' % (n, names[:200]))


def call(label_or_class, fn, *args):
    targets = of(label_or_class) if not label_or_class.startswith('P') else [P()]
    conv = tuple(float(a) for a in args)
    for t in targets:
        r = t.call_method(fn, conv) if conv else t.call_method(fn)
        say('call %s.%s%s -> %s' % (t.get_actor_label(), fn, conv, r))


def tune(*pairs):
    """Try look numbers live: a dynamic copy of MI_AnimeLook_JumpCut on the PIE volume only (no asset changes)."""
    v = ppv()
    mid = getattr(builtins, '_a3_mid', None)
    if mid is None or not unreal.SystemLibrary.is_valid(mid) or getattr(builtins, '_a3_world', None) != W().get_name() + str(id(W())):
        mid = (unreal.MaterialLibrary.create_dynamic_material_instance(
            W(), unreal.load_asset('/Game/Game/Materials/MI_AnimeLook_JumpCut')))
        builtins._a3_mid = mid
        builtins._a3_world = W().get_name() + str(id(W()))
        s = v.get_editor_property('settings')
        s.set_editor_property('weighted_blendables', unreal.WeightedBlendables(array=[unreal.WeightedBlendable(weight=1.0, object=mid)]))
        v.set_editor_property('settings', s)
    for p in pairs:
        n, val = p.split('=')
        if ',' in val:
            r, g, b = [float(x) for x in val.split(',')]
            mid.set_vector_parameter_value(n, unreal.LinearColor(r, g, b, 1.0))
        else:
            mid.set_scalar_parameter_value(n, float(val))
    say('tune %s' % (pairs,))


def ppset(*pairs):
    """PIE-only volume settings (exposure etc.) to try."""
    v = ppv()
    s = v.get_editor_property('settings')
    for p in pairs:
        k, val = p.split('=')
        if k == 'method':
            s.set_editor_property('override_auto_exposure_method', True)
            s.set_editor_property('auto_exposure_method', unreal.AutoExposureMethod.AEM_MANUAL if val == 'manual' else unreal.AutoExposureMethod.AEM_HISTOGRAM)
        elif k == 'physical':
            s.set_editor_property('override_auto_exposure_apply_physical_camera_exposure', True)
            s.set_editor_property('auto_exposure_apply_physical_camera_exposure', val == '1')
        elif k in ('color_saturation', 'color_contrast'):
            f = float(val)
            s.set_editor_property('override_' + k, True)
            s.set_editor_property(k, unreal.Vector4(f, f, f, 1.0))
        else:
            s.set_editor_property('override_' + k, True)
            s.set_editor_property(k, float(val))
    v.set_editor_property('settings', s)
    say('ppset %s' % (pairs,))


def win():
    GS.set_global_time_dilation(W(), 1.0)
    b = of('BP_BossFreeze')[0]
    b.call_method('EnemyTakeHit', (999.0, P().get_actor_location(), 0.0, 0.0, 0.0))
    say('boss defeated=%s' % b.get_editor_property('EnemyIsDefeated'))
    P().call_method('PlayerReachWin')
    say('win: HasWon=%s FlowState=%s' % (P().get_editor_property('HasWon'), GM().get_editor_property('FlowState')))


def fpsset():
    """plaza with boss and goons awake, look state as is: player stands at the plaza entrance looking in"""
    p = P()
    p.call_method('PlayerDebugTeleport', (unreal.Vector(7300, 0, 100.0), 0.0))
    GS.get_player_controller(W(), 0).set_control_rotation(unreal.Rotator(roll=0.0, pitch=-10.0, yaw=0.0))
    for e in of('BP_EnemyBase'):
        e.call_method('EnemyWake')
    say('fpsset at plaza, woke %d' % len(of('BP_EnemyBase')))


def refill():
    p = P()
    h = p.get_editor_property('Health')
    if 0.0 < h < 100.0:
        p.call_method('PlayerTakeHit', (h - 100.0,))
    say('refill %.0f -> %.0f lost=%s; %s' % (h, p.get_editor_property('Health'), p.get_editor_property('IsLost'),
        ' '.join('%s%s awake=%s' % (e.get_actor_label(), vt(e.get_actor_location()), e.get_editor_property('EnemyIsAwake')) for e in of('BP_EnemyBase'))))


mode = sys.argv[1]
try:
    globals()[mode](*sys.argv[2:])
except Exception:
    import traceback
    say('ERROR %s %s' % (mode, traceback.format_exc()))


def _warn_main():
    gs = sorted(of('BP_Goon'), key=lambda g: g.get_actor_location().y)
    g = gs[len(gs) // 2]
    g.call_method('EnemyShowWarning', (True,))
    say('warn on %s %s' % (g.get_actor_label(), vt(g.get_actor_location())))


if mode == 'warn':
    try:
        _warn_main()
    except Exception:
        import traceback
        say('ERROR warn %s' % traceback.format_exc())
