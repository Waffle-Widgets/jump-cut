"""Graph text for "the thugs stop being one creature" (beats 1-3 clean-up, Nov 13).

What was wrong, read off the Blueprints rather than guessed:
  * BP_Player.PlayerPunch damaged EVERY enemy inside the punch arc, on every punch. Three goons standing together
    took the same hits on the same frames, so they flinched together and died together.
  * BP_Goon has no state of its own: every goon had the same speed, wind-up, cooldown, health and aggro range, woke
    on the same frame, walked the same straight line at the player, and swung on the same frame.
  * One hit react, one death and one punch montage for all of them.

What this does:
  * Light punches (hits 1 and 2) land on the ONE nearest enemy in the arc. The finisher still sweeps everybody.
  * BP_EnemyBase gains EnemyVary (off by default, so the bosses and stand-ins are untouched; on for BP_Goon).
    With it on, each goon rolls its own speed, wind-up, health, aggro range and stand-off distance at spawn, keeps
    apart from its neighbours, circles the player at its stand-off distance while it waits, and only
    EnemyMaxAttackers (1) may be winding up at a time - the others hold and circle, then take their turn.
  * Life (the second pass, same day): each goon rolls its own size (0.93-1.08), and a goon that is waiting its
    turn at stand-off range throws a feint every 4-9 s (EnemyAnimTaunts) and stands for it instead of sliding.
  * Hit reacts, deaths and punches are picked per hit from arrays; a blow from behind or the side picks the
    matching clip (tools/unreal_goon_variety_anims.py makes the montages).

Usage (maker-safe: this file only prints text):
    python tools/goon_individual_graphs.py > JumpCut/Saved/jcpy/goon_individual.json
The builder pushes each graph with BlueprintTools.write_graph_dsl, compiles, then reads back and COUNTS NODES
(the duplicate-append trap) - see docs/devlog/2026-11-13-the-thugs-stop-being-one-creature.md.

Variables to add first (BP_EnemyBase): EnemyVary bool (instance editable), EnemyOrbitSide float 1.0,
EnemyHoldRange float 260, EnemySepRadius float 170, EnemyMaxAttackers int 1, EnemyScratchCount int,
EnemyScratchVec Vector, EnemyAnimPunchAlts / EnemyAnimHitAlts / EnemyAnimDeathAlts AnimMontage ARRAY,
EnemyAnimHitHeavy, EnemyAnimHitBack, EnemyAnimDeathBack, EnemyAnimDeathLeft, EnemyAnimDeathRight AnimMontage.
Second pass: EnemyTauntLeft float, EnemyTauntBusyLeft float, EnemyAnimTaunts AnimMontage ARRAY.
(BP_Player): PunchBestDist float, PunchBestTarget BP_EnemyBase object.
New functions: EnemyVarySetup, EnemyIsMidAttack -> Busy bool, EnemyScanOthers, EnemySteerMove (Hold bool),
EnemyPickPunchAnim -> Anim, EnemyPickHitAnim (FromLocation Vector, Heavy bool) -> Anim,
EnemyPickDeathAnim (FromLocation Vector) -> Anim.
"""
import json

V = 'Variables|Default|'
ENEMY_CLASS = '"/Game/Game/Blueprints/BP_EnemyBase.BP_EnemyBase_C"'
ENEMY, PLAYER = {}, {}

ENEMY['EnemyVarySetup'] = f'''
(fn EnemyVarySetup ()
  (if ({V}GetEnemyVary)
    ({V}SetEnemyMoveSpeed (* ({V}GetEnemyMoveSpeed) (Math|Random|RandomFloatinRange :Min 0.8 :Max 1.2)))
    ({V}SetEnemyWindup (* ({V}GetEnemyWindup) (Math|Random|RandomFloatinRange :Min 0.85 :Max 1.4)))
    ({V}SetEnemyMaxHealth (* ({V}GetEnemyMaxHealth) (Math|Random|RandomFloatinRange :Min 0.8 :Max 1.25)))
    ({V}SetEnemyAggroRange (* ({V}GetEnemyAggroRange) (Math|Random|RandomFloatinRange :Min 0.7 :Max 1.1)))
    ({V}SetEnemyHoldRange (Math|Random|RandomFloatinRange :Min 230.0 :Max 330.0))
    ({V}SetEnemyOrbitSide (select (Math|Random|RandomBool) 1.0 (- 0.0 1.0)))
    ({V}SetEnemyAttackCooldownLeft (Math|Random|RandomFloatinRange :Min 0.0 :Max 1.0))
    ({V}SetEnemyTauntLeft (Math|Random|RandomFloatinRange :Min 1.5 :Max 6.0))
    (Transformation|SetActorScale3D :NewScale3D (* (Transformation|GetActorScale3D) (Math|Random|RandomFloatinRange :Min 0.93 :Max 1.08)))
    (Transformation|SetActorRotation :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw (+ (.yaw (Transformation|GetActorRotation)) (Math|Random|RandomFloatinRange :Min (- 0.0 50.0) :Max 50.0))) :bTeleportPhysics true)))
'''

