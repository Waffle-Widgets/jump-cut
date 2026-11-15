"""Beat 1 explosion, stage 1: the two assets.

  GC_CrashCar      the wreck cut into Chaos pieces, from SM_CrashCar, same recipe as GC_CrateStack
  M_FXExplosion    T_FX_Explosion_6x6 as a 36-frame flipbook card, driven by a 'Frame' scalar

Run:  py <repo>/tools/b1x_assets.py
Writes Saved/jcpy/b1x_assets.json. Saves the two assets (they are new, not placed actors).
"""
import unreal, os, sys, json, traceback

MODE = sys.argv[1] if len(sys.argv) > 1 else 'all'   # all | gc | mat

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
res = {}
SM = '/Game/Game/Imported/City/SM_CrashCar'
GC = '/Game/Game/Destruction/GC_CrashCar'
TEX = '/Game/Game/FX/Textures/T_FX_Explosion_6x6'
MATDIR = '/Game/Game/Materials'
SIDE = 6.0

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    assert ues.get_editor_world().get_name() == 'Lvl_JumpCut', 'wrong world'
    assert ues.get_game_world() is None, 'PIE is running'

    # ---------------------------------------------------------------- GC_CrashCar
    DBL = unreal.DataflowBlueprintLibrary
    if MODE in ('all', 'gc'):
     if True:
      gc = unreal.load_asset(GC)
      sm = unreal.load_asset(SM)
      assert gc is not None and sm is not None, 'missing GC or SM'
      r = {'vars': [str(v) for v in DBL.get_dataflow_variable_list(gc)]}
      r['override'] = str(DBL.override_dataflow_variable_object(gc, 'SourceStaticMesh', sm))
      r['regen'] = str(DBL.regenerate_asset_from_dataflow(gc))
      r['mats'] = [m.get_name() if m else None for m in gc.get_editor_property('materials')]
      try:
          r['pieces'] = gc.get_editor_property('geometry_collection').num_elements('Transform')
      except Exception as e:
          r['pieces'] = 'n/a %s' % e
      r['saved'] = unreal.EditorAssetLibrary.save_loaded_asset(gc)
      res['gc'] = r

    # ---------------------------------------------------------------- M_FXExplosion
    if MODE == 'gc':
        raise SystemExit
    at = unreal.AssetToolsHelpers.get_asset_tools()
    mel = unreal.MaterialEditingLibrary
    tex = unreal.load_asset(TEX)
    assert tex is not None, 'missing ' + TEX
    name = 'M_FXExplosion'
    path = '%s/%s' % (MATDIR, name)
    m = unreal.load_asset(path)
    if m is None:
        m = at.create_asset(name, MATDIR, unreal.Material, unreal.MaterialFactoryNew())
    else:
        mel.delete_all_material_expressions(m)
    m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
    # ADDITIVE: the sheet is drawn on black, so the background adds nothing and no alpha is needed.
    m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
    m.set_editor_property('two_sided', True)

    def ex(cls, x, y):
        return mel.create_material_expression(m, cls, x, y)

    # one cell of the 6x6 sheet
    tc = ex(unreal.MaterialExpressionTextureCoordinate, -1500, 0)
    tc.set_editor_property('u_tiling', 1.0 / SIDE)
    tc.set_editor_property('v_tiling', 1.0 / SIDE)
    # Frame 0..35 -> (col, row)
    fr = ex(unreal.MaterialExpressionScalarParameter, -1500, 250)
    fr.set_editor_property('parameter_name', 'Frame')
    fr.set_editor_property('default_value', 0.0)
    six = ex(unreal.MaterialExpressionConstant, -1500, 400)
    six.set_editor_property('r', SIDE)
    ffl = ex(unreal.MaterialExpressionFloor, -1350, 250)   # a fractional Frame lands between cells
    mel.connect_material_expressions(fr, '', ffl, '')
    dv = ex(unreal.MaterialExpressionDivide, -1250, 300)
    mel.connect_material_expressions(ffl, '', dv, 'A')
    mel.connect_material_expressions(six, '', dv, 'B')
    flr = ex(unreal.MaterialExpressionFloor, -1050, 300)          # row
    mel.connect_material_expressions(dv, '', flr, '')
    mul = ex(unreal.MaterialExpressionMultiply, -900, 420)        # row*6
    mel.connect_material_expressions(flr, '', mul, 'A')
    mel.connect_material_expressions(six, '', mul, 'B')
    sub = ex(unreal.MaterialExpressionSubtract, -750, 420)        # col = Frame - row*6
    mel.connect_material_expressions(ffl, '', sub, 'A')
    mel.connect_material_expressions(mul, '', sub, 'B')
    offu = ex(unreal.MaterialExpressionDivide, -600, 420)         # col/6
    mel.connect_material_expressions(sub, '', offu, 'A')
    mel.connect_material_expressions(six, '', offu, 'B')
    offv = ex(unreal.MaterialExpressionDivide, -600, 250)         # row/6
    mel.connect_material_expressions(flr, '', offv, 'A')
    mel.connect_material_expressions(six, '', offv, 'B')
    app = ex(unreal.MaterialExpressionAppendVector, -430, 330)
    mel.connect_material_expressions(offu, '', app, 'A')
    mel.connect_material_expressions(offv, '', app, 'B')
    add = ex(unreal.MaterialExpressionAdd, -280, 120)
    mel.connect_material_expressions(tc, '', add, 'A')
    mel.connect_material_expressions(app, '', add, 'B')
    ts = ex(unreal.MaterialExpressionTextureSample, -120, 0)
    ts.set_editor_property('texture', tex)
    mel.connect_material_expressions(add, '', ts, 'UVs')
    # glow stays modest: this project's look posterises and a hot emissive clips to white
    glow = ex(unreal.MaterialExpressionScalarParameter, -120, 320)
    glow.set_editor_property('parameter_name', 'Glow')
    # 1.6 came out of the posteriser with a white core and a lavender fringe (PIE capture,
    # 2026-11-15). This look clips hot emissives; judge it from a frame, never from the number.
    glow.set_editor_property('default_value', 1.1)
    em = ex(unreal.MaterialExpressionMultiply, 60, 120)
    mel.connect_material_expressions(ts, 'RGB', em, 'A')
    mel.connect_material_expressions(glow, '', em, 'B')
    mel.connect_material_property(em, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    one = ex(unreal.MaterialExpressionConstant, 60, 330)
    one.set_editor_property('r', 1.0)
    mel.connect_material_property(one, '', unreal.MaterialProperty.MP_OPACITY)
    mel.recompile_material(m)
    res['mat'] = {'path': m.get_path_name(),
                  'saved': unreal.EditorAssetLibrary.save_loaded_asset(m),
                  'params': [str(p) for p in mel.get_scalar_parameter_names(m)]
                  if hasattr(mel, 'get_scalar_parameter_names') else 'n/a'}
    res['ok'] = True
except SystemExit:
    res['ok'] = True
except Exception as e:
    res['ok'] = False
    res['error'] = '%r\n%s' % (e, traceback.format_exc())
with open(os.path.join(OUT, 'b1x_assets.json'), 'w') as fh:
    json.dump(res, fh, indent=1)
print('B1X ASSETS DONE ok=%s' % res.get('ok'))
