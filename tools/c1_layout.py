"""C1: places the grey-box level in Lvl_JumpCut from the tables below. Run in the editor (Play mode stopped):
    py C:/Users/thecl/code/jump-cut/tools/c1_layout.py
It first deletes every actor it placed before (tag 'C1_Layout' only), then places everything again. It never touches
Floor_Base's transform, the sun/sky/fog, PlayerStart_Cafe or Player_Main (the player stays at (0,0,100) INSIDE the cafe:
the cafe is built around the origin). Writes Saved/c1_layout.txt. Does not save the level.

Units are cm, Z up, floor top at Z=0. The route runs along +X:
  cafe x -630..630, y -515..515 (interior 12 x 10 m), door in the east wall (x=615, y -150..150)
  street x 630..6600, y -500..500 (buildings 8 m high either side)
  plaza x 6600..9640, y -1520..1520 (interior 30 x 30 m), entry gate x=6620, exit gate x=9620 (5 m openings, y -250..250)
  exit run x 9640..10630, y -250..250, finish marker Marker_Win at x=10220
"""
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())
TAG = 'C1_Layout'
MAT = '/Game/Game/Materials/'
CUBE = '/Engine/BasicShapes/Cube.Cube'
BP = '/Game/Game/Blueprints/'
WALL, FLOOR, PROPR, PROPB = 'M_GreyWall', 'M_GreyFloor', 'M_PropRed', 'M_PropBlue'
H = 400.0  # wall height

# (label, centre x, y, z, size x, y, z, yaw, material)
BOXES = [
    # cafe
    ('C1_Cafe_WallN', 0, 515, H / 2, 1260, 30, H, 0, WALL),
    ('C1_Cafe_WallS', 0, -515, H / 2, 1260, 30, H, 0, WALL),
    ('C1_Cafe_WallW', -615, 0, H / 2, 30, 1000, H, 0, WALL),
    ('C1_Cafe_WallE_South', 615, -325, H / 2, 30, 350, H, 0, WALL),
    ('C1_Cafe_WallE_North', 615, 325, H / 2, 30, 350, H, 0, WALL),
    ('C1_Cafe_Car', -520, 0, 75, 400, 200, 150, 0, PROPR),
    ('C1_Cafe_CarCab', -470, 0, 185, 180, 170, 70, 0, PROPR),
    ('C1_Cafe_Driver', -380, 220, 90, 50, 50, 180, 0, PROPB),
    ('C1_Cafe_Counter', 200, -380, 55, 500, 80, 110, 0, PROPB),
    # street
    ('C1_Street_BuildingN', 3615, 900, 400, 6000, 800, 800, 0, WALL),
    ('C1_Street_BuildingS', 3615, -900, 400, 6000, 800, 800, 0, WALL),
    # plaza (west wall and east wall leave a 5 m opening for each gate)
    ('C1_Plaza_WallW_North', 6620, 875, H / 2, 40, 1250, H, 0, WALL),
    ('C1_Plaza_WallW_South', 6620, -875, H / 2, 40, 1250, H, 0, WALL),
    ('C1_Plaza_WallN', 8120, 1520, H / 2, 3040, 40, H, 0, WALL),
    ('C1_Plaza_WallS', 8120, -1520, H / 2, 3040, 40, H, 0, WALL),
    ('C1_Plaza_WallE_North', 9620, 875, H / 2, 40, 1250, H, 0, WALL),
    ('C1_Plaza_WallE_South', 9620, -875, H / 2, 40, 1250, H, 0, WALL),
    # run beyond the exit gate
    ('C1_Run_WallN', 10135, 265, H / 2, 990, 30, H, 0, WALL),
    ('C1_Run_WallS', 10135, -265, H / 2, 990, 30, H, 0, WALL),
    ('C1_Run_End', 10630, 0, H / 2, 30, 560, H, 0, WALL),
    # Floor_Base ends at x = 10000: extra slab (top at Z=0) so the run beyond the exit gate has a floor
    ('C1_Floor_RunExtra', 10600, 0, -50, 1200, 3200, 100, 0, FLOOR),
]

# (label, blueprint, x, y, z, yaw, {variable: value})
ACTORS = [
    ('Gate_PlazaEntry', 'BP_PlazaGate', 6620, 0, H / 2, 0, {'GateStartsOpen': True, 'GateClosesBehindPlayer': True}),
    ('Gate_PlazaExit', 'BP_PlazaGate', 9620, 0, H / 2, 0, {'GateStartsOpen': False, 'GateClosesBehindPlayer': False}),
    ('Checkpoint_StreetEnd', 'BP_Checkpoint', 6300, 0, 0, 0, {}),
    ('Spawner_Street', 'BP_GoonSpawner', 4600, 0, 0, 180, {'GoonCount': 3}),
    ('Marker_Crash', 'BP_SceneMarker', -200, -100, 0, 0, {'MarkerId': 'Marker_Crash'}),
    ('Marker_RewindGiven', 'BP_SceneMarker', -300, 330, 0, 0, {'MarkerId': 'Marker_RewindGiven'}),
    ('Marker_FreezeFrameGiven', 'BP_SceneMarker', 8120, 0, 0, 0, {'MarkerId': 'Marker_FreezeFrameGiven'}),
    ('Marker_BossSpot', 'BP_SceneMarker', 8120, 0, 0, 180, {'MarkerId': 'Marker_BossSpot'}),
    ('Marker_Win', 'BP_SceneMarker', 10220, 0, 0, 0, {'MarkerId': 'Marker_Win', 'MarkerEndsGame': True}),
]

log = []
try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = ues.get_editor_world()
    if world.get_name() != 'Lvl_JumpCut' or ues.get_game_world() is not None:
        raise RuntimeError('wrong world (%s) or PIE running' % world.get_name())
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    removed = 0
    for a in list(eas.get_all_level_actors()):
        if unreal.Name(TAG) in a.get_editor_property('tags'):
            eas.destroy_actor(a)
            removed += 1
    log.append('removed %d earlier C1 actors' % removed)

    cube = unreal.load_asset(CUBE)

    def tag(a, label):
        a.set_actor_label(label)
        a.set_editor_property('tags', [unreal.Name(TAG)])

    for label, x, y, z, sx, sy, sz, yaw, mat in BOXES:
        a = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z),
                                       unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
        comp = a.static_mesh_component
        comp.set_mobility(unreal.ComponentMobility.STATIC)
        comp.set_static_mesh(cube)
        comp.set_material(0, unreal.load_asset(MAT + mat))
        a.set_actor_scale3d(unreal.Vector(sx / 100.0, sy / 100.0, sz / 100.0))
        tag(a, label)
    log.append('placed %d boxes' % len(BOXES))

    for label, bpname, x, y, z, yaw, vars_ in ACTORS:
        cls = unreal.load_class(None, '%s%s.%s_C' % (BP, bpname, bpname))
        a = eas.spawn_actor_from_class(cls, unreal.Vector(x, y, z), unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
        tag(a, label)
        for k, v in vars_.items():
            a.set_editor_property(k, v)
        a.set_actor_location_and_rotation(unreal.Vector(x, y, z), unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw), False, True)
        log.append('%s at %s' % (label, a.get_actor_location()))

    # flat grey floor material (Floor_Base itself is not moved)
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == 'Floor_Base':
            a.static_mesh_component.set_material(0, unreal.load_asset(MAT + FLOOR))
            log.append('Floor_Base material set')
except Exception as e:
    log.append('ERROR: %r' % e)
with open(ROOT + 'c1_layout.txt', 'w') as f:
    f.write('\n'.join(log))
