"""Beat 1 feedback round 3: READ ONLY probe. Answers, from the editor world (no PIE):

  cars      every car-ish actor and geometry collection: hidden flags, collision, transform,
            and the MATERIAL on every slot of each one (the 'missing textures' report).
  gcasset   GC_CrashCar's own materials array vs SM_CrashCar's, in slot order.
  times     the director's live cinematic numbers on the CDO *and* on the placed actor
            (CLAUDE.md: a placed-actor-only change is reverted by the next script run).
  player    where the player pawn starts, and how high its mesh sits above its capsule in the
            REFERENCE POSE (the Meshy root-at-pelvis float) - the levitation suspects.
  fx        what FX/Niagara material and texture assets exist to build fire and a power-up pop from.

  py <repo>/tools/b1y_probe.py
Writes <project>/Saved/jcpy/b1y_probe.json and changes nothing.
"""
import unreal, os, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
res = {}

def mat_rows(comp):
    rows = []
    try:
        n = comp.get_num_materials()
    except Exception:
        return rows
    for i in range(n):
        m = None
        try:
            m = comp.get_material(i)
        except Exception:
            pass
        ov = None
        try:
            ovs = comp.get_editor_property('override_materials')
            if i < len(ovs) and ovs[i] is not None:
                ov = ovs[i].get_path_name()
        except Exception:
            pass
        rows.append({'slot': i,
                     'effective': m.get_path_name() if m else None,
                     'override': ov})
    return rows

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    res['editor_world'] = ues.get_editor_world().get_name()
    res['pie_running'] = ues.get_game_world() is not None
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    allac = eas.get_all_level_actors()
    res['actor_count'] = len(allac)
    by_label = {}
    for a in allac:
        by_label.setdefault(a.get_actor_label(), a)

    # ---------- cars ----------
    cars = {}
    for a in allac:
        lab = a.get_actor_label()
        cls = a.get_class().get_name()
        interesting = ('car' in lab.lower() or 'crash' in lab.lower()
                       or cls == 'GeometryCollectionActor')
        if not interesting:
            continue
        d = {'class': cls,
             'loc': [round(v, 1) for v in a.get_actor_location().to_tuple()],
             'rot': [round(v, 1) for v in a.get_actor_rotation().to_tuple()],
             'scale': [round(v, 3) for v in a.get_actor_scale3d().to_tuple()],
             'hidden_in_game': bool(a.get_editor_property('hidden')),
             'hidden_in_editor': bool(a.is_temporarily_hidden_in_editor()),
             'collides': a.get_actor_enable_collision(),
             'tags': [str(t) for t in a.get_editor_property('tags')],
             'pkg': a.get_outermost().get_name()}
        gcc = a.get_component_by_class(unreal.GeometryCollectionComponent)
        smc = a.get_component_by_class(unreal.StaticMeshComponent)
        if gcc:
            rc = gcc.get_editor_property('rest_collection')
            d['rest'] = rc.get_path_name() if rc else None
            try:
                d['object_type'] = str(gcc.get_editor_property('object_type'))
            except Exception:
                pass
            d['visible'] = gcc.is_visible()
            d['mats'] = mat_rows(gcc)
        if smc:
            sm = smc.get_editor_property('static_mesh')
            d['mesh'] = sm.get_path_name() if sm else None
            d['visible'] = smc.is_visible()
            d['mats'] = mat_rows(smc)
        cars[lab] = d
    res['cars'] = cars

    # ---------- the GC asset vs the static mesh, slot by slot ----------
    ga = {}
    gc = unreal.load_asset('/Game/Game/Destruction/GC_CrashCar')
    if gc:
        try:
            ms = gc.get_editor_property('materials')
            ga['gc_materials'] = [(m.get_path_name() if m else None) for m in ms]
        except Exception as e:
            ga['gc_materials_err'] = str(e)
    sm = unreal.load_asset('/Game/Game/Imported/City/SM_CrashCar')
    if sm is None:
        # find it by name in the asset registry instead of guessing the folder
        ar = unreal.AssetRegistryHelpers.get_asset_registry()
        for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath('/Script/Engine', 'StaticMesh'), False):
            if str(ad.asset_name) == 'SM_CrashCar':
                sm = ad.get_asset()
                break
    if sm:
        ga['sm_path'] = sm.get_path_name()
        ga['sm_materials'] = []
        for i in range(sm.get_num_sections(0)):
            pass
        try:
            sms = sm.get_editor_property('static_materials')
            ga['sm_materials'] = [{'slot': i,
                                   'name': str(s.material_slot_name),
                                   'mat': s.material_interface.get_path_name() if s.material_interface else None}
                                  for i, s in enumerate(sms)]
        except Exception as e:
            ga['sm_materials_err'] = str(e)
    res['gcasset'] = ga

    # ---------- the director's cinematic numbers ----------
    t = {}
    bp = unreal.load_asset('/Game/Game/Blueprints/BP_OpeningDirector')
    names = ['CinePlayOpening', 'CineLength', 'CineImpactTime', 'CineBodyTime', 'CineEndYaw',
             'ObjectiveState', 'UseFireHazard', 'AutoBeats',
             'ExplTB', 'ExplTC', 'ExplTD', 'ExplSayAt', 'ExplFlashSecs']
    if bp:
        cdo = unreal.get_default_object(bp.generated_class())
        t['cdo'] = {}
        for n in names:
            try:
                t['cdo'][n] = str(cdo.get_editor_property(n))
            except Exception as e:
                t['cdo'][n] = 'ERR ' + str(e)
        pa = by_label.get('B1_OpeningDirector') or by_label.get('BP_OpeningDirector')
        if pa is None:
            for a in allac:
                if a.get_class().get_name() == 'BP_OpeningDirector_C':
                    pa = a
                    break
        if pa:
            t['placed_label'] = pa.get_actor_label()
            t['placed_loc'] = [round(v, 1) for v in pa.get_actor_location().to_tuple()]
            t['placed'] = {}
            for n in names:
                try:
                    t['placed'][n] = str(pa.get_editor_property(n))
                except Exception as e:
                    t['placed'][n] = 'ERR ' + str(e)
            # which actors the director holds references to
            for n in ('CineRealCar', 'ExplCarGC', 'CineRealDriver', 'CineSeqActor', 'ObjBeacon'):
                try:
                    v = pa.get_editor_property(n)
                    t['placed'][n] = v.get_actor_label() if v else None
                except Exception as e:
                    t['placed'][n] = 'ERR ' + str(e)
        else:
            t['placed'] = 'NO PLACED DIRECTOR FOUND'
        # count how many directors are in the world (orphan check)
        t['director_actors'] = [a.get_actor_label() for a in allac
                                if a.get_class().get_name() == 'BP_OpeningDirector_C']
    res['times'] = t

    # ---------- the player: where he starts and how high his mesh rides ----------
    p = {}
    starts = [a for a in allac if 'PlayerStart' in a.get_class().get_name()]
    p['player_starts'] = [{'label': a.get_actor_label(),
                           'loc': [round(v, 1) for v in a.get_actor_location().to_tuple()]}
                          for a in starts]
    pbp = unreal.load_asset('/Game/Game/Blueprints/BP_Player')
    if pbp:
        pcdo = unreal.get_default_object(pbp.generated_class())
        cap = pcdo.get_component_by_class(unreal.CapsuleComponent)
        if cap:
            p['capsule_half_height'] = cap.get_unscaled_capsule_half_height()
            p['capsule_radius'] = cap.get_unscaled_capsule_radius()
        msh = pcdo.get_component_by_class(unreal.SkeletalMeshComponent)
        if msh:
            p['mesh_rel_loc'] = [round(v, 2) for v in msh.get_relative_location().to_tuple()]
            p['mesh_rel_rot'] = [round(v, 2) for v in msh.get_relative_rotation().to_tuple()]
            sk = msh.get_editor_property('skeletal_mesh_asset')
            p['mesh'] = sk.get_path_name() if sk else None
            p['anim_mode'] = str(msh.get_editor_property('animation_mode'))
            ac = msh.get_editor_property('anim_class')
            p['anim_class'] = str(ac) if ac else None
            if sk:
                # reference-pose heights: bone 0 and the lowest bone, in COMPONENT space
                try:
                    rs = sk.get_editor_property('skeleton')
                    p['skeleton'] = rs.get_path_name() if rs else None
                except Exception:
                    pass
                try:
                    b = sk.get_bounds()
                    p['mesh_bounds_origin_z'] = round(b.origin.z, 2)
                    p['mesh_bounds_ext_z'] = round(b.box_extent.z, 2)
                except Exception as e:
                    p['bounds_err'] = str(e)
        for n in ('PlayerAnimDeath', 'HasFreezeFrame', 'InputLocked'):
            try:
                p[n] = str(pcdo.get_editor_property(n))
            except Exception:
                pass
    res['player'] = p

    # ---------- what we have to make fire and a power-up pop out of ----------
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    fx = {}
    for cls_pkg, cls_name, key in (('/Script/Niagara', 'NiagaraSystem', 'niagara_systems'),
                                   ('/Script/Engine', 'Material', 'materials'),
                                   ('/Script/Engine', 'MaterialInstanceConstant', 'material_instances'),
                                   ('/Script/Engine', 'Texture2D', 'fx_textures'),
                                   ('/Script/Engine', 'SoundWave', 'sounds')):
        got = []
        for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath(cls_pkg, cls_name), False):
            pn = str(ad.package_name)
            if not pn.startswith('/Game/Game'):
                continue
            if key == 'fx_textures' and '/FX/' not in pn and '/UI/' not in pn:
                continue
            got.append(pn)
        fx[key] = sorted(got)
    res['fx'] = fx

except Exception:
    res['error'] = traceback.format_exc()

if not os.path.isdir(OUT):
    os.makedirs(OUT)
with open(os.path.join(OUT, 'b1y_probe.json'), 'w') as f:
    json.dump(res, f, indent=1, sort_keys=True)
print('B1Y_PROBE_DONE ' + os.path.join(OUT, 'b1y_probe.json'))