# VarySetup runs FIRST, so the rolled max health and speed are the ones the rest of setup copies.
ENEMY['EnemySetup'] = f'''
(fn EnemySetup ()
  (CallFunction|EnemyVarySetup)
  ({V}SetEnemyHealth ({V}GetEnemyMaxHealth))
  (Class|CharacterMovementComponent|SetMaxWalkSpeed :self (Variables|Character|GetCharacterMovement) :MaxWalkSpeed ({V}GetEnemyMoveSpeed))
  ({V}SetEnemyHomeLocation (Transformation|GetActorLocation))
  ({V}SetEnemyHomeYaw (.yaw (Transformation|GetActorRotation)))
  ({V}SetEnemyIsAwake ({V}GetEnemyStartsAwake))
  (CallFunction|EnemyShowWarning :Show false))
'''

ENEMY['EnemyIsMidAttack'] = f'''
(fn EnemyIsMidAttack ()
  (return (and ({V}GetEnemyIsWindingUp) (not ({V}GetEnemyIsDefeated)))))
'''

# One pass over the other enemies gives both answers a goon needs each frame: how many are already winding up
# (EnemyScratchCount) and which way to lean to keep off its neighbours (EnemyScratchVec). The DSL has no mutable
# locals, so both accumulate in member variables. "d > 1" is how a goon skips itself.
ENEMY['EnemyScanOthers'] = f'''
(fn EnemyScanOthers ()
  (bind me (Transformation|GetActorLocation))
  ({V}SetEnemyScratchCount 0)
  ({V}SetEnemyScratchVec (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z 0.0))
  (bind others (Actor|GetAllActorsOfClass {ENEMY_CLASS}))
  (for o others
    (bind diff (- me (Transformation|GetActorLocation :self o)))
    (bind flat (Math|Vector|MakeVector :X (.x diff) :Y (.y diff) :Z 0.0))
    (bind d (Math|Vector|VectorLength flat))
    (bind hp (CallFunction|EnemyGetHealthNow :self o))
    (bind busy (CallFunction|EnemyIsMidAttack :self o))
    (if (and (> d 1.0) (> hp 0.0))
      (if busy
        ({V}SetEnemyScratchCount (+ ({V}GetEnemyScratchCount) 1)))
      (if (< d ({V}GetEnemySepRadius))
        ({V}SetEnemyScratchVec (+ ({V}GetEnemyScratchVec) (* (Math|Vector|Normalize flat) (- 1.0 (/ d ({V}GetEnemySepRadius))))))))))
'''

