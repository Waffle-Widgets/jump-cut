"""Beat 1 feedback round 4: READ ONLY probe for the breakable wall, the fire, the driver and
the player's first second. Writes <project>/Saved/jcpy/b1z_probe.json. Changes nothing.

    py <repo>/tools/b1z_probe.py
"""
import unreal, os, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
res = {}

def v(x):
    try:
        return [round(x.x, 2), round(x.y, 2), round(x.z, 2)]
    except Exception:
        return None

def rot(r):
    return [round(r.roll, 2), round(r.pitch, 2), round(r.yaw, 2)]

def mats(comp):
    out = []
    try:
        n = comp.get_num_materials()
    except Exception:
        return out
    for i in range(n):
        try:
            m = comp.get_material(i)
            out.append(m.get_name() if m else None)
        except Exception:
            out.append('?')
    return out

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    res['world'] = ues.get_editor_world().get_name()
    res['pie'] = ues.get_game_world() is not None
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    allac = eas.get_all_level_actors()
    res['actor_count'] = len(allac)
    by_label = {}
    for a in allac:
        by_label.setdefault(a.get_actor_label(), a)

    WANT = ['B1_Cine_WallPatch', 'City_CafeShell', 'City_CafeCrashCar', 'B1_Cafe_CrashCar_GC',
            'C1_Cafe_CrashDriver', 'B1_Cafe_Fire', 'B1_Cafe_FireLight', 'B1_Cafe_BlastRing',
            'B1_Cafe_DebrisFloor', 'Coworker_Cafe', 'B1_Cine_Director', 'B1_Objective_Beacon',
            'B1_Cafe_Explosion', 'B1_Cine_ExplCam', 'B1_Cine_Seq']
    acts = {}
    for lab in WANT:
        a = by_label.get(lab)
        if a is None:
            acts[lab] = None
            continue
        row = {'class': a.get_class().get_name(), 'loc': v(a.get_actor_location()),
               'rot': rot(a.get_actor_rotation()), 'scale': v(a.get_actor_scale3d())}
        try:
            row['hidden'] = bool(a.get_editor_property('hidden'))
        except Exception:
            pass
        try:
            o = a.get_actor_bounds(False)
            row['bounds_origin'] = v(o[0]); row['bounds_extent'] = v(o[1])
        except Exception:
            pass
        comps = []
        for c in a.get_components_by_class(unreal.SceneComponent):
            cr = {'name': c.get_name(), 'class': c.get_class().get_name()}
            if isinstance(c, unreal.StaticMeshComponent):
                sm = c.static_mesh
                cr['mesh'] = sm.get_name() if sm else None
                cr['mats'] = mats(c)
            if isinstance(c, unreal.SkeletalMeshComponent):
                try:
                    sk = c.get_skeletal_mesh_asset()
                except Exception:
                    sk = None
                cr['mesh'] = sk.get_name() if sk else None
                cr['mats'] = mats(c)
                try:
                    cr['anim_class'] = str(c.get_editor_property('anim_class'))
                except Exception:
                    pass
                if sk:
                    pa = sk.get_editor_property('physics_asset')
                    cr['physics_asset'] = pa.get_path_name() if pa else None
            if c.get_class().get_name() == 'NiagaraComponent':
                try:
                    cr['system'] = str(c.get_editor_property('asset'))
                except Exception:
                    pass
            try:
                rt = c.get_relative_transform()
                cr['rel_loc'] = v(rt.translation)
                cr['rel_scale'] = v(rt.scale3d)
                cr['rel_rot'] = rot(rt.rotation.rotator())
            except Exception:
                pass
            comps.append(cr)
        row['components'] = comps
        acts[lab] = row
    res['actors'] = acts

    # ---- the cafe shell mesh itself: bounds and slots (to size an intact wall panel)
    shell = by_label.get('City_CafeShell')
    if shell:
        smc = shell.get_component_by_class(unreal.StaticMeshComponent)
        sm = smc.static_mesh
        if sm:
            b = sm.get_bounds()
            res['cafeshell_mesh'] = {
                'path': sm.get_path_name(),
                'origin': v(b.origin), 'extent': v(b.box_extent),
                'slots': [str(s.material_slot_name) for s in sm.get_editor_property('static_materials')],
                'slot_mats': [s.material_interface.get_path_name() if s.material_interface else None
                              for s in sm.get_editor_property('static_materials')],
            }

    # ---- player start + the player BP
    ps = []
    for a in allac:
        if a.get_class().get_name() == 'PlayerStart':
            ps.append({'label': a.get_actor_label(), 'loc': v(a.get_actor_location()),
                       'rot': rot(a.get_actor_rotation())})
    res['player_starts'] = ps

    # ---- the crash driver's skeletal mesh asset: does it have a physics asset for ragdoll?
    sks = {}
    for path in ('/Game/Game/Meshy/SK_CrashDriver', '/Game/Game/Meshy/SK_CafeWalker'):
        sk = unreal.load_asset(path)
        if sk is None:
            sks[path] = None
            continue
        pa = sk.get_editor_property('physics_asset')
        sks[path] = {'physics_asset': pa.get_path_name() if pa else None,
                     'bones': len(sk.get_editor_property('skeleton').get_editor_property('bone_tree')) if sk.get_editor_property('skeleton') else None}
    res['skeletals'] = sks

except Exception as e:
    res['error'] = repr(e)
    res['tb'] = traceback.format_exc()

with open(os.path.join(OUT, 'b1z_probe.json'), 'w') as fh:
    json.dump(res, fh, indent=1)
print('b1z_probe wrote', os.path.join(OUT, 'b1z_probe.json'))
