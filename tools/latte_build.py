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
src -= Vel.xy * Vel.z * exp(-r2 / 0.004);
float prev = Texture2DSample(Prev, PrevSampler, src + 0.5).r;
float r = sqrt(r2);
float inj = Pour.z * (1.0 - smoothstep(Misc.x * 0.6, Misc.x, r));
float v = max(prev, inj);
float rim = Misc.y * smoothstep(Misc.x * 0.9, Misc.x * 1.1, r) * (1.0 - smoothstep(Misc.x * 1.3, Misc.x * 1.7, r));
v = lerp(v, 0.0, saturate(rim));
v = lerp(v, 0.0, saturate(Vel.w * exp(-r2 / 0.00022)));
v = lerp(v, smoothstep(0.0, 1.0, v), Misc.z);
v *= (dot(p, p) < 0.2304) ? 1.0 : 0.0;
return float3(v, v, v);
"""

SURF = r"""
float2 p = UV - 0.5;
float v = Texture2DSample(Sim, SimSampler, UV).r;
float n = sin(p.x * 37.0 + sin(p.y * 23.0) * 2.0) * sin(p.y * 31.0 + sin(p.x * 19.0) * 2.0);
float3 crema = lerp(float3(0.105, 0.040, 0.012), float3(0.165, 0.068, 0.022), 0.5 + 0.5 * n);
float3 halo = float3(0.36, 0.20, 0.09);
float3 milk = float3(0.80, 0.74, 0.62);
float3 c = lerp(crema, halo, smoothstep(0.04, 0.30, v));
c = lerp(c, milk, smoothstep(0.30, 0.55, v));
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
    if len(c.get_editor_property('vector_parameters')) != 3:
        ps = []
        for n, dv in (('Pour', (0, 0, 0, 0)), ('Vel', (0, 0, 0, 0)), ('Misc', (0.035, 0, 0.25, 0))):
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
    mel.update_material_instance(mi)
    got = mel.get_material_instance_texture_parameter_value(mi, tex_name)
    say('   reads back %s' % (got.get_name() if got else None))
    return mi


def flat(name, rgb, unlit=False):
    path = '%s/%s' % (DIR, name)
    m = eal.load_asset(path)
    if m is None:
        m = at.create_asset(name, DIR, unreal.Material, unreal.MaterialFactoryNew())
    mel.delete_all_material_expressions(m)
    c = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -300, 0)
    c.set_editor_property('constant', unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1))
    if unlit:
        m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
        mel.connect_material_property(c, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    else:
        mel.connect_material_property(c, '', unreal.MaterialProperty.MP_BASE_COLOR)
    mel.recompile_material(m)
    say('flat material %s' % path)
    return m


def assets():
    a = rt('RT_LatteA')
    b = rt('RT_LatteB')
    c = collection()
    sim = material('M_LatteSim', SIM, 'Prev', {'Pour': 0, 'Vel': 0, 'Misc': 0}, {}, a)
    surf = material('M_LatteSurface', SURF, 'Sim', {}, {'Bright': 0.42}, a)
    made = [a, b, c, sim, surf, flat('M_LatteCup', (0.85, 0.83, 0.78)), flat('M_LatteSteel', (0.42, 0.44, 0.47)),
            flat('M_LatteMilk', (0.80, 0.75, 0.64), True), flat('M_LatteBar', (0.75, 0.55, 0.25), True),
            instance('MI_LatteSim_FromA', sim, 'Prev', a), instance('MI_LatteSim_FromB', sim, 'Prev', b),
            instance('MI_LatteSurface_A', surf, 'Sim', a), instance('MI_LatteSurface_B', surf, 'Sim', b)]
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
    {'assets': assets, 'where': where, 'place': place}[mode]()
except Exception:
    import traceback
    say(traceback.format_exc())
finally:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write('\n'.join(log) + '\n')