# Hold = circling at the stand-off distance while waiting for a turn; otherwise closing in. Either way the goon
# leans off its neighbours (EnemyScratchVec, from EnemyScanOthers) and drifts round the player on its own side.
ENEMY['EnemySteerMove'] = f'''
(fn EnemySteerMove (Hold)
  (CallFunction|EnemyFacePlayer)
  (bind diff (- (Transformation|GetActorLocation :self ({V}GetPlayerRef)) (Transformation|GetActorLocation)))
  (bind flat (Math|Vector|MakeVector :X (.x diff) :Y (.y diff) :Z 0.0))
  (bind dist (Math|Vector|VectorLength flat))
  (bind toP (Math|Vector|Normalize flat))
  (bind tang (* (Math|Vector|MakeVector :X (- 0.0 (.y toP)) :Y (.x toP) :Z 0.0) ({V}GetEnemyOrbitSide)))
  (bind radial (select Hold (Math|Float|Clamp(Float) :Value (/ (- dist ({V}GetEnemyHoldRange)) 80.0) :Min (- 0.0 1.0) :Max 1.0) 1.0))
  (bind dir (+ (+ (* toP radial) (* tang (select Hold 0.7 0.3))) (* ({V}GetEnemyScratchVec) 1.6)))
  (Pawn|Input|AddMovementInput :WorldDirection (Math|Vector|Normalize dir) :ScaleValue (select Hold 0.6 1.0)))
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
      ({V}SetEnemyAttackCooldownLeft (* ({V}GetEnemyAttackCooldown) (select ({V}GetEnemyVary) (Math|Random|RandomFloatinRange :Min 0.8 :Max 1.5) 1.0)))
      ({V}SetEnemyOrbitSide (select (Math|Random|RandomBool) 1.0 (- 0.0 1.0))))
    (else
      (bind d (CallFunction|EnemyDistToPlayer))
      (if ({V}GetEnemyVary)
        (CallFunction|EnemyScanOthers)
        (if (> ({V}GetEnemyTauntBusyLeft) 0.0)
          (CallFunction|EnemyFacePlayer)
          ({V}SetEnemyTauntBusyLeft (- ({V}GetEnemyTauntBusyLeft) DeltaSeconds))
          (elif (and (or (> ({V}GetEnemyAttackCooldownLeft) 0.0) (>= ({V}GetEnemyScratchCount) ({V}GetEnemyMaxAttackers))) (<= d (+ ({V}GetEnemyHoldRange) 60.0)))
            (CallFunction|EnemySteerMove :Hold true)
            ({V}SetEnemyTauntLeft (- ({V}GetEnemyTauntLeft) DeltaSeconds))
            (if (and (and (<= ({V}GetEnemyTauntLeft) 0.0) (> d (+ ({V}GetEnemyAttackRange) 60.0))) (> (Utilities|Array|Length ({V}GetEnemyAnimTaunts)) 0))
              (bind len (Animation|PlayAnimMontage :AnimMontage (Utilities|Array|Get(acopy) ({V}GetEnemyAnimTaunts) (Math|Random|RandomIntegerinRange :Min 0 :Max (Utilities|Array|LastIndex ({V}GetEnemyAnimTaunts)))) :InPlayRate (Math|Random|RandomFloatinRange :Min 0.9 :Max 1.15)))
              ({V}SetEnemyTauntBusyLeft (* len 0.8))
              ({V}SetEnemyTauntLeft (Math|Random|RandomFloatinRange :Min 4.0 :Max 9.0)))
            (elif (> d ({V}GetEnemyAttackRange))
              (CallFunction|EnemySteerMove :Hold false)
              (else
                (CallFunction|EnemyFacePlayer)
                (if (and (<= ({V}GetEnemyAttackCooldownLeft) 0.0) (< ({V}GetEnemyScratchCount) ({V}GetEnemyMaxAttackers)))
                  ({V}SetEnemyIsWindingUp true)
                  ({V}SetEnemyWindupLeft ({V}GetEnemyWindup))
                  (CallFunction|EnemyShowWarning :Show true))))))
        (elif (> d ({V}GetEnemyAttackRange))
          (CallFunction|EnemyWalkToPlayer)
          (else
            (CallFunction|EnemyFacePlayer)
            (if (<= ({V}GetEnemyAttackCooldownLeft) 0.0)
              ({V}SetEnemyIsWindingUp true)
              ({V}SetEnemyWindupLeft ({V}GetEnemyWindup))
              (CallFunction|EnemyShowWarning :Show true))))))))
'''

ENEMY['EnemyPickPunchAnim'] = f'''
(fn EnemyPickPunchAnim ()
  (if (> (Utilities|Array|Length ({V}GetEnemyAnimPunchAlts)) 0)
    (return (Utilities|Array|Get(acopy) ({V}GetEnemyAnimPunchAlts) (Math|Random|RandomIntegerinRange :Min 0 :Max (Utilities|Array|LastIndex ({V}GetEnemyAnimPunchAlts)))))
    (else
      (return ({V}GetEnemyAnimPunch)))))
'''

