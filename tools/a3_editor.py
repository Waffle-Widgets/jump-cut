# One-off editor step from the first build (Nov 12), copied from the ignored JumpCut/Saved/ so the level set-up can be traced.
# Run with `py <path> <step>` in the Unreal editor console (a3_pie.py: during Play mode; the others: Play mode stopped).
# Read it before re-running: steps change placed actors in Lvl_JumpCut and some save the level.
"""A3 editor steps.  py a3_editor.py <mode> [args]  -> writes Saved/a3_editor.txt
  probe        world, dirty packages, r.CustomDepth, anime assets load, Lvl_Cafe deps, volumes, character CustomDepth
"""
import os, sys, traceback
import unreal

out = []
def P(*a): out.append(' '.join(str(x) for x in a))
eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
MATS = '/Game/Game/Materials/'
ANIME = ['M_AnimeLook', 'MI_AnimeLook', 'MI_AnimeLook_Cafe', 'M_AnimeChar', 'M_AnimeFlat', 'M_AnimeSurface', 'M_AnimeShaft',
         'MI_Cafe_Top', 'MI_Cafe_Trousers', 'MI_CafeWalker']


def dirty():
    return ([str(p.get_name()) for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()],
            [str(p.get_name()) for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()])


def cvar(n):
    try:
        return unreal.SystemLibrary.get_console_variable_int_value(n)
    except Exception as e:
        return 'ERR %s' % e


def probe():
    w = UES.get_editor_world()
    P('WORLD', w.get_path_name())
    dm, dc = dirty()
    P('DIRTY_MAPS', dm)
    P('DIRTY_CONTENT', dc)
    P('r.CustomDepth', cvar('r.CustomDepth'))
    for n in ANIME:
        p = MATS + n
        if not eal.does_asset_exist(p):
            P('MISSING', p)
            continue
        a = unreal.load_asset(p)
        extra = ''
        if isinstance(a, unreal.MaterialInstanceConstant):
            extra = 'parent=%s' % (a.get_editor_property('parent').get_path_name() if a.get_editor_property('parent') else None)
        elif isinstance(a, unreal.Material):
            extra = 'domain=%s nodes=%d' % (a.get_editor_property('material_domain'), mel.get_num_material_expressions(a))
        P('LOADED', p, type(a).__name__, extra)
    # MI_AnimeLook_Cafe parameter values
    mi = unreal.load_asset(MATS + 'MI_AnimeLook_Cafe')
    if mi:
        sc = mi.get_editor_property('scalar_parameter_values')
        P('CAFE_SCALARS', ', '.join('%s=%.3f' % (s.parameter_info.name, s.parameter_value) for s in sc))
        vc = mi.get_editor_property('vector_parameter_values')
        P('CAFE_VECTORS', ', '.join('%s=(%.3f,%.3f,%.3f)' % (v.parameter_info.name, v.parameter_value.r, v.parameter_value.g, v.parameter_value.b) for v in vc))
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    opts = unreal.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True)
    for pkg in ('/Game/Game/Maps/Lvl_Cafe',):
        deps = reg.get_dependencies(pkg, opts) or []
        P('DEPS', pkg, len(deps))
        missing = []
        for d in deps:
            ds = str(d)
            if ds.startswith('/Script') or ds.startswith('/Engine'):
                continue
            if not eal.does_asset_exist(ds):
                missing.append(ds)
        P('DEPS_MISSING', missing)
    for a in EAS.get_all_level_actors():
        if isinstance(a, unreal.PostProcessVolume):
            s = a.get_editor_property('settings')
            bl = [b.get_editor_property('object') for b in s.get_editor_property('weighted_blendables').get_editor_property('array')]
            P('PPV', a.get_actor_label(), 'unbound', a.get_editor_property('unbound'), 'enabled', a.get_editor_property('enabled'),
              'blendables', [b.get_path_name() if b else None for b in bl],
              'exp_method_ov', s.get_editor_property('override_auto_exposure_method'), s.get_editor_property('auto_exposure_method'),
              'bias', s.get_editor_property('auto_exposure_bias'))
        if isinstance(a, (unreal.DirectionalLight, unreal.SkyLight, unreal.ExponentialHeightFog, unreal.SkyAtmosphere)):
            extra = ''
            if isinstance(a, unreal.DirectionalLight):
                lc = a.light_component
                extra = 'intensity=%.2f rot=%s' % (lc.intensity, a.get_actor_rotation())
            elif isinstance(a, unreal.SkyLight):
                extra = 'intensity=%.2f' % a.light_component.intensity
            P('LIGHT', a.get_actor_label(), type(a).__name__, extra)
    for n in ('BP_Player', 'BP_EnemyBase', 'BP_Goon', 'BP_BossFreeze'):
        c = unreal.load_class(None, '/Game/Game/Blueprints/%s.%s_C' % (n, n))
        cdo = unreal.get_default_object(c)
        m = cdo.mesh
        P('CDO', n, 'mesh', m.get_editor_property('skeletal_mesh_asset').get_name() if m.get_editor_property('skeletal_mesh_asset') else None,
          'rcd', m.get_editor_property('render_custom_depth'), 'stencil', m.get_editor_property('custom_depth_stencil_value'),
          'mats', [x.get_name() if x else None for x in m.get_editor_property('override_materials')])
    for a in EAS.get_all_level_actors():
        if isinstance(a, unreal.Character):
            m = a.mesh
            P('PLACED', a.get_actor_label(), a.get_class().get_name(), 'rcd', m.get_editor_property('render_custom_depth'),
              'loc', a.get_actor_location())


