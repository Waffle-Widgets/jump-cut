"""Beat 1's fire hazard: the materials and the level actors BP_Coworker drives.

    py <repo>/tools/b1_fire_actors.py           make/refresh
    py <repo>/tools/b1_fire_actors.py report    read back, change nothing

Makes two materials of our own:
  M_FireHot    unlit orange - the flame cone on the car
  M_BlastRing  unlit masked - our own T_FX_WarnRing sheet as a warning ring on the floor,
               so the blast radius is a thing you can see and walk out of rather than a number

Places (tag B1_Fire, so a re-run replaces exactly its own actors), all hidden in game at start -
BP_Coworker shows them when the car catches:
  B1_Cafe_Fire       a cone on the car's bonnet; BP_Coworker scales it every tick so it licks
  B1_Cafe_FireLight  an orange point light, no shadows (same rule as Cafe_WarmFill_A/B: Lumen is
                     off on purpose, so warmth comes from small direct lights)
  B1_Cafe_BlastRing  a flat plane the size of the blast, on the floor

Never saves. Save with jc_save_actors.py.
"""
import unreal, os, sys

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
TAG = 'B1_Fire'
MATDIR = '/Game/Game/Materials'
RING_TEX = '/Game/Game/FX/Textures/T_FX_WarnRing'
CONE = '/Engine/BasicShapes/Cone.Cone'
PLANE = '/Engine/BasicShapes/Plane.Plane'

CAR = (-520.0, 0.0, 0.0)
BLAST_RADIUS = 700.0

MODE = 'make'
for a in sys.argv[1:]:
    if a in ('make', 'report'):
        MODE = a

