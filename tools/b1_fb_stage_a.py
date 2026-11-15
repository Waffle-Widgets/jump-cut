"""Nov 14 feedback, stage A: the two cars, and the objective marker.

    py <repo>/tools/b1_fb_stage_a.py report     read back, change nothing
    py <repo>/tools/b1_fb_stage_a.py apply      make the changes (does NOT save)

1 (two cars) The cinematic car's transform keys stop moving at frame 186 (6.20 s) at
  exactly (-520, 0, 0) rot 0 - the real wreck's placed transform. The director was
  revealing the real wreck at CineImpactTime 4.70 s (frame 141), while the spawnable
  was still in the air at x=-900, so both were on screen for 1.5 s. Reveal moves to
  6.20 s and the CineCar spawnable is despawned on that same frame, so they never
  coexist (two identical coincident meshes would also be a perfect depth tie - #67).
  The thrown body despawns on the frame the real one appears, for the same reason.

3 (markers) B1_Objective_Beacon becomes a cone pointing down. The other spheres at the
  first objective are switched off.
"""
import unreal, os, sys

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
SEQ = '/Game/Game/Cinematics/LS_Beat1_Opening'
DIR_BP = '/Game/Game/Blueprints/BP_OpeningDirector'
CONE = '/Engine/BasicShapes/Cone.Cone'

CAR_SETTLE_FRAME = 186      # 6.20 s at 30 fps
BODY_SWAP_FRAME = 194       # 6.4667 s - the frame the real body appears
NEW_IMPACT_TIME = 6.20

MODE = 'report'
for a in sys.argv[1:]:
    if a in ('report', 'apply'):
        MODE = a

L = []
def say(s): L.append(str(s)); print(str(s))

