# Packet C1c + D2 graphs, written with the Unreal MCP's write_graph_dsl and kept here as text so they can be rebuilt.
# See docs/FIRST_BUILD_DESIGN.md sections 1.1 (EnemyTakeHit), 5.2 (Freeze Frame) and 7 (BP_PlazaGate).
# `python tools/d2_graphs.py` writes JumpCut/Saved/d2_graphs.json ({"<graph refPath>": "<dsl>"}).
#
# C1c (fixes from D1's check):
#   BP_PlazaGate: new float GatePastDepth (default 120, T) and two new functions, GateIsPastGateway (out Past bool) and
#     GateSendGoonsHome. GateCheckTrigger now closes when the player is in the trigger circle OR more than
#     GatePastDepth cm past the gate line on the plaza side (the side the TriggerSphere sits on, so no rotation is
#     assumed). 120 cm = 20 cm half slab + 42 cm capsule radius + 58 cm spare: the slab never lands on the player.
#     The close branch also sends every BP_Goon home asleep (EnemyResetToStart), so none can punch through the gate.
#     Only gates with GateClosesBehindPlayer (the entry gate) run any of it; Gate_PlazaExit is unaffected.
#   BP_EnemyBase.EnemyTakeHit: one new first step, "if not EnemyIsAwake: EnemyWake" (rest = B1's graph, unchanged).
# D2 (the player's Freeze Frame, BP_Player): FreezeFrameStart, PlayerTickFreezeFrame, PlayerFreezeFrameEnd.
#   Deviations from the note, both to keep enemies from being left wrong:
#   - PlayerTickFreezeFrame re-applies PlayerStopAllEnemies true every tick while the freeze lasts, so goons spawned
#     or respawned mid-freeze (GoonSpawnerRespawn) are stopped within a frame. (EnemySetTimeStopped true is idempotent.)
#   - PlayerFreezeFrameEnd also zeroes FreezeFrameTimeLeft, and only un-stops enemies when neither IsLost nor HasWon,
#     so a freeze ending on the lose screen never restarts the world behind it. (PlayerLose already sets IsLost
#     before it calls PlayerFreezeFrameEnd, then stops everything.)
import json
import os

P = '/Game/Game/Blueprints/BP_Player.BP_Player'
E = '/Game/Game/Blueprints/BP_EnemyBase.BP_EnemyBase'
G = '/Game/Game/Blueprints/BP_PlazaGate.BP_PlazaGate'
GOON_CLASS = '"/Game/Game/Blueprints/BP_Goon.BP_Goon_C"'
V = 'Variables|Default|'

GATE = {}

GATE['GateIsPastGateway'] = f'''
(fn GateIsPastGateway ()
  (bind here (Transformation|GetActorLocation))
  (bind tr (- (Transformation|GetWorldLocation :self ({V}GetTriggerSphere)) here))
  (bind into (Math|Vector|Normalize (Math|Vector|MakeVector :X (.x tr) :Y (.y tr) :Z 0.0)))
  (bind pd (- (Transformation|GetActorLocation :self ({V}GetPlayerRef)) here))
  (bind depth (Math|Vector|DotProduct :A (Math|Vector|MakeVector :X (.x pd) :Y (.y pd) :Z 0.0) :B into))
  (bind past (> depth ({V}GetGatePastDepth)))
  (return past))
'''

GATE['GateSendGoonsHome'] = f'''
(fn GateSendGoonsHome ()
  (bind goons (Actor|GetAllActorsOfClass {GOON_CLASS}))
  (for g goons
    (Class|BPEnemyBase|EnemyResetToStart :self g)))
'''

GATE['GateCheckTrigger'] = f'''
(fn GateCheckTrigger ()
  (if (and (and ({V}GetGateClosesBehindPlayer) ({V}GetGateTriggerArmed)) ({V}GetGateIsOpen))
    (Utilities|IsValid ({V}GetGateEnemyToWake)
      (:"Is Valid"
        (bind inside (CallFunction|GateInTrigger))
        (bind past (CallFunction|GateIsPastGateway))
        (if (or inside past)
          (CallFunction|PlazaGateClose)
          ({V}SetGateTriggerArmed false)
          (Class|BPEnemyBase|EnemyWake :self ({V}GetGateEnemyToWake))
          (Class|BPPlayer|PlayerTrailReset :self ({V}GetPlayerRef))
          (CallFunction|GateSendGoonsHome)))
      (:"Is Not Valid"))))
'''

