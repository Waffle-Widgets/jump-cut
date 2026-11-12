# Packet B1 graphs (BP_EnemyBase, BP_Player), written with the Unreal MCP's write_graph_dsl and kept here as text
# so they can be rebuilt. See docs/FIRST_BUILD_DESIGN.md section 1. `python tools/b1_graphs.py` writes
# JumpCut/Saved/b1_graphs.json ({"<graph refPath>": "<dsl>"}), which an execute_tool_script reads and writes.
import json
import os

E = '/Game/Game/Blueprints/BP_EnemyBase.BP_EnemyBase'
P = '/Game/Game/Blueprints/BP_Player.BP_Player'
ENEMY_CLASS = '"/Game/Game/Blueprints/BP_EnemyBase.BP_EnemyBase_C"'

V = 'Variables|Default|'

ENEMY = {}

ENEMY['EventGraph'] = f'''
(event EventBeginPlay
  (CallFunction|EnemySetup))
(event EventTick (DeltaSeconds)
  (if (not ({V}GetEnemyTimeStopped))
    (if ({V}GetEnemyIsDefeated)
      ({V}SetEnemyDefeatLingerLeft (- ({V}GetEnemyDefeatLingerLeft) DeltaSeconds))
      (if (<= ({V}GetEnemyDefeatLingerLeft) 0.0)
        (Actor|DestroyActor))
      (else
        (Utilities|IsValid ({V}GetPlayerRef)
          (:"Is Valid"
            (if (> ({V}GetEnemyStunLeft) 0.0)
              ({V}SetEnemyStunLeft (- ({V}GetEnemyStunLeft) DeltaSeconds))
              (else
                (if (> ({V}GetEnemyAttackCooldownLeft) 0.0)
                  ({V}SetEnemyAttackCooldownLeft (- ({V}GetEnemyAttackCooldownLeft) DeltaSeconds)))
                (if ({V}GetEnemyIsAwake)
                  (CallFunction|EnemyThink :DeltaSeconds DeltaSeconds)
                  (else
                    (if (> ({V}GetEnemyAggroRange) 0.0)
                      (bind d (CallFunction|EnemyDistToPlayer))
                      (if (< d ({V}GetEnemyAggroRange))
                        (CallFunction|EnemyWake))))))))
          (:"Is Not Valid"
            (CallFunction|EnemyFindPlayer)))))))
'''

ENEMY['EnemySetup'] = f'''
(fn EnemySetup ()
  ({V}SetEnemyHealth ({V}GetEnemyMaxHealth))
  (Class|CharacterMovementComponent|SetMaxWalkSpeed :self (Variables|Character|GetCharacterMovement) :MaxWalkSpeed ({V}GetEnemyMoveSpeed))
  ({V}SetEnemyHomeLocation (Transformation|GetActorLocation))
  ({V}SetEnemyHomeYaw (.yaw (Transformation|GetActorRotation)))
  ({V}SetEnemyIsAwake ({V}GetEnemyStartsAwake))
  (CallFunction|EnemyShowWarning :Show false))
'''

ENEMY['EnemyFindPlayer'] = f'''
(fn EnemyFindPlayer ()
  (bind pl (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter :PlayerIndex 0))
    (:then
      ({V}SetPlayerRef pl))
    (:CastFailed)))
'''

ENEMY['EnemyDistToPlayer'] = f'''
(fn EnemyDistToPlayer ()
  (bind d (- (Transformation|GetActorLocation :self ({V}GetPlayerRef)) (Transformation|GetActorLocation)))
  (return (Math|Vector|VectorLengthXY d)))
'''

ENEMY['EnemyFacePlayer'] = f'''
(fn EnemyFacePlayer ()
  (bind d (- (Transformation|GetActorLocation :self ({V}GetPlayerRef)) (Transformation|GetActorLocation)))
  (Transformation|SetActorRotation :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw (Math|Trig|Atan2(Degrees) (.y d) (.x d))) :bTeleportPhysics false))
'''

