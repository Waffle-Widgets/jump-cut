"""Latte-art mini game: the assets a Blueprint cannot make for itself.

    py <repo>/tools/latte_build.py assets     two render targets + the pour simulation and cup-surface materials
    py <repo>/tools/latte_build.py where      where the cafe counter is (changes nothing)
Result: <project>/Saved/jcpy/latte_build.txt.  Play mode must be stopped.

HOW THE POUR WORKS (Sun Nov 15).  The cup's surface is a 512 px picture, white = milk foam, black = crema.
Every frame M_LatteSim redraws it from the previous frame (two render targets, swapped):
  * a LOW pour is a source on the surface: everything already drawn is pushed away from the spout (plus a mirror
    source outside the cup wall, so the pattern bends round the wall instead of leaving), and white is laid at the spout.
    A moving spout drags a thin brown rim with it, which is what makes a wiggle come out as rosetta stripes.
  * a HIGH pour sinks: it lays no white, punches a brown dot and drags the surface along the way the pitcher moves -
    the "cut through" that turns a blob into a heart.
That is the real technique reduced to two rules (docs/devlog entry lists the sources).
"""
import os
import sys
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'latte_build.txt')
DIR = '/Game/Game/Materials/Latte'
log = []
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()


def say(s):
    log.append(str(s))
    unreal.log('[latte] %s' % s)


SIM = r"""
float2 p = UV - 0.5;
float2 s = Pour.xy;
float2 d = p - s;
float r2 = dot(d, d);
float R = 0.47;
float s2 = max(dot(s, s), 0.0001);
float2 si = s * (R * R / s2);
float2 di = p - si;
float2 vel = d / max(r2, 0.0009) + di / max(dot(di, di), 0.0009);
float2 src = p - Pour.w * vel;
src += (Pour.w * 0.45 + Vel.z * 0.00003) * float2(sin(p.y * 46.0 + Fx.w * 3.1), cos(p.x * 41.0 - Fx.w * 2.7));
src -= Vel.xy * Vel.z * exp(-r2 / 0.0042);
float2 pv = Texture2DSample(Prev, PrevSampler, src + 0.5).rg;
float prev = pv.x;
float r = sqrt(r2);
float inj = Pour.z * (1.0 - smoothstep(Misc.x * 0.6, Misc.x, r));
float v = max(prev, inj);
float rim = Misc.y * smoothstep(Misc.x * 0.9, Misc.x * 1.1, r) * (1.0 - smoothstep(Misc.x * 1.3, Misc.x * 1.7, r));
v = lerp(v, 0.0, saturate(rim));
v = lerp(v, 0.16, saturate(Vel.w * exp(-r2 / 0.00007)));
v = lerp(v, smoothstep(0.0, 1.0, v), Misc.z);
v *= (dot(p, p) < 0.2304) ? 1.0 : 0.0;
float g = lerp(pv.y, 0.5 + 0.5 * sin(Fx.w * 11.0), saturate(inj));
return float3(v, g, 0.0);
"""

