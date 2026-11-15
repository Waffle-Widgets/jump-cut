"""Beat 1's opening cinematic: builds /Game/Game/Cinematics/LS_Beat1_Opening from this recipe.

    py <repo>/tools/b1_opening_cine.py            build (idempotent: rebuilds the sequence from scratch)
    py <repo>/tools/b1_opening_cine.py report     read back what is in the asset, change nothing

The cinematic is 11 s, 30 fps, four shots:
  A 0.0-4.0  the peaceful cafe, a slow push west down the room
  B 4.0-7.0  the car comes through the west wall
  C 6.2-8.8  the driver is thrown out of the cab, lands where BP_CrashDriver stands (the car's
             RIGHT side), and the car catches fire part-way through this shot
  D 8.8-11.0 settle behind the player, then control is handed over

EVERYTHING the sequence animates is a SPAWNABLE, so the sequence owns no level actor and leaves
nothing behind: four cine cameras, one flying car, one flying body. The REAL wreck, the REAL
BP_CrashDriver and the wall patch are hidden/shown by BP_OpeningDirector on its own clock -
deliberately NOT by a Sequencer visibility track, whose bHidden-vs-Visible sense is easy to get
backwards and hard to see.

The flying car and the flying body have collision OFF: the car's path runs straight through where
the coworker stands and a solid one would punt her across the room.

Writes JumpCut/Saved/jcpy/b1_cine_build.txt. Never saves - save with the editor/jc_save_actors.
"""
import unreal, os, sys, math

FPS = 30
LEN = 11.0
SEQ_DIR = '/Game/Game/Cinematics'
SEQ_NAME = 'LS_Beat1_Opening'
SEQ_PATH = '%s/%s' % (SEQ_DIR, SEQ_NAME)

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
if not os.path.isdir(OUT):
    os.makedirs(OUT)
log = []
def say(s):
    log.append(str(s))
    print(str(s))

def flush(name='b1_cine_build.txt'):
    with open(os.path.join(OUT, name), 'w') as fh:
        fh.write('\n'.join(log))

MODE = 'build'
for a in sys.argv[1:]:
    if a in ('build', 'report'):
        MODE = a

# ---------------------------------------------------------------- camera moves
# (label, [(t, x, y, z, roll, pitch, yaw), ...], focal_mm)
CAMS = [
    ('CineCam_A_Peace', [
        (0.0,  470.0, -300.0, 195.0, 0.0, -4.0, 158.0),
        (4.2,  300.0, -140.0, 178.0, 0.0, -3.0, 172.0)], 22.0),
    ('CineCam_B_Crash', [
        (3.9,  130.0, 300.0, 125.0, 0.0, -1.0, 196.0),
        (4.60, 125.0, 300.0, 125.0, 0.0, -1.0, 197.0),
        (4.70, 118.0, 296.0, 131.0, 2.5, -3.5, 199.5),   # the hit
        (4.82, 122.0, 303.0, 120.0, -2.0, 0.5, 195.0),
        (4.95, 117.0, 298.0, 127.0, 1.2, -2.0, 198.5),
        (5.20, 112.0, 300.0, 124.0, 0.0, -2.0, 198.0),
        (7.10,  80.0, 300.0, 122.0, 0.0, -3.0, 201.0)], 24.0),
    ('CineCam_C_Body', [
        (6.10, -70.0, 430.0, 165.0, 0.0, -7.0, 243.0),
        (8.90, -40.0, 400.0, 140.0, 0.0, -9.0, 238.0)], 28.0),
    # Ends on CineEndYaw (172) so the hand-off to the player's own camera does not snap, and so
    # the player is already looking at the body he is being told to go and check.
    ('CineCam_D_Hand', [
        (8.70, 345.0, 35.0, 238.0, 0.0, -9.0, 176.0),
        (11.0, 250.0, 10.0, 216.0, 0.0, -7.0, 172.0)], 26.0),
]

# camera cut ranges (binding label, start s, end s)
CUTS = [
    ('CineCam_A_Peace', 0.0, 4.0),
    ('CineCam_B_Crash', 4.0, 6.2),
    ('CineCam_C_Body',  6.2, 8.8),
    ('CineCam_D_Hand',  8.8, LEN),
]