ENEMY['EnemyWalkToPlayer'] = f'''
(fn EnemyWalkToPlayer ()
  (CallFunction|EnemyFacePlayer)
  (bind d (- (Transformation|GetActorLocation :self ({V}GetPlayerRef)) (Transformation|GetActorLocation)))
  (Pawn|Input|AddMovementInput :WorldDirection (Math|Vector|Normalize (Math|Vector|MakeVector :X (.x d) :Y (.y d) :Z 0.0)) :ScaleValue 1.0))
'''

ENEMY['EnemyShowWarning'] = f'''
(fn EnemyShowWarning (Show)
  (Rendering|SetVisibility :self ({V}GetWarnSign) :bNewVisibility Show))
'''

ENEMY['EnemyPunchPlayer'] = f'''
(fn EnemyPunchPlayer (Damage)
  (bind d (CallFunction|EnemyDistToPlayer))
  (if (<= d ({V}GetEnemyHitReach))
    (Class|BPPlayer|PlayerTakeHit :self ({V}GetPlayerRef) :Damage Damage)
    (Class|BPPlayer|PlayerKnockFrom :self ({V}GetPlayerRef) :FromLocation (Transformation|GetActorLocation) :Strength ({V}GetEnemyKnockOnPlayer))))
'''

ENEMY['EnemyChasePunchStep'] = f'''
(fn EnemyChasePunchStep (DeltaSeconds)
  (if ({V}GetEnemyIsWindingUp)
    (CallFunction|EnemyFacePlayer)
    ({V}SetEnemyWindupLeft (- ({V}GetEnemyWindupLeft) DeltaSeconds))
    (if (<= ({V}GetEnemyWindupLeft) 0.0)
      ({V}SetEnemyIsWindingUp false)
      (CallFunction|EnemyShowWarning :Show false)
      (CallFunction|EnemyPunchPlayer :Damage ({V}GetEnemyDamage))
      ({V}SetEnemyAttackCooldownLeft ({V}GetEnemyAttackCooldown)))
    (else
      (bind d (CallFunction|EnemyDistToPlayer))
      (if (> d ({V}GetEnemyAttackRange))
        (CallFunction|EnemyWalkToPlayer)
        (else
          (CallFunction|EnemyFacePlayer)
          (if (<= ({V}GetEnemyAttackCooldownLeft) 0.0)
            ({V}SetEnemyIsWindingUp true)
            ({V}SetEnemyWindupLeft ({V}GetEnemyWindup))
            (CallFunction|EnemyShowWarning :Show true)))))))
'''

ENEMY['EnemyThink'] = '''
(fn EnemyThink (DeltaSeconds)
  (CallFunction|EnemyChasePunchStep :DeltaSeconds DeltaSeconds))
'''

ENEMY['EnemyWake'] = f'''
(fn EnemyWake ()
  ({V}SetEnemyIsAwake true))
'''

ENEMY['EnemyTakeHit'] = f'''
(fn EnemyTakeHit (Damage FromLocation KnockStrength KnockUp StunTime)
  (if (not ({V}GetEnemyIsDefeated))
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

ENEMY['EnemySetTimeStopped'] = f'''
(fn EnemySetTimeStopped (Stopped)
  ({V}SetEnemyTimeStopped Stopped)
  (Variables|Actor|SetCustomTimeDilation :CustomTimeDilation (select Stopped 0.0 1.0))
  (if (not Stopped)
    (if (> (Math|Vector|VectorLength ({V}GetEnemyPendingKnock)) 0.0)
      (Character|LaunchCharacter :LaunchVelocity ({V}GetEnemyPendingKnock) :bXYOverride true :bZOverride true)
      ({V}SetEnemyPendingKnock (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z 0.0)))))
