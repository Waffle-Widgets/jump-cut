# Beat 1 feedback round 7 (2026-11-15): the marker glows, the caption box pulses, getting Freeze
# Frame is a moment of its own, and the pan after the explosion ENDS ON THE PLAYER'S OWN CAMERA.
# Written with the Unreal MCP's write_graph_dsl and kept here as text so it can be rebuilt.
# `python tools/b1u_graphs.py` writes JumpCut/Saved/b1u_graphs.json.
#
# NOTHING HERE EDITS BP_Player. It was LFS-locked by another computer that night, so the two things
# that want the player's camera reach it from the director with GetComponentByClass(CameraComponent):
# CinePlayerFov (the push-in when the power lands) and the last leg of CineExplCamStep.
#
# THE HAND-OFF. The explosion camera used to finish on a fixed pose (ExplCamD: 180, 60, 210, yaw -5,
# 75 deg lens) and then blend 0.6 s to wherever the player's camera happened to be - which, after
# walking west to the coworker, was pointing west. CineExplFacePlayer now turns the model AND the
# controller toward ObjStreetLoc at 0.9 s, while the camera is on the wreck and he is out of frame,
# and the last leg lerps to the follow camera's LIVE world pose with the lens opening 75 -> 90.
# Measured in PIE by tools/b1u_pie.py: 0.01 cm, 0.00 deg and 0.00 deg of FOV between the last
# cinematic frame and the first frame of play.
#
# THE POWER MOMENT runs on REAL time: global time dilation drops to 0.06, so DeltaSeconds is tiny and
# the step divides it back out by the dilation. The overlay's bars and caption timer do the same in
# EventTick, or the letterbox would take 50 s to close.
#
# New variables are STATE ONLY (bool/float that start at zero). Every tuning number is a literal in
# the graph, because a placed actor does not reliably pick up a new variable's class default.
import json, os

D = '/Game/Game/Blueprints/BP_OpeningDirector.BP_OpeningDirector'
W = '/Game/Game/UI/WBP_CineOverlay.WBP_CineOverlay'
V = 'Variables|Default|'
WV = 'Variables|WBP_CineOverlay|'
CAMC = '"/Script/Engine.CameraComponent"'

# director: (name, type)
VARS = [('PowerCine', 'bool'), ('PowerT', 'float'), ('FlashAlpha', 'float'), ('ExplFaced', 'bool'),
        ('BeaconLit', 'bool')]
# director: (name, [(param, type)])
FNS = [('CineBeaconDress', []), ('CinePowerBegin', []), ('CinePowerStep', [('RealDelta', 'float')]),
       ('CinePowerEnd', []), ('CinePlayerFov', [('Fov', 'float')]), ('CineFlashPush', []),
       ('CineExplFacePlayer', []), ('CineExplCamFov', [('Fov', 'float')])]
# overlay widget: a full-screen Border "FlashBox" (white square brush, tint 0.78/0.96/1.0, render
# opacity 0, anchors 0,0-1,1), CapText.AutoWrapText = false, and:
WVARS = [('CapPulseT', 'float'), ('CapOn', 'bool')]
WFNS = [('CineFlashSet', [('Alpha', 'float')]), ('CineCaptionPulseStep', [('DeltaSeconds', 'float')])]