# the car: still outside, then through the wall, then settles
CAR_KEYS = [
    (0.0,   -2400.0, 0.0,   0.0,  0.0, 0.0, 0.0),
    (4.55,  -1500.0, 0.0,   0.0,  0.0, 0.0, 0.0),
    (4.70,   -900.0, 0.0,   6.0,  1.5, 1.0, 1.5),   # bursting the wall
    (4.95,   -610.0, 0.0,  14.0, -2.0, 2.5, -2.0),
    (5.20,   -470.0, 0.0,   6.0,  1.0, -1.5, 2.5),  # overshoot
    (5.60,   -512.0, 0.0,   1.0, -0.4, 0.4, -0.8),  # rock back
    (6.20,   -520.0, 0.0,   0.0,  0.0, 0.0, 0.0),   # at rest = the placed wreck
]

log.append('')
TEMPS = []   # every throwaway actor, destroyed in the finally below

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = ues.get_editor_world()
    if world.get_name() != 'Lvl_JumpCut':
        raise RuntimeError('wrong world: %s' % world.get_name())
    if ues.get_game_world() is not None:
        raise RuntimeError('PIE is running - stop it first')
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    # ---- find the real actors we copy from
    real_car = real_driver = None
    for a in eas.get_all_level_actors():
        lab = a.get_actor_label()
        if lab == 'City_CafeCrashCar':
            real_car = a
        elif lab == 'C1_Cafe_CrashDriver':
            real_driver = a
    if real_car is None or real_driver is None:
        raise RuntimeError('could not find City_CafeCrashCar / C1_Cafe_CrashDriver')

    car_smc = real_car.get_component_by_class(unreal.StaticMeshComponent)
    car_mesh = car_smc.static_mesh
    car_mats = [car_smc.get_material(i) for i in range(len(car_smc.get_materials()))]
    car_xf = real_car.get_actor_transform()
    say('real car   : mesh=%s  loc=%s  rot=%s' % (
        car_mesh.get_path_name(), car_xf.translation, car_xf.rotation.rotator()))

    drv_skc = real_driver.get_component_by_class(unreal.SkeletalMeshComponent)
    drv_mesh = drv_skc.skeletal_mesh if hasattr(drv_skc, 'skeletal_mesh') else drv_skc.get_skeletal_mesh_asset()
    drv_mats = [drv_skc.get_material(i) for i in range(len(drv_skc.get_materials()))]
    drv_loc = real_driver.get_actor_location()
    drv_rot = real_driver.get_actor_rotation()
    drv_rel = drv_skc.get_relative_transform()
    say('real driver: mesh=%s  loc=%s  rot=(r%.1f p%.1f y%.1f)' % (
        drv_mesh.get_path_name() if drv_mesh else None, drv_loc, drv_rot.roll, drv_rot.pitch, drv_rot.yaw))
    say('   DriverMesh relative: loc=%s rot=%s' % (drv_rel.translation, drv_rel.rotation.rotator()))

    if MODE == 'report':
        s = unreal.load_asset(SEQ_PATH)
        if s is None:
            say('NO SEQUENCE at %s' % SEQ_PATH)
        else:
            say('')
            say('sequence %s  %0.2f..%0.2f s  rate=%s' % (
                SEQ_PATH, s.get_playback_start_seconds(), s.get_playback_end_seconds(), s.get_display_rate()))
            for b in s.get_bindings():
                say('  binding %-22s tracks=%d' % (b.get_name(), len(b.get_tracks())))
                for t in b.get_tracks():
                    for sec in t.get_sections():
                        chans = sec.get_all_channels()
                        say('      %-30s %7.2f..%7.2f  channels=%d keys=%s' % (
                            t.get_class().get_name(), sec.get_start_frame_seconds(),
                            sec.get_end_frame_seconds(), len(chans),
                            [c.get_num_keys() for c in chans]))
            for t in s.get_tracks():
                say('  master track %s' % t.get_class().get_name())
                for sec in t.get_sections():
                    say('      %7.2f..%7.2f' % (sec.get_start_frame_seconds(), sec.get_end_frame_seconds()))
        flush('b1_cine_report.txt')
        raise SystemExit

    # ---- make (or wipe) the sequence
    old = unreal.load_asset(SEQ_PATH)
    if old is not None:
        say('')
        say('existing sequence found - wiping its tracks and bindings')
        for t in list(old.get_tracks()):
            old.remove_track(t)
        for b in list(old.get_bindings()):
            b.remove()
        seq = old
    else:
        at = unreal.AssetToolsHelpers.get_asset_tools()
        seq = at.create_asset(SEQ_NAME, SEQ_DIR, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
        say('')
        say('created %s' % seq.get_path_name())

    seq.set_display_rate(unreal.FrameRate(FPS, 1))
    seq.set_playback_start_seconds(0.0)
    seq.set_playback_end_seconds(LEN)

    def fr(t):
        return unreal.FrameNumber(int(round(t * FPS)))

    def key_transform(binding, keys, label):
        """keys: [(t, x, y, z, roll, pitch, yaw)] -> a 3D transform section covering the sequence."""
        tr = binding.add_track(unreal.MovieScene3DTransformTrack)
        sec = tr.add_section()
        sec.set_range_seconds(0.0, LEN)
        ch = sec.get_all_channels()
        names = [str(c.channel_name) for c in ch]
        if label == 'first':
            say('   transform channels: %s' % names)
        order = [1, 2, 3, 4, 5, 6]  # x,y,z,roll,pitch,yaw -> channels 0..5
        for k in keys:
            t = k[0]
            for ci, vi in enumerate(order):
                ch[ci].add_key(fr(t), float(k[vi]),
                               interpolation=unreal.MovieSceneKeyInterpolation.AUTO)
        return sec

    first = True
    cam_bindings = {}
    for name, keys, focal in CAMS:
        tmp = eas.spawn_actor_from_class(unreal.CineCameraActor,
                                         unreal.Vector(keys[0][1], keys[0][2], keys[0][3]),
                                         unreal.Rotator(keys[0][4], keys[0][5], keys[0][6]))
        TEMPS.append(tmp)
        tmp.set_actor_label(name)
        cc = tmp.get_cine_camera_component()
        cc.set_editor_property('current_focal_length', focal)
        fs = cc.get_editor_property('focus_settings')
        fs.set_editor_property('focus_method', unreal.CameraFocusMethod.DISABLE)
        cc.set_editor_property('focus_settings', fs)
        b = seq.add_spawnable_from_instance(tmp)
        b.set_name(name)
        key_transform(b, keys, 'first' if first else name)
        first = False
        cam_bindings[name] = b
        eas.destroy_actor(tmp)
        say('   camera %-18s %d keys  focal %.0fmm' % (name, len(keys), focal))

    # ---- the flying car
    tmp = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(-2400, 0, 0), unreal.Rotator())
    TEMPS.append(tmp)
    tmp.set_actor_label('CineCar')
    smc = tmp.static_mesh_component
    smc.set_mobility(unreal.ComponentMobility.MOVABLE)
    smc.set_static_mesh(car_mesh)
    for i, m in enumerate(car_mats):
        if m:
            smc.set_material(i, m)
    tmp.set_actor_enable_collision(False)
    smc.set_editor_property('cast_shadow', True)
    car_b = seq.add_spawnable_from_instance(tmp)
    car_b.set_name('CineCar')
    key_transform(car_b, CAR_KEYS, 'CineCar')
    eas.destroy_actor(tmp)
    say('   CineCar           %d keys, collision OFF, movable' % len(CAR_KEYS))

    # ---- the flying body: arc from the cab to exactly where BP_CrashDriver stands
    dx, dy, dz = drv_loc.x, drv_loc.y, drv_loc.z
    # A SkeletalMeshActor's SkeletalMeshComponent IS its root, so set_relative_transform on it
    # is the actor transform and the transform track overwrites it every frame - which is why the
    # first build had him standing bolt upright in mid-air. The real BP_CrashDriver renders at
    # actor yaw 140 with the mesh at relative pitch -78 and +18 z; a rotator is applied
    # Yaw*Pitch*Roll, so actor rot (roll 0, pitch -78, yaw 140) at z = +18 is the SAME world pose.
    # The last key is therefore exactly where the real body appears, and the hand-off is seamless.
    # He is thrown out of the car's RIGHT side (-Y), not its left: asked for on 2026-11-15, and
    # -Y is also screen-right from where the player is standing. The arc is mirrored in y and the
    # tumble roll with it, and it ends exactly where the placed BP_CrashDriver stands - from which
    # frame the REAL one takes over as a ragdoll (BP_OpeningDirector.DriverRagdoll).
    DRV_KEYS = [
        (0.0,   -2350.0,    0.0,  60.0,   0.0, -78.0,  10.0),   # slumped in the cab, off screen
        (4.55,  -1450.0,    0.0,  60.0,   0.0, -78.0,  10.0),   # riding in
        (4.95,   -560.0,    0.0,  70.0,   0.0, -78.0,  10.0),   # the cab, at the moment of impact
        (5.10,   -505.0,  -40.0, 150.0,  60.0, -70.0, -20.0),   # out through the screen
        (5.40,   -462.0, -118.0, 250.0, 170.0, -50.0, -70.0),   # apex, tumbling
        (5.75,   -428.0, -172.0, 150.0, 280.0, -60.0, -112.0),
        (6.00,   -406.0, -200.0,  45.0, 340.0, -72.0, -133.0),
        (6.20,       dx,     dy,  26.0, 360.0, -78.0, drv_rot.yaw),
        (6.45,       dx,     dy,  18.0, 360.0, -78.0, drv_rot.yaw),
    ]
    tmp = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(-470, 10, 185), unreal.Rotator())
    TEMPS.append(tmp)
    tmp.set_actor_label('CineDriver')
    sk = tmp.skeletal_mesh_component
    sk.set_mobility(unreal.ComponentMobility.MOVABLE)
    try:
        sk.set_skeletal_mesh_asset(drv_mesh)
    except Exception:
        sk.set_editor_property('skeletal_mesh_asset', drv_mesh)
    for i, m in enumerate(drv_mats):
        if m:
            sk.set_material(i, m)
    sk.set_relative_transform(drv_rel, False, False)
    tmp.set_actor_enable_collision(False)
    drv_b = seq.add_spawnable_from_instance(tmp)
    drv_b.set_name('CineDriver')
    key_transform(drv_b, DRV_KEYS, 'CineDriver')
    eas.destroy_actor(tmp)
    say('   CineDriver        %d keys, lands at %s rot(r%.1f p%.1f y%.1f)' % (
        len(DRV_KEYS), drv_loc, drv_rot.roll, drv_rot.pitch, drv_rot.yaw))

    # ---- camera cuts
    cut = seq.add_track(unreal.MovieSceneCameraCutTrack)
    for name, a, b in CUTS:
        sec = cut.add_section()
        sec.set_range_seconds(a, b)
        sec.set_camera_binding_id(seq.get_binding_id(cam_bindings[name]))
        say('   cut %-18s %5.2f -> %5.2f' % (name, a, b))

    say('')
    say('built: %d bindings, %d master tracks, %0.1f s at %d fps'
        % (len(seq.get_bindings()), len(seq.get_tracks()), LEN, FPS))
    say('NOT SAVED. Save /Game/Game/Cinematics/LS_Beat1_Opening before committing.')
except SystemExit:
    pass
except Exception as e:
    import traceback
    say('ERROR %r' % e)
    say(traceback.format_exc())
finally:
    # A throwaway that outlives a failed run becomes a REAL actor in the level that nothing
    # else cleans up - the first run left a CineDriver standing in mid-air in the cafe, visible
    # in the peaceful shot, and it took a screenshot to find. Never leave cleanup to the
    # happy path.
    left = 0
    try:
        eas2 = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        alive = set(a.get_name() for a in eas2.get_all_level_actors())
        for t in TEMPS:
            try:
                if t.get_name() in alive:
                    eas2.destroy_actor(t)
                    left += 1
            except Exception:
                pass
    except Exception:
        pass
    if left:
        say('finally: destroyed %d throwaway actor(s) a failure had left behind' % left)
flush()
