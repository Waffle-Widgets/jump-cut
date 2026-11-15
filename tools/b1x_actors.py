"""Beat 1 explosion, stage 2: the level actors (tag B1_Expl), and the wreck swap.

  B1_Cafe_CrashCar_GC  GeometryCollectionActor on GC_CrashCar, standing where the wreck stands.
                       It REPLACES City_CafeCrashCar (hidden + collision off), exactly the way
                       City_Cafe_06_CafeTable was replaced by City_Cafe_05_CafeTable_GC.
  B1_Cafe_Explosion    a camera-facing card in M_FXExplosion; the director billboards it and
                       walks its 'Frame' 0..35 over 1.2 s, then hides it.
  B1_Cine_ExplCam      the camera the director drives for the explosion-and-pan cinematic.

  py <repo>/tools/b1x_actors.py          make/refresh
  py <repo>/tools/b1x_actors.py report   read back, change nothing
Never saves. Save with tools/jc_save_actors.py.
"""
import unreal, os, sys, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
TAG = 'B1_Expl'
GC = '/Game/Game/Destruction/GC_CrashCar'
PLANE = '/Engine/BasicShapes/Plane.Plane'
MAT = '/Game/Game/Materials/M_FXExplosion'
WRECK = 'City_CafeCrashCar'
MODE = 'make'
for a in sys.argv[1:]:
    if a in ('make', 'report'):
        MODE = a