def openmap(path):
    dm, dc = dirty()
    P('DIRTY_MAPS_BEFORE', dm)
    if dm:
        P('STOPPED: dirty map packages')
        return
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    ok = les.load_level(path)
    P('LOAD', path, ok, 'WORLD', UES.get_editor_world().get_path_name())


LOOK_JC = 'MI_AnimeLook_JumpCut'
# this level's sun (Sun_Main): pitch -45, yaw -35; KeyDir points towards it, lifted a little like the cafe's
SUN_PITCH, SUN_YAW = -45.0, -35.0


def key_dir():
    import math
    pr, yr = math.radians(SUN_PITCH), math.radians(SUN_YAW)
    return (-math.cos(pr) * math.cos(yr), -math.cos(pr) * math.sin(yr), -math.sin(pr) + 0.25)


def make_mi():
    """MI_AnimeLook_JumpCut: a child of M_AnimeLook starting from MI_AnimeLook_Cafe's numbers (the painted background +
    cel-shaded characters), KeyDir towards this level's sun."""
    path = MATS + LOOK_JC
    if eal.does_asset_exist(path):
        mi = unreal.load_asset(path)
        P('exists', path)
    else:
        mi = unreal.AssetToolsHelpers.get_asset_tools().create_asset(LOOK_JC, MATS[:-1], unreal.MaterialInstanceConstant,
                                                                     unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi, unreal.load_asset(MATS + 'M_AnimeLook'))
        P('created', path)
    cafe = unreal.load_asset(MATS + 'MI_AnimeLook_Cafe')
    for s in cafe.get_editor_property('scalar_parameter_values'):
        mel.set_material_instance_scalar_parameter_value(mi, str(s.parameter_info.name), s.parameter_value)
    for v in cafe.get_editor_property('vector_parameter_values'):
        mel.set_material_instance_vector_parameter_value(mi, str(v.parameter_info.name), v.parameter_value)
    k = key_dir()
    mel.set_material_instance_vector_parameter_value(mi, 'KeyDir', unreal.LinearColor(k[0], k[1], k[2], 1.0))
    mel.update_material_instance(mi)
    P('KeyDir', k)


def set_look(*pairs):
    mi = unreal.load_asset(MATS + LOOK_JC)
    for p in pairs:
        n, v = p.split('=')
        if ',' in v:
            r, g, b = [float(x) for x in v.split(',')]
            mel.set_material_instance_vector_parameter_value(mi, n, unreal.LinearColor(r, g, b, 1.0))
        else:
            mel.set_material_instance_scalar_parameter_value(mi, n, float(v))
        P('set', n, v)
    mel.update_material_instance(mi)


def final():
    get_look()
    dm, dc = dirty()
    P('DIRTY_MAPS', dm)
    P('DIRTY_CONTENT', dc)
    a = find_ppv()
    s = a.get_editor_property('settings')
    P('PPV', a.get_actor_label(), 'unbound', a.get_editor_property('unbound'), 'enabled', a.get_editor_property('enabled'),
      'priority', a.get_editor_property('priority'),
      'blendables', [b.get_editor_property('object').get_path_name() for b in s.get_editor_property('weighted_blendables').get_editor_property('array')],
      'motion_blur', s.get_editor_property('override_motion_blur_amount'), s.get_editor_property('motion_blur_amount'),
      'fringe', s.get_editor_property('scene_fringe_intensity'), 'flare', s.get_editor_property('lens_flare_intensity'),
      'exposure_override', s.get_editor_property('override_auto_exposure_method'))