SURF = r"""
float2 p = UV - 0.5;
float2 fd = p - Fx.xy;
float fr = length(fd);
float rip = Fx.z * sin(fr * 130.0 - Fx.w * 16.0) * exp(-fr * 9.0);
float2 uv2 = UV + normalize(fd + 0.00001) * rip * 0.006;
float2 sm = Texture2DSample(Sim, SimSampler, uv2).rg;
float v = sm.x;
float em = Texture2DSample(Sim, SimSampler, uv2 + float2(0.006, 0.006)).r - Texture2DSample(Sim, SimSampler, uv2 - float2(0.006, 0.006)).r;
float n = sin(p.x * 37.0 + sin(p.y * 23.0) * 2.0) * sin(p.y * 31.0 + sin(p.x * 19.0) * 2.0);
float3 crema = lerp(float3(0.17, 0.070, 0.022), float3(0.25, 0.110, 0.038), 0.5 + 0.5 * n);
float3 halo = float3(0.42, 0.25, 0.12);
float3 milk = float3(0.66, 0.61, 0.50);
float3 c = lerp(crema, halo, smoothstep(0.04, 0.30, v));
c = lerp(c, milk * (0.76 + 0.24 * sm.y), smoothstep(0.24, 0.62, v));
c += em * 0.20;
c *= 1.0 + rip * 0.35;
c += 0.05 * smoothstep(0.25, 0.0, length(p - float2(0.18, -0.16)));
float ga = length(p - GuideA.xy);
float ring = (1.0 - smoothstep(0.005, 0.009, abs(ga - GuideA.z))) * step(0.5, frac(atan2(p.y - GuideA.y, p.x - GuideA.x) * 1.9099 + Fx.w * 0.6));
float gx0 = min(GuideB.x, GuideB.y);
float gx1 = max(GuideB.x, GuideB.y);
float gdir = sign(GuideB.y - GuideB.x);
float gt = saturate((p.x - GuideB.x) / (GuideB.y - GuideB.x + 0.00001));
float gamp = GuideB.z * lerp(1.0, 0.35, gt);
float wave = gamp * sin((p.x - GuideB.x) * 123.0);
float slope = gamp * 123.0 * cos((p.x - GuideB.x) * 123.0);
float path = (1.0 - smoothstep(0.005, 0.009, abs(p.y - wave) / sqrt(1.0 + slope * slope))) * step(gx0, p.x) * step(p.x, gx1) * max(step(0.004, GuideB.z), step(0.5, frac(p.x * gdir * 14.0 - Fx.w * 1.6)));
float gl = saturate(ring * GuideA.w + path * GuideB.w) * ShowGuide;
c = lerp(c, float3(0.05, 0.50, 0.62), gl);
float rr = length(p);
c *= lerp(1.0, 0.55, smoothstep(0.40, 0.48, rr));
return c * Bright;
"""


def rt(name):
    path = '%s/%s' % (DIR, name)
    t = eal.load_asset(path)
    if t is None:
        t = at.create_asset(name, DIR, unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew())
    t.set_editor_property('render_target_format', unreal.TextureRenderTargetFormat.RTF_RGBA16F)
    t.set_editor_property('size_x', 512)
    t.set_editor_property('size_y', 512)
    t.set_editor_property('clear_color', unreal.LinearColor(0, 0, 0, 1))
    t.set_editor_property('address_x', unreal.TextureAddress.TA_CLAMP)
    t.set_editor_property('address_y', unreal.TextureAddress.TA_CLAMP)
    say('render target %s %sx%s' % (path, t.get_editor_property('size_x'), t.get_editor_property('size_y')))
    return t


def material(name, code, tex_name, vectors, scalars, default_tex):
    path = '%s/%s' % (DIR, name)
    m = eal.load_asset(path)
    if m is None:
        m = at.create_asset(name, DIR, unreal.Material, unreal.MaterialFactoryNew())
    mel.delete_all_material_expressions(m)
    m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
    c = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -200, 0)
    c.set_editor_property('code', code.strip())
    c.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    names = ['UV', tex_name] + [v for v in vectors] + [s for s in scalars]
    ins = []
    for n in names:
        ci = unreal.CustomInput()
        ci.set_editor_property('input_name', n)
        ins.append(ci)
    c.set_editor_property('inputs', ins)
    uv = mel.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -700, -200)
    say('uv %s' % mel.connect_material_expressions(uv, '', c, 'UV'))
    t = mel.create_material_expression(m, unreal.MaterialExpressionTextureObjectParameter, -700, 0)
    t.set_editor_property('parameter_name', tex_name)
    t.set_editor_property('texture', default_tex)
    t.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    say('tex %s' % mel.connect_material_expressions(t, '', c, tex_name))
    y = 200
    for n, dv in vectors.items():
        # a Material Parameter Collection, not a material parameter: the graph tool can only write the collection
        # form of Set Vector Parameter Value, and it saves making a dynamic material at all
        e = mel.create_material_expression(m, unreal.MaterialExpressionCollectionParameter, -700, y)
        e.set_editor_property('collection', MPC[0])
        e.set_editor_property('parameter_name', n)
        say('vec %s %s' % (n, mel.connect_material_expressions(e, '', c, n)))
        y += 220
    for n, dv in scalars.items():
        e = mel.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -700, y)
        e.set_editor_property('parameter_name', n)
        e.set_editor_property('default_value', dv)
        say('scalar %s %s' % (n, mel.connect_material_expressions(e, '', c, n)))
        y += 120
    say('emissive %s' % mel.connect_material_property(c, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR))
    if name == 'M_LatteSurface':
        m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_MASKED)
        k = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -200, 400)
        k.set_editor_property('code', 'return (length(UV - 0.5) < 0.48) ? 1.0 : 0.0;')
        k.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT1)
        ci = unreal.CustomInput(); ci.set_editor_property('input_name', 'UV')
        k.set_editor_property('inputs', [ci])
        mel.connect_material_expressions(uv, '', k, 'UV')
        say('mask %s' % mel.connect_material_property(k, '', unreal.MaterialProperty.MP_OPACITY_MASK))
    mel.recompile_material(m)
    say('material %s' % path)
    return m


