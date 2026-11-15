# Beat 1 feedback round 6 (2026-11-15): the coworker moves to the car's OTHER side, the thrown
# body and the real one never co-exist, and the hand-off to the player camera stops snapping.
# Written with the Unreal MCP's write_graph_dsl and kept here as text so it can be rebuilt.
# `python tools/b1v_graphs.py` writes JumpCut/Saved/b1v_graphs.json.
#
# WHY THE PLAYER TURNS WITH THE MOVEMENT COMPONENT RATHER THAN A SET-ROTATION.
# "The players model needs to rotate, with animation." The anim blueprint is a blend space driven
# by GetVelocity's XY length, so a SetActorRotation turn is the idle pose sliding round on the
# spot - no animation at all. Feeding AddMovementInput instead gives the blend space real velocity
# (so the walk plays) and lets orient_rotation_to_movement do the turn at the character's own
# 500 deg/s yaw rate. There is no turn-in-place clip in this project to montage: the 38 _CWM clips
# are idle, walk, jog, attacks, hit reacts, deaths, jump/fall/land and nothing else.
#
# AND WHY MoveLocked IS LEFT TRUE WHILE THAT HAPPENS. BP_Player.PlayerRefreshMoveLock DERIVES
# MoveLocked from InputLocked every tick, so clearing MoveLocked would be undone next frame. But
# it only acts on the TRANSITION - `if (and locked (not MoveLocked))` - so with MoveLocked already
# true it never calls DisableMovement again. Setting the movement mode to MOVE_Walking from
# outside is therefore stable, and InputLocked stays true so nothing the player presses lands.
import json, os

D = '/Game/Game/Blueprints/BP_OpeningDirector.BP_OpeningDirector'
P = '/Game/Game/Blueprints/BP_Player.BP_Player'
V = 'Variables|Default|'

G = {}

# ---------------------------------------------------------------- BP_Player: the turn
# MOVE_Walking so AddMovementInput has something to push. Called once, from CineTurnBegin.
G[P + ':PlayerCineTurnBegin'] = f'''
(fn PlayerCineTurnBegin ()
  (Pawn|Components|CharacterMovement|SetMovementMode
    :self (Variables|Character|GetCharacterMovement) :NewMovementMode "MOVE_Walking"))
'''

# Returns true the frame the turn is finished. The 4 deg dead band is what stops the character
# shuffling for ever around a target he can never hit exactly.
G[P + ':PlayerCineTurnStep'] = f'''
(fn PlayerCineTurnStep (TargetYaw Scale)
  (bind err (Math|Rotator|NormalizeAxis
    :Angle (- TargetYaw (.yaw (Transformation|GetActorRotation)))))
  (if (and (< err 4.0) (> err -4.0))
    (Components|Movement|StopMovementImmediately :self (Variables|Character|GetCharacterMovement))
    (Transformation|SetActorRotation
      :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw TargetYaw)
      :bTeleportPhysics true)
    (return true)
    (else
      (Pawn|Input|AddMovementInput
        :WorldDirection (Math|Vector|GetForwardVector
          :InRot (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw TargetYaw))
        :ScaleValue Scale :bForce true)
      (return false))))
'''

# ---------------------------------------------------------------- BP_OpeningDirector: the turn
G[D + ':CineTurnBegin'] = f'''
(fn CineTurnBegin ()
  (bind pl ({V}GetPlayerRef))
  ({V}SetCineTurnOn true)
  ({V}SetCineTurnDone false)
  (Utilities|IsValid pl
    (:"Is Valid"
      ({V}SetCineTurnFromYaw (.yaw (Transformation|GetActorRotation :self pl)))
      (Class|BPPlayer|PlayerCineTurnBegin :self pl))))
'''

G[D + ':CinePlayerTurnStep'] = f'''
(fn CinePlayerTurnStep ()
  (bind pl ({V}GetPlayerRef))
  (Utilities|IsValid pl
    (:"Is Valid"
      (if (and ({V}GetCineTurnOn) (not ({V}GetCineTurnDone)))
        (bind done (Class|BPPlayer|PlayerCineTurnStep :self pl
          :TargetYaw ({V}GetCineEndYaw) :Scale ({V}GetCineTurnScale)))
        (if done
          ({V}SetCineTurnDone true))))))
'''