def get_look():
    mi = unreal.load_asset(MATS + LOOK_JC)
    P('SCALARS', ', '.join('%s=%.3f' % (s.parameter_info.name, s.parameter_value) for s in mi.get_editor_property('scalar_parameter_values')))
    P('VECTORS', ', '.join('%s=(%.3f,%.3f,%.3f)' % (v.parameter_info.name, v.parameter_value.r, v.parameter_value.g, v.parameter_value.b)
                           for v in mi.get_editor_property('vector_parameter_values')))


def find_ppv():
    for a in EAS.get_all_level_actors():
        if isinstance(a, unreal.PostProcessVolume) and a.get_actor_label() == 'PP_AnimeLook':
            return a
    return None


def make_ppv():
    if UES.get_editor_world().get_path_name().split('.')[0] != '/Game/Game/Maps/Lvl_JumpCut':
        P('STOPPED wrong world')
        return
    a = find_ppv()
    if a is None:
        a = EAS.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 300), unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0))
        a.set_actor_label('PP_AnimeLook')
        P('spawned PP_AnimeLook')
    a.set_editor_property('unbound', True)
    a.set_editor_property('priority', 1.0)
    s = a.get_editor_property('settings')

    def ov(k, v):
        s.set_editor_property('override_' + k, True)
        s.set_editor_property(k, v)
    ov('motion_blur_amount', 0.0)          # drawn frames don't smear
    ov('scene_fringe_intensity', 0.0)
    ov('lens_flare_intensity', 0.0)
    s.set_editor_property('weighted_blendables', unreal.WeightedBlendables(
        array=[unreal.WeightedBlendable(weight=1.0, object=unreal.load_asset(MATS + LOOK_JC))]))
    a.set_editor_property('settings', s)
    P('PPV ok', a.get_path_name())


def pp(*pairs):
    """pp key=value ... on PP_AnimeLook's settings (override_ set too). Exposure: method=manual|histogram"""
    a = find_ppv()
    s = a.get_editor_property('settings')
    for p in pairs:
        k, v = p.split('=')
        if k == 'method':
            val = unreal.AutoExposureMethod.AEM_MANUAL if v == 'manual' else unreal.AutoExposureMethod.AEM_HISTOGRAM
            s.set_editor_property('override_auto_exposure_method', True)
            s.set_editor_property('auto_exposure_method', val)
        elif k == 'physical':
            s.set_editor_property('override_auto_exposure_apply_physical_camera_exposure', True)
            s.set_editor_property('auto_exposure_apply_physical_camera_exposure', v == '1')
        elif k in ('color_saturation', 'color_contrast'):
            f = float(v)
            s.set_editor_property('override_' + k, True)
            s.set_editor_property(k, unreal.Vector4(f, f, f, 1.0))
        else:
            s.set_editor_property('override_' + k, True)
            s.set_editor_property(k, float(v))
        P('pp', k, v)
    a.set_editor_property('settings', s)


def compile_chars():
    for n in ('BP_Player', 'BP_EnemyBase', 'BP_Goon', 'BP_BossFreeze'):
        bp = unreal.load_asset('/Game/Game/Blueprints/' + n)
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    for n in ('BP_Player', 'BP_EnemyBase', 'BP_Goon', 'BP_BossFreeze'):
        cdo = unreal.get_default_object(unreal.load_class(None, '/Game/Game/Blueprints/%s.%s_C' % (n, n)))
        P('CDO', n, 'rcd', cdo.mesh.get_editor_property('render_custom_depth'))
    for a in EAS.get_all_level_actors():
        if isinstance(a, unreal.Character):
            P('PLACED', a.get_actor_label(), 'rcd', a.mesh.get_editor_property('render_custom_depth'))


def mark_placed():
    """Placed characters keep the old value in memory: switch it on per instance, re-set the transform so the level
    knows it changed."""
    for a in EAS.get_all_level_actors():
        if isinstance(a, unreal.Character):
            m = a.mesh
            m.modify()
            m.set_render_custom_depth(True)
            retransform(a)
            P('PLACED', a.get_actor_label(), 'rcd', a.mesh.get_editor_property('render_custom_depth'))


def retransform(a):
    a.modify()
    a.set_actor_transform(a.get_actor_transform(), False, False)


def save_level():
    ok = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    P('save_current_level', ok)


def save(*paths):
    for p in paths:
        P('save', p, eal.save_asset(p, only_if_is_dirty=False))


try:
    mode = sys.argv[1] if len(sys.argv) > 1 else 'probe'
    globals()[mode](*sys.argv[2:])
    P('DONE', mode)
except Exception:
    P('ERROR', traceback.format_exc())
with open(os.path.join(unreal.Paths.project_saved_dir(), 'a3_editor.txt'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