MPC = []


def collection():
    path = '%s/MPC_Latte' % DIR
    c = eal.load_asset(path)
    if c is None:
        c = at.create_asset('MPC_Latte', DIR, unreal.MaterialParameterCollection, unreal.MaterialParameterCollectionFactoryNew())
    if len(c.get_editor_property('vector_parameters')) != 6:
        ps = []
        for n, dv in (('Pour', (0, 0, 0, 0)), ('Vel', (0, 0, 0, 0)), ('Misc', (0.035, 0, 0.25, 0)), ('Fx', (0, 0, 0, 0)), ('GuideA', (0, 0, 0.06, 0)), ('GuideB', (0, 0, 0, 0))):
            v = unreal.CollectionVectorParameter()
            v.set_editor_property('parameter_name', n)
            v.set_editor_property('default_value', unreal.LinearColor(*dv))
            ps.append(v)
        c.set_editor_property('vector_parameters', ps)
    say('collection %s %s' % (path, [str(v.get_editor_property('parameter_name')) for v in c.get_editor_property('vector_parameters')]))
    MPC.append(c)
    return c


def instance(name, parent, tex_name, tex):
    path = '%s/%s' % (DIR, name)
    mi = eal.load_asset(path)
    if mi is None:
        mi = at.create_asset(name, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, parent)
    say('instance %s %s=%s %s' % (name, tex_name, tex.get_name(), mel.set_material_instance_texture_parameter_value(mi, tex_name, tex)))
    if mel.get_material_instance_texture_parameter_value(mi, tex_name) != tex:
        # the helper answers False for a render target; write the override itself
        tv = unreal.TextureParameterValue()
        info = unreal.MaterialParameterInfo()
        info.set_editor_property('name', tex_name)
        tv.set_editor_property('parameter_info', info)
        tv.set_editor_property('parameter_value', tex)
        mi.set_editor_property('texture_parameter_values', [tv])
    if name.startswith('MI_LatteSurface'):
        mel.set_material_instance_scalar_parameter_value(mi, 'ShowGuide', 1.0)      # the cup shows the guide; the GOAL picture does not
    mel.update_material_instance(mi)
    got = mel.get_material_instance_texture_parameter_value(mi, tex_name)
    say('   reads back %s' % (got.get_name() if got else None))
    return mi