'''

ENEMY['EnemyResetToStart'] = f'''
(fn EnemyResetToStart ()
  (if (not ({V}GetEnemyIsDefeated))
    (Transformation|SetActorLocationAndRotation :NewLocation ({V}GetEnemyHomeLocation) :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw ({V}GetEnemyHomeYaw)) :bSweep false :bTeleport true)
    (Components|Movement|StopMovementImmediately :self (Variables|Character|GetCharacterMovement))
    ({V}SetEnemyHealth ({V}GetEnemyMaxHealth))
    ({V}SetEnemyIsAwake ({V}GetEnemyStartsAwake))
    ({V}SetEnemyWindupLeft 0.0)
    ({V}SetEnemyAttackCooldownLeft 0.0)
    ({V}SetEnemyStunLeft 0.0)
    ({V}SetEnemyDefeatLingerLeft 0.0)
    ({V}SetEnemyIsWindingUp false)
    ({V}SetEnemyPendingKnock (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z 0.0))
    (CallFunction|EnemyShowWarning :Show false)
    (CallFunction|EnemyResetHook)))
'''

ENEMY['EnemyGetHealthNow'] = f'''
(fn EnemyGetHealthNow ()
  (return ({V}GetEnemyHealth)))
'''

# ---------------------------------------------------------------- BP_Player

PLAYER = {}

PLAYER['EventGraph'] = f'''
(event EventTick (DeltaSeconds)
  (if (not ({V}GetPlayerSetupDone))
    (CallFunction|PlayerSetup))
  (CallFunction|PlayerTickTimers :DeltaSeconds DeltaSeconds)
  (CallFunction|PlayerTickInput)
  (CallFunction|PlayerTickTrail :DeltaSeconds DeltaSeconds)
  (CallFunction|PlayerTickRewindSlide :DeltaSeconds DeltaSeconds)
  (CallFunction|PlayerTickBossFreeze :DeltaSeconds DeltaSeconds)
  (CallFunction|PlayerTickFreezeFrame :DeltaSeconds DeltaSeconds)
  (CallFunction|PlayerTickDowned :DeltaSeconds DeltaSeconds)
  (CallFunction|PlayerTickFall)
  (CallFunction|PlayerRefreshMoveLock))
'''

PLAYER['PlayerSetup'] = f'''
(fn PlayerSetup ()
  ({V}SetHealth ({V}GetMaxHealth))
  ({V}SetCheckpointLocation (Transformation|GetActorLocation))
  ({V}SetCheckpointYaw (.yaw (Transformation|GetActorRotation)))
  ({V}SetPlayerSetupDone true)
  (CallFunction|PlayerTrailReset))
'''

_timers = ['ComboTimeLeft', 'PunchIntervalLeft', 'HitFlashLeft', 'HitSafeLeft', 'RewindCooldownLeft', 'FreezeCooldownLeft']
PLAYER['PlayerTickTimers'] = '(fn PlayerTickTimers (DeltaSeconds)\n' + '\n'.join(
    f'  (if (> ({V}Get{t}) 0.0)\n    ({V}Set{t} (Math|Float|Max(Float) 0.0 (- ({V}Get{t}) DeltaSeconds))))' for t in _timers) + ')\n'


def _key(name, a, b):
    return (f'  ({V}Set{name}DownNow (or (Game|Player|IsInputKeyDown :self pc :Key "{a}") '
            f'(Game|Player|IsInputKeyDown :self pc :Key "{b}")))')


PLAYER['PlayerTickInput'] = f'''
(fn PlayerTickInput ()
  (bind pc (Game|GetPlayerController :PlayerIndex 0))
{_key('Attack', 'LeftMouseButton', 'Gamepad_FaceButton_Left')}
{_key('Rewind', 'Q', 'Gamepad_LeftShoulder')}
{_key('Freeze', 'E', 'Gamepad_RightShoulder')}
  (if (and (and ({V}GetAttackDownNow) (not ({V}GetAttackWasDown))) (<= ({V}GetPunchIntervalLeft) 0.0))
    ({V}SetPunchIntervalLeft ({V}GetPunchInterval))
    (CallFunction|PlayerPunch))
  (if (and ({V}GetRewindDownNow) (not ({V}GetRewindWasDown)))
    (CallFunction|RewindStart))
  (if (and ({V}GetFreezeDownNow) (not ({V}GetFreezeWasDown)))
    (CallFunction|FreezeFrameStart))
  ({V}SetAttackWasDown ({V}GetAttackDownNow))
  ({V}SetRewindWasDown ({V}GetRewindDownNow))
  ({V}SetFreezeWasDown ({V}GetFreezeDownNow)))
