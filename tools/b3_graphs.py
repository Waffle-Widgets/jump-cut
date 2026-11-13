# Packet B3 graphs (BP_GoonSpawner), written with the Unreal MCP's write_graph_dsl and kept here as text so they can be
# rebuilt. See docs/FIRST_BUILD_DESIGN.md section 3. BP_Goon has no graph at all (only defaults, listed below).
# `python tools/b3_graphs.py` writes JumpCut/Saved/b3_graphs.json ({"<graph refPath>": "<dsl>"}), which an
# execute_tool_script reads (AssetTools.read_file) and writes graph by graph.
#
# BP_Goon (child of BP_EnemyBase), class defaults set with ObjectTools.set_properties:
#   Default__BP_Goon_C: EnemyMaxHealth 40, EnemyHealth 40, EnemyAggroRange 1500 (everything else = the base's)
#   Default__BP_Goon_C:CharacterMesh0: OverrideMaterials [M_Goon, M_Goon] (both mannequin slots: rust orange)
#   Its EventGraph's default BeginPlay / Tick (with Parent: calls) and ActorBeginOverlap nodes were deleted, so the
#   base's BeginPlay and Tick run unchanged.
#
# BP_GoonSpawner (Actor): components SpawnerRoot (Scene, root), SpawnerArrow (Arrow, under the root).
#   GoonCount int 3 (instance editable), GoonSpacing float 150, SpawnedGoons BP_Goon array.
import json
import os

S = '/Game/Game/Blueprints/BP_GoonSpawner.BP_GoonSpawner'
GOON_CLASS = '"/Game/Game/Blueprints/BP_Goon.BP_Goon_C"'

V = 'Variables|Default|'

SPAWNER = {}

SPAWNER['EventGraph'] = '''
(event EventBeginPlay
  (CallFunction|GoonSpawnerSpawnGroup))
'''

# offset of goon i across the arrow = (i - (GoonCount - 1) / 2) x GoonSpacing; the half is a float (0.5) so an even
# count is centred too. The int -> float conversions are explicit: mixing int and float in one (- ...) / (* ...)
# made the graph tool type the whole chain as Integer (0.5 truncated).
SPAWNER['GoonSpawnerSpawnGroup'] = f'''
(fn GoonSpawnerSpawnGroup ()
  (bind here (Transformation|GetActorLocation))
  (bind right (Transformation|GetActorRightVector))
  (bind rot (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw (.yaw (Transformation|GetActorRotation))))
  (bind mid (* (- (Math|Conversions|ToFloat(Integer) ({V}GetGoonCount)) 1.0) 0.5))
  (for i (range ({V}GetGoonCount))
    (bind off (* (- (Math|Conversions|ToFloat(Integer) i) mid) ({V}GetGoonSpacing)))
    (bind at (+ (+ here (* right off)) (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z 100.0)))
    (bind g (Game|SpawnActorfromClass {GOON_CLASS} (Math|Transform|MakeTransform :Location at :Rotation rot) "AlwaysSpawn" "MultiplyWithRoot"))
    (Utilities|Array|Add :TargetArray ({V}GetSpawnedGoons) :NewItem g)))
'''

SPAWNER['GoonSpawnerClear'] = f'''
(fn GoonSpawnerClear ()
  (for g ({V}GetSpawnedGoons)
    (Utilities|IsValid g
      (:"Is Valid"
        (Actor|DestroyActor :self g))
      (:"Is Not Valid")))
  (Utilities|Array|Clear :TargetArray ({V}GetSpawnedGoons)))
'''

SPAWNER['GoonSpawnerRespawn'] = '''
(fn GoonSpawnerRespawn ()
  (CallFunction|GoonSpawnerClear)
  (CallFunction|GoonSpawnerSpawnGroup))
'''


def build():
    return {f'{S}:{name}': code.strip() for name, code in SPAWNER.items()}


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    dst = os.path.join(here, '..', 'JumpCut', 'Saved', 'b3_graphs.json')
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(build(), f, indent=1)
    print('wrote', os.path.normpath(dst), len(build()), 'graphs')
