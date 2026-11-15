"""Beat 1 opening: place the objective beacon, set BP_OpeningDirector's class defaults, and wire
the placed director to the actors it drives.

    py <repo>/tools/b1_opening_wire.py            place + wire
    py <repo>/tools/b1_opening_wire.py report     read it all back, change nothing

Run AFTER b1_opening_cine.py and b1_opening_actors.py. Never saves.

The beacon is a single unlit CONE, point down, that the director teleports to whatever the current
objective is - one actor for all five objectives, rather than five markers to keep in step. 230 cm
up so it clears the driver's body and the counter and is visible from the far end of the room.

It was a sphere until the owner asked for a downward cone on 2026-11-15. That change was made on the
placed actor in a live session and NOT in this script, so the next run of this script put the sphere
straight back - confirmed from a PIE capture. The shape lives here now.
"""
import unreal, os, sys

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
log = []
def say(s):
    log.append(str(s)); print(str(s))

TAG = 'B1_Cine'
BP_PATH = '/Game/Game/Blueprints/BP_OpeningDirector'
CONE = '/Engine/BasicShapes/Cone.Cone'      # +Z is the apex, so roll 180 points it down
BEACON_ROT = (180.0, 0.0, 0.0)              # (roll, pitch, yaw)
BEACON_SCALE = (0.45, 0.45, 0.75)
BEACON_MAT = '/Game/Game/Materials/M_PropBlue'

