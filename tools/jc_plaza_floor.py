"""Gives the boss plaza's floor a paved look, on that one actor only (Sun Nov 15, GameStation).

    py tools/jc_plaza_floor.py apply     import the texture, make M_PlazaPavers + three instances, put them on City_PlazaPaving
    py tools/jc_plaza_floor.py revert    put the kit's three flat colours back on City_PlazaPaving

The floor was the kit's M_CityBrick / M_CityWall / M_CityConcrete: flat colours, shared with half the city, so they
cannot be changed. This makes one small material (texture x tint) and overrides the three slots on the placed
actor. The mesh's UVs are 1 unit = 1 m, so the material halves them: the texture is 2 m of paving.
"""
import os, sys
import unreal
out = []
def say(s):
    out.append(s); unreal.log('[plaza-floor] ' + s)
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace(os.sep, '/')
D = '/Game/Game/Materials/Plaza'
E = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
a = next(x for x in sub.get_all_level_actors() if x.get_actor_label() == 'City_PlazaPaving')
c = a.static_mesh_component
try:
    if sys.argv[1] == 'revert':
        for i, n in enumerate(('M_CityBrick', 'M_CityWall', 'M_CityConcrete')):
            c.set_material(i, E.load_asset('/Game/Game/Materials/City/' + n))
        pk = []
    else:
        tex = E.load_asset(D + '/T_PlazaPavers')
        if tex is None:
            t = unreal.AssetImportTask()
            t.set_editor_property('filename', REPO + '/Art/Textures/T_PlazaPavers.png')
            t.set_editor_property('destination_path', D)
            t.set_editor_property('automated', True); t.set_editor_property('save', False); t.set_editor_property('replace_existing', True)
            AT.import_asset_tasks([t])
            tex = E.load_asset(D + '/T_PlazaPavers')
        say('texture %s' % (tex.get_path_name() if tex else None))
        mat = E.load_asset(D + '/M_PlazaPavers')
        if mat is None:
            mat = AT.create_asset('M_PlazaPavers', D, unreal.Material, unreal.MaterialFactoryNew())
            uv = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -900, 0)
            uv.set_editor_property('u_tiling', 0.5); uv.set_editor_property('v_tiling', 0.5)
            ts = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -650, 0)
            ts.set_editor_property('parameter_name', 'Tex'); ts.set_editor_property('texture', tex)
            MEL.connect_material_expressions(uv, '', ts, 'UVs')
            tint = MEL.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -650, 300)
            tint.set_editor_property('parameter_name', 'Tint'); tint.set_editor_property('default_value', unreal.LinearColor(0.7, 0.6, 0.45, 1))
            mul = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -350, 100)
            MEL.connect_material_expressions(ts, 'RGB', mul, 'A'); MEL.connect_material_expressions(tint, '', mul, 'B')
            MEL.connect_material_property(mul, '', unreal.MaterialProperty.MP_BASE_COLOR)
            ro = MEL.create_material_expression(mat, unreal.MaterialExpressionConstant, -350, 350)
            ro.set_editor_property('r', 0.85)
            MEL.connect_material_property(ro, '', unreal.MaterialProperty.MP_ROUGHNESS)
            MEL.recompile_material(mat)
        pk = [tex.get_outermost(), mat.get_outermost()]
        tints = {'MI_PlazaBorder': (0.46, 0.22, 0.17), 'MI_PlazaStoneA': (0.74, 0.60, 0.42), 'MI_PlazaStoneB': (0.60, 0.45, 0.33)}
        for i, n in enumerate(('MI_PlazaBorder', 'MI_PlazaStoneA', 'MI_PlazaStoneB')):
            mi = E.load_asset(D + '/' + n)
            if mi is None:
                mi = AT.create_asset(n, D, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                MEL.set_material_instance_parent(mi, mat)
            r, g, b = tints[n]
            MEL.set_material_instance_vector_parameter_value(mi, 'Tint', unreal.LinearColor(r, g, b, 1))
            MEL.update_material_instance(mi)
            c.set_material(i, mi); pk.append(mi.get_outermost())
    a.set_actor_transform(a.get_actor_transform(), False, True)
    say('City_PlazaPaving now wears %s' % [m.get_name() for m in c.get_materials()])
    say('SAVED ok=%s' % unreal.EditorLoadingAndSavingUtils.save_packages(pk + [a.get_outermost()], False))
except Exception as ex:
    say('ERROR %s' % ex)
open(os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'plaza_floor.txt'), 'w').write('\n'.join(out) + '\n')