G = {}    # director graphs
G['CineBeaconDress']=f'''
(fn CineBeaconDress ()
  (bind bk ({V}GetObjectiveBeacon))
  ({V}SetBeaconLit true)
  (Utilities|IsValid bk
    (:"Is Valid"
      (Rendering|Material|SetMaterial
        :self (Actor|GetComponentbyClass :self bk :ComponentClass "/Script/Engine.StaticMeshComponent")
        :ElementIndex 0 :Material "/Game/Game/Materials/M_ObjectiveGlow.M_ObjectiveGlow"))))
'''
G['CineBeaconStep']=f'''
(fn CineBeaconStep (DeltaSeconds)
  ({V}SetObjectiveBob (+ ({V}GetObjectiveBob) DeltaSeconds))
  (if (not ({V}GetBeaconLit))
    (CallFunction|CineBeaconDress))
  (if (> ({V}GetObjectiveState) 0)
    (bind spot (CallFunction|CineObjectiveSpot))
    (bind bob ({V}GetObjectiveBob))
    (bind bk ({V}GetObjectiveBeacon))
    (bind k (+ 1.0 (* 0.14 (Math|Trig|Sin(Radians) (* bob 5.0)))))
    (Transformation|SetActorLocation :self bk
      :NewLocation (Math|Vector|MakeVector :X (.x spot) :Y (.y spot)
        :Z (+ (+ (.z spot) ({V}GetObjectiveHeight)) (* 16.0 (Math|Trig|Sin(Radians) (* bob 2.4)))))
      :bSweep false :bTeleport true)
    (Transformation|SetActorScale3D :self bk
      :NewScale3D (Math|Vector|MakeVector :X (* 0.5 k) :Y (* 0.5 k) :Z (* 0.85 k)))
    (CallFunction|CineHideActor :Target bk :Hide false)
    (else
      (CallFunction|CineHideActor :Target ({V}GetObjectiveBeacon) :Hide true))))
'''
G['CinePlayerFov']=f'''
(fn CinePlayerFov (Fov)
  (bind pl ({V}GetPlayerRef))
  (Utilities|IsValid pl
    (:"Is Valid"
      (Camera|SetFieldOfView (Actor|GetComponentbyClass :self pl :ComponentClass {CAMC}) Fov))))
'''
G['CineExplCamFov']=f'''
(fn CineExplCamFov (Fov)
  (bind cam ({V}GetExplCam))
  (Utilities|IsValid cam
    (:"Is Valid"
      (Camera|SetFieldOfView (Actor|GetComponentbyClass :self cam :ComponentClass {CAMC}) Fov))))
'''
G['CineFlashPush']=f'''
(fn CineFlashPush ()
  (Utilities|IsValid ({V}GetOverlayRef)
    (:"Is Valid"
      (Class|WBPCineOverlay|CineFlashSet :self ({V}GetOverlayRef) :Alpha ({V}GetFlashAlpha)))))
'''
G['CinePowerBegin']=f'''
(fn CinePowerBegin ()
  (bind pl ({V}GetPlayerRef))
  ({V}SetPowerCine true)
  ({V}SetPowerT 0.0)
  ({V}SetFlashAlpha 0.9)
  ({V}SetObjectiveState 0)
  ({V}SetBarTarget 1.0)
  (Class|BPPlayer|SetInputLocked :self pl :InputLocked true)
  (Class|BPPlayer|SetMoveLocked :self pl :MoveLocked true)
  (Utilities|Time|SetGlobalTimeDilation :TimeDilation 0.06)
  (Audio|PlaySound2D :Sound "/Game/Game/Audio/SFX_PowerFreezeFrame.SFX_PowerFreezeFrame")
  (CallFunction|CineSay :Msg "FREEZE FRAME" :Secs 3.0)
  (CallFunction|CineFlashPush))
'''
G['CinePowerStep']=f'''
(fn CinePowerStep (RealDelta)
  ({V}SetPowerT (+ ({V}GetPowerT) RealDelta))
  (bind t ({V}GetPowerT))
  ({V}SetFlashAlpha (select (< t 0.45) (* 0.9 (- 1.0 (/ t 0.45))) 0.0))
  (CallFunction|CineFlashPush)
  (bind kin (select (< t 0.25) (/ t 0.25) 1.0))
  (bind kraw (/ (- 2.2 t) 0.5))
  (bind kout (select (> kraw 1.0) 1.0 (select (< kraw 0.0) 0.0 kraw)))
  (CallFunction|CinePlayerFov :Fov (- 90.0 (* 26.0 (* kin kout))))
  (if (>= t 2.2)
    (CallFunction|CinePowerEnd)))
'''
G['CinePowerEnd']=f'''
(fn CinePowerEnd ()
  (bind pl ({V}GetPlayerRef))
  ({V}SetPowerCine false)
  ({V}SetFlashAlpha 0.0)
  (Utilities|Time|SetGlobalTimeDilation :TimeDilation 1.0)
  (CallFunction|CinePlayerFov :Fov 90.0)
  (CallFunction|CineFlashPush)
  ({V}SetBarTarget 0.0)
  (Class|BPPlayer|SetInputLocked :self pl :InputLocked false)
  (Class|BPPlayer|SetMoveLocked :self pl :MoveLocked false)
  ({V}SetObjectiveState 2))
'''
G['CineObjDriver']=f'''
(fn CineObjDriver ()
  (bind dr ({V}GetDriverRef))
  (Utilities|IsValid dr
    (:"Is Valid"
      (if ({V}GetAutoBeats)
        (Class|BPCrashDriver|DriverTryTouch :self dr))
      (if (Class|BPCrashDriver|GetDriverTouched :self dr)
        (CallFunction|CinePowerBegin)))))
'''
G['CineExplFacePlayer']=f'''
(fn CineExplFacePlayer ()
  (bind pl ({V}GetPlayerRef))
  (bind to (- ({V}GetObjStreetLoc) (Transformation|GetActorLocation :self pl)))
  (bind yaw (Math|Trig|Atan2(Degrees) (.y to) (.x to)))
  (Transformation|SetActorRotation :self pl
    :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw yaw) :bTeleportPhysics true)
  (Pawn|SetControlRotation :self (Pawn|GetController :self pl)
    :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw yaw)))
'''
G['CineExplBegin']=f'''
(fn CineExplBegin ()
  (bind pl ({V}GetPlayerRef))
  ({V}SetExplCine true)
  ({V}SetRescueCine false)
  ({V}SetExplT 0.0)
  ({V}SetExplSaid false)
  ({V}SetExplFaced false)
  ({V}SetObjectiveState 0)
  ({V}SetBarTarget 1.0)
  (Class|BPPlayer|SetInputLocked :self pl :InputLocked true)
  (Class|BPPlayer|SetMoveLocked :self pl :MoveLocked true)
  (if (Class|BPPlayer|GetFreezeFrameActive :self pl)
    (Class|BPPlayer|PlayerFreezeFrameEnd :self pl))
  (CallFunction|CineExplFire)
  (CallFunction|CineExplCardOn)
  (CallFunction|CineExplCamFov :Fov 75.0)
  (bind cam ({V}GetExplCam))
  (Utilities|IsValid cam
    (:"Is Valid"
      (Transformation|SetActorLocationAndRotation :self cam :NewLocation ({V}GetExplCamALoc)
        :NewRotation ({V}GetExplCamARot) :bSweep false :bTeleport true)
      (Game|Player|SetViewTargetwithBlend :self (Game|GetPlayerController :PlayerIndex 0)
        :NewViewTarget cam :BlendTime 0.35 :BlendFunc "VTBlend_EaseInOut" :BlendExp 2.0
        :bLockOutgoing false))))
'''
G['CineExplStep']=f'''
(fn CineExplStep (DeltaSeconds)
  ({V}SetExplT (+ ({V}GetExplT) DeltaSeconds))
  (bind t ({V}GetExplT))
  (if (and (> t 0.9) (not ({V}GetExplFaced)))
    ({V}SetExplFaced true)
    (CallFunction|CineExplFacePlayer))
  (CallFunction|CineExplCamStep)
  (CallFunction|CineExplCardStep)
  (if (not ({V}GetExplSaid))
    (if (> t ({V}GetExplSayAt))
      ({V}SetExplSaid true)
      (CallFunction|CineSay :Msg "That was meant for you. They are waiting outside." :Secs 5.0)))
  (if (>= t ({V}GetExplTD))
    (CallFunction|CineExplEnd)))
'''
# The last leg no longer ends on a fixed pose: it ends on the PLAYER'S OWN camera, read live, with
# the lens opened from 75 to the follow camera's 90 on the way. CineExplFacePlayer has already
# turned the model and the controller towards the street, so when CineExplEnd hands the view back
# nothing on screen moves.
G['CineExplCamStep']=f'''
(fn CineExplCamStep ()
  (bind t ({V}GetExplT))
  (bind tb ({V}GetExplTB))
  (bind tc ({V}GetExplTC))
  (bind td ({V}GetExplTD))
  (bind cam ({V}GetExplCam))
  (Utilities|IsValid cam
    (:"Is Valid"
      (if (< t tb)
        (bind a (/ t tb))
        (Transformation|SetActorLocationAndRotation :self cam
          :NewLocation (Math|Vector|Lerp(Vector) :A ({V}GetExplCamALoc) :B ({V}GetExplCamBLoc) :Alpha a)
          :NewRotation (Math|Rotator|Lerp(Rotator) :A ({V}GetExplCamARot) :B ({V}GetExplCamBRot) :Alpha a :bShortestPath true)
          :bSweep false :bTeleport true)
        (elif (< t tc)
          (bind b0 (/ (- t tb) (- tc tb)))
          (bind b (* (* b0 b0) (- 3.0 (* 2.0 b0))))
          (Transformation|SetActorLocationAndRotation :self cam
            :NewLocation (Math|Vector|Lerp(Vector) :A ({V}GetExplCamBLoc) :B ({V}GetExplCamCLoc) :Alpha b)
            :NewRotation (Math|Rotator|Lerp(Rotator) :A ({V}GetExplCamBRot) :B ({V}GetExplCamCRot) :Alpha b :bShortestPath true)
            :bSweep false :bTeleport true)
          (else
            (bind raw (/ (- t tc) (- td tc)))
            (bind c0 (select (> raw 1.0) 1.0 raw))
            (bind c (* (* c0 c0) (- 3.0 (* 2.0 c0))))
            (bind pcam (Actor|GetComponentbyClass :self ({V}GetPlayerRef) :ComponentClass {CAMC}))
            (Transformation|SetActorLocationAndRotation :self cam
              :NewLocation (Math|Vector|Lerp(Vector) :A ({V}GetExplCamCLoc) :B (Transformation|GetWorldLocation :self pcam) :Alpha c)
              :NewRotation (Math|Rotator|Lerp(Rotator) :A ({V}GetExplCamCRot) :B (Transformation|GetWorldRotation :self pcam) :Alpha c :bShortestPath true)
              :bSweep false :bTeleport true)
            (CallFunction|CineExplCamFov :Fov (+ 75.0 (* 15.0 c)))))))))
'''
G['CineExplEnd']=f'''
(fn CineExplEnd ()
  (bind pl ({V}GetPlayerRef))
  ({V}SetExplCine false)
  ({V}SetExplDone true)
  ({V}SetBarTarget 0.0)
  (CallFunction|CineHideActor :Target ({V}GetExplCard) :Hide true)
  (Class|BPPlayer|SetInputLocked :self pl :InputLocked false)
  (Class|BPPlayer|SetMoveLocked :self pl :MoveLocked false)
  (Game|Player|SetViewTargetwithBlend :self (Game|GetPlayerController :PlayerIndex 0)
    :NewViewTarget pl :BlendTime 0.2 :BlendFunc "VTBlend_EaseInOut" :BlendExp 2.0 :bLockOutgoing false)
  ({V}SetObjectiveState 3))
'''
G['CineDirectorStep']=f'''
(fn CineDirectorStep (DeltaSeconds)
  (bind nt (+ ({V}GetCineTime) DeltaSeconds))
  (if ({V}GetPowerCine)
    (CallFunction|CinePowerStep :RealDelta (/ DeltaSeconds (Utilities|Time|GetGlobalTimeDilation)))
    (elif ({V}GetExplCine)
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
              (CallFunction|CineBeginOpening)))))))
  (if (and ({V}GetRagdollOn) (not ({V}GetRagdollDone)))
    ({V}SetRagdollT (+ ({V}GetRagdollT) DeltaSeconds))
    (if (> ({V}GetRagdollT) ({V}GetRagdollSettle))
      ({V}SetRagdollDone true)
      (CallFunction|CineDriverRagdollStop)))
  (CallFunction|CinePlayerTurnStep)
  (CallFunction|CineFireTimeStep)
  (CallFunction|CineBeaconStep :DeltaSeconds DeltaSeconds))
'''
G['EventGraph']=f'''
(event EventBeginPlay
  (CallFunction|CineOverlayMake)
  (CallFunction|CineFindPlayer)
  (if ({V}GetCinePlayOpening)
    (CallFunction|CineSceneBeforeCrash)
    (else
      (CallFunction|CineShowWreck)
      (CallFunction|CineShowBody)
      ({V}SetCineDone true)
      ({V}SetObjectiveState 1))))

(event Collision|EventActorBeginOverlap (OtherActor))

(event EventTick (DeltaSeconds)
  (CallFunction|CineOverlayStep :DeltaSeconds (/ DeltaSeconds (Utilities|Time|GetGlobalTimeDilation)))
  (Utilities|IsValid ({V}GetPlayerRef)
    (:"Is Valid"
      (CallFunction|CineDirectorStep :DeltaSeconds DeltaSeconds))
    (:"Is Not Valid"
      (CallFunction|CineFindPlayer))))
'''