# ---------------------------------------------------------------- the hand-off
# THE SNAP HAD THREE PARTS, NOT ONE, all measured: the sequence's last cut ended at
# (250, 10, 216) pitch -7 while the player's own camera sits at (396.107, -55.669, 102.642)
# pitch 0 - a 194 cm jump - and the cine camera's 26 mm lens on a 23.76 mm sensor is 49.1 deg
# against the follow camera's 90 deg. Two of the three are fixed in b1_opening_cine.py (the cut
# now ENDS on the measured pose, and CineCam_D_Hand's lens is 11.88 mm = exactly 90 deg). This
# function covers the third: a Level Sequence with a camera cut track reverts the view the instant
# it stops, so there is nothing to blend FROM. B1_Cine_HandCam is a plain CameraActor parked at
# that same pose with FOV 90, so setting it as the view target with blend 0 changes nothing on
# screen - and then blending from IT to the pawn absorbs however far the player's turn carried him
# off the origin. The sequence runs to 11.2 while CineLength is 11.0 so the DIRECTOR always stops
# it first; letting it finish on its own schedule is itself a one-frame pop.
G[D + ':CineHandOverCamera'] = f'''
(fn CineHandOverCamera ()
  (bind pl ({V}GetPlayerRef))
  (bind pc (Game|GetPlayerController :PlayerIndex 0))
  (bind hc ({V}GetCineHandCam))
  (bind sa ({V}GetCineSeqActor))
  (Utilities|IsValid sa
    (:"Is Valid"
      (Sequencer|Player|Stop :self (Class|LevelSequenceActor|GetSequencePlayer :self sa))
      (Utilities|IsValid hc
        (:"Is Valid"
          (Game|Player|SetViewTargetwithBlend :self pc :NewViewTarget hc :BlendTime 0.0
            :BlendFunc "VTBlend_Linear" :BlendExp 1.0 :bLockOutgoing false)
          (Game|Player|SetViewTargetwithBlend :self pc :NewViewTarget pl
            :BlendTime ({V}GetCineHandBlend) :BlendFunc "VTBlend_EaseInOut" :BlendExp 2.0
            :bLockOutgoing false))))))
'''

G[D + ':CineFinishOpening'] = f'''
(fn CineFinishOpening ()
  (bind pl ({V}GetPlayerRef))
  ({V}SetCineRunning false)
  ({V}SetCineDone true)
  ({V}SetCineTurnOn false)
  ({V}SetCineTurnDone true)
  (CallFunction|CineShowWreck)
  (CallFunction|CineShowBody)
  (Pawn|SetControlRotation :self (Pawn|GetController :self pl)
    :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw ({V}GetCineEndYaw)))
  (Class|BPPlayer|SetInputLocked :self pl :InputLocked false)
  (Class|BPPlayer|SetMoveLocked :self pl :MoveLocked false)
  ({V}SetObjectiveState 1)
  ({V}SetBarTarget 0.0)
  (CallFunction|CineSay :Msg "Check on the driver." :Secs 5.0)
  (CallFunction|CineHandOverCamera)
  (Utilities|IsValid ({V}GetCoworkerRef)
    (:"Is Valid"
      (Class|BPCoworker|SetRescueRequiresFreeze :self ({V}GetCoworkerRef)
        :RescueRequiresFreeze false))))
'''

# ---------------------------------------------------------------- reset, and the step
G[D + ':CineSceneBeforeCrash'] = f'''
(fn CineSceneBeforeCrash ()
  (CallFunction|CineHideActor :Target ({V}GetCineWallGC) :Hide false)
  (CallFunction|CineHideActor :Target ({V}GetCineRealCar) :Hide true)
  (CallFunction|CineHideActor :Target ({V}GetExplCarGC) :Hide true)
  (CallFunction|CineHideActor :Target ({V}GetCineRealDriver) :Hide true)
  (CallFunction|CineHideActor :Target ({V}GetObjectiveBeacon) :Hide true)
  (CallFunction|CineHideActor :Target ({V}GetCineFireActor) :Hide true)
  (CallFunction|CineHideActor :Target ({V}GetCineFireLight) :Hide true)
  ({V}SetCineFireLit false)
  ({V}SetCineWallDone false)
  ({V}SetCineFireDone false)
  ({V}SetRagdollOn false)
  ({V}SetRagdollDone false)
  ({V}SetRagdollT 0.0)
  ({V}SetCineTurnOn false)
  ({V}SetCineTurnDone false)
  (CallFunction|CineFireDilate :Rate 0.0))
'''