res = {'mode': MODE}

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    assert ues.get_editor_world().get_name() == 'Lvl_JumpCut', 'wrong world'
    assert ues.get_game_world() is None, 'PIE is running - stop it first'
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    by_label = {a.get_actor_label(): a for a in eas.get_all_level_actors()}

    def describe(a):
        d = {'class': a.get_class().get_name(),
             'loc': [round(v, 1) for v in a.get_actor_location().to_tuple()],
             'rot': [round(v, 1) for v in a.get_actor_rotation().to_tuple()],
             'scale': [round(v, 3) for v in a.get_actor_scale3d().to_tuple()],
             'hidden': bool(a.get_editor_property('hidden')),
             'collides': a.get_actor_enable_collision(),
             'tags': [str(t) for t in a.get_editor_property('tags')],
             'pkg': a.get_outermost().get_name()}
        c = a.get_component_by_class(unreal.GeometryCollectionComponent)
        if c:
            d['rest'] = c.get_editor_property('rest_collection').get_path_name() if c.get_editor_property('rest_collection') else None
            d['damage_threshold'] = list(c.get_editor_property('damage_threshold'))
            try:
                d['object_type'] = str(c.get_editor_property('object_type'))
            except Exception:
                pass
        return d

    if MODE == 'report':
        rows = {}
        for a in eas.get_all_level_actors():
            if unreal.Name(TAG) in a.get_editor_property('tags') or a.get_actor_label() == WRECK:
                rows[a.get_actor_label()] = describe(a)
        # what an existing, known-good table GC looks like, for comparison
        t = by_label.get('City_Cafe_05_CafeTable_GC')
        if t:
            rows['(reference) City_Cafe_05_CafeTable_GC'] = describe(t)
        res['actors'] = rows
        raise SystemExit

    wreck = by_label.get(WRECK)
    assert wreck is not None, 'no %s in the level' % WRECK
    loc, rot, scale = wreck.get_actor_location(), wreck.get_actor_rotation(), wreck.get_actor_scale3d()
    res['wreck_was'] = describe(wreck)

    # ---- wipe our own actors only
    removed = []
    for a in list(eas.get_all_level_actors()):
        if unreal.Name(TAG) in a.get_editor_property('tags'):
            removed.append(a.get_actor_label())
            eas.destroy_actor(a)
    res['removed'] = removed

    # ---- the wreck becomes the geometry collection
    gc_asset = unreal.load_asset(GC)
    assert gc_asset is not None, 'missing ' + GC
    g = eas.spawn_actor_from_class(unreal.GeometryCollectionActor, loc, rot)
    g.set_actor_label('B1_Cafe_CrashCar_GC')
    g.set_actor_scale3d(scale)
    g.set_editor_property('tags', [unreal.Name(TAG), unreal.Name('JC_Chaos')])
    gcc = g.get_component_by_class(unreal.GeometryCollectionComponent)
    gcc.set_rest_collection(gc_asset)
    # high: a punch must NOT take the car apart - only the blast does, through ApplyExternalStrain
    gcc.set_editor_property('damage_threshold', [500000.0, 500000.0, 500000.0])
    # KINEMATIC, not the Dynamic a GeometryCollectionActor spawns with. Measured in PIE: dynamic,
    # this wreck's bounds reached z -19405 within four seconds of BeginPlay - it falls out of the
    # world before the player can look at it. CineExplFire switches it to Dynamic at the blast.
    gcc.set_editor_property('object_type', unreal.ObjectStateTypeEnum.CHAOS_OBJECT_KINEMATIC)
    gcc.set_editor_property('enable_clustering', True)
    gcc.set_editor_property('notify_breaks', True)
    g.set_folder_path('Chaos')
    res['gc_actor'] = describe(g)

    # the static wreck stops being the thing you see, but is never deleted (the city placer owns it)
    wreck.modify()
    wreck.set_actor_hidden_in_game(True)
    wreck.set_is_temporarily_hidden_in_editor(True)
    wreck.set_actor_enable_collision(False)
    wreck.set_actor_transform(wreck.get_actor_transform(), False, True)   # dirties its own package
    res['wreck_now'] = describe(wreck)

    # ---- the explosion card
    card = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(loc.x + 10.0, loc.y, 150.0),
                                      unreal.Rotator())
    c = card.static_mesh_component
    c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_static_mesh(unreal.load_asset(PLANE))
    c.set_material(0, unreal.load_asset(MAT))
    c.set_editor_property('cast_shadow', False)
    card.set_actor_scale3d(unreal.Vector(9.0, 9.0, 9.0))
    card.set_actor_enable_collision(False)
    card.set_actor_label('B1_Cafe_Explosion')
    card.set_editor_property('tags', [unreal.Name(TAG)])
    card.set_actor_hidden_in_game(True)
    res['card'] = describe(card)

    # ---- something for the debris to land on
    # The city kit's floors are collision-trace COMPLEX-AS-SIMPLE, and Chaos geometry-collection
    # particles do not collide with triangle-mesh collision: the first broken wreck fell straight
    # through the cafe and kept going to z -44289. A plain box collider under the wreck is what
    # stops it. Hidden in game; it is only there for the physics.
    floor = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(loc.x, loc.y, -15.0),
                                       unreal.Rotator())
    fc = floor.static_mesh_component
    fc.set_mobility(unreal.ComponentMobility.STATIC)
    fc.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube.Cube'))
    fc.set_editor_property('cast_shadow', False)
    floor.set_actor_scale3d(unreal.Vector(16.0, 12.0, 0.3))   # 1600 x 1200 x 30, top face at z = 0
    floor.set_actor_label('B1_Cafe_DebrisFloor')
    floor.set_editor_property('tags', [unreal.Name(TAG)])
    floor.set_actor_hidden_in_game(True)
    floor.set_actor_enable_collision(True)
    res['debris_floor'] = describe(floor)

    # ---- the explosion cinematic's camera
    cam = eas.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(180.0, -300.0, 200.0),
                                     unreal.Rotator(0.0, -8.2, 156.8))
    cam.set_actor_label('B1_Cine_ExplCam')
    cam.set_editor_property('tags', [unreal.Name(TAG)])
    cc = cam.camera_component
    cc.set_editor_property('field_of_view', 75.0)
    cc.set_editor_property('constrain_aspect_ratio', False)
    res['cam'] = describe(cam)

    res['ok'] = True
    res['note'] = 'NOT SAVED. lock + save: %s' % json.dumps(
        sorted({g.get_outermost().get_name(), wreck.get_outermost().get_name(),
                card.get_outermost().get_name(), cam.get_outermost().get_name(),
                floor.get_outermost().get_name()}))
except SystemExit:
    res['ok'] = True
except Exception as e:
    res['ok'] = False
    res['error'] = '%r\n%s' % (e, traceback.format_exc())
with open(os.path.join(OUT, 'b1x_actors.json'), 'w') as fh:
    json.dump(res, fh, indent=1)
print('B1X ACTORS %s ok=%s' % (MODE, res.get('ok')))