# ---------------------------------------------------------------- round 8: beats 2 and 3
# These REPLACE the entries of the same name above (later assignment wins).
# "The quest markers moving to the goons and boss don't go away when the player approaches"
# (2026-11-15): from objective 3 on, the marker hides itself within 1200 cm. Objective 5 no longer
# switches itself off 520 cm short of the boss; it lasts until he hands over Splice, which gets the
# same held-time moment as Freeze Frame (PowerKind 1), and objective 6 then points at Marker_Win
# (14400, 0, 0) so the walk after the boss has somewhere to go. New state variable: PowerKind (int).
VARS.append(('PowerKind', 'int'))
G['CineBeaconStep']=f'''
(fn CineBeaconStep (DeltaSeconds)
  ({V}SetObjectiveBob (+ ({V}GetObjectiveBob) DeltaSeconds))
  (if (not ({V}GetBeaconLit))
    (CallFunction|CineBeaconDress))
  (if (> ({V}GetObjectiveState) 0)
    (bind spot (CallFunction|CineObjectiveSpot))
    (bind bob ({V}GetObjectiveBob))
    (bind bk ({V}GetObjectiveBeacon))
    (bind k (+ 1.0 (* 0.14 (Math|Trig|Sin(Radians) (* bob 5.0)))))
    (bind near (and (>= ({V}GetObjectiveState) 3)
      (< (Math|Vector|VectorLengthXY (- spot (Transformation|GetActorLocation :self ({V}GetPlayerRef)))) 1200.0)))
    (Transformation|SetActorLocation :self bk
      :NewLocation (Math|Vector|MakeVector :X (.x spot) :Y (.y spot)
        :Z (+ (+ (.z spot) ({V}GetObjectiveHeight)) (* 16.0 (Math|Trig|Sin(Radians) (* bob 2.4)))))
      :bSweep false :bTeleport true)
    (Transformation|SetActorScale3D :self bk
      :NewScale3D (Math|Vector|MakeVector :X (* 0.5 k) :Y (* 0.5 k) :Z (* 0.85 k)))
    (CallFunction|CineHideActor :Target bk :Hide near)
    (else
      (CallFunction|CineHideActor :Target ({V}GetObjectiveBeacon) :Hide true))))
'''
G['CinePowerBegin']=f'''
(fn CinePowerBegin ()
  (bind pl ({V}GetPlayerRef))
  ({V}SetPowerCine true)
  ({V}SetPowerT 0.0)
  ({V}SetFlashAlpha 0.9)
  ({V}SetObjectiveState 0)
  ({V}SetBarTarget 1.0)
  (Class|BPPlayer|SetInputLocked :self pl :InputLocked true)
  (Class|BPPlayer|SetMoveLocked :self pl :MoveLocked true)
  (Utilities|Time|SetGlobalTimeDilation :TimeDilation 0.06)
  (if (== ({V}GetPowerKind) 1)
    (Audio|PlaySound2D :Sound "/Game/Game/Audio/SFX_PowerSplice.SFX_PowerSplice")
    (CallFunction|CineSay :Msg "SPLICE" :Secs 3.0)
    (else
      (Audio|PlaySound2D :Sound "/Game/Game/Audio/SFX_PowerFreezeFrame.SFX_PowerFreezeFrame")
      (CallFunction|CineSay :Msg "FREEZE FRAME" :Secs 3.0)))
  (CallFunction|CineFlashPush))
'''
G['CinePowerEnd']=f'''
(fn CinePowerEnd ()
  (bind pl ({V}GetPlayerRef))
  ({V}SetPowerCine false)
  ({V}SetFlashAlpha 0.0)
  (Utilities|Time|SetGlobalTimeDilation :TimeDilation 1.0)
  (CallFunction|CinePlayerFov :Fov 90.0)
  (CallFunction|CineFlashPush)
  ({V}SetBarTarget 0.0)
  (Class|BPPlayer|SetInputLocked :self pl :InputLocked false)
  (Class|BPPlayer|SetMoveLocked :self pl :MoveLocked false)
  ({V}SetObjectiveState (select (== ({V}GetPowerKind) 1) 6 2)))
'''
G['CineObjGoons']=f'''
(fn CineObjGoons ()
  (bind n (CallFunction|CineGoonsLeft))
  (if (> n 0)
    ({V}SetGoonsSeen true)
    (else
      (if ({V}GetGoonsSeen)
        ({V}SetObjectiveState 5)
        (CallFunction|CineSay :Msg "One more. The man with the cleaver." :Secs 4.0)))))
'''
# State 5 used to switch itself off at x > 7600, 520 cm short of the boss, and nothing replaced it.
# It now lasts until the boss hands over Splice, which gets the same held-time moment as Freeze
# Frame; the marker hides itself by distance (CineBeaconStep), and state 6 points at Marker_Win.
G['CineObjBoss']=f'''
(fn CineObjBoss ()
  (if (Class|BPPlayer|GetHasSplice :self ({V}GetPlayerRef))
    ({V}SetPowerKind 1)
    (CallFunction|CinePowerBegin)))
'''
G['CineObjectiveSpot']=f'''
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
            (elif (== s 6)
              (return (Math|Vector|MakeVector :X 14400.0 :Y 0.0 :Z 0.0))
              (else
                (return (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z 0.0))))))))))
'''