def flat(name, rgb, unlit=False, shaded=False, wobble=False):
    """A one-colour material. `shaded` = unlit with its own soft light from above the staff side: the cup sits in the
    counter's shadow, where a lit material goes black through the cel look and a plain unlit one has no form."""
    path = '%s/%s' % (DIR, name)
    m = eal.load_asset(path)
    if m is None:
        m = at.create_asset(name, DIR, unreal.Material, unreal.MaterialFactoryNew())
    mel.delete_all_material_expressions(m)
    c = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -500, 0)
    c.set_editor_property('constant', unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1))
    if shaded:
        m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
        n = mel.create_material_expression(m, unreal.MaterialExpressionVertexNormalWS, -500, 200)
        k = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -200, 0)
        k.set_editor_property('code', 'float d = saturate(dot(normalize(N), normalize(float3(0.25, -0.45, 0.85))) * 0.5 + 0.5); return Color * lerp(0.42, 1.0, d * d);')
        k.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
        ins = []
        for nm in ('Color', 'N'):
            ci = unreal.CustomInput(); ci.set_editor_property('input_name', nm); ins.append(ci)
        k.set_editor_property('inputs', ins)
        mel.connect_material_expressions(c, '', k, 'Color')
        mel.connect_material_expressions(n, '', k, 'N')
        mel.connect_material_property(k, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        if wobble:
            # the milk stream: it sways and thickens as it falls, in world space so the mesh's scale does not matter
            wp = mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -500, 400)
            tm = mel.create_material_expression(m, unreal.MaterialExpressionTime, -500, 550)
            w = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -200, 400)
            w.set_editor_property('code', 'float a = sin(P.z * 1.7 + T * 21.0) * 0.10 + sin(P.z * 3.9 - T * 33.0) * 0.05; float b = cos(P.z * 2.3 + T * 17.0) * 0.08; return float3(a, b, 0.0);')
            w.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
            ins = []
            for nm in ('P', 'T'):
                ci = unreal.CustomInput(); ci.set_editor_property('input_name', nm); ins.append(ci)
            w.set_editor_property('inputs', ins)
            mel.connect_material_expressions(wp, '', w, 'P')
            mel.connect_material_expressions(tm, '', w, 'T')
            mel.connect_material_property(w, '', unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    elif unlit:
        m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
        mel.connect_material_property(c, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    else:
        m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
        mel.connect_material_property(c, '', unreal.MaterialProperty.MP_BASE_COLOR)
    mel.recompile_material(m)
    say('flat material %s' % path)
    return m


def assets():
    a = rt('RT_LatteA')
    b = rt('RT_LatteB')
    c = collection()
    sim = material('M_LatteSim', SIM, 'Prev', {'Pour': 0, 'Vel': 0, 'Misc': 0, 'Fx': 0}, {}, a)
    surf = material('M_LatteSurface', SURF, 'Sim', {'Fx': 0, 'GuideA': 0, 'GuideB': 0}, {'Bright': 0.42, 'ShowGuide': 0.0}, a)
    made = [a, b, c, sim, surf, flat('M_LatteCup', (0.17, 0.16, 0.14), shaded=True), flat('M_LatteSteel', (0.10, 0.11, 0.13), shaded=True),
            flat('M_LatteMilk', (0.30, 0.285, 0.25), shaded=True, wobble=True), flat('M_LatteBar', (0.40, 0.26, 0.10), True),
            instance('MI_LatteSim_FromA', sim, 'Prev', a), instance('MI_LatteSim_FromB', sim, 'Prev', b),
            instance('MI_LatteSurface_A', surf, 'Sim', a), instance('MI_LatteSurface_B', surf, 'Sim', b)]
    for i in range(3):
        t = eal.load_asset('%s/T_LatteGoal_%d' % (DIR, i))          # drawn by tools/latte_goals.py
        made.append(instance('MI_LatteGuide_%d' % i, surf, 'Sim', t if t is not None else a))
    ok = unreal.EditorLoadingAndSavingUtils.save_packages([x.get_outermost() for x in made], False)
    say('SAVED ok=%s' % ok)


def where():
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in sub.get_all_level_actors():
        l = a.get_actor_label()
        if any(k in l for k in ('Counter', 'Register', 'Espresso', 'Coworker_Cafe', 'Player_Main', 'Pastry')):
            o, e = a.get_actor_bounds(False)
            say('%-28s loc (%.0f %.0f %.0f) yaw %.0f  box centre (%.0f %.0f %.0f) half (%.0f %.0f %.0f)' % (
                l, a.get_actor_location().x, a.get_actor_location().y, a.get_actor_location().z, a.get_actor_rotation().yaw,
                o.x, o.y, o.z, e.x, e.y, e.z))


def kit():
    # Art/Blender/latte_kit.py's three models. Imported from Art/ (never from inside Content/), no dialog.
    src = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()), '..', 'Art', 'Blender', 'export', 'Latte')
    dest = '/Game/Game/Imported/Latte'
    saved = []
    for n in ('SM_LatteCup', 'SM_LatteSaucer', 'SM_LattePitcher', 'SM_LatteStream'):
        t = unreal.AssetImportTask()
        t.set_editor_property('filename', os.path.normpath(os.path.join(src, n + '.fbx')).replace(os.sep, '/'))
        t.set_editor_property('destination_path', dest)
        t.set_editor_property('automated', True)
        t.set_editor_property('replace_existing', True)
        t.set_editor_property('save', False)
        at.import_asset_tasks([t])
        m = eal.load_asset('%s/%s' % (dest, n))
        if m is None:
            say('IMPORT FAILED %s (%s)' % (n, list(t.get_editor_property('imported_object_paths')))); continue
        unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).set_nanite_settings(m, unreal.MeshNaniteSettings(enabled=False), True)
        b = m.get_bounding_box()
        say('%s tris %d box x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f slots %d' % (n, m.get_num_triangles(0), b.min.x, b.max.x, b.min.y, b.max.y,
                                                                              b.min.z, b.max.z, len(m.get_editor_property('static_materials'))))
        saved.append(m.get_outermost())
    for a in eal.list_assets(dest, False):
        o = eal.load_asset(a.split('.')[0])
        if o is not None and o.get_outermost() not in saved:
            saved.append(o.get_outermost())
    say('SAVED %s (%d packages)' % (unreal.EditorLoadingAndSavingUtils.save_packages(saved, False), len(saved)))


