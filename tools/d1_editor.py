# One-off editor step from the first build (Nov 12), copied from the ignored JumpCut/Saved/ so the level set-up can be traced.
# Run with `py <path> <step>` in the Unreal editor console (a3_pie.py: during Play mode; the others: Play mode stopped).
# Read it before re-running: steps change placed actors in Lvl_JumpCut and some save the level.
"""D1 / C1b editor steps (NOT during PIE). py <this> <step>. Appends to Saved/d1_editor.txt.
steps:
  c1b      checkpoint trigger radius 550 on the placed Checkpoint_StreetEnd; Floor_Base material re-set; full transforms re-set
  mats     make M_WarnFreeze (unlit cyan) and M_Boss (lit flat violet), save them
  place    place Boss_Freeze at Marker_BossSpot, link the gates
  save     save the current level (map + external actors)
  show     print the linked actors
"""
import sys
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())
args = sys.argv[1:] or ['show']
log = ['--- ' + ' '.join(args)]
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def by_label(lab):
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == lab:
            return a
    return None


def comp(a, name):
    for c in a.get_components_by_class(unreal.SceneComponent):
        if c.get_name() == name:
            return c
    return None


def retransform(a):
    a.modify()
    a.set_actor_transform(unreal.Transform(a.get_actor_location(), a.get_actor_rotation(), a.get_actor_scale3d()), False, True)


def make_mat(name, rgb, unlit):
    MEL = unreal.MaterialEditingLibrary
    path = '/Game/Game/Materials/' + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        m = unreal.load_asset(path)
        MEL.delete_all_material_expressions(m)
    else:
        m = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, '/Game/Game/Materials', unreal.Material,
                                                                     unreal.MaterialFactoryNew())
    col = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -300, 0)
    col.set_editor_property('constant', unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1.0))
    if unlit:
        m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
        MEL.connect_material_property(col, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    else:
        MEL.connect_material_property(col, '', unreal.MaterialProperty.MP_BASE_COLOR)
        rough = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -300, 200)
        rough.set_editor_property('r', 0.7)
        MEL.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.recompile_material(m)
    log.append('%s save = %s' % (name, unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)))


try:
    step = args[0]
    if step == 'c1b':
        cp = by_label('Checkpoint_StreetEnd')
        ts = comp(cp, 'TriggerSphere')
        ts.modify()
        ts.set_sphere_radius(550.0, False)
        retransform(cp)
        log.append('checkpoint radius now %s' % ts.get_scaled_sphere_radius())
        fl = by_label('Floor_Base')
        smc = fl.static_mesh_component
        smc.modify()
        smc.set_material(0, unreal.load_asset('/Game/Game/Materials/M_GreyFloor'))
        retransform(fl)
        log.append('floor mats %s' % [m.get_name() for m in smc.get_materials()])
    elif step == 'mats':
        make_mat('M_WarnFreeze', (0.0, 0.85, 1.0), True)
        make_mat('M_Boss', (0.28, 0.04, 0.42), False)
    elif step == 'place':
        boss = by_label('Boss_Freeze')
        mk = by_label('Marker_BossSpot')
        cls = unreal.load_class(None, '/Game/Game/Blueprints/BP_BossFreeze.BP_BossFreeze_C')
        loc = mk.get_actor_location()
        # capsule centre above the floor (Z = 0): half height of the capsule
        if boss is None:
            boss = eas.spawn_actor_from_class(cls, unreal.Vector(loc.x, loc.y, 200.0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
            boss.set_actor_label('Boss_Freeze')
        hh = boss.capsule_component.get_scaled_capsule_half_height()
        boss.set_editor_property('BossExitGate', by_label('Gate_PlazaExit'))
        ge = by_label('Gate_PlazaEntry')
        ge.set_editor_property('GateEnemyToWake', boss)
        boss.set_actor_transform(unreal.Transform(unreal.Vector(loc.x, loc.y, hh + 2.0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0), unreal.Vector(1, 1, 1)), False, True)
        retransform(ge)
        retransform(boss)
        log.append('boss at %s yaw %s halfheight %s' % (boss.get_actor_location(), boss.get_actor_rotation().yaw, hh))
    elif step == 'save':
        log.append('save_current_level = %s' % unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
    boss = by_label('Boss_Freeze')
    if boss:
        log.append('Boss_Freeze %s BossExitGate=%s pkg=%s' % (boss.get_actor_location(), boss.get_editor_property('BossExitGate'), boss.get_package().get_name()))
    ge = by_label('Gate_PlazaEntry')
    log.append('Gate_PlazaEntry GateEnemyToWake=%s' % ge.get_editor_property('GateEnemyToWake'))
    log.append('checkpoint radius %s' % comp(by_label('Checkpoint_StreetEnd'), 'TriggerSphere').get_scaled_sphere_radius())
except Exception:
    import traceback
    log.append('ERROR ' + traceback.format_exc())
with open(ROOT + 'd1_editor.txt', 'a') as f:
    f.write('\n'.join(log) + '\n')
