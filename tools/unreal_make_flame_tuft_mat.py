"""M_FlameTuft: a FLAME-SHAPED cel sprite for Niagara, instead of a disc.

Why this exists. `M_FlameParticle3D` masks every sprite to a hard circle with a dark rim, and a
cluster of those reads as COINS, not fire - which is exactly what the editor capture of NS_CarFire
showed and what the `niagara-fx` skill warns about. The cure is the silhouette, not the colour:

  * the mask radius varies with angle (five soft lobes), so each sprite is a tuft rather than a disc;
  * the lobes are rotated per particle by ParticleRandom, so a cluster does not repeat one motif;
  * the colour bands run on d/r rather than d, so they follow the lobes instead of cutting across them;
  * the near-black outer rim is gone (0.55 instead of 0.22) - that rim is what draws the coin's edge.

Unlit + Masked, same as the disc version, so it stays crisp through the posterising look rather
than blooming. Run in the editor console:
    py <repo>/tools/unreal_make_flame_tuft_mat.py
Safe to re-run: the material is rebuilt in place, so emitters keep pointing at it.
"""
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()).rstrip('/')
MAT = '/Game/Game/Materials'
at = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary

path = f'{MAT}/M_FlameTuft'
if eal.does_asset_exist(path):
    m = unreal.load_asset(path)
    mel.delete_all_material_expressions(m)
else:
    m = at.create_asset('M_FlameTuft', MAT, unreal.Material, unreal.MaterialFactoryNew())
m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_MASKED)
m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
m.set_editor_property('two_sided', True)
for flag in ('used_with_niagara_sprites', 'used_with_niagara_ribbons', 'used_with_niagara_mesh_particles'):
    m.set_editor_property(flag, True)

y = [0]
notes = []


def e(cls, x=-900):
    y[0] += 120
    return mel.create_material_expression(m, cls, x, y[0])


def custom(code, inputs, out_type):
    c = e(unreal.MaterialExpressionCustom, -400)
    c.set_editor_property('code', code)
    c.set_editor_property('output_type', out_type)
    ins = []
    for n, _, _ in inputs:
        ci = unreal.CustomInput()
        ci.set_editor_property('input_name', n)
        ins.append(ci)
    c.set_editor_property('inputs', ins)
    for n, node, pin in inputs:
        mel.connect_material_expressions(node, pin, c, n)
    return c


pc = e(unreal.MaterialExpressionParticleColor)
uv = e(unreal.MaterialExpressionTextureCoordinate)

rnd = None
try:
    rnd = e(unreal.MaterialExpressionParticleRandom)
    notes.append('ParticleRandom: yes')
except Exception as ex:
    notes.append('ParticleRandom: NOT AVAILABLE (%s) - lobes will not be rotated per particle'
                 % str(ex)[:60])

# r(angle) is the tuft silhouette; t = d/r runs the colour bands along it.
SHAPE = ("float2 p = UV - 0.5;\n"
         "float d = length(p) * 2.0;\n"
         "float a = atan2(p.y, p.x) + R * 6.2831853;\n"
         "float r = 0.80 + 0.20 * sin(a * 5.0 + sin(a * 3.0));\n"
         "float t = d / max(r, 0.001);\n")

col_inputs = [('C', pc, 'RGB'), ('UV', uv, '')]
mask_inputs = [('UV', uv, '')]
if rnd is not None:
    col_inputs.append(('R', rnd, ''))
    mask_inputs.append(('R', rnd, ''))
    PRE = ""
else:
    PRE = "float R = 0.0;\n"

col = custom(PRE + SHAPE +
             "float m = max(C.r, max(C.g, C.b));\n"
             "return t < 0.28 ? lerp(C, float3(m, m, m), 0.35)\n"
             "     : (t < 0.72 ? C : C * 0.55);",
             col_inputs, unreal.CustomMaterialOutputType.CMOT_FLOAT3)
mask = custom(PRE + SHAPE + "return t < 1.0 ? 1.0 : 0.0;",
              mask_inputs, unreal.CustomMaterialOutputType.CMOT_FLOAT1)

mel.connect_material_property(col, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.connect_material_property(mask, '', unreal.MaterialProperty.MP_OPACITY_MASK)
mel.recompile_material(m)
eal.save_loaded_asset(m)
with open(f'{ROOT}/Saved/flame_tuft_mat.txt', 'w') as fh:
    fh.write('M_FlameTuft made\n' + '\n'.join(notes) + '\n')
print('FLAME_TUFT_MAT_DONE ' + '; '.join(notes))