def guide():
    # guide <0|1|2>: freeze what is on the cup right now (RT_LatteA, left by the last Play session) as that pattern's
    # sample picture. Pour it first with latte_pie.py, STOP Play, then run this, then `assets` to point the guide at it.
    i = int(sys.argv[2])
    rt_a = eal.load_asset('%s/RT_LatteA' % DIR)
    name = '%s/T_LatteGuide_%d' % (DIR, i)
    if eal.does_asset_exist(name):
        eal.delete_asset(name)
        unreal.SystemLibrary.collect_garbage()
    t = unreal.RenderingLibrary.render_target_create_static_texture2d_editor_only(rt_a, name, unreal.TextureCompressionSettings.TC_HDR,
                                                                               unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    say('guide %d -> %s' % (i, t.get_path_name() if t else None))
    if t:
        say('SAVED %s' % unreal.EditorLoadingAndSavingUtils.save_packages([t.get_outermost()], False))


def goals():
    # the drawn goal pictures (tools/latte_goals.py). Linear data, not colour: red = foam, green = layering.
    src = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()), '..', 'Art', 'UI', 'Latte')
    saved = []
    for i in range(3):
        n = 'T_LatteGoal_%d' % i
        t = unreal.AssetImportTask()
        t.set_editor_property('filename', os.path.normpath(os.path.join(src, n + '.png')).replace(os.sep, '/'))
        t.set_editor_property('destination_path', DIR)
        t.set_editor_property('automated', True)
        t.set_editor_property('replace_existing', True)
        t.set_editor_property('save', False)
        at.import_asset_tasks([t])
        tex = eal.load_asset('%s/%s' % (DIR, n))
        if tex is None:
            say('IMPORT FAILED %s' % n); continue
        tex.set_editor_property('srgb', False)
        tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP)
        tex.set_editor_property('mip_gen_settings', unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
        tex.set_editor_property('address_x', unreal.TextureAddress.TA_CLAMP)
        tex.set_editor_property('address_y', unreal.TextureAddress.TA_CLAMP)
        say('goal %s %sx%s srgb %s' % (n, tex.blueprint_get_size_x(), tex.blueprint_get_size_y(), tex.get_editor_property('srgb')))
        saved.append(tex.get_outermost())
    say('SAVED %s' % unreal.EditorLoadingAndSavingUtils.save_packages(saved, False))


def place():
    # on the cafe counter (City_Cafe_00_CafeCounter, top at z 110), between the espresso machine and the pastry case.
    # Yaw -90 puts the camera on the customer side looking across the counter.
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    old = [a for a in sub.get_all_level_actors() if a.get_actor_label() == 'Latte_Game']
    loc, rot = unreal.Vector(-285.0, -240.0, 119.2), unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0)
    if old:
        a = old[0]
        say('already placed: moving it')
    else:
        cls = unreal.load_object(None, '/Game/Game/Blueprints/BP_LatteGame.BP_LatteGame_C')
        a = sub.spawn_actor_from_class(cls, loc, rot)
        a.set_actor_label('Latte_Game')
    a.set_is_spatially_loaded(False)          # it must exist on the first frame: it holds the opening back
    a.set_actor_transform(unreal.Transform(loc, rot, unreal.Vector(1, 1, 1)), False, False)
    say('placed %s package %s' % (a.get_path_name(), a.get_outermost().get_name()))
    gm = eal.load_asset('/Game/Game/Blueprints/BP_JumpCutGameMode')        # its JumpCutStartPlay calls LatteTryBegin
    bp = eal.load_asset('/Game/Game/Blueprints/BP_LatteGame')
    say('SAVED %s' % unreal.EditorLoadingAndSavingUtils.save_packages([a.get_outermost(), gm.get_outermost(), bp.get_outermost()], False))


try:
    mode = sys.argv[1] if len(sys.argv) > 1 else 'where'
    {'assets': assets, 'where': where, 'place': place, 'kit': kit, 'guide': guide, 'goals': goals}[mode]()
except Exception:
    import traceback
    say(traceback.format_exc())
finally:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write('\n'.join(log) + '\n')
