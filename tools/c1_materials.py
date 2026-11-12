"""C1: flat-colour grey-box materials (lit, constant colour, rough). Run in the editor: py <full path>.
Writes Saved/c1_materials.txt. Saves only these assets."""
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())
MATS = {
    'M_GreyWall': (0.30, 0.30, 0.32),
    'M_GreyFloor': (0.12, 0.12, 0.13),
    'M_GateColor': (0.80, 0.35, 0.05),
    'M_CheckGreen': (0.05, 0.60, 0.15),
    'M_PropBlue': (0.10, 0.25, 0.60),
    'M_PropRed': (0.60, 0.08, 0.08),
}
log = []
try:
    MEL = unreal.MaterialEditingLibrary
    for name, rgb in MATS.items():
        path = '/Game/Game/Materials/' + name
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            m = unreal.load_asset(path)
            MEL.delete_all_material_expressions(m)
        else:
            m = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
                name, '/Game/Game/Materials', unreal.Material, unreal.MaterialFactoryNew())
        col = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -300, 0)
        col.set_editor_property('constant', unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1.0))
        MEL.connect_material_property(col, '', unreal.MaterialProperty.MP_BASE_COLOR)
        rough = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -300, 200)
        rough.set_editor_property('r', 0.9)
        MEL.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
        MEL.recompile_material(m)
        log.append('%s save = %s' % (name, unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)))
except Exception as e:
    log.append('ERROR: %r' % e)
with open(ROOT + 'c1_materials.txt', 'w') as f:
    f.write('\n'.join(log))