def finish():
    open(os.path.join(OUT, 'b1_fb_stage_a.txt'), 'w').write('\n'.join(L))

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    if ues.get_editor_world().get_name() != 'Lvl_JumpCut':
        raise RuntimeError('wrong world')
    if ues.get_game_world() is not None:
        raise RuntimeError('PIE is running - stop it first')
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = {a.get_actor_label(): a for a in eas.get_all_level_actors()}

    # ---- what the spawnable car template actually is, and where the real wreck is ----
    seq = unreal.load_asset(SEQ)
    binds = {b.get_name(): b for b in seq.get_bindings()}
    car_b, body_b = binds.get('CineCar'), binds.get('CineDriver')
    tmpl = car_b.get_object_template()
    tm = None
    for c in tmpl.get_components_by_class(unreal.StaticMeshComponent):
        tm = c.get_editor_property('static_mesh')
    say('CineCar template mesh = %s  scale=%s' % (tm.get_name() if tm else None, tmpl.get_actor_scale3d()))
    real = actors.get('City_CafeCrashCar')
    rm = None
    for c in real.get_components_by_class(unreal.StaticMeshComponent):
        rm = c.get_editor_property('static_mesh')
    say('real wreck  mesh = %s  loc=%s rot=%s scale=%s' % (
        rm.get_name() if rm else None, real.get_actor_location(),
        real.get_actor_rotation(), real.get_actor_scale3d()))

    # ---- what is visible around the first objective ----
    say('\n-- actors with a visible mesh within 450 cm of the driver --')
    drv = actors.get('C1_Cafe_CrashDriver')
    dloc = drv.get_actor_location()
    for a in eas.get_all_level_actors():
        if (a.get_actor_location() - dloc).length() > 450:
            continue
        parts = []
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            m = c.get_editor_property('static_mesh')
            parts.append('SM:%s vis=%s hid=%s' % (m.get_name() if m else None,
                         c.is_visible(), c.get_editor_property('hidden_in_game')))
        for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
            m = c.get_editor_property('skeletal_mesh_asset')
            parts.append('SK:%s vis=%s hid=%s' % (m.get_name() if m else None,
                         c.is_visible(), c.get_editor_property('hidden_in_game')))
        if parts:
            say('  %-26s actorHidden=%s  %s' % (a.get_actor_label(), a.get_editor_property('hidden'), ' | '.join(parts)))

    # ---- the director's reveal times ----
    bp = unreal.load_asset(DIR_BP)
    cdo = unreal.get_default_object(bp.generated_class())
    pa = actors.get('B1_Cine_Director')
    for n in ('CineImpactTime', 'CineBodyTime', 'CineLength'):
        say('%-16s cdo=%s placed=%s' % (n, cdo.get_editor_property(n), pa.get_editor_property(n)))

    if MODE == 'report':
        finish(); raise SystemExit

    # ================= apply =================
    say('\n== applying ==')

    # 1a. reveal the real wreck when the cinematic one has stopped
    cdo.set_editor_property('CineImpactTime', NEW_IMPACT_TIME)
    try:
        pa.set_editor_property('CineImpactTime', NEW_IMPACT_TIME)
        say('CineImpactTime placed -> %s' % pa.get_editor_property('CineImpactTime'))
    except Exception as e:
        say('CineImpactTime placed REFUSED: %s' % e)
    say('CineImpactTime cdo    -> %s' % cdo.get_editor_property('CineImpactTime'))

    # 1b. despawn each spawnable on the frame its real counterpart appears
    def set_spawn_off(binding, frame):
        for t in binding.get_tracks():
            if not isinstance(t, unreal.MovieSceneSpawnTrack):
                continue
            for s in t.get_sections():
                for ch in s.get_all_channels():
                    for k in list(ch.get_keys()):
                        ch.remove_key(k)
                    ch.add_key(unreal.FrameNumber(0), True)
                    ch.add_key(unreal.FrameNumber(frame), False)
                    say('%s spawn keys -> %s' % (binding.get_name(),
                        [(k.get_time().frame_number.value, k.get_value()) for k in ch.get_keys()]))
    set_spawn_off(car_b, CAR_SETTLE_FRAME)
    set_spawn_off(body_b, BODY_SWAP_FRAME)

    # 3. the objective beacon becomes a cone pointing down
    bc = actors.get('B1_Objective_Beacon')
    cone = unreal.load_asset(CONE)
    if cone is None:
        raise RuntimeError('no cone mesh at %s' % CONE)
    for c in bc.get_components_by_class(unreal.StaticMeshComponent):
        keep = list(c.get_editor_property('override_materials'))
        if not keep:
            keep = [c.get_material(0)]
        c.set_static_mesh(cone)
        for i, m in enumerate(keep):
            if m:
                c.set_material(i, m)
        say('beacon mesh -> %s  material -> %s' % (cone.get_name(), [m.get_name() if m else None for m in keep]))
    t = bc.get_actor_transform()
    bc.set_actor_transform(unreal.Transform(
        t.translation, unreal.Rotator(0.0, 180.0, 0.0), unreal.Vector(0.45, 0.45, 0.7)), False, False)
    say('beacon transform -> loc=%s rot=%s scale=%s' % (
        bc.get_actor_location(), bc.get_actor_rotation(), bc.get_actor_scale3d()))

    # 3b. the second sphere at the first objective is the crash driver's OWN prototype
    #     sphere component, standing inside his body mesh. The two Marker_* spheres
    #     nearby are already invisible (vis=False), so they are not it. The coworker
    #     carries the identical leftover at the next objective - same fix, same pass.
    for lab in ('C1_Cafe_CrashDriver', 'Coworker_Cafe'):
        a = actors.get(lab)
        if a is None:
            say('%s: not in level' % lab); continue
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            m = c.get_editor_property('static_mesh')
            if m is None or m.get_name() != 'Sphere':
                continue
            c.set_visibility(False, False)
            c.set_hidden_in_game(True, False)
            say('%s.%s (Sphere) vis=%s hid=%s' % (lab, c.get_name(),
                c.is_visible(), c.get_editor_property('hidden_in_game')))
        tr = a.get_actor_transform()
        a.set_actor_transform(tr, False, False)   # dirty the package

    say('\n-- packages to lock + save --')
    for lab in ('B1_Objective_Beacon', 'B1_Cine_Director', 'C1_Cafe_CrashDriver', 'Coworker_Cafe'):
        a = actors.get(lab)
        if a is not None:
            say('  %-24s %s' % (lab, a.get_outermost().get_name()))
    say('  asset %s' % SEQ)
    say('  asset %s' % DIR_BP)

    say('\nDONE (nothing saved - run jc_save_actors.py / save the assets)')
    finish()
except SystemExit:
    pass
except Exception as e:
    import traceback
    say('FAILED: %s' % e); say(traceback.format_exc()); finish()