# ---------------------------------------------------------------- round 9: the boss speaks, the demo ends
# Later assignments replace the entries of the same name above.
#  * CineWallEnsure / CineWallRetry: the cafe wall's break is applied on one frame and sometimes does
#    not take (measured: 1 run in 3 left the panel standing, bounds x-extent 35 cm five seconds
#    later). Every 0.35 s, up to 6 times, the break is applied again while the x-extent is under 60.
#  * CineBoss*: entering the plaza (x > 6950) cuts to a low camera pushing in on the boss for three
#    lines, holds him with a rolling 0.4 s stun, turns the player to face him, and returns on the
#    player's live camera exactly as the explosion pan does.
#  * CineOutro*: after the Splice moment, one line, fade to black, the ending card, fade, OpenLevel.
# New director state: BossRef (BP_EnemyBase object), BossCine, BossT, BossIntroDone, BossSaid,
# OutroCine, OutroT, OutroStage, FadeAlpha, WallTries, WallNextT. Overlay: a black full-screen
# Border "FadeBox" at ZOrder 1 (under the caption, over the bars) and CineFadeSet(Alpha).
VARS += [('BossCine', 'bool'), ('BossT', 'float'), ('BossIntroDone', 'bool'), ('BossSaid', 'int'),
         ('OutroCine', 'bool'), ('OutroT', 'float'), ('OutroStage', 'int'), ('FadeAlpha', 'float'),
         ('WallTries', 'int'), ('WallNextT', 'float')]
