"""Read-only probe for the beat-1 opening cinematic work. Writes Saved/jcpy/b1_cine_probe.txt.
Run:  py <repo>/tools/b1_cine_probe.py
Touches nothing: no spawn, no set, no save.
"""
import unreal, os

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
if not os.path.isdir(OUT):
    os.makedirs(OUT)
log = []
def say(s):
    log.append(str(s))

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    w = ues.get_editor_world()
    say('editor world: %s   PIE: %s' % (w.get_name(), ues.get_game_world() is not None))
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    acts = list(eas.get_all_level_actors())
    say('total actors: %d' % len(acts))

    # --- cafe box ---
    say('')
    say('=== CAFE AREA actors (x -1200..900, y -700..700) ===')
    rows = []
    for a in acts:
        try:
            L = a.get_actor_location()
        except Exception:
            continue
        if -1200 <= L.x <= 900 and -700 <= L.y <= 700:
            cls = a.get_class().get_name()
            try:
                o, e = a.get_actor_bounds(False)
            except Exception:
                o, e = unreal.Vector(), unreal.Vector()
            rows.append((L.x, L.y, L.z, a.get_actor_label(), cls,
                         a.get_actor_rotation().yaw, e.x, e.y, e.z,
                         bool(a.get_editor_property('hidden') if hasattr(a, 'hidden') else False)))
    rows.sort()
    for r in rows:
        say('%9.1f %9.1f %7.1f  yaw%7.1f  ext(%6.0f %6.0f %6.0f)  %-34s %s' %
            (r[0], r[1], r[2], r[5], r[6], r[7], r[8], r[3], r[4]))

    # --- player start / pawn ---
    say('')
    say('=== PlayerStart / pawn-ish ===')
    for a in acts:
        cls = a.get_class().get_name()
        if 'PlayerStart' in cls or 'PlayerStart' in a.get_actor_label() or cls in ('BP_Player_C',):
            say('%-34s %-24s %s yaw=%.1f' % (a.get_actor_label(), cls, a.get_actor_location(), a.get_actor_rotation().yaw))

    # --- beat 1 actor instance values ---
    say('')
    say('=== beat-1 instance values ===')
    WANT = {
        'BP_Coworker_C': ['ShrapnelSpawnLocation', 'CoworkerSafeOffset', 'RescueRequiresFreeze',
                          'AutoFreezeOnExplosion', 'ExplosionDelay', 'ShrapnelSpeed', 'CoworkerDead',
                          'RescueTriesUsed', 'PlayerRef'],
        'BP_CrashDriver_C': ['TouchRange', 'DriverTouched'],
        'BP_SceneMarker_C': ['MarkerId', 'MarkerGrantsFreezeFrame', 'MarkerEndsGame'],
        'BP_GoonSpawner_C': ['GoonCount'],
    }
    for a in acts:
        cls = a.get_class().get_name()
        if cls in WANT:
            bits = []
            for p in WANT[cls]:
                try:
                    bits.append('%s=%s' % (p, a.get_editor_property(p)))
                except Exception as e:
                    bits.append('%s=<%s>' % (p, type(e).__name__))
            say('%-30s %-20s %s' % (a.get_actor_label(), cls, a.get_actor_location()))
            say('      ' + '  '.join(bits))

    # --- what blueprints exist ---
    say('')
    say('=== /Game/Game/Blueprints ===')
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    for folder in ['/Game/Game/Blueprints', '/Game/Game/Cinematics', '/Game/Game/FX',
                   '/Game/Game/FX/Textures', '/Game/Game/Materials', '/Game/Game/UI', '/Game/Game/Audio']:
        ar.scan_paths_synchronous([folder], True)
        names = []
        for d in ar.get_assets_by_path(folder, recursive=True):
            names.append('%s(%s)' % (str(d.asset_name), str(d.asset_class_path.asset_name)))
        say('%s -> %d' % (folder, len(names)))
        if folder != '/Game/Game/Audio':
            for n in sorted(names):
                say('   ' + n)

    # --- existing level sequences anywhere ---
    say('')
    say('=== LevelSequence assets in /Game ===')
    ar.scan_paths_synchronous(['/Game'], True)
    f = unreal.ARFilter(class_paths=[unreal.TopLevelAssetPath('/Script/LevelSequence', 'LevelSequence')],
                        recursive_classes=True, package_paths=['/Game'], recursive_paths=True)
    for d in ar.get_assets(f):
        say('   %s' % str(d.package_name))

    # --- player blueprint vars of interest ---
    say('')
    say('=== BP_Player / GameMode variable names ===')
    for bp in ['/Game/Game/Blueprints/BP_Player.BP_Player',
               '/Game/Game/Blueprints/BP_JumpCutGameMode.BP_JumpCutGameMode',
               '/Game/Game/Blueprints/BP_Coworker.BP_Coworker',
               '/Game/Game/Blueprints/BP_CrashDriver.BP_CrashDriver',
               '/Game/Game/Blueprints/BP_SceneMarker.BP_SceneMarker']:
        o = unreal.load_object(None, bp)
        if o is None:
            say('%s MISSING' % bp); continue
        gen = o.generated_class()
        vs = [str(p.get_name()) for p in unreal.BlueprintEditorLibrary.get_blueprint_variables(o)] if hasattr(unreal.BlueprintEditorLibrary, 'get_blueprint_variables') else []
        say('--- %s' % bp.split('/')[-1])
        if vs:
            say('   vars: ' + ', '.join(vs))
        else:
            cdo = unreal.get_default_object(gen)
            say('   (no var API) cdo=%s' % cdo.get_name())
except Exception as e:
    import traceback
    say('ERROR %r' % e)
    say(traceback.format_exc())

with open(os.path.join(OUT, 'b1_cine_probe.txt'), 'w') as fh:
    fh.write('\n'.join(log))
print('b1_cine_probe wrote %d lines' % len(log))
