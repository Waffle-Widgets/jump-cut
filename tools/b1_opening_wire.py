"""Beat 1 opening: place the objective beacon, set BP_OpeningDirector's class defaults, and wire
the placed director to the actors it drives.

    py <repo>/tools/b1_opening_wire.py            place + wire
    py <repo>/tools/b1_opening_wire.py report     read it all back, change nothing

Run AFTER b1_opening_cine.py and b1_opening_actors.py. Never saves.

The beacon is a plain unlit sphere the director teleports to whatever the current objective is -
one actor for all three objectives, rather than three markers to keep in step. 230 cm up so it
clears the driver's body and the counter and is visible from the far end of the room.
"""
import unreal, os, sys

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
log = []
def say(s):
    log.append(str(s)); print(str(s))

TAG = 'B1_Cine'
BP_PATH = '/Game/Game/Blueprints/BP_OpeningDirector'
SPHERE = '/Engine/BasicShapes/Sphere.Sphere'
BEACON_MAT = '/Game/Game/Materials/M_PropBlue'

DEFAULTS = {
    'CinePlayOpening': True,
    'CineLength': 11.0,
    'CineImpactTime': 4.70,
    'CineBodyTime': 6.45,
    'CineEndYaw': 172.0,
    'ObjectiveHeight': 230.0,
    'ObjectiveState': 0,
    'ObjDriverLoc': unreal.Vector(-380.0, 220.0, 0.0),   # the crash driver
    # 430 is 950 cm from the car against a 700 cm blast - clear, with margin, and still inside
    # the room so the player is never told to walk through a wall.
    'ObjSafeLoc': unreal.Vector(430.0, -40.0, 0.0),
    'ObjStreetLoc': unreal.Vector(820.0, 0.0, 0.0),      # out of the door, onto the street
    'ObjStreetDoneX': 1200.0,                            # past this the beacon switches off
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
                                       'CineWallPatch', 'ObjectiveBeacon']:
                say('   %-18s %s' % (k, d.get_editor_property(k)))
        for lab in ('B1_Cine_WallPatch', 'B1_Cine_Seq', 'B1_Objective_Beacon'):
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
                                   unreal.Rotator())
    smc = b.static_mesh_component
    smc.set_mobility(unreal.ComponentMobility.MOVABLE)
    smc.set_static_mesh(unreal.load_asset(SPHERE))
    smc.set_material(0, unreal.load_asset(BEACON_MAT))
    smc.set_editor_property('cast_shadow', False)
    b.set_actor_scale3d(unreal.Vector(0.5, 0.5, 0.5))
    b.set_actor_enable_collision(False)
    b.set_actor_label('B1_Objective_Beacon')
    b.set_editor_property('tags', [unreal.Name(TAG)])
    b.set_actor_location_and_rotation(unreal.Vector(-380.0, 220.0, 230.0), unreal.Rotator(), False, True)
    say('B1_Objective_Beacon placed at %s scale %s' % (b.get_actor_location(), b.get_actor_scale3d()))

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
        'CineRealCar': by_label.get('City_CafeCrashCar'),
        'CineRealDriver': by_label.get('C1_Cafe_CrashDriver'),
        'CineWallPatch': by_label.get('B1_Cine_WallPatch'),
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
