"""The cafe sign moves outside, and the boss plaza gets props along its walls (Sun Nov 15, GameStation).

    py tools/jc_boss_dress.py sign      City_CafeSign: out of the cafe, projecting from the street face of the wall
    py tools/jc_boss_dress.py dress     places City_BossDress_* props round the EDGE of the plaza. Run again = replaces them.
    py tools/jc_boss_dress.py undress   removes them

The plaza is 30 x 30 m of paving inside four plain walls with about a dozen props: it reads as a grey box. Nothing
new is modelled here. Every prop is a model already in the game (M Station's Meshy pieces and the Tripo ones),
stood within 1.3 m of a wall so the fight keeps its floor. The gates (y -300..300 on the east and west walls) and
the four lamps are left clear. The arena itself (issue #50: "dress the edges without changing the arena") is
untouched: nothing is nearer the middle than 13.3 m from it on any axis.
"""
import os, sys
import unreal
MODE = sys.argv[1]
out = []
def say(s):
    out.append(s); unreal.log('[boss-dress] ' + s)
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
S = '/Game/Game/Imported/Street/%s/SM_%s'
def T(x, y, z, yaw, sc=1.0):
    return unreal.Transform(location=unreal.Vector(x, y, z), rotation=unreal.Rotator(roll=0, pitch=0, yaw=yaw), scale=unreal.Vector(sc, sc, sc))
if MODE == 'sign':
    a = next(x for x in sub.get_all_level_actors() if x.get_actor_label() == 'City_CafeSign')
    a.set_actor_transform(T(651.0, -250.0, 0.0, 0.0), False, True)
    o, e = a.get_actor_bounds(False)
    say('City_CafeSign now x %.0f..%.0f y %.0f..%.0f z %.0f..%.0f' % (o.x-e.x, o.x+e.x, o.y-e.y, o.y+e.y, o.z-e.z, o.z+e.z))
    say('SAVED ok=%s' % unreal.EditorLoadingAndSavingUtils.save_packages([a.get_outermost()], False))
else:
    old = [x for x in sub.get_all_level_actors() if x.get_actor_label().startswith('City_BossDress_')]
    pk = [x.get_outermost() for x in old]
    for x in old:
        sub.destroy_actor(x)
    say('removed %d old dressing actors' % len(old))
    if pk:
        say('old packages saved (deletes their files) ok=%s' % unreal.EditorLoadingAndSavingUtils.save_packages(pk, False))
    if MODE == 'dress':
        N, Sy, E, Wx = 1418.0, -1418.0, 9520.0, 6720.0
        P = [  # model, x, y, z, yaw, scale
            ('PotRowM', 7150, N, 0, 180, 1), ('ShopDisplayM', 7520, N, 0, 180, 1), ('ShopDisplayM', 7720, N, 0, 180, 1),
            ('BenchM', 7930, N, 0, 180, 1), ('AFrameBoardM', 8300, 1360, 0, 180, 1), ('VendingMachineM', 8420, N, 0, 180, 1),
            ('VendingMachineM', 8545, N, 0, 180, 1), ('PotRowM', 8960, N, 0, 180, 1), ('BicycleM', 9150, 1400, 0, 180, 1),
            ('PlanterM', 9500, N, 0, 180, 1),
            ('PlanterM', 6760, Sy, 0, 0, 1), ('BenchM', 8540, Sy, 0, 0, 1), ('ScooterM', 9290, -1385, 0, 0, 1),
            ('GasBottlesM', 9500, -1440, 0, 0, 0.7), ('AFrameBoardM', 7780, -1360, 0, 0, 1),
            ('VendingMachineM', E, 560, 0, 90, 1), ('BenchM', E, 840, 0, 90, 1), ('PotRowM', E, 1150, 0, 90, 1),
            ('PlanterM', E, -560, 0, 90, 1), ('ShopDisplayM', E, -820, 0, 90, 1), ('BenchM', E, -1100, 0, 90, 1),
            ('BenchM', Wx, 560, 0, -90, 1), ('PlanterM', Wx, 820, 0, -90, 1), ('HedgeM', Wx, 1120, 0, -90, 1),
            ('VendingMachineM', Wx, -520, 0, -90, 1), ('VendingMachineM', Wx, -645, 0, -90, 1), ('PotRowM', Wx, -1000, 0, -90, 1),
            ('ACUnitM', 7400, 1432, 250, 180, 1), ('ACUnitM', 8760, 1432, 250, 180, 1),
            ('ACUnitM', 7260, -1432, 250, 0, 1), ('ACUnitM', 9020, -1432, 250, 0, 1),
        ]
        made = []
        for i, (m, x, y, z, yaw, sc) in enumerate(P):
            mesh = unreal.EditorAssetLibrary.load_asset(S % (m, m))
            if mesh is None:
                say('MISSING %s' % m); continue
            a = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z))
            a.set_actor_label('City_BossDress_%02d_%s' % (i, m))
            a.static_mesh_component.set_static_mesh(mesh)
            a.static_mesh_component.set_mobility(unreal.ComponentMobility.STATIC)
            a.tags = ['JC_City', 'JC_BossDress']
            a.set_actor_transform(T(x, y, z, yaw, sc), False, True)
            made.append(a)
        # lantern strings: the kit's own, with the materials an existing one wears
        src = next((x for x in sub.get_all_level_actors() if x.get_actor_label().startswith('City_Lantern_')), None)
        if src:
            lm = src.static_mesh_component.static_mesh; mats = src.static_mesh_component.get_materials()
            for i, (x, y, yaw) in enumerate([(7500, 1475, 180), (8740, 1475, 180), (7500, -1475, 0), (8740, -1475, 0), (9575, 900, 90), (9575, -900, 90), (6665, 900, -90), (6665, -900, -90)]):
                a = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, 345))
                a.set_actor_label('City_BossDress_L%d_LanternString' % i)
                a.static_mesh_component.set_static_mesh(lm)
                for k, mt in enumerate(mats):
                    a.static_mesh_component.set_material(k, mt)
                a.static_mesh_component.set_mobility(unreal.ComponentMobility.STATIC)
                a.set_actor_enable_collision(False)
                a.tags = ['JC_City', 'JC_BossDress']
                a.set_actor_transform(T(x, y, 345, yaw), False, True)
                made.append(a)
        near = min(max(abs(a.get_actor_location().x - 8120.0), abs(a.get_actor_location().y)) for a in made)
        say('placed %d dressing actors; the nearest to the middle of the arena is %.0f cm from it' % (len(made), near))
        say('SAVED ok=%s' % unreal.EditorLoadingAndSavingUtils.save_packages([a.get_outermost() for a in made], False))
open(os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'boss_dress.txt'), 'w').write('\n'.join(out) + '\n')