'''

PLAYER['PlayerCanAct'] = f'''
(fn PlayerCanAct ()
  (return (not (or (or (or ({V}GetIsRewinding) ({V}GetIsFrozenByBoss)) (or ({V}GetIsDowned) ({V}GetIsLost))) (or ({V}GetHasWon) ({V}GetInputLocked))))))
'''

# ComboStep is written once, at the end, from its old value: `step` is a pure chain on ComboStep, so it must not be
# read after ComboStep is set.
PLAYER['PlayerPunch'] = f'''
(fn PlayerPunch ()
  (bind can (CallFunction|PlayerCanAct))
  (if can
    (if (<= ({V}GetComboTimeLeft) 0.0)
      ({V}SetComboStep 0))
    (bind step (+ ({V}GetComboStep) 1))
    (bind fin (>= step 3))
    (bind dmg (select fin ({V}GetPunchDamageFinisher) ({V}GetPunchDamage)))
    (bind kb (select fin ({V}GetKnockbackFinisher) ({V}GetKnockbackLight)))
    (bind ku (select fin ({V}GetKnockUpFinisher) 0.0))
    (bind st (select fin ({V}GetHitStunFinisher) ({V}GetHitStunLight)))
    (bind here (Transformation|GetActorLocation))
    (bind fwd (Transformation|GetActorForwardVector))
    (bind foes (Actor|GetAllActorsOfClass {ENEMY_CLASS}))
    (for foe foes
      (bind to (- (Transformation|GetActorLocation :self foe) here))
      (bind dir (Math|Vector|Normalize (Math|Vector|MakeVector :X (.x to) :Y (.y to) :Z 0.0)))
      (if (and (<= (Math|Vector|VectorLengthXY to) ({V}GetPunchRange)) (>= (Math|Vector|DotProduct :A fwd :B dir) ({V}GetPunchArcDot)))
        (Class|BPEnemyBase|EnemyTakeHit :self foe :Damage dmg :FromLocation here :KnockStrength kb :KnockUp ku :StunTime st)))
    ({V}SetComboStep (select fin 0 step))
    ({V}SetComboTimeLeft ({V}GetComboWindow))))
'''

PLAYER['PlayerTakeHit'] = f'''
(fn PlayerTakeHit (Damage)
  (if (not (or (or ({V}GetIsRewinding) ({V}GetIsDowned)) (or (or ({V}GetIsLost) ({V}GetHasWon)) (> ({V}GetHitSafeLeft) 0.0))))
    ({V}SetHealth (Math|Float|Max(Float) 0.0 (- ({V}GetHealth) Damage)))
    ({V}SetHitFlashLeft ({V}GetHitFlashTime))
    (if (<= ({V}GetHealth) 0.0)
      (CallFunction|PlayerHealthHitZero))))
'''

PLAYER['PlayerKnockFrom'] = f'''
(fn PlayerKnockFrom (FromLocation Strength)
  (bind can (CallFunction|PlayerCanAct))
  (if can
    (bind away (- (Transformation|GetActorLocation) FromLocation))
    (bind flat (Math|Vector|Normalize (Math|Vector|MakeVector :X (.x away) :Y (.y away) :Z 0.0)))
    (Character|LaunchCharacter :LaunchVelocity (+ (* flat Strength) (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z 100.0)) :bXYOverride true :bZOverride true)))
'''

PLAYER['PlayerHealthHitZero'] = f'''
(fn PlayerHealthHitZero ()
  (if (and ({V}GetHasRewind) (<= ({V}GetRewindCooldownLeft) 0.0))
    ({V}SetIsDowned true)
    ({V}SetDownedTimeLeft ({V}GetDownedGraceTime))
    (else
      (CallFunction|PlayerLose))))
