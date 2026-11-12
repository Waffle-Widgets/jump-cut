# Packet D1 graphs (BP_BossFreeze and the boss-freeze functions on BP_Player), written with the Unreal MCP's
# write_graph_dsl and kept here as text so they can be rebuilt. See docs/FIRST_BUILD_DESIGN.md section 5.1.
# `python tools/d1_graphs.py` writes JumpCut/Saved/d1_graphs.json ({"<graph refPath>": "<dsl>"}).
#
# BP_BossFreeze (child of BP_EnemyBase). Its EventGraph's default BeginPlay / Tick (Parent: calls) and
# ActorBeginOverlap nodes were deleted; the three hooks were added with add_event and are written below.
#   Class defaults (Default__BP_BossFreeze_C): EnemyMaxHealth 240, EnemyHealth 240, EnemyMoveSpeed 380, EnemyDamage 15,
#   EnemyWindup 0.7, EnemyAttackCooldown 1.6, EnemyKnockTakenScale 0.25, EnemyStunTakenScale 0, EnemyAggroRange 0,
#   BossFreezeRadius 1200, BossFreezeWindup 1.2, BossFreezeDuration 3, BossFreezeCooldown 9, BossFirstFreezeDelay 4,
#   BossFreeHitDamage 12, BossFreeHitInterval 0.8, BossBrokenStun 1.5. BossExitGate (BP_PlazaGate ref) instance editable.
#   :CollisionCylinder  half height 115, radius 45 (the 1.3x mannequin fits inside)
#   :CharacterMesh0     scale 1.3, relative Z -116, both slots M_Boss (flat violet)
#   FreezeRing (added StaticMeshComponent under the capsule): engine Cylinder, M_WarnFreeze (unlit cyan),
#     NoCollision, no shadow, hidden, relative Z -113.5 (0.5..2.5 cm above the floor), scale 24 x 24 x 0.02
#     (radius 1200 cm; re-set from BossFreezeRadius on his first think).
#   Placed: Boss_Freeze at (8120, 0, 117) yaw 180 (capsule centre 115 + 2 above the floor), BossExitGate = Gate_PlazaExit;
#   Gate_PlazaEntry.GateEnemyToWake = Boss_Freeze (JumpCut/Saved/d1_editor.py place).
# C1b (level, JumpCut/Saved/d1_editor.py c1b): Checkpoint_StreetEnd's TriggerSphere radius 550 on the placed instance
#   (class default stays 250); Floor_Base's M_GreyFloor re-set and saved into its actor file.
#   The inherited WarnSign is moved to 165 cm above the capsule centre and scaled 0.55 on his first think (he is taller).
import json
import os

BOSS = '/Game/Game/Blueprints/BP_BossFreeze.BP_BossFreeze'
P = '/Game/Game/Blueprints/BP_Player.BP_Player'
V = 'Variables|Default|'
PL = f'({V}GetPlayerRef)'

B = {}

