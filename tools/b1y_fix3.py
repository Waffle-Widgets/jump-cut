"""Feedback item 3: one car, and the car has its textures.

(a) TEXTURES. Every Geometry Collection in /Game/Game/Destruction draws the materials its source FBX
    came in with - MS_City* in Imported/City, which are MaterialInstanceConstants of
    FBXLegacyPhongSurfaceMaterial with DiffuseColor 0.8: Unreal's flat grey import placeholder. The
    real look materials are M_City* in Materials/City, and every placed City_* STATIC actor overrides
    to them per slot (measured: 0 static actors draw an MS_ directly). Nothing told the collections.
    So MS_<Name> -> M_<Name>, slot for slot, on the collection ASSET, which fixes every actor using it.
    This affects the exploding car (7 slots, on camera in a cinematic) and also the cafe tables,
    barriers and crate stacks that shatter in beats 2-3.

(b) TWO CARS. CineImpactTime is the moment the director reveals the real wreck. The cinematic car's
    keys stop at frame 186 = 6.20 s, so 6.20 is the only correct value; b1_fb_stage_a.py set it on
    Nov 14 and the later run of b1_opening_wire.py put its 4.70 default straight back (CLAUDE.md:
    a change made only on a placed actor is reverted by the next run of the script that places it).
    At 4.70 the wreck appears while the spawnable is still in the air at x=-900: two cars for 1.5 s.
    Fixed here on the CDO and the placed actor, and in b1_opening_wire.py's DEFAULTS by hand.

    py <repo>/tools/b1y_fix3.py          report
    py <repo>/tools/b1y_fix3.py apply    change it, save, read back
Writes Saved/jcpy/b1y_fix3.json.
"""
import unreal, os, sys, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
MODE = sys.argv[1] if len(sys.argv) > 1 else 'report'
IMPACT = 6.20
SRC = '/Game/Game/Imported/City/MS_'
DST = '/Game/Game/Materials/City/M_'
GCS = ['GC_CrashCar', 'GC_CafeTable', 'GC_Barrier', 'GC_CrateStack']
res = {'mode': MODE}

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    assert ues.get_game_world() is None, 'PIE is running - stop it first'
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    allac = eas.get_all_level_actors()
    pkgs = []

    # ---------------- (a) geometry collection materials ----------------
    gcrows = {}
    for n in GCS:
        p = '/Game/Game/Destruction/' + n
        a = unreal.load_asset(p)
        if a is None:
            gcrows[n] = 'NOT FOUND'
            continue
        before = [(m.get_path_name() if m else None) for m in a.get_editor_property('materials')]
        want = []
        for m in before:
            if m and m.startswith(SRC):
                short = m.split('.')[0].split('/')[-1][3:]          # MS_CityWall -> CityWall
                repl = unreal.load_asset(DST + short)
                want.append(repl if repl is not None else unreal.load_asset(m.split('.')[0]))
            else:
                want.append(unreal.load_asset(m.split('.')[0]) if m else None)
        row = {'before': [None if m is None else m.split('.')[0].split('/')[-1] for m in before],
               'after_wanted': [None if m is None else m.get_name() for m in want]}
        if MODE == 'apply' and row['before'] != row['after_wanted']:
            a.set_editor_property('materials', want)
            got = [(m.get_path_name() if m else None) for m in a.get_editor_property('materials')]
            row['after_read'] = [None if m is None else m.split('.')[0].split('/')[-1] for m in got]
            row['took'] = row['after_read'] == row['after_wanted']
            pkgs.append(a.get_outermost())
        gcrows[n] = row
    res['collections'] = gcrows

    # ---------------- (b) the reveal time ----------------
    bp = unreal.load_asset('/Game/Game/Blueprints/BP_OpeningDirector')
    cdo = unreal.get_default_object(bp.generated_class())
    pa = None
    for x in allac:
        if x.get_class().get_name() == 'BP_OpeningDirector_C':
            pa = x
            break
    t = {'cdo_before': cdo.get_editor_property('CineImpactTime'),
         'placed_before': pa.get_editor_property('CineImpactTime') if pa else None,
         'placed_label': pa.get_actor_label() if pa else None,
         'placed_pkg': pa.get_outermost().get_name() if pa else None}
    if MODE == 'apply':
        cdo.set_editor_property('CineImpactTime', IMPACT)
        t['cdo_after'] = cdo.get_editor_property('CineImpactTime')
        pkgs.append(bp.get_outermost())
        if pa:
            pa.modify()
            pa.set_editor_property('CineImpactTime', IMPACT)
            t['placed_after'] = pa.get_editor_property('CineImpactTime')
            pkgs.append(pa.get_outermost())
    res['impact'] = t

    # ---------------- save, then read back off what the ACTORS draw ----------------
    if MODE == 'apply' and pkgs:
        uniq = []
        for p in pkgs:
            if p not in uniq:
                uniq.append(p)
        res['saved'] = bool(unreal.EditorLoadingAndSavingUtils.save_packages(uniq, False))
        res['packages'] = [p.get_name() for p in uniq]
    live = {}
    for x in allac:
        c = x.get_component_by_class(unreal.GeometryCollectionComponent)
        if c is None:
            continue
        live[x.get_actor_label()] = [(c.get_material(i).get_path_name().split('.')[0].split('/')[-1]
                                      if c.get_material(i) else None) for i in range(c.get_num_materials())]
    res['live_actor_materials'] = live
except Exception:
    res['error'] = traceback.format_exc()

with open(os.path.join(OUT, 'b1y_fix3.json'), 'w') as f:
    json.dump(res, f, indent=1, default=str)
print('B1Y_FIX3_%s saved=%s' % (MODE.upper(), res.get('saved')))