ENEMY['EnemyPickHitAnim'] = f'''
(fn EnemyPickHitAnim (FromLocation Heavy)
  (bind to (- FromLocation (Transformation|GetActorLocation)))
  (bind f (Math|Vector|DotProduct :A (Transformation|GetActorForwardVector) :B (Math|Vector|Normalize (Math|Vector|MakeVector :X (.x to) :Y (.y to) :Z 0.0))))
  (if (> (Utilities|Array|Length ({V}GetEnemyAnimHitAlts)) 0)
    (if (< f (- 0.0 0.3))
      (return ({V}GetEnemyAnimHitBack))
      (elif Heavy
        (return ({V}GetEnemyAnimHitHeavy))
        (else
          (return (Utilities|Array|Get(acopy) ({V}GetEnemyAnimHitAlts) (Math|Random|RandomIntegerinRange :Min 0 :Max (Utilities|Array|LastIndex ({V}GetEnemyAnimHitAlts))))))))
    (else
      (return ({V}GetEnemyAnimHitReact)))))
'''

ENEMY['EnemyPickDeathAnim'] = f'''
(fn EnemyPickDeathAnim (FromLocation)
  (bind to (- FromLocation (Transformation|GetActorLocation)))
  (bind dir (Math|Vector|Normalize (Math|Vector|MakeVector :X (.x to) :Y (.y to) :Z 0.0)))
  (bind f (Math|Vector|DotProduct :A (Transformation|GetActorForwardVector) :B dir))
  (bind r (Math|Vector|DotProduct :A (Transformation|GetActorRightVector) :B dir))
  (if (> (Utilities|Array|Length ({V}GetEnemyAnimDeathAlts)) 0)
    (if (< f (- 0.0 0.5))
      (return ({V}GetEnemyAnimDeathBack))
      (elif (> f 0.5)
        (return (Utilities|Array|Get(acopy) ({V}GetEnemyAnimDeathAlts) (Math|Random|RandomIntegerinRange :Min 0 :Max (Utilities|Array|LastIndex ({V}GetEnemyAnimDeathAlts)))))
        (elif (> r 0.0)
          (return ({V}GetEnemyAnimDeathRight))
          (else
            (return ({V}GetEnemyAnimDeathLeft))))))
    (else
      (return ({V}GetEnemyAnimDeath)))))
'''

ENEMY['EnemyPunchPlayer'] = f'''
(fn EnemyPunchPlayer (Damage)
  (bind anim (CallFunction|EnemyPickPunchAnim))
  (Animation|PlayAnimMontage :AnimMontage anim)
  (bind d (CallFunction|EnemyDistToPlayer))
  (if (<= d ({V}GetEnemyHitReach))
    (Class|BPPlayer|PlayerTakeHit :self ({V}GetPlayerRef) :Damage Damage)
    (Class|BPPlayer|PlayerKnockFrom :self ({V}GetPlayerRef) :FromLocation (Transformation|GetActorLocation) :Strength ({V}GetEnemyKnockOnPlayer))))
'''