DEFAULTS = {
    'CinePlayOpening': True,
    'CineLength': 11.0,
    # 6.20 s = frame 186, where the cinematic car's transform keys STOP and the spawnable is
    # despawned. Do not lower it: at 4.70 the real wreck is revealed while the spawnable is
    # still in the air at x=-900, which is the 'two cars' defect. It was set to 6.20 live on
    # Nov 14 and this default put 4.70 straight back on the next run (reported again Nov 15).
    'CineImpactTime': 6.20,
    'CineBodyTime': 6.45,
    # 4.70 s = the frame the cinematic car reaches the wall (b1_opening_cine.CAR_KEYS). The wall
    # is a Geometry Collection now, so it comes apart here instead of a grey patch vanishing.
    'CineWallTime': 4.70,
    # the third cut is a shot of the car on its own, so that is where it catches fire (Team Owner,
    # 2026-11-15). Cut C runs 6.2 -> 8.8.
    'CineFireTime': 7.00,
    'CineWallDone': False, 'CineFireDone': False, 'CineFireLit': False,
    'WallBreakStrain': 5000000.0,     # the strain a punch uses on a crate stack
    'WallBreakImpulse': 420.0,        # cm/s outward, bVelChange, from a point OUTSIDE the wall
    # the thrown body is a ragdoll from the frame it lands. Off = the old keyframed landing pose.
    'DriverRagdoll': True,
    # 1.8 s of free physics is what carried him off the intended spot. The arc now lands him
    # where he belongs, so the ragdoll only has to do the slump.
    'RagdollSettle': 1.2,
    'RagdollT': 0.0, 'RagdollOn': False, 'RagdollDone': False,
    'CineEndYaw': 172.0,
    'ObjectiveHeight': 230.0,
    'ObjectiveState': 0,
    # The car drives in heading +X, so its RIGHT side is -Y - and that is also screen-right from
    # where the player stands. He used to land at y +220, the car's left. Moved 2026-11-15.
    #
    # Moved AGAIN 2026-11-15 ("the ragdoll went to a place that was hard to get to"). The old
    # (-395, -215) is inside City_Cafe_00_CafeCounter's footprint (x -584..-76, y -285..-196):
    # measured with real traces by tools/b1w_spot.py, the floor there is at z = 150 - the COUNTER
    # TOP - and a player capsule neither fits nor can reach it. The body was being thrown onto the
    # service side of the bar, which is the whole complaint.
    #
    # (-300, -60) is open cafe floor at z = 2.0, on the player's side of the counter, in the
    # corridor between the wreck's right flank and the bar. Two numbers chose it over the first
    # candidate (-200, -60), and both were measured in PIE rather than reasoned about:
    #   * a settled ragdoll's MASS ends about 55 cm +X / -Y of the actor's origin (the body
    #     collapses out of a head-down pose), so the spot has to leave that much room towards
    #     the counter or his legs end up inside it;
    #   * BP_CrashDriver.TouchRange is a plain XY distance from the PLAYER, and the player starts
    #     at the origin. At (-200, -60) that distance is 209 against a range of 220, so Freeze
    #     Frame was granted on the first frame after the cinematic and "walk over and check on
    #     him" stopped existing. Measured: objective jumped straight to 3 with the player still
    #     standing at (0, 0, 94). TouchRange comes down to 120 below to keep the walk real.
    'ObjDriverLoc': unreal.Vector(-300.0, -60.0, 0.0),  # the crash driver
    # 430 is 950 cm from the car against a 700 cm blast - clear, with margin, and still inside
    # the room so the player is never told to walk through a wall.
    'ObjSafeLoc': unreal.Vector(430.0, -40.0, 0.0),
    'ObjStreetLoc': unreal.Vector(820.0, 0.0, 0.0),      # out of the door, onto the street
    'ObjStreetDoneX': 1200.0,                            # past this the beacon switches off
    # --- the explosion-and-pan cinematic (b1x_graphs.py). Four poses, three lerps: A holds on the
    # wreck as it comes apart, B->C swings off it, C->D settles looking out of the cafe door.
    'ExplTB': 1.8, 'ExplTC': 3.6, 'ExplTD': 5.2,
    'ExplSayAt': 2.6,                                    # the voice speaks as the camera reaches the door
    'ExplFlashSecs': 1.6,                                # 36 frames of T_FX_Explosion_6x6 at 22.5 fps
    'ExplCardMin': 6.0, 'ExplCardMax': 11.0,             # the fireball card grows 600 -> 1100 cm
    'ExplBlastStrain': 5000000.0,                        # same strain a punch uses on a crate stack
    # 900 threw the debris 30 m across the room and out through the walls; 350 keeps it in the cafe
    'ExplBlastImpulse': 350.0,                           # cm/s outward, bVelChange
    'ExplCamALoc': unreal.Vector(120.0, 330.0, 240.0),
    'ExplCamARot': unreal.Rotator(0.0, -11.8, -152.7),
    'ExplCamBLoc': unreal.Vector(110.0, 300.0, 232.0),
    'ExplCamBRot': unreal.Rotator(0.0, -11.5, -154.5),
    'ExplCamCLoc': unreal.Vector(150.0, 190.0, 222.0),
    'ExplCamCRot': unreal.Rotator(0.0, -9.0, -80.0),
    'ExplCamDLoc': unreal.Vector(180.0, 60.0, 210.0),
    'ExplCamDRot': unreal.Rotator(0.0, -8.8, -5.4),
    'ExplCine': False, 'ExplDone': False, 'ExplSaid': False, 'ExplT': 0.0,
    # --- beats 2 and 3: the goons on the street, then the boss
    'ObjGoonLoc': unreal.Vector(4600.0, 0.0, 0.0),       # Spawner_Street
    'ObjBossLoc': unreal.Vector(8120.0, 0.0, 0.0),       # Boss_Freeze / Marker_BossSpot
    'ObjBossDoneX': 7600.0,
    # Spawner_Beat4 stands at x = 12900 and fills its group at BeginPlay, so the goon count has to
    # be fenced to the beat-2 stretch or it never reaches zero.
    'GoonZoneMaxX': 6500.0,
    'GoonsSeen': False, 'GoonsLeftNow': 0,
}

# BP_Coworker's fire hazard. Set on the CDO *and* on the placed actor: a placed actor keeps its
# own serialized value, and Coworker_Cafe has already been bitten by exactly that once
# (AutoFreezeOnExplosion/ExplosionDelay came back zero-initialised after a variable was added).
COWORKER_DEFAULTS = {
    'UseFireHazard': True,
    'BlastRadius': 700.0,
    'FuseSeconds': 9.0,
    'HoldSpeed': 560.0,
    'HoldStopDist': 120.0,
    'BlastPlayerDamage': 30.0,
    'FireLit': False,
    'Blown': False,
    'Holding': False,
    'FuseLeft': 0.0,
    'FireFlicker': 0.0,
    'BlastOrigin': unreal.Vector(-520.0, 0.0, 0.0),
}