G['CineWallRetry']=f'''
(fn CineWallRetry ()
  (bind gc ({V}GetCineWallGC))
  (Utilities|IsValid gc
    (:"Is Valid"
      (bind (org ext) (Collision|GetActorBounds :self gc :bOnlyCollidingComponents false))
      (if (< (.x ext) 60.0)
        ({V}SetWallTries (+ ({V}GetWallTries) 1))
        (CallFunction|CineBreakWall)
        (else
          ({V}SetWallTries 99))))))
'''
G['CineWallEnsure']=f'''
(fn CineWallEnsure (DeltaSeconds)
  (if (and ({V}GetCineWallDone) (< ({V}GetWallTries) 6))
    ({V}SetWallNextT (+ ({V}GetWallNextT) DeltaSeconds))
    (if (> ({V}GetWallNextT) 0.35)
      ({V}SetWallNextT 0.0)
      (CallFunction|CineWallRetry))))
'''
G['CineBossFind']=f'''
(fn CineBossFind ()
  (bind all (Actor|GetAllActorsOfClass :ActorClass "/Game/Game/Blueprints/BP_BossFreeze.BP_BossFreeze_C"))
  (for b all
    ({V}SetBossRef b)))
'''
G['CineBossHold']=f'''
(fn CineBossHold ()
  (bind b ({V}GetBossRef))
  (Utilities|IsValid b
    (:"Is Valid"
      (Class|BPEnemyBase|SetEnemyStunLeft :self b :EnemyStunLeft 0.4))))
'''
G['CineBossFacePlayer']=f'''
(fn CineBossFacePlayer ()
  (bind pl ({V}GetPlayerRef))
  (bind to (- ({V}GetObjBossLoc) (Transformation|GetActorLocation :self pl)))
  (bind yaw (Math|Trig|Atan2(Degrees) (.y to) (.x to)))
  (Components|Movement|StopMovementImmediately :self (Actor|GetComponentbyClass :self pl :ComponentClass "/Script/Engine.CharacterMovementComponent"))
  (Transformation|SetActorRotation :self pl
    :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw yaw) :bTeleportPhysics true)
  (Pawn|SetControlRotation :self (Pawn|GetController :self pl)
    :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw yaw)))
'''
# 0 - 7.7 s: a low camera pushes in on him while he speaks. 7.7 - 8.7 s: it travels to the player's
# own camera (live pose, lens 55 -> 90), so control comes back with nothing moving on screen.
G['CineBossCamStep']=f'''
(fn CineBossCamStep ()
  (bind t ({V}GetBossT))
  (bind cam ({V}GetExplCam))
  (bind look (+ ({V}GetObjBossLoc) (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z 185.0)))
  (bind a0 (select (> (/ t 7.7) 1.0) 1.0 (/ t 7.7)))
  (bind a (* (* a0 a0) (- 3.0 (* 2.0 a0))))
  (bind pos (Math|Vector|Lerp(Vector)
    :A (+ ({V}GetObjBossLoc) (Math|Vector|MakeVector :X -360.0 :Y -170.0 :Z 105.0))
    :B (+ ({V}GetObjBossLoc) (Math|Vector|MakeVector :X -210.0 :Y -70.0 :Z 150.0)) :Alpha a))
  (bind rot (Math|Rotator|FindLookatRotation :Start pos :Target look))
  (Utilities|IsValid cam
    (:"Is Valid"
      (if (< t 7.7)
        (Transformation|SetActorLocationAndRotation :self cam :NewLocation pos :NewRotation rot
          :bSweep false :bTeleport true)
        (else
          (bind c0 (select (> (- t 7.7) 1.0) 1.0 (- t 7.7)))
          (bind c (* (* c0 c0) (- 3.0 (* 2.0 c0))))
          (bind pcam (Actor|GetComponentbyClass :self ({V}GetPlayerRef) :ComponentClass {CAMC}))
          (Transformation|SetActorLocationAndRotation :self cam
            :NewLocation (Math|Vector|Lerp(Vector) :A pos :B (Transformation|GetWorldLocation :self pcam) :Alpha c)
            :NewRotation (Math|Rotator|Lerp(Rotator) :A rot :B (Transformation|GetWorldRotation :self pcam) :Alpha c :bShortestPath true)
            :bSweep false :bTeleport true)
          (CallFunction|CineExplCamFov :Fov (+ 55.0 (* 35.0 c))))))))
'''
G['CineBossBegin']=f'''
(fn CineBossBegin ()
  (bind pl ({V}GetPlayerRef))
  ({V}SetBossCine true)
  ({V}SetBossIntroDone true)
  ({V}SetBossT 0.0)
  ({V}SetBossSaid 0)
  ({V}SetObjectiveState 0)
  ({V}SetBarTarget 1.0)
  (Class|BPPlayer|SetInputLocked :self pl :InputLocked true)
  (Class|BPPlayer|SetMoveLocked :self pl :MoveLocked true)
  (CallFunction|CineBossFind)
  (CallFunction|CineBossHold)
  (CallFunction|CineBossFacePlayer)
  (CallFunction|CineExplCamFov :Fov 55.0)
  (CallFunction|CineBossCamStep)
  (bind cam ({V}GetExplCam))
  (Utilities|IsValid cam
    (:"Is Valid"
      (Game|Player|SetViewTargetwithBlend :self (Game|GetPlayerController :PlayerIndex 0)
        :NewViewTarget cam :BlendTime 0.5 :BlendFunc "VTBlend_EaseInOut" :BlendExp 2.0
        :bLockOutgoing false))))
'''
G['CineBossStep']=f'''
(fn CineBossStep (DeltaSeconds)
  ({V}SetBossT (+ ({V}GetBossT) DeltaSeconds))
  (bind t ({V}GetBossT))
  (CallFunction|CineBossHold)
  (CallFunction|CineBossCamStep)
  (if (and (> t 0.5) (< ({V}GetBossSaid) 1))
    ({V}SetBossSaid 1)
    (CallFunction|CineSay :Msg "So you are the one who stopped the clock." :Secs 2.3))
  (if (and (> t 2.9) (< ({V}GetBossSaid) 2))
    ({V}SetBossSaid 2)
    (CallFunction|CineSay :Msg "That power was never meant for you." :Secs 2.3))
  (if (and (> t 5.3) (< ({V}GetBossSaid) 3))
    ({V}SetBossSaid 3)
    (CallFunction|CineSay :Msg "Let me show you how a scene gets cut." :Secs 2.3))
  (if (>= t 8.7)
    (CallFunction|CineBossEnd)))
'''
G['CineBossEnd']=f'''
(fn CineBossEnd ()
  (bind pl ({V}GetPlayerRef))
  ({V}SetBossCine false)
  ({V}SetBarTarget 0.0)
  (Class|BPPlayer|SetInputLocked :self pl :InputLocked false)
  (Class|BPPlayer|SetMoveLocked :self pl :MoveLocked false)
  (Game|Player|SetViewTargetwithBlend :self (Game|GetPlayerController :PlayerIndex 0)
    :NewViewTarget pl :BlendTime 0.2 :BlendFunc "VTBlend_EaseInOut" :BlendExp 2.0 :bLockOutgoing false)
  ({V}SetObjectiveState 5))
'''
# Objective 4 also moves on if the player simply walks into the plaza without clearing the street,
# so the boss intro, the Splice moment and the ending cannot be skipped by running past the goons.
G['CineObjGoons']=f'''
(fn CineObjGoons ()
  (bind n (CallFunction|CineGoonsLeft))
  (if (> (.x (Transformation|GetActorLocation :self ({V}GetPlayerRef))) 6950.0)
    ({V}SetObjectiveState 5)
    (elif (> n 0)
      ({V}SetGoonsSeen true)
      (else
        (if ({V}GetGoonsSeen)
          ({V}SetObjectiveState 5)
          (CallFunction|CineSay :Msg "One more. The man with the cleaver." :Secs 4.0))))))
'''
G['CineObjBoss']=f'''
(fn CineObjBoss ()
  (if (Class|BPPlayer|GetHasSplice :self ({V}GetPlayerRef))
    ({V}SetPowerKind 1)
    (CallFunction|CinePowerBegin)
    (elif (and (not ({V}GetBossIntroDone))
               (> (.x (Transformation|GetActorLocation :self ({V}GetPlayerRef))) 6950.0))
      (CallFunction|CineBossBegin))))
'''
G['CinePowerEnd']=f'''
(fn CinePowerEnd ()
  (bind pl ({V}GetPlayerRef))
  ({V}SetPowerCine false)
  ({V}SetFlashAlpha 0.0)
  (Utilities|Time|SetGlobalTimeDilation :TimeDilation 1.0)
  (CallFunction|CinePlayerFov :Fov 90.0)
  (CallFunction|CineFlashPush)
  (if (== ({V}GetPowerKind) 1)
    (CallFunction|CineOutroBegin)
    (else
      ({V}SetBarTarget 0.0)
      (Class|BPPlayer|SetInputLocked :self pl :InputLocked false)
      (Class|BPPlayer|SetMoveLocked :self pl :MoveLocked false)
      ({V}SetObjectiveState 2))))
'''
# The demo ends here: one line about where the story goes next, a fade to black, the team's own
# ending card, and back to the title screen without anyone having to press anything.
G['CineOutroBegin']=f'''
(fn CineOutroBegin ()
  ({V}SetOutroCine true)
  ({V}SetOutroT 0.0)
  ({V}SetOutroStage 0)
  ({V}SetObjectiveState 0)
  ({V}SetBarTarget 1.0)
  (CallFunction|CineSay :Msg "Whoever sent them is waiting in the ruins to the east." :Secs 4.6))
'''
G['CineFadePush']=f'''
(fn CineFadePush ()
  (Utilities|IsValid ({V}GetOverlayRef)
    (:"Is Valid"
      (Class|WBPCineOverlay|CineFadeSet :self ({V}GetOverlayRef) :Alpha ({V}GetFadeAlpha)))))
'''
G['CineOutroWin']=f'''
(fn CineOutroWin ()
  ({V}SetBarAlpha 0.0)
  ({V}SetBarTarget 0.0)
  (Class|BPPlayer|PlayerReachWin :self ({V}GetPlayerRef)))
'''
G['CineOutroStep']=f'''
(fn CineOutroStep (DeltaSeconds)
  ({V}SetOutroT (+ ({V}GetOutroT) DeltaSeconds))
  (bind t ({V}GetOutroT))
  (bind fin (select (< t 4.0) 0.0 (select (> t 5.4) 1.0 (/ (- t 4.0) 1.4))))
  (bind fout (select (< t 6.0) 1.0 (select (> t 7.0) 0.0 (- 7.0 t))))
  (bind fend (select (< t 13.0) 0.0 (select (> t 14.0) 1.0 (- t 13.0))))
  ({V}SetFadeAlpha (select (< t 5.7) fin (select (< t 13.0) fout fend)))
  (CallFunction|CineFadePush)
  (if (and (> t 5.7) (< ({V}GetOutroStage) 1))
    ({V}SetOutroStage 1)
    (CallFunction|CineOutroWin))
  (if (and (> t 14.3) (< ({V}GetOutroStage) 2))
    ({V}SetOutroStage 2)
    (Game|OpenLevel(byName) (Utilities|String|StringToName (Game|GetCurrentLevelName true)))))
'''
G['CineDirectorStep']=f'''
(fn CineDirectorStep (DeltaSeconds)
  (bind nt (+ ({V}GetCineTime) DeltaSeconds))
  (if ({V}GetPowerCine)
    (CallFunction|CinePowerStep :RealDelta (/ DeltaSeconds (Utilities|Time|GetGlobalTimeDilation)))
    (elif ({V}GetOutroCine)
      (CallFunction|CineOutroStep :DeltaSeconds DeltaSeconds)
      (elif ({V}GetBossCine)
        (CallFunction|CineBossStep :DeltaSeconds DeltaSeconds)
        (elif ({V}GetExplCine)
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
                  (CallFunction|CineBeginOpening)))))))))
  (if (and ({V}GetRagdollOn) (not ({V}GetRagdollDone)))
    ({V}SetRagdollT (+ ({V}GetRagdollT) DeltaSeconds))
    (if (> ({V}GetRagdollT) ({V}GetRagdollSettle))
      ({V}SetRagdollDone true)
      (CallFunction|CineDriverRagdollStop)))
  (CallFunction|CinePlayerTurnStep)
  (CallFunction|CineFireTimeStep)
  (CallFunction|CineWallEnsure :DeltaSeconds DeltaSeconds)
  (CallFunction|CineBeaconStep :DeltaSeconds DeltaSeconds))
'''