# The stand-in redirect (beat 5, now a nice-to-have) is kept exactly; only the two montage choices changed.
ENEMY['EnemyTakeHit'] = f'''
(fn EnemyTakeHit (Damage FromLocation KnockStrength KnockUp StunTime)
  (bind here (Transformation|GetActorLocation))
  (bind toward (- FromLocation here))
  (bind blockSpot (+ here (* (Math|Vector|Normalize (Math|Vector|MakeVector :X (.x toward) :Y (.y toward) :Z 0.0)) 95.0)))
  (bind away (- here FromLocation))
  (bind flat (Math|Vector|Normalize (Math|Vector|MakeVector :X (.x away) :Y (.y away) :Z 0.0)))
  (bind knock (* (+ (* flat KnockStrength) (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z KnockUp)) ({V}GetEnemyKnockTakenScale)))
  (bind stun (* StunTime ({V}GetEnemyStunTakenScale)))
  (if (and (not ({V}GetEnemyIsDefeated)) (not ({V}GetEnemyTimeStopped)))
    (CallFunction|EnemyPickStandIn)
    (else
      ({V}SetEnemyRedirectFound false)))
  (if ({V}GetEnemyRedirectFound)
    (Transformation|SetActorLocation :self ({V}GetEnemyRedirectTarget) :NewLocation blockSpot :bSweep false :bTeleport true)
    (Transformation|SetActorRotation :self ({V}GetEnemyRedirectTarget) :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw (.yaw (Math|Rotator|FindLookAtRotation :Start blockSpot :Target FromLocation))) :bTeleportPhysics false)
    (CallFunction|EnemyTakeHit :self ({V}GetEnemyRedirectTarget) :Damage Damage :FromLocation FromLocation :KnockStrength KnockStrength :KnockUp KnockUp :StunTime StunTime)
    (elif (not ({V}GetEnemyIsDefeated))
      (if (not ({V}GetEnemyIsAwake))
        (CallFunction|EnemyWake))
      ({V}SetEnemyHealth (Math|Float|Max(Float) 0.0 (- ({V}GetEnemyHealth) Damage)))
      (bind hitAnim (CallFunction|EnemyPickHitAnim :FromLocation FromLocation :Heavy (>= StunTime 0.5)))
      (bind deathAnim (CallFunction|EnemyPickDeathAnim :FromLocation FromLocation))
      (if ({V}GetEnemyTimeStopped)
        ({V}SetEnemyPendingKnock (+ ({V}GetEnemyPendingKnock) knock))
        (else
          (Character|LaunchCharacter :LaunchVelocity knock :bXYOverride true :bZOverride true)))
      (if (> stun 0.0)
        ({V}SetEnemyStunLeft (Math|Float|Max(Float) ({V}GetEnemyStunLeft) stun))
        ({V}SetEnemyIsWindingUp false)
        (CallFunction|EnemyShowWarning :Show false))
      (if (> ({V}GetEnemyHealth) 0.0)
        (Animation|PlayAnimMontage :AnimMontage hitAnim)
        (else
          (Animation|PlayAnimMontage :AnimMontage deathAnim)
          ({V}SetEnemyIsDefeated true)
          ({V}SetEnemyDefeatLingerLeft ({V}GetEnemyDefeatLinger))
          (CallFunction|EnemyShowWarning :Show false)
          (CallFunction|EnemyDefeatedHook))))))
'''

# Hits 1 and 2 pick ONE target: the nearest living enemy in the arc. Hit 3 (the finisher) still sweeps them all.
# PunchBestDist / PunchBestTarget are member variables because the DSL has no mutable locals.
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
    (Animation|PlayAnimMontage :AnimMontage (select fin ({V}GetPlayerAnimPunchFinisher) (select (== step 2) ({V}GetPlayerAnimPunchB) ({V}GetPlayerAnimPunchA))))
    ({V}SetPunchBestDist 100000.0)
    (bind foes (Actor|GetAllActorsOfClass {ENEMY_CLASS}))
    (for foe foes
      (bind to (- (Transformation|GetActorLocation :self foe) here))
      (bind dir (Math|Vector|Normalize (Math|Vector|MakeVector :X (.x to) :Y (.y to) :Z 0.0)))
      (bind hp (Class|BPEnemyBase|EnemyGetHealthNow :self foe))
      (if (and (> hp 0.0) (and (<= (Math|Vector|VectorLengthXY to) ({V}GetPunchRange)) (>= (Math|Vector|DotProduct :A fwd :B dir) ({V}GetPunchArcDot))))
        (if fin
          (Class|BPEnemyBase|EnemyTakeHit :self foe :Damage dmg :FromLocation here :KnockStrength kb :KnockUp ku :StunTime st)
          (elif (< (Math|Vector|VectorLengthXY to) ({V}GetPunchBestDist))
            ({V}SetPunchBestDist (Math|Vector|VectorLengthXY to))
            ({V}SetPunchBestTarget foe)))))
    (if (and (not fin) (< ({V}GetPunchBestDist) 99999.0))
      (Class|BPEnemyBase|EnemyTakeHit :self ({V}GetPunchBestTarget) :Damage dmg :FromLocation here :KnockStrength kb :KnockUp ku :StunTime st))
    ({V}SetComboStep (select fin 0 step))
    ({V}SetComboTimeLeft ({V}GetComboWindow))))
'''

if __name__ == '__main__':
    print(json.dumps({'enemy': ENEMY, 'player': PLAYER}, indent=1))
