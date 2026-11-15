"""Beat 1 opening cinematic: the assets and level actors around LS_Beat1_Opening.

    py <repo>/tools/b1_opening_actors.py          make/refresh them
    py <repo>/tools/b1_opening_actors.py report   read back, change nothing

Makes:
  /Game/Game/Blueprints/BP_OpeningDirector   empty Actor Blueprint (graphs come from b1_opening_graphs.py)
Places (tag B1_Cine, so a re-run replaces exactly its own actors):
  B1_Cine_WallPatch   a plain cube in M_CafeWall standing 4 cm PROUD of the west wall's inner face,
                      so the peaceful shot has an unbroken wall for the car to come through. No
                      collision (cosmetic only). Deliberately NOT coplanar with the shell: a flush
                      face is the exact depth tie that caused #67.
  B1_Cine_Seq         a LevelSequenceActor on LS_Beat1_Opening, auto-play OFF (the director plays it)
  B1_Cine_Director    BP_OpeningDirector

Never saves. Save the actor packages with jc_save_actors.py and the Blueprint with the editor.
"""
import unreal, os, sys

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
log = []
def say(s):
    log.append(str(s)); print(str(s))

TAG = 'B1_Cine'
BP_DIR = '/Game/Game/Blueprints'
BP_NAME = 'BP_OpeningDirector'
BP_PATH = '%s/%s' % (BP_DIR, BP_NAME)
SEQ_PATH = '/Game/Game/Cinematics/LS_Beat1_Opening'
CUBE = '/Engine/BasicShapes/Cube.Cube'
# The cafe's wall material lives under Materials/City, NOT Materials/ - loading the wrong path
# returns None and the patch renders as the grey checker default, which is what the first
# build's peaceful shot showed.
WALL_MAT = '/Game/Game/Materials/City/M_CafeWall'

# the patch: 16 cm thick, 440 wide, 230 tall, centre x = -596 (inner face of the west wall is ~-600)
PATCH = dict(loc=(-596.0, 0.0, 115.0), scale=(0.16, 4.4, 2.3))

MODE = 'make'
for a in sys.argv[1:]:
    if a in ('make', 'report'):
        MODE = a

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    if ues.get_editor_world().get_name() != 'Lvl_JumpCut':
        raise RuntimeError('wrong world')
    if ues.get_game_world() is not None:
        raise RuntimeError('PIE is running - stop it first')
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    if MODE == 'report':
        for a in eas.get_all_level_actors():
            if unreal.Name(TAG) in a.get_editor_property('tags'):
                say('%-22s %-26s %s  hidden=%s' % (a.get_actor_label(), a.get_class().get_name(),
                                                   a.get_actor_location(),
                                                   a.get_editor_property('hidden')))
        bp = unreal.load_asset(BP_PATH)
        say('%s -> %s' % (BP_PATH, bp))
        raise SystemExit

    # ---------------- the Blueprint
    bp = unreal.load_asset(BP_PATH)
    if bp is None:
        fac = unreal.BlueprintFactory()
        fac.set_editor_property('parent_class', unreal.Actor)
        bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(BP_NAME, BP_DIR, unreal.Blueprint, fac)
        say('created %s (parent Actor)' % bp.get_path_name())
    else:
        say('%s already exists' % BP_PATH)

    seq = unreal.load_asset(SEQ_PATH)
    if seq is None:
        raise RuntimeError('run b1_opening_cine.py first - no %s' % SEQ_PATH)

    # ---------------- wipe our own previous actors
    removed = 0
    for a in list(eas.get_all_level_actors()):
        if unreal.Name(TAG) in a.get_editor_property('tags'):
            eas.destroy_actor(a); removed += 1
    say('removed %d earlier %s actors' % (removed, TAG))

    def tag(a, label):
        a.set_actor_label(label)
        a.set_editor_property('tags', [unreal.Name(TAG)])

    # ---------------- wall patch
    p = eas.spawn_actor_from_class(unreal.StaticMeshActor,
                                   unreal.Vector(*PATCH['loc']), unreal.Rotator())
    smc = p.static_mesh_component
    smc.set_mobility(unreal.ComponentMobility.MOVABLE)   # the director hides it; movable keeps that cheap
    smc.set_static_mesh(unreal.load_asset(CUBE))
    wm = unreal.load_asset(WALL_MAT)
    if wm is None:
        raise RuntimeError('wall material not found: %s' % WALL_MAT)
    smc.set_material(0, wm)
    p.set_actor_scale3d(unreal.Vector(*PATCH['scale']))
    p.set_actor_enable_collision(False)
    tag(p, 'B1_Cine_WallPatch')
    p.set_actor_location_and_rotation(unreal.Vector(*PATCH['loc']), unreal.Rotator(), False, True)
    say('B1_Cine_WallPatch at %s scale %s, collision off' % (p.get_actor_location(), p.get_actor_scale3d()))

    # ---------------- level sequence actor
    s = eas.spawn_actor_from_class(unreal.LevelSequenceActor, unreal.Vector(0, 0, 0), unreal.Rotator())
    try:
        s.set_sequence(seq)
    except Exception:
        s.set_editor_property('level_sequence', unreal.SoftObjectPath(SEQ_PATH + '.LS_Beat1_Opening'))
    ps = s.get_editor_property('playback_settings')
    say('   playback_settings fields: %s' % sorted(ps.to_dict().keys()))
    for fld, val in (('auto_play', False), ('restore_state', True)):
        try:
            ps.set_editor_property(fld, val)
            say('   playback_settings.%s = %s' % (fld, val))
        except Exception as e:
            say('   playback_settings.%s NOT set (%s)' % (fld, type(e).__name__))
    s.set_editor_property('playback_settings', ps)
    for fld, val in (('auto_play', False), ('b_auto_play', False)):
        try:
            s.set_editor_property(fld, val)
            say('   actor.%s = %s' % (fld, val))
        except Exception:
            pass
    tag(s, 'B1_Cine_Seq')
    say('B1_Cine_Seq -> %s' % s.get_sequence())

    # ---------------- director
    cls = unreal.load_class(None, '%s.%s_C' % (BP_PATH, BP_NAME))
    if cls is None:
        say('WARNING: %s_C not loadable yet (Blueprint never compiled) - placing it next run' % BP_NAME)
    else:
        d = eas.spawn_actor_from_class(cls, unreal.Vector(0.0, 0.0, 300.0), unreal.Rotator())
        tag(d, 'B1_Cine_Director')
        d.set_actor_location_and_rotation(unreal.Vector(0.0, 0.0, 300.0), unreal.Rotator(), False, True)
        say('B1_Cine_Director placed at %s' % d.get_actor_location())

    say('')
    say('NOT SAVED.')
except SystemExit:
    pass
except Exception as e:
    import traceback
    say('ERROR %r' % e); say(traceback.format_exc())
with open(os.path.join(OUT, 'b1_opening_actors.txt'), 'w') as fh:
    fh.write('\n'.join(log))
