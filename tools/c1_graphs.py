# Packet C1 graphs (BP_PlazaGate, BP_Checkpoint, BP_SceneMarker), written with the Unreal MCP's write_graph_dsl and kept
# here as text so they can be rebuilt. See docs/FIRST_BUILD_DESIGN.md section 7.
# `python tools/c1_graphs.py` writes JumpCut/Saved/c1_graphs.json ({"<graph refPath>": "<dsl>"}).
#
# Components (all added with ActorTools.add_component, scene roots promoted with set_parent_component):
#   BP_PlazaGate:    GateRoot (root), GateMesh (cube, scale 0.4 x 5 x 4 = a 5 m wide, 4 m high slab, BlockAll),
#                    TriggerSphere (radius 300, NoCollision). Place the actor at Z = 200 (half the slab height):
#                    GateMesh relative Z = 0 is "closed", GateOpenHeight is "open".
#   BP_Checkpoint:   CheckpointRoot, PostMesh, TakenSign (hidden), RespawnPoint (Scene), TriggerSphere (250)
#   BP_SceneMarker:  MarkerRoot, MarkerArrow, TriggerSphere (250)
import json
import os

B = '/Game/Game/Blueprints/'
V = 'Variables|Default|'
G = {}


def find_player(prefix):
    return f'''
(fn {prefix}FindPlayer ()
  (bind pl (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter :PlayerIndex 0))
    (:then
      ({V}SetPlayerRef pl))
    (:CastFailed)))
'''


def in_trigger(name):
    return f'''
(fn {name} ()
  (bind c (Transformation|GetWorldLocation :self ({V}GetTriggerSphere)))
  (bind d (- c (Transformation|GetActorLocation :self ({V}GetPlayerRef))))
  (bind dist (Math|Vector|VectorLengthXY d))
  (bind r (Components|Sphere|GetScaledSphereRadius :self ({V}GetTriggerSphere)))
  (bind inside (< dist r))
  (return inside))
'''


def tick(first_call, find, other):
    return f'''
(event EventTick (DeltaSeconds)
  {first_call}
  (Utilities|IsValid ({V}GetPlayerRef)
    (:"Is Valid"
      {other})
    (:"Is Not Valid"
      (CallFunction|{find}))))
'''


# ---------------- BP_PlazaGate
GATE = 'BP_PlazaGate.BP_PlazaGate:'
G[GATE + 'EventGraph'] = '''
(event EventBeginPlay
  (CallFunction|GateSetup))
''' + tick('(CallFunction|GateTickStep :DeltaSeconds DeltaSeconds)', 'GateFindPlayer', '(CallFunction|GateCheckTrigger)')
G[GATE + 'GateFindPlayer'] = find_player('Gate')
G[GATE + 'GateInTrigger'] = in_trigger('GateInTrigger')
G[GATE + 'PlazaGateOpen'] = f'''
(fn PlazaGateOpen ()
  ({V}SetGateIsOpen true))
'''
G[GATE + 'PlazaGateClose'] = f'''
(fn PlazaGateClose ()
  (if (not ({V}GetGateLockedOpen))
    ({V}SetGateIsOpen false)))
'''
G[GATE + 'PlazaGateOpenForGood'] = f'''
(fn PlazaGateOpenForGood ()
  ({V}SetGateLockedOpen true)
  ({V}SetGateIsOpen true))
'''
G[GATE + 'PlazaGateResetToStart'] = f'''
(fn PlazaGateResetToStart ()
  (if (not ({V}GetGateLockedOpen))
    ({V}SetGateTriggerArmed true)
    ({V}SetGateIsOpen ({V}GetGateStartsOpen))))
'''
G[GATE + 'GateSetup'] = f'''
(fn GateSetup ()
  ({V}SetGateIsOpen ({V}GetGateStartsOpen))
  (bind rel (Class|SceneComponent|GetRelativeLocation :self ({V}GetGateMesh)))
  (bind z (select ({V}GetGateStartsOpen) ({V}GetGateOpenHeight) 0.0))
  (Transformation|SetRelativeLocation :self ({V}GetGateMesh) :NewLocation (Math|Vector|MakeVector :X (.x rel) :Y (.y rel) :Z z)))
'''
G[GATE + 'GateTickStep'] = f'''
(fn GateTickStep (DeltaSeconds)
  (bind rel (Class|SceneComponent|GetRelativeLocation :self ({V}GetGateMesh)))
  (bind target (select ({V}GetGateIsOpen) ({V}GetGateOpenHeight) 0.0))
  (bind nz (Math|Interpolation|FInterptoConstant :Current (.z rel) :Target target :DeltaTime DeltaSeconds :InterpSpeed ({V}GetGateMoveSpeed)))
  (Transformation|SetRelativeLocation :self ({V}GetGateMesh) :NewLocation (Math|Vector|MakeVector :X (.x rel) :Y (.y rel) :Z nz)))
'''
G[GATE + 'GateCheckTrigger'] = f'''
(fn GateCheckTrigger ()
  (if (and (and ({V}GetGateClosesBehindPlayer) ({V}GetGateTriggerArmed)) ({V}GetGateIsOpen))
    (Utilities|IsValid ({V}GetGateEnemyToWake)
      (:"Is Valid"
        (bind inside (CallFunction|GateInTrigger))
        (if inside
          (CallFunction|PlazaGateClose)
          ({V}SetGateTriggerArmed false)
          (Class|BPEnemyBase|EnemyWake :self ({V}GetGateEnemyToWake))))
      (:"Is Not Valid"))))
'''

# ---------------- BP_Checkpoint
CP = 'BP_Checkpoint.BP_Checkpoint:'
G[CP + 'EventGraph'] = tick('', 'CheckpointFindPlayer', '(CallFunction|CheckpointTickStep)')
G[CP + 'CheckpointFindPlayer'] = find_player('Checkpoint')
G[CP + 'CheckpointInTrigger'] = in_trigger('CheckpointInTrigger')
G[CP + 'CheckpointTickStep'] = f'''
(fn CheckpointTickStep ()
  (if (not ({V}GetCheckpointTaken))
    (bind inside (CallFunction|CheckpointInTrigger))
    (if inside
      (bind rp ({V}GetRespawnPoint))
      (Class|BPPlayer|PlayerStoreCheckpoint :self ({V}GetPlayerRef) :Location (Transformation|GetWorldLocation :self rp) :Yaw (.yaw (Transformation|GetWorldRotation :self rp)))
      ({V}SetCheckpointTaken true)
      (Rendering|SetVisibility :self ({V}GetTakenSign) :bNewVisibility true))))
'''

# ---------------- BP_SceneMarker
MK = 'BP_SceneMarker.BP_SceneMarker:'
G[MK + 'EventGraph'] = tick('', 'MarkerFindPlayer', '(CallFunction|MarkerTickStep)')
G[MK + 'MarkerFindPlayer'] = find_player('Marker')
G[MK + 'MarkerInTrigger'] = in_trigger('MarkerInTrigger')
G[MK + 'MarkerTickStep'] = f'''
(fn MarkerTickStep ()
  (if ({V}GetMarkerEndsGame)
    (bind inside (CallFunction|MarkerInTrigger))
    (if inside
      (Class|BPPlayer|PlayerReachWin :self ({V}GetPlayerRef)))))
'''


def build():
    return {B + k: v.strip() for k, v in G.items()}


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    dst = os.path.join(here, '..', 'JumpCut', 'Saved', 'c1_graphs.json')
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(build(), f, indent=1)
    print('wrote', os.path.normpath(dst), len(build()), 'graphs')