B['EventGraph'] = f'''
(event EventEnemyThink (DeltaSeconds)
  (if (not ({V}GetBossRingSized))
    (bind r (/ ({V}GetBossFreezeRadius) 50.0))
    (Transformation|SetRelativeScale3D :self ({V}GetFreezeRing) :NewScale3D (Math|Vector|MakeVector :X r :Y r :Z 0.02))
    (Transformation|SetRelativeLocation :self ({V}GetWarnSign) :NewLocation (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z 165.0))
    (Transformation|SetRelativeScale3D :self ({V}GetWarnSign) :NewScale3D (Math|Vector|MakeVector :X 0.55 :Y 0.55 :Z 0.55))
    ({V}SetBossFreezeCooldownLeft ({V}GetBossFirstFreezeDelay))
    ({V}SetBossRingSized true))
  (if (== ({V}GetBossState) 0)
    (CallFunction|BossThinkFight :DeltaSeconds DeltaSeconds)
    (else
      (if (== ({V}GetBossState) 1)
        (CallFunction|BossThinkFreezeWindup :DeltaSeconds DeltaSeconds)
        (else
          (CallFunction|BossThinkFreeHits :DeltaSeconds DeltaSeconds))))))
(event EventEnemyDefeatedHook
  (Rendering|SetVisibility :self ({V}GetFreezeRing) :bNewVisibility false)
  (Utilities|IsValid ({V}GetBossExitGate)
    (:"Is Valid"
      (Class|BPPlazaGate|PlazaGateOpenForGood :self ({V}GetBossExitGate))
      (CallFunction|BossHandOverPower))
    (:"Is Not Valid"
      (CallFunction|BossHandOverPower))))
(event EventEnemyResetHook
  ({V}SetBossState 0)
  (Rendering|SetVisibility :self ({V}GetFreezeRing) :bNewVisibility false)
  ({V}SetBossFreezeCooldownLeft ({V}GetBossFirstFreezeDelay))
  ({V}SetBossFreezeWindupLeft 0.0)
  ({V}SetBossHoldLeft 0.0)
  ({V}SetBossFreeHitLeft 0.0))
'''

# The IsValid macro ends the exec flow, so the defeat hook's player part is its own function, called from both branches.
B['BossHandOverPower'] = f'''
(fn BossHandOverPower ()
  (Utilities|IsValid {PL}
    (:"Is Valid"
      (Class|BPPlayer|PlayerFreezeBreak :self {PL})
      (Class|BPPlayer|PlayerGrantFreezeFrame :self {PL}))
    (:"Is Not Valid")))
'''

B['BossStartFreezeWindup'] = f'''
(fn BossStartFreezeWindup ()
  ({V}SetBossState 1)
  ({V}SetBossFreezeWindupLeft ({V}GetBossFreezeWindup))
  (Rendering|SetVisibility :self ({V}GetFreezeRing) :bNewVisibility true)
  ({V}SetEnemyIsWindingUp false)
  (CallFunction|EnemyShowWarning :Show false))
'''

B['BossThinkFight'] = f'''
(fn BossThinkFight (DeltaSeconds)
  ({V}SetBossFreezeCooldownLeft (- ({V}GetBossFreezeCooldownLeft) DeltaSeconds))
  (bind d (CallFunction|EnemyDistToPlayer))
  (if (and (and (<= ({V}GetBossFreezeCooldownLeft) 0.0) (not ({V}GetEnemyIsWindingUp))) (<= d ({V}GetBossFreezeRadius)))
    (CallFunction|BossStartFreezeWindup)
    (else
      (CallFunction|EnemyChasePunchStep :DeltaSeconds DeltaSeconds))))
'''

# Deviation from the note: after PlayerFreezeApply he goes to state 2 only if the player really is frozen (the apply
# returns early while rewinding or in the 0.5 s after a rewind). Otherwise state 2 would read "freeze broken early" on
# its first tick and daze him for BossBrokenStun although nothing broke it.
B['BossThinkFreezeWindup'] = f'''
(fn BossThinkFreezeWindup (DeltaSeconds)
  (CallFunction|EnemyFacePlayer)
  ({V}SetBossFreezeWindupLeft (- ({V}GetBossFreezeWindupLeft) DeltaSeconds))
  (if (<= ({V}GetBossFreezeWindupLeft) 0.0)
    (Rendering|SetVisibility :self ({V}GetFreezeRing) :bNewVisibility false)
    ({V}SetBossFreezeCooldownLeft ({V}GetBossFreezeCooldown))
    (bind d (CallFunction|EnemyDistToPlayer))
    (if (<= d ({V}GetBossFreezeRadius))
      (Class|BPPlayer|PlayerFreezeApply :self {PL} :Duration ({V}GetBossFreezeDuration))
      (if (Class|BPPlayer|GetIsFrozenbyBoss :self {PL})
        ({V}SetBossHoldLeft ({V}GetBossFreezeDuration))
        ({V}SetBossFreeHitLeft 0.3)
        ({V}SetBossState 2)
        (else
          ({V}SetBossState 0)))
      (else
        ({V}SetBossState 0)))))
'''