GW = {}   # overlay widget graphs
GW['CineFlashSet']=f'''
(fn CineFlashSet (Alpha)
  (Widget|SetRenderOpacity ({WV}GetFlashBox) Alpha))
'''
GW['CineCaptionSet']=f'''
(fn CineCaptionSet (Msg)
  (Widget|SetText(Text) ({WV}GetCapText) Msg)
  ({V}SetCapPulseT 0.0)
  ({V}SetCapOn true)
  (Widget|SetVisibility ({WV}GetCapBox) "HitTestInvisible"))
'''
GW['CineCaptionOff']=f'''
(fn CineCaptionOff ()
  ({V}SetCapOn false)
  (Widget|SetVisibility ({WV}GetCapBox) "Collapsed"))
'''
GW['CineCaptionPulseStep']=f'''
(fn CineCaptionPulseStep (DeltaSeconds)
  (if ({V}GetCapOn)
    ({V}SetCapPulseT (+ ({V}GetCapPulseT) DeltaSeconds))
    (bind t ({V}GetCapPulseT))
    (bind pop (select (< t 0.3) (* 0.28 (- 1.0 (/ t 0.3))) 0.0))
    (bind wave (* 0.5 (+ 1.0 (Math|Trig|Sin(Radians) (* t 5.0)))))
    (bind s (+ (+ 1.0 pop) (* 0.035 wave)))
    (Widget|Transform|SetRenderScale ({WV}GetCapBox) (Math|Vector2D|MakeVector2D s s))
    (Appearance|SetBrushColor ({WV}GetCapBox)
      (Math|Color|MakeColor :R 0.0 :G (* 0.16 wave) :B (* 0.24 wave) :A 0.72))))
'''
GW['EventGraph']='''
(event UserInterface|EventPreConstruct (IsDesignTime))

(event UserInterface|EventConstruct)

(event UserInterface|EventTick (MyGeometry InDeltaTime)
  (CallFunction|CineCaptionPulseStep :DeltaSeconds InDeltaTime))
'''

GW['CineFadeSet'] = f'''
(fn CineFadeSet (Alpha)
  (Widget|SetRenderOpacity ({WV}GetFadeBox) Alpha))
'''

if __name__ == '__main__':
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, 'JumpCut', 'Saved', 'b1u_graphs.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    graphs = {'%s:%s' % (D, k): v.strip() + '\n' for k, v in G.items()}
    graphs.update({'%s:%s' % (W, k): v.strip() + '\n' for k, v in GW.items()})
    with open(out, 'w') as fh:
        json.dump({'vars': VARS, 'fns': FNS, 'wvars': WVARS, 'wfns': WFNS, 'graphs': graphs}, fh, indent=1)
    print('wrote %s (%d graphs)' % (out, len(graphs)))