ENEMY = {}

ENEMY['EnemyTakeHit'] = f'''
(fn EnemyTakeHit (Damage FromLocation KnockStrength KnockUp StunTime)
  (if (not ({V}GetEnemyIsDefeated))
    (if (not ({V}GetEnemyIsAwake))
      (CallFunction|EnemyWake))
    ({V}SetEnemyHealth (Math|Float|Max(Float) 0.0 (- ({V}GetEnemyHealth) Damage)))
    (bind away (- (Transformation|GetActorLocation) FromLocation))
    (bind flat (Math|Vector|Normalize (Math|Vector|MakeVector :X (.x away) :Y (.y away) :Z 0.0)))
    (bind knock (* (+ (* flat KnockStrength) (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z KnockUp)) ({V}GetEnemyKnockTakenScale)))
    (if ({V}GetEnemyTimeStopped)
      ({V}SetEnemyPendingKnock (+ ({V}GetEnemyPendingKnock) knock))
      (else
        (Character|LaunchCharacter :LaunchVelocity knock :bXYOverride true :bZOverride true)))
    (bind stun (* StunTime ({V}GetEnemyStunTakenScale)))
    (if (> stun 0.0)
      ({V}SetEnemyStunLeft (Math|Float|Max(Float) ({V}GetEnemyStunLeft) stun))
      ({V}SetEnemyIsWindingUp false)
      (CallFunction|EnemyShowWarning :Show false))
    (if (<= ({V}GetEnemyHealth) 0.0)
      ({V}SetEnemyIsDefeated true)
      ({V}SetEnemyDefeatLingerLeft ({V}GetEnemyDefeatLinger))
      (CallFunction|EnemyShowWarning :Show false)
      (CallFunction|EnemyDefeatedHook))))
'''

PLAYER = {}

PLAYER['FreezeFrameStart'] = f'''
(fn FreezeFrameStart ()
  (if (not (or (or (not ({V}GetHasFreezeFrame)) ({V}GetFreezeFrameActive)) (> ({V}GetFreezeCooldownLeft) 0.0)))
    (bind can (CallFunction|PlayerCanAct))
    (if can
      ({V}SetFreezeFrameActive true)
      ({V}SetFreezeFrameTimeLeft ({V}GetFreezeFrameDuration))
      (CallFunction|PlayerStopAllEnemies :Stopped true))))
'''

PLAYER['PlayerTickFreezeFrame'] = f'''
(fn PlayerTickFreezeFrame (DeltaSeconds)
  (if ({V}GetFreezeFrameActive)
    ({V}SetFreezeFrameTimeLeft (Math|Float|Max(Float) 0.0 (- ({V}GetFreezeFrameTimeLeft) DeltaSeconds)))
    (if (<= ({V}GetFreezeFrameTimeLeft) 0.0)
      (CallFunction|PlayerFreezeFrameEnd)
      (else
        (CallFunction|PlayerStopAllEnemies :Stopped true)))))
'''

PLAYER['PlayerFreezeFrameEnd'] = f'''
(fn PlayerFreezeFrameEnd ()
  (if ({V}GetFreezeFrameActive)
    ({V}SetFreezeFrameActive false)
    ({V}SetFreezeFrameTimeLeft 0.0)
    ({V}SetFreezeCooldownLeft ({V}GetFreezeFrameCooldown))
    (if (not (or ({V}GetIsLost) ({V}GetHasWon)))
      (CallFunction|PlayerStopAllEnemies :Stopped false))))
'''


def build():
    out = {}
    for base, graphs in ((G, GATE), (E, ENEMY), (P, PLAYER)):
        for name, code in graphs.items():
            out[f'{base}:{name}'] = code.strip()
    return out


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    dst = os.path.join(here, '..', 'JumpCut', 'Saved', 'd2_graphs.json')
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(build(), f, indent=1)
    print('wrote', os.path.normpath(dst), len(build()), 'graphs')