B['BossThinkFreeHits'] = f'''
(fn BossThinkFreeHits (DeltaSeconds)
  ({V}SetBossHoldLeft (- ({V}GetBossHoldLeft) DeltaSeconds))
  (if (not (Class|BPPlayer|GetIsFrozenbyBoss :self {PL}))
    (if (> ({V}GetBossHoldLeft) 0.1)
      ({V}SetEnemyStunLeft ({V}GetBossBrokenStun)))
    ({V}SetBossState 0)
    (else
      (bind d (CallFunction|EnemyDistToPlayer))
      (if (> d ({V}GetEnemyAttackRange))
        (CallFunction|EnemyWalkToPlayer)
        (else
          ({V}SetBossFreeHitLeft (- ({V}GetBossFreeHitLeft) DeltaSeconds))
          (if (<= ({V}GetBossFreeHitLeft) 0.0)
            (CallFunction|EnemyPunchPlayer :Damage ({V}GetBossFreeHitDamage))
            ({V}SetBossFreeHitLeft ({V}GetBossFreeHitInterval))))))))
'''

PLAYER = {}

PLAYER['PlayerFreezeApply'] = f'''
(fn PlayerFreezeApply (Duration)
  (if (not (or (or ({V}GetIsRewinding) ({V}GetIsLost)) (or ({V}GetHasWon) (> ({V}GetHitSafeLeft) 0.0))))
    ({V}SetIsFrozenByBoss true)
    ({V}SetFrozenTimeLeft Duration)))
'''

PLAYER['PlayerFreezeBreak'] = f'''
(fn PlayerFreezeBreak ()
  ({V}SetIsFrozenByBoss false)
  ({V}SetFrozenTimeLeft 0.0))
'''

PLAYER['PlayerTickBossFreeze'] = f'''
(fn PlayerTickBossFreeze (DeltaSeconds)
  (if ({V}GetIsFrozenByBoss)
    ({V}SetFrozenTimeLeft (- ({V}GetFrozenTimeLeft) DeltaSeconds))
    (if (<= ({V}GetFrozenTimeLeft) 0.0)
      (CallFunction|PlayerFreezeBreak))))
'''

PLAYER['PlayerGrantFreezeFrame'] = f'''
(fn PlayerGrantFreezeFrame ()
  ({V}SetHasFreezeFrame true))
'''

# C1b fix 3 (BP_PlazaGate): the close-behind trigger also resets the player's Rewind trail, so a Rewind inside the
# plaza can't slide back out through the shut entry gate. (Full graph; the rest is C1's, unchanged.)
GATE = {}
GATE['GateCheckTrigger'] = f'''
(fn GateCheckTrigger ()
  (if (and (and ({V}GetGateClosesBehindPlayer) ({V}GetGateTriggerArmed)) ({V}GetGateIsOpen))
    (Utilities|IsValid ({V}GetGateEnemyToWake)
      (:"Is Valid"
        (bind inside (CallFunction|GateInTrigger))
        (if inside
          (CallFunction|PlazaGateClose)
          ({V}SetGateTriggerArmed false)
          (Class|BPEnemyBase|EnemyWake :self ({V}GetGateEnemyToWake))
          (Class|BPPlayer|PlayerTrailReset :self ({V}GetPlayerRef))))
      (:"Is Not Valid"))))
'''


def build():
    out = {}
    for base, graphs in ((BOSS, B), (P, PLAYER), ('/Game/Game/Blueprints/BP_PlazaGate.BP_PlazaGate', GATE)):
        for name, code in graphs.items():
            out[f'{base}:{name}'] = code.strip()
    return out


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    dst = os.path.join(here, '..', 'JumpCut', 'Saved', 'd1_graphs.json')
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(build(), f, indent=1)
    print('wrote', os.path.normpath(dst), len(build()), 'graphs')