G[D + ':CineDirectorStep'] = f'''
(fn CineDirectorStep (DeltaSeconds)
  (bind nt (+ ({V}GetCineTime) DeltaSeconds))
  (if ({V}GetExplCine)
    (CallFunction|CineExplStep :DeltaSeconds DeltaSeconds)
    (elif ({V}GetRescueCine)
      (CallFunction|CineRescueStep :DeltaSeconds DeltaSeconds)
      (elif ({V}GetCineRunning)
        ({V}SetCineTime nt)
        (if (and (>= nt ({V}GetCineWallTime)) (not ({V}GetCineWallDone)))
          ({V}SetCineWallDone true)
          (CallFunction|CineBreakWall))
        (if (and (>= nt ({V}GetCineFireTime)) (not ({V}GetCineFireDone)))
          ({V}SetCineFireDone true)
          (CallFunction|CineLightFire))
        (if (>= nt ({V}GetCineImpactTime))
          (CallFunction|CineShowWreck))
        (if (>= nt ({V}GetCineBodyTime))
          (CallFunction|CineShowBody))
        (if (and (>= nt ({V}GetCineTurnStart)) (not ({V}GetCineTurnOn)))
          (CallFunction|CineTurnBegin))
        (if (>= nt ({V}GetCineLength))
          (CallFunction|CineFinishOpening))
        (elif ({V}GetCineDone)
          (CallFunction|CineObjectiveAdvance)
          (elif (not (Class|BPPlayer|GetInputLocked :self ({V}GetPlayerRef)))
            (CallFunction|CineBeginOpening))))))
  (if (and ({V}GetRagdollOn) (not ({V}GetRagdollDone)))
    ({V}SetRagdollT (+ ({V}GetRagdollT) DeltaSeconds))
    (if (> ({V}GetRagdollT) ({V}GetRagdollSettle))
      ({V}SetRagdollDone true)
      (CallFunction|CineDriverRagdollStop)))
  (CallFunction|CinePlayerTurnStep)
  (CallFunction|CineFireTimeStep)
  (CallFunction|CineBeaconStep :DeltaSeconds DeltaSeconds))
'''

# ---------------------------------------------------------------- the beacon follows HER now
# The coworker moved to the car's +Y side ("the coworker needs to be on the other side of the car
# then because he's blocking the path right now"), and that move BREAKS the beat unless this
# changes too. Measured: BP_Coworker.InteractRange is 280 cm and she used to stand 260 cm from the
# driver's body, so the rescue fired the instant the player reached the driver and it never
# mattered that objective 2's beacon pointed at ObjSafeLoc, 950 cm the OTHER way. At her new spot
# she is 295 cm from the body - outside that range - so the player has to walk to her, and the
# beacon has to say so. It also matches the caption that is already on screen at that moment:
# "The car is going to blow. Get her out."
#
# It is a STORED VECTOR (ObjCoworkerLoc, set by b1_opening_wire.py from the same constant that
# places her), not a live GetActorLocation on CoworkerRef. Calling a member function on a null
# reference aborts the whole Blueprint function with "Accessed None", and this one is read every
# tick by CineBeaconStep - so the three objective spots that already exist (ObjDriverLoc,
# ObjSafeLoc, ObjStreetLoc) are all constants for exactly that reason. Keep it that way.
G[D + ':CineObjectiveSpot'] = f'''
(fn CineObjectiveSpot ()
  (bind s ({V}GetObjectiveState))
  (if (== s 1)
    (return ({V}GetObjDriverLoc))
    (elif (== s 2)
      (return ({V}GetObjCoworkerLoc))
      (elif (== s 3)
        (return ({V}GetObjStreetLoc))
        (elif (== s 4)
          (return ({V}GetObjGoonLoc))
          (elif (== s 5)
            (return ({V}GetObjBossLoc))
            (else
              (return (Math|Vector|MakeVector 0.0)))))))))
'''

if __name__ == '__main__':
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, 'JumpCut', 'Saved', 'b1v_graphs.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w') as fh:
        json.dump({'graphs': G}, fh, indent=1)
    print('wrote %s (%d graphs)' % (out, len(G)))