'''

PLAYER['PlayerTickDowned'] = f'''
(fn PlayerTickDowned (DeltaSeconds)
  (if ({V}GetIsDowned)
    ({V}SetDownedTimeLeft (- ({V}GetDownedTimeLeft) DeltaSeconds))
    (if (<= ({V}GetDownedTimeLeft) 0.0)
      ({V}SetIsDowned false)
      (CallFunction|PlayerLose))))
'''

PLAYER['PlayerTickFall'] = f'''
(fn PlayerTickFall ()
  (if (and (< (.z (Transformation|GetActorLocation)) ({V}GetFallLoseZ)) (not (or (or ({V}GetIsDowned) ({V}GetIsLost)) (or ({V}GetIsRewinding) ({V}GetHasWon)))))
    ({V}SetHealth 0.0)
    (CallFunction|PlayerHealthHitZero)))
'''

PLAYER['PlayerLose'] = f'''
(fn PlayerLose ()
  ({V}SetIsLost true)
  (CallFunction|PlayerFreezeFrameEnd)
  (CallFunction|PlayerStopAllEnemies :Stopped true))
'''

PLAYER['PlayerRefreshMoveLock'] = f'''
(fn PlayerRefreshMoveLock ()
  (bind want (or (or (or ({V}GetIsRewinding) ({V}GetIsFrozenByBoss)) (or ({V}GetIsDowned) ({V}GetIsLost))) (or ({V}GetHasWon) ({V}GetInputLocked))))
  (bind cm (Variables|Character|GetCharacterMovement))
  (if (and want (not ({V}GetMoveLocked)))
    (Pawn|Components|CharacterMovement|DisableMovement :self cm)
    (Components|Movement|StopMovementImmediately :self cm)
    ({V}SetMoveLocked true))
  (if (and (not want) ({V}GetMoveLocked))
    (Pawn|Components|CharacterMovement|SetMovementMode :self cm :NewMovementMode "MOVE_Falling")
    ({V}SetMoveLocked false)))
'''

PLAYER['PlayerStoreCheckpoint'] = f'''
(fn PlayerStoreCheckpoint (Location Yaw)
  ({V}SetCheckpointLocation Location)
  ({V}SetCheckpointYaw Yaw))
'''

PLAYER['PlayerReachWin'] = f'''
(fn PlayerReachWin ()
  (if (not ({V}GetIsLost))
    ({V}SetHasWon true)))
'''

PLAYER['PlayerSetInputLocked'] = f'''
(fn PlayerSetInputLocked (Locked)
  ({V}SetInputLocked Locked))
'''

PLAYER['PlayerStopAllEnemies'] = f'''
(fn PlayerStopAllEnemies (Stopped)
  (bind foes (Actor|GetAllActorsOfClass {ENEMY_CLASS}))
  (for foe foes
    (Class|BPEnemyBase|EnemySetTimeStopped :self foe :Stopped Stopped)))
'''

PLAYER['PlayerDebugTeleport'] = f'''
(fn PlayerDebugTeleport (Location Yaw)
  (Transformation|SetActorLocation :NewLocation Location :bSweep false :bTeleport true)
  (Transformation|SetActorRotation :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw Yaw) :bTeleportPhysics true))
'''

PLAYER['PlayerGetHealthNow'] = f'''
(fn PlayerGetHealthNow ()
  (return ({V}GetHealth)))
'''


def build():
    out = {}
    for base, graphs in ((E, ENEMY), (P, PLAYER)):
        for name, code in graphs.items():
            out[f'{base}:{name}'] = code.strip()
    return out


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    dst = os.path.join(here, '..', 'JumpCut', 'Saved', 'b1_graphs.json')
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(build(), f, indent=1)
    print('wrote', os.path.normpath(dst), len(build()), 'graphs')