log = []
def say(s): log.append(str(s)); print(str(s))

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    if ues.get_editor_world().get_name() != 'Lvl_JumpCut':
        raise RuntimeError('wrong world')
    if ues.get_game_world() is not None:
        raise RuntimeError('PIE is running - stop it first')
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    if MODE == 'report':
        for a in eas.get_all_level_actors():
            if unreal.Name(TAG) in a.get_editor_property('tags'):
                say('%-22s %-20s %s hidden=%s scale=%s' % (
                    a.get_actor_label(), a.get_class().get_name(), a.get_actor_location(),
                    a.get_editor_property('hidden'), a.get_actor_scale3d()))
        for m in ('M_FireHot', 'M_BlastRing'):
            say('%s -> %s' % (m, unreal.load_asset('%s/%s' % (MATDIR, m))))
        raise SystemExit

    at = unreal.AssetToolsHelpers.get_asset_tools()
    mel = unreal.MaterialEditingLibrary

    def unlit_colour(name, r, g, b, glow):
        path = '%s/%s' % (MATDIR, name)
        m = unreal.load_asset(path)
        if m is None:
            m = at.create_asset(name, MATDIR, unreal.Material, unreal.MaterialFactoryNew())
        else:
            mel.delete_all_material_expressions(m)
        m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
        m.set_editor_property('two_sided', True)
        c = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -400, 0)
        c.set_editor_property('constant', unreal.LinearColor(r * glow, g * glow, b * glow, 1.0))
        mel.connect_material_property(c, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        mel.recompile_material(m)
        say('%s built (unlit %.2f %.2f %.2f x%.1f)' % (name, r, g, b, glow))
        return m

    # glow 1.7, not 3.0: this project's look posterises and clips, and at 3.0 the flame came out
    # of the tonemapper WHITE instead of orange (see the Nov 14 capture). Judge an emissive by a
    # frame through MI_AnimeLook_JumpCut, never by the number.
    unlit_colour('M_FireHot', 1.0, 0.34, 0.05, 1.7)

    # the ring: our own warn-ring sheet as a mask, red, unlit, translucent
    name = 'M_BlastRing'
    path = '%s/%s' % (MATDIR, name)
    ring = unreal.load_asset(path)
    if ring is None:
        ring = at.create_asset(name, MATDIR, unreal.Material, unreal.MaterialFactoryNew())
    else:
        mel.delete_all_material_expressions(ring)
    ring.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
    ring.set_editor_property('blend_mode', unreal.BlendMode.BLEND_TRANSLUCENT)
    ring.set_editor_property('two_sided', True)
    tex = unreal.load_asset(RING_TEX)
    if tex is None:
        raise RuntimeError('missing %s' % RING_TEX)
    ts = mel.create_material_expression(ring, unreal.MaterialExpressionTextureSample, -500, 0)
    ts.set_editor_property('texture', tex)
    col = mel.create_material_expression(ring, unreal.MaterialExpressionConstant3Vector, -500, 250)
    col.set_editor_property('constant', unreal.LinearColor(2.4, 0.12, 0.08, 1.0))
    mel.connect_material_property(col, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.connect_material_property(ts, 'R', unreal.MaterialProperty.MP_OPACITY)
    mel.recompile_material(ring)
    say('M_BlastRing built from %s (R channel -> opacity)' % RING_TEX)

    # ---------------- wipe our own actors
    removed = 0
    for a in list(eas.get_all_level_actors()):
        if unreal.Name(TAG) in a.get_editor_property('tags'):
            eas.destroy_actor(a); removed += 1
    say('removed %d earlier %s actors' % (removed, TAG))

    def place_mesh(label, mesh, mat, loc, scale, rot=None):
        a = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc),
                                       rot or unreal.Rotator())
        c = a.static_mesh_component
        c.set_mobility(unreal.ComponentMobility.MOVABLE)
        c.set_static_mesh(unreal.load_asset(mesh))
        c.set_material(0, mat)
        c.set_editor_property('cast_shadow', False)
        a.set_actor_scale3d(unreal.Vector(*scale))
        a.set_actor_enable_collision(False)
        a.set_actor_label(label)
        a.set_editor_property('tags', [unreal.Name(TAG)])
        a.set_actor_hidden_in_game(True)
        a.set_actor_location_and_rotation(unreal.Vector(*loc), rot or unreal.Rotator(), False, True)
        say('%-20s at %s scale %s hidden=%s' % (label, a.get_actor_location(),
                                                a.get_actor_scale3d(),
                                                a.get_editor_property('hidden')))
        return a

    fire = place_mesh('B1_Cafe_Fire', CONE, unreal.load_asset(MATDIR + '/M_FireHot'),
                      (CAR[0] + 20.0, 0.0, 150.0), (2.9, 2.9, 2.1))
    ring_a = place_mesh('B1_Cafe_BlastRing', PLANE, ring,
                        (CAR[0], 0.0, 4.0), (BLAST_RADIUS * 2.0 / 100.0, BLAST_RADIUS * 2.0 / 100.0, 1.0))

    lt = eas.spawn_actor_from_class(unreal.PointLight, unreal.Vector(CAR[0] + 20.0, 0.0, 230.0),
                                    unreal.Rotator())
    lc = lt.point_light_component
    lc.set_mobility(unreal.ComponentMobility.MOVABLE)
    lc.set_editor_property('intensity', 14.0)
    lc.set_editor_property('intensity_units', unreal.LightUnits.CANDELAS)
    lc.set_editor_property('light_color', unreal.Color(255, 138, 48, 255))
    lc.set_editor_property('attenuation_radius', 1100.0)
    lc.set_editor_property('cast_shadows', False)
    lt.set_actor_label('B1_Cafe_FireLight')
    lt.set_editor_property('tags', [unreal.Name(TAG)])
    lt.set_actor_hidden_in_game(True)
    lt.set_actor_location_and_rotation(unreal.Vector(CAR[0] + 20.0, 0.0, 230.0), unreal.Rotator(), False, True)
    say('B1_Cafe_FireLight at %s hidden=%s' % (lt.get_actor_location(), lt.get_editor_property('hidden')))

    say('')
    say('blast radius %.0f cm from %s: safe is x > %.0f, and the cafe door is at x = 615'
        % (BLAST_RADIUS, CAR, CAR[0] + BLAST_RADIUS))
    say('NOT SAVED.')
except SystemExit:
    pass
except Exception as e:
    import traceback
    say('ERROR %r' % e); say(traceback.format_exc())
with open(os.path.join(OUT, 'b1_fire_actors.txt'), 'w') as fh:
    fh.write('\n'.join(log))