MODE = 'wire'
for a in sys.argv[1:]:
    if a in ('wire', 'report'):
        MODE = a

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    if ues.get_editor_world().get_name() != 'Lvl_JumpCut':
        raise RuntimeError('wrong world')
    if ues.get_game_world() is not None:
        raise RuntimeError('PIE is running - stop it first')
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    acts = list(eas.get_all_level_actors())
    by_label = {}
    for a in acts:
        by_label[a.get_actor_label()] = a

    cls = unreal.load_class(None, '%s.%s_C' % (BP_PATH, 'BP_OpeningDirector'))
    if cls is None:
        raise RuntimeError('BP_OpeningDirector_C not loadable - compile it first')

    if MODE == 'report':
        cdo = unreal.get_default_object(cls)
        say('--- class defaults')
        for k in DEFAULTS:
            say('   %-18s %s' % (k, cdo.get_editor_property(k)))
        d = by_label.get('B1_Cine_Director')
        if d:
            say('--- placed B1_Cine_Director')
            for k in list(DEFAULTS) + ['CineSeqActor', 'CineRealCar', 'CineRealDriver',
                                       'CineWallGC', 'CineFireActor', 'CineFireLight',
                                       'CineFireFX', 'CineDriverBP', 'ObjectiveBeacon',
                                       'ExplCam', 'ExplCard', 'ExplCarGC']:
                say('   %-18s %s' % (k, d.get_editor_property(k)))
        for lab in ('B1_Cafe_WallPanel_GC', 'B1_Cine_Seq', 'B1_Objective_Beacon',
                    'B1_Cine_ExplCam', 'B1_Cafe_Explosion', 'B1_Cafe_CrashCar_GC'):
            a = by_label.get(lab)
            say('%-22s %s' % (lab, (a.get_actor_location() if a else 'MISSING')))
        raise SystemExit

    # ---------------- class defaults
    cdo = unreal.get_default_object(cls)
    for k, v in DEFAULTS.items():
        cdo.set_editor_property(k, v)
    say('class defaults set on %s' % cdo.get_name())
    for k in DEFAULTS:
        say('   %-18s %s' % (k, cdo.get_editor_property(k)))

    # ---------------- the beacon
    b = by_label.get('B1_Objective_Beacon')
    if b is not None:
        eas.destroy_actor(b)
        say('removed old beacon')
    b = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(-380.0, 220.0, 230.0),
                                   unreal.Rotator(*BEACON_ROT))
    smc = b.static_mesh_component
    smc.set_mobility(unreal.ComponentMobility.MOVABLE)
    smc.set_static_mesh(unreal.load_asset(CONE))
    smc.set_material(0, unreal.load_asset(BEACON_MAT))
    smc.set_editor_property('cast_shadow', False)
    b.set_actor_scale3d(unreal.Vector(*BEACON_SCALE))
    b.set_actor_enable_collision(False)
    b.set_actor_label('B1_Objective_Beacon')
    b.set_editor_property('tags', [unreal.Name(TAG)])
    b.set_actor_location_and_rotation(unreal.Vector(-380.0, 220.0, 230.0),
                                      unreal.Rotator(*BEACON_ROT), False, True)
    say('B1_Objective_Beacon placed at %s rot %s scale %s' % (
        b.get_actor_location(), b.get_actor_rotation(), b.get_actor_scale3d()))

    # ---------------- wire the placed director
    # Always re-place it. A placed actor keeps the class layout it was spawned with, so one
    # spawned before a variable became instance-editable refuses the write with
    # "cannot be edited on instances" - which is a stale instance, not a wrong property name.
    d = by_label.get('B1_Cine_Director')
    if d is not None:
        eas.destroy_actor(d)
        say('removed the old (stale-class) B1_Cine_Director')
    d = eas.spawn_actor_from_class(cls, unreal.Vector(0.0, 0.0, 300.0), unreal.Rotator())
    d.set_actor_label('B1_Cine_Director')
    d.set_editor_property('tags', [unreal.Name(TAG)])
    say('placed a fresh B1_Cine_Director')
    wiring = {
        'CineSeqActor': by_label.get('B1_Cine_Seq'),
        # THE WRECK IS DRAWN TWICE OVER, BY TWO DIFFERENT ACTORS, AND ONLY ONE OF THEM IS ON
        # SCREEN AT A TIME. City_CafeCrashCar is the plain static mesh - the same asset, drawn
        # the same way as every other city prop, and tie-fixed by #67 (0f9b13c). It is what the
        # opening reveals and what the player walks up to. B1_Cafe_CrashCar_GC is the geometry
        # collection, and it is only shown at the instant the blast breaks it (CineExplFire).
        #
        # Why: "the car is flickering badly" (2026-11-15). Both actors stand at (-520, 0, 0) and
        # their bounds agree to 0.1 cm, but the collection's are 0.05 cm LARGER in y and z - the
        # fracture pieces are inflated slightly outward, so along every cut line across the whole
        # body two pieces overlap by about a millimetre. That is a depth tie with real area,
        # spread over the entire car, which is the #67 mechanism at car scale. The static mesh
        # has no cut lines at all. The collection is still what explodes; it is just not what
        # stands there for the thirty seconds before.
        'CineRealCar': by_label.get('City_CafeCrashCar'),
        'ExplCarGC': by_label.get('B1_Cafe_CrashCar_GC'),
        'ExplCam': by_label.get('B1_Cine_ExplCam'),
        'ExplCard': by_label.get('B1_Cafe_Explosion'),
        'CineRealDriver': by_label.get('C1_Cafe_CrashDriver'),
        'CineWallGC': by_label.get('B1_Cafe_WallPanel_GC'),
        'CineFireActor': by_label.get('B1_Cafe_Fire'),
        'CineFireLight': by_label.get('B1_Cafe_FireLight'),
        'CineDriverBP': by_label.get('C1_Cafe_CrashDriver'),
        'ObjectiveBeacon': b,
        'DriverRef': by_label.get('C1_Cafe_CrashDriver'),
        'CoworkerRef': by_label.get('Coworker_Cafe'),
    }
    for k, v in wiring.items():
        if v is None:
            say('   !! %s has nothing to point at' % k)
            continue
        d.set_editor_property(k, v)
        back = d.get_editor_property(k)
        say('   %-16s -> %-24s  read back: %s' % (
            k, v.get_actor_label(), (back.get_actor_label() if back else 'NONE')))
    # ---------------- the fire's particle system, by COMPONENT
    # The graph DSL cannot reach a component on another actor, so the director holds the
    # NiagaraComponent itself. Niagara|SetPaused on it does both halves of the Team Owner's
    # 2026-11-15 note: paused until the third cut, so lighting it is a real burst from nothing,
    # and paused again whenever Freeze Frame is running, so the fire stops with everything else.
    fire = by_label.get('B1_Cafe_Fire')
    fx = None
    if fire is not None:
        for c in fire.get_components_by_class(unreal.NiagaraComponent):
            fx = c
            break
    if fx is None:
        say('   !! no NiagaraComponent on B1_Cafe_Fire - run b1y_firefx.py first')
    else:
        # It must not run before the director says so: auto-activate off AND paused.
        fx.set_editor_property('auto_activate', True)
        d.set_editor_property('CineFireFX', fx)
        back = d.get_editor_property('CineFireFX')
        say('   %-16s -> %-24s  read back: %s' % ('CineFireFX', fx.get_name(),
                                                  (back.get_name() if back else 'NONE')))

    # ---------------- the crash driver: the car's RIGHT side, and a mesh that can ragdoll
    drv = by_label.get('C1_Cafe_CrashDriver')
    if drv is None:
        say('   !! C1_Cafe_CrashDriver is not in the level')
    else:
        # -140 was the resting yaw for the old arc, which came in from the north-west. The body
        # now travels almost straight down the room (cab (-560, 0) -> (-200, -60), a bearing of
        # -9.5 deg), so it comes to rest lying across that line rather than along it.
        drv.set_actor_location_and_rotation(DEFAULTS['ObjDriverLoc'],
                                            unreal.Rotator(0.0, 0.0, -60.0), False, True)
        # 220 was tuned when the body lay 450 cm from the player's start. The body is closer
        # now, so the range comes down with it or there is no walk left. Set on the CDO AND on
        # the placed actor: a placed actor keeps its own serialized value.
        drv.set_editor_property('TouchRange', 120.0)
        say('   TouchRange (placed) -> %s' % drv.get_editor_property('TouchRange'))
        mesh = drv.get_component_by_class(unreal.SkeletalMeshComponent)
        if mesh is not None:
            # SetAllBodiesSimulatePhysics does nothing on a component with no collision.
            mesh.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
            say('   DriverMesh collision -> %s' % mesh.get_collision_enabled())
        say('   C1_Cafe_CrashDriver -> %s rot %s' % (drv.get_actor_location(), drv.get_actor_rotation()))

    # a set_editor_property on a placed actor does not dirty its package: re-set the transform
    d.set_actor_location_and_rotation(unreal.Vector(0.0, 0.0, 300.0), unreal.Rotator(), False, True)

    # ---------------- BP_Coworker's fire hazard
    say('')
    cw_cls = unreal.load_class(None, '/Game/Game/Blueprints/BP_Coworker.BP_Coworker_C')
    cw_cdo = unreal.get_default_object(cw_cls)
    for k, v in COWORKER_DEFAULTS.items():
        cw_cdo.set_editor_property(k, v)
    say('BP_Coworker class defaults set')
    cw = by_label.get('Coworker_Cafe')
    if cw is None:
        say('   !! Coworker_Cafe is not in the level')
    else:
        # Only the instance-editable dials can be written on a placed actor; FireLit/Blown/
        # Holding/FuseLeft/FireFlicker are runtime state and deliberately are not exposed.
        for k, v in COWORKER_DEFAULTS.items():
            if k in ('FireLit', 'Blown', 'Holding', 'FuseLeft', 'FireFlicker'):
                continue
            cw.set_editor_property(k, v)
        cw_wiring = {
            'FireActor': by_label.get('B1_Cafe_Fire'),
            'FireLight': by_label.get('B1_Cafe_FireLight'),
            'BlastRing': by_label.get('B1_Cafe_BlastRing'),
        }
        for k, v in cw_wiring.items():
            if v is None:
                say('   !! %s has nothing to point at (run b1_fire_actors.py first)' % k)
                continue
            cw.set_editor_property(k, v)
            back = cw.get_editor_property(k)
            say('   %-14s -> %-22s read back: %s' % (
                k, v.get_actor_label(), (back.get_actor_label() if back else 'NONE')))
        for k in COWORKER_DEFAULTS:
            say('   %-18s %s' % (k, cw.get_editor_property(k)))
        for k in ('ExplosionDelay', 'RescueRequiresFreeze', 'BulletTimeOnExplosion',
                  'CoworkerSafeOffset'):
            try:
                say('   (existing) %-18s %s' % (k, cw.get_editor_property(k)))
            except Exception as e:
                say('   (existing) %-18s <%s>' % (k, type(e).__name__))
        xf = cw.get_actor_transform()
        cw.set_actor_location_and_rotation(xf.translation, xf.rotation.rotator(), False, True)

    say('')
    say('NOT SAVED. Save with jc_save_actors.py and AssetTools.save_assets.')
except SystemExit:
    pass
except Exception as e:
    import traceback
    say('ERROR %r' % e); say(traceback.format_exc())
with open(os.path.join(OUT, 'b1_opening_wire.txt'), 'w') as fh:
    fh.write('\n'.join(log))
