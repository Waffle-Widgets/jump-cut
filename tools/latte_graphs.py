"""BP_LatteGame's graphs as text, so they can be rebuilt.  `python tools/latte_graphs.py` writes
JumpCut/Saved/latte_graphs.json, which the MCP's write_graph_dsl reads (one entry per graph).

Controls: mouse moves the pitcher; LEFT button = pour from high (sinks, fills, cuts); RIGHT = pour close (lays white foam).
The cup must be filled to finish. What counts as each pattern is in LatteJudge.
"""
import json, os

V = 'Variables|Default|'
A = '"/Game/Game/Materials/Latte/RT_LatteA.RT_LatteA"'
B = '"/Game/Game/Materials/Latte/RT_LatteB.RT_LatteB"'
G = {}

G['EventGraph'] = f'''
(event EventBeginPlay
  (Rendering|ClearRenderTarget2D :TextureRenderTarget {A})
  (Rendering|ClearRenderTarget2D :TextureRenderTarget {B})
  (Rendering|Material|SetMaterial :self ({V}GetSurface) :ElementIndex 0 :Material "/Game/Game/Materials/Latte/MI_LatteSurface_A.MI_LatteSurface_A")
  (Rendering|Material|SetMaterial :self ({V}GetCup) :ElementIndex 0 :Material "/Game/Game/Materials/Latte/M_LatteCup.M_LatteCup")
  (Rendering|Material|SetMaterial :self ({V}GetSaucer) :ElementIndex 0 :Material "/Game/Game/Materials/Latte/M_LatteCup.M_LatteCup")
  (Rendering|Material|SetMaterial :self ({V}GetPitcher) :ElementIndex 0 :Material "/Game/Game/Materials/Latte/M_LatteSteel.M_LatteSteel")
  (Rendering|Material|SetMaterial :self ({V}GetStream) :ElementIndex 0 :Material "/Game/Game/Materials/Latte/M_LatteMilk.M_LatteMilk")
  (Rendering|Material|SetMaterial :self ({V}GetFillBar) :ElementIndex 0 :Material "/Game/Game/Materials/Latte/M_LatteBar.M_LatteBar")
  (Rendering|Material|SetMaterial :self ({V}GetFillMark) :ElementIndex 0 :Material "/Game/Game/Materials/Latte/M_LatteMilk.M_LatteMilk")
  (CallFunction|LatteShow :Show false)
  (Rendering|SetVisibility :self ({V}GetWorldText) :bNewVisibility false)
  (bind startPlayer (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter 0))
    (:then
      (Class|BPPlayer|PlayerSetInputLocked :self startPlayer :Locked true))
    (:CastFailed)))

(event EventTick (DeltaSeconds)
  (if ({V}GetLatteActive)
    (CallFunction|LatteStep :Dt DeltaSeconds)
    (elif (and (>= ({V}GetShift) 1) (!= ({V}GetShift) 5))
      (CallFunction|LatteShiftStep :Dt DeltaSeconds))))
'''

G['LatteShow'] = f'''
(fn LatteShow (Show)
  (Rendering|SetVisibility :self ({V}GetPitcher) :bNewVisibility Show)
  (Rendering|SetVisibility :self ({V}GetPrompt) :bNewVisibility Show)
  (Rendering|SetVisibility :self ({V}GetStatus) :bNewVisibility Show)
  (Rendering|SetVisibility :self ({V}GetFillBar) :bNewVisibility Show)
  (Rendering|SetVisibility :self ({V}GetFillMark) :bNewVisibility Show)
  (Rendering|SetVisibility :self ({V}GetGuide) :bNewVisibility Show)
  (Rendering|SetVisibility :self ({V}GetGuideLabel) :bNewVisibility Show)
  (Rendering|SetVisibility :self ({V}GetStream) :bNewVisibility false))
'''

REG = '(Math|Vector|MakeVector :X -540.0 :Y -240.0 :Z 185.0)'          # above City_Cafe_01_CafeRegister
WALK = f'(Pawn|Components|CharacterMovement|SetMovementMode :self (Class|Character|GetCharacterMovement :self ({V}GetLattePlayer)) :NewMovementMode "MOVE_Walking")'


def say(text):
    return f'(Rendering|Components|TextRender|SetText :self ({V}GetWorldText) :Value (Utilities|Text|MakeLiteralText :Value "{text}"))'


# THE SHIFT.  Shift: 0 title, 1 an order is in (walk to the cup), 2 pouring, 3 served (the customer takes it),
# 4 noon (walk to the register), 5 clocked out - which is the moment the player's input unlocks, and
# BP_OpeningDirector starts the opening on exactly that.  Through 1-4 the player's own input stays LOCKED (so no
# attacks, and the director waits) and LatteWalkStep walks him and turns the camera itself.
G['LatteTryBegin'] = f'''
(fn LatteTryBegin (Player)
  ({V}SetLattePlayer Player)
  (if ({V}GetLatteDone)
    (Class|BPPlayer|PlayerSetInputLocked :self Player :Locked false)
    (else
      (Class|BPPlayer|PlayerSetInputLocked :self Player :Locked true)
      ({V}SetShift 1)
      ({V}SetTextLoc (+ (Transformation|GetActorLocation :self self) (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z 48.0)))
      (Rendering|SetVisibility :self ({V}GetWorldText) :bNewVisibility true)
      {say("ORDER IN: ONE LATTE<br>Go behind the counter<br>Press E at the cup")}
      {WALK})))
'''

G['LatteStartPour'] = f'''
(fn LatteStartPour ()
  ({V}SetShift 2)
  ({V}SetLatteActive true)
  (Rendering|SetVisibility :self ({V}GetWorldText) :bNewVisibility false)
  (Game|Player|SetViewTargetwithBlend :self (Game|GetPlayerController 0) :NewViewTarget self :BlendTime 0.6)
  (Input|SetInputModeGameAndUI :PlayerController (Game|GetPlayerController 0) :bHideCursorDuringCapture false)
  (Class|PlayerController|SetShowMouseCursor :self (Game|GetPlayerController 0) :bShowMouseCursor true)
  (CallFunction|LatteShow :Show true)
  (CallFunction|LatteReset))
'''

G['LatteClockOut'] = f'''
(fn LatteClockOut ()
  ({V}SetShift 5)
  ({V}SetLatteDone true)
  (Rendering|SetVisibility :self ({V}GetWorldText) :bNewVisibility false)
  (Class|BPPlayer|PlayerSetInputLocked :self ({V}GetLattePlayer) :Locked false))
'''

G['LatteWalkStep'] = f'''
(fn LatteWalkStep ()
  (bind pawn ({V}GetLattePlayer))
  (bind pc (Game|GetPlayerController 0))
  (bind (dx dy) (Game|Player|GetInputMouseDelta :self pc))
  (Pawn|Input|AddControllerYawInput :self pawn :Val dx)
  (Pawn|Input|AddControllerPitchInput :self pawn :Val (* dy -1.0))
  (bind rot (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw (.yaw (Pawn|GetControlRotation :self pc))))
  (bind fwd (- (select (Game|Player|IsInputKeyDown :self pc :Key "W") 1.0 0.0) (select (Game|Player|IsInputKeyDown :self pc :Key "S") 1.0 0.0)))
  (bind side (- (select (Game|Player|IsInputKeyDown :self pc :Key "D") 1.0 0.0) (select (Game|Player|IsInputKeyDown :self pc :Key "A") 1.0 0.0)))
  (Pawn|Input|AddMovementInput :self pawn :WorldDirection (Math|Vector|GetForwardVector :InRot rot) :ScaleValue fwd)
  (Pawn|Input|AddMovementInput :self pawn :WorldDirection (Math|Vector|GetRightVector :InRot rot) :ScaleValue side)
  (bind cm (Game|GetPlayerCameraManager 0))
  (bind cam (Camera|GetCameraLocation :self cm))
  (bind crot (Camera|GetCameraRotation :self cm))
  (bind tl (+ cam (+ (* (Math|Vector|GetForwardVector :InRot crot) 230.0) (* (Math|Vector|GetUpVector :InRot crot) -62.0))))
  (Transformation|SetWorldLocation :self ({V}GetWorldText) :NewLocation tl)
  (Transformation|SetWorldRotation :self ({V}GetWorldText) :NewRotation (Math|Rotator|FindLookatRotation :Start tl :Target cam)))
'''

G['LatteShiftStep'] = f'''
(fn LatteShiftStep (Dt)
  (CallFunction|LatteWalkStep)
  (bind pc (Game|GetPlayerController 0))
  (bind pl (Transformation|GetActorLocation :self ({V}GetLattePlayer)))
  (bind me (Transformation|GetActorLocation :self self))
  (bind dcup (+ (* (- (.x pl) (.x me)) (- (.x pl) (.x me))) (* (- (.y pl) (.y me)) (- (.y pl) (.y me)))))
  (bind dreg (+ (* (- (.x pl) -540.0) (- (.x pl) -540.0)) (* (- (.y pl) -240.0) (- (.y pl) -240.0))))
  (bind edown (Game|Player|IsInputKeyDown :self pc :Key "E"))
  (if (== ({V}GetShift) 1)
    (if (and edown (and (not ({V}GetEWas)) (< dcup 32400.0)))
      (CallFunction|LatteStartPour))
    (elif (== ({V}GetShift) 3)
      (if (and edown (and (not ({V}GetEWas)) (< dcup 32400.0)))
        ({V}SetShift 6)
        ({V}SetShiftT 0.0)
        {say("ORDER UP!<br>The customer takes the latte")})
      (elif (== ({V}GetShift) 6)
      ({V}SetShiftT (+ ({V}GetShiftT) Dt))
      (if (> ({V}GetShiftT) 1.8)
        (Rendering|SetVisibility :self ({V}GetCup) :bNewVisibility false)
        (Rendering|SetVisibility :self ({V}GetSaucer) :bNewVisibility false)
        (Rendering|SetVisibility :self ({V}GetSurface) :bNewVisibility false))
      (if (> ({V}GetShiftT) 3.4)
        ({V}SetShift 4)
        ({V}SetTextLoc {REG})
        {say("12:00  YOUR SHIFT IS OVER<br>Press E at the register to clock out")})
      (elif (== ({V}GetShift) 4)
        (if (and edown (and (not ({V}GetEWas)) (< dreg 32400.0)))
          (CallFunction|LatteClockOut))))))
  ({V}SetEWas edown))
'''

P1 = '1. Hold LEFT mouse: pour from high, anywhere, until the bar reaches the mark'
G['LatteReset'] = f'''
(fn LatteReset ()
  (Rendering|ClearRenderTarget2D :TextureRenderTarget {A})
  (Rendering|ClearRenderTarget2D :TextureRenderTarget {B})
  (Rendering|Material|SetMaterial :self ({V}GetSurface) :ElementIndex 0 :Material "/Game/Game/Materials/Latte/MI_LatteSurface_A.MI_LatteSurface_A")
  ({V}SetFlipA true)
  ({V}SetFill 0.3)
  ({V}SetPitX 0.0)
  ({V}SetPitY 0.0)
  ({V}SetPrevX 0.0)
  ({V}SetPrevY 0.0)
  ({V}SetPitH 8.0)
  ({V}SetLowTime 0.0)
  ({V}SetLowSince 9.0)
  ({V}SetCutDist 0.0)
  ({V}SetWiggles 0)
  ({V}SetBlobs 0)
  ({V}SetLastSign 0.0)
  ({V}SetLowGap 9.0)
  ({V}SetEnding false)
  ({V}SetEndTimer 0.0)
  (Rendering|Components|TextRender|SetText :self ({V}GetStatus) :Value (Utilities|Text|MakeLiteralText :Value " "))
  (if (not ({V}GetKeepPattern))
    ({V}SetPattern (Math|Random|RandomIntegerinRange 0 2)))
  ({V}SetKeepPattern false)
  (if (== ({V}GetPattern) 0)
    (Rendering|Material|SetMaterial :self ({V}GetGuide) :ElementIndex 0 :Material "/Game/Game/Materials/Latte/MI_LatteGuide_0.MI_LatteGuide_0")
    (elif (== ({V}GetPattern) 1)
      (Rendering|Material|SetMaterial :self ({V}GetGuide) :ElementIndex 0 :Material "/Game/Game/Materials/Latte/MI_LatteGuide_1.MI_LatteGuide_1")
      (else
        (Rendering|Material|SetMaterial :self ({V}GetGuide) :ElementIndex 0 :Material "/Game/Game/Materials/Latte/MI_LatteGuide_2.MI_LatteGuide_2"))))
  (if (== ({V}GetPattern) 0)
    (Rendering|Components|TextRender|SetText :self ({V}GetPrompt) :Value (Utilities|Text|MakeLiteralText :Value "LATTE ART: HEART<br>{P1}<br>2. Hold RIGHT mouse inside the ring until the ring goes<br>3. Let go. Hold LEFT and follow the line down through the circle. Let go<br>R: start over"))
    (elif (== ({V}GetPattern) 1)
      (Rendering|Components|TextRender|SetText :self ({V}GetPrompt) :Value (Utilities|Text|MakeLiteralText :Value "LATTE ART: ROSETTA<br>{P1}<br>2. Hold RIGHT mouse: follow the wavy line up, then rest in the small ring<br>3. Let go. Hold LEFT and follow the straight line back down. Let go<br>R: start over"))
      (else
        (Rendering|Components|TextRender|SetText :self ({V}GetPrompt) :Value (Utilities|Text|MakeLiteralText :Value "LATTE ART: TULIP<br>{P1}<br>2. Hold RIGHT mouse in each ring, bottom to top. Let go between rings<br>3. Hold LEFT and follow the line down through the stack. Let go<br>R: start over"))))))
'''

G['LatteStep'] = f'''
(fn LatteStep (Dt)
  (bind pc (Game|GetPlayerController 0))
  (if (and (Game|Player|IsInputKeyDown :self pc :Key "R") (not ({V}GetRWas)))
    ({V}SetKeepPattern true)
    (CallFunction|LatteReset))
  (if ({V}GetEnding)
    ({V}SetEndTimer (- ({V}GetEndTimer) Dt))
    (if ({V}GetEndWin)
      (if (and (Game|Player|IsInputKeyDown :self pc :Key "E") (not ({V}GetEWas)))
        (CallFunction|LatteFinish))
      (elif (<= ({V}GetEndTimer) 0.0)
        (CallFunction|LatteReset)))
    (else
      ({V}SetLowGap (+ ({V}GetLowGap) Dt))
      ({V}SetSimT (+ ({V}GetSimT) Dt))
      ({V}SetPourAmt (Math|Interpolation|FInterpTo :Current ({V}GetPourAmt) :Target (select (or (Game|Player|IsInputKeyDown :self pc :Key "RightMouseButton") (Game|Player|IsInputKeyDown :self pc :Key "LeftMouseButton")) 1.0 0.0) :DeltaTime Dt :InterpSpeed 6.0))
      (Rendering|Material|SetVectorParameterValue :Collection "/Game/Game/Materials/Latte/MPC_Latte.MPC_Latte" :ParameterName "Fx" :ParameterValue (Utilities|Struct|MakeLinearColor :R (/ ({V}GetPitX) 12.0) :G (/ ({V}GetPitY) 12.0) :B ({V}GetPourAmt) :A ({V}GetSimT)))
      (bind (ml md mok) (Game|Player|ConvertMouseLocationToWorldSpace :self pc))
      (bind me (Transformation|GetActorLocation :self self))
      (bind rel (- (+ ml (* md (/ (- (.z me) (.z ml)) (select (< (.z md) -0.05) (.z md) -0.05)))) me))
      (bind tx (Math|Vector|DotProduct rel (Transformation|GetActorForwardVector :self self)))
      (bind ty (Math|Vector|DotProduct rel (Transformation|GetActorRightVector :self self)))
      ({V}SetPrevX ({V}GetPitX))
      ({V}SetPrevY ({V}GetPitY))
      (if mok
        ({V}SetPitX (Math|Interpolation|FInterpTo :Current ({V}GetPitX) :Target (select (< tx -5.2) -5.2 (select (> tx 5.2) 5.2 tx)) :DeltaTime Dt :InterpSpeed 20.0))
        ({V}SetPitY (Math|Interpolation|FInterpTo :Current ({V}GetPitY) :Target (select (< ty -5.2) -5.2 (select (> ty 5.2) 5.2 ty)) :DeltaTime Dt :InterpSpeed 20.0)))
      (bind low (Game|Player|IsInputKeyDown :self pc :Key "RightMouseButton"))
      (bind high (and (Game|Player|IsInputKeyDown :self pc :Key "LeftMouseButton") (not low)))
      ({V}SetPitH (Math|Interpolation|FInterpTo :Current ({V}GetPitH) :Target (select low 2.6 8.0) :DeltaTime Dt :InterpSpeed 10.0))
      (if (or low high)
        (CallFunction|LattePour :Dt Dt :Low low :Dx (* (- ({V}GetPitY) ({V}GetPrevY)) 12.0)))
      (Transformation|SetRelativeLocation :self ({V}GetPitcher) :NewLocation (Math|Vector|MakeVector :X ({V}GetPitX) :Y ({V}GetPitY) :Z (+ ({V}GetPitH) 0.2)))
      (Transformation|SetRelativeLocation :self ({V}GetStream) :NewLocation (Math|Vector|MakeVector :X ({V}GetPitX) :Y ({V}GetPitY) :Z 0.0))
      (Transformation|SetRelativeScale3D :self ({V}GetStream) :NewScale3D (Math|Vector|MakeVector :X (select low 1.25 0.6) :Y (select low 1.25 0.6) :Z ({V}GetPitH)))
      (Rendering|SetVisibility :self ({V}GetStream) :bNewVisibility (or low high))
      (Transformation|SetRelativeLocation :self ({V}GetFillBar) :NewLocation (Math|Vector|MakeVector :X (+ -6.0 (* ({V}GetFill) 6.0)) :Y -10.0 :Z 0.0))
      (Transformation|SetRelativeScale3D :self ({V}GetFillBar) :NewScale3D (Math|Vector|MakeVector :X (* ({V}GetFill) 0.12) :Y 0.008 :Z 0.004))
      (CallFunction|LatteGuideStep)
      (if (or (>= ({V}GetFill) 1.0) (and (not (or low high)) (and (>= ({V}GetCutDist) 0.4) (select (== ({V}GetPattern) 0) (>= ({V}GetLowTime) 3.8) (select (== ({V}GetPattern) 1) (>= ({V}GetWiggles) 12) (and (>= ({V}GetBlobs) 3) (> ({V}GetLowGap) 0.15)))))))
        (CallFunction|LatteJudge))))
  ({V}SetRWas (Game|Player|IsInputKeyDown :self pc :Key "R"))
  ({V}SetEWas (Game|Player|IsInputKeyDown :self pc :Key "E")))
'''

G['LattePour'] = f'''
(fn LattePour (Dt Low Dx)
  (bind su (/ ({V}GetPitX) 12.0))
  (bind sv (/ ({V}GetPitY) 12.0))
  (bind vx (/ (- ({V}GetPitX) ({V}GetPrevX)) 12.0))
  (bind vy (/ (- ({V}GetPitY) ({V}GetPrevY)) 12.0))
  (bind sp2 (+ (* vx vx) (* vy vy)))
  (bind rim (select (< ({V}GetLowSince) 0.25) 1.0 (select (> (* sp2 8000.0) 1.0) 1.0 (* sp2 8000.0))))
  (if Low
    (Rendering|Material|SetVectorParameterValue :Collection "/Game/Game/Materials/Latte/MPC_Latte.MPC_Latte" :ParameterName "Pour" :ParameterValue (Utilities|Struct|MakeLinearColor :R su :G sv :B 1.0 :A (* Dt 0.012)))
    (Rendering|Material|SetVectorParameterValue :Collection "/Game/Game/Materials/Latte/MPC_Latte.MPC_Latte" :ParameterName "Vel" :ParameterValue (Utilities|Struct|MakeLinearColor :R 0.0 :G 0.0 :B 0.0 :A 0.0))
    (Rendering|Material|SetVectorParameterValue :Collection "/Game/Game/Materials/Latte/MPC_Latte.MPC_Latte" :ParameterName "Misc" :ParameterValue (Utilities|Struct|MakeLinearColor :R 0.035 :G rim :B 0.25 :A 0.0))
    (else
      (Rendering|Material|SetVectorParameterValue :Collection "/Game/Game/Materials/Latte/MPC_Latte.MPC_Latte" :ParameterName "Pour" :ParameterValue (Utilities|Struct|MakeLinearColor :R su :G sv :B 0.0 :A 0.0))
      (Rendering|Material|SetVectorParameterValue :Collection "/Game/Game/Materials/Latte/MPC_Latte.MPC_Latte" :ParameterName "Vel" :ParameterValue (Utilities|Struct|MakeLinearColor :R vx :G vy :B 0.9 :A 0.5))
      (Rendering|Material|SetVectorParameterValue :Collection "/Game/Game/Materials/Latte/MPC_Latte.MPC_Latte" :ParameterName "Misc" :ParameterValue (Utilities|Struct|MakeLinearColor :R 0.035 :G 0.0 :B 0.25 :A 0.0))))
  (if ({V}GetFlipA)
    (Rendering|DrawMaterialtoRenderTarget :TextureRenderTarget {B} :Material "/Game/Game/Materials/Latte/MI_LatteSim_FromA.MI_LatteSim_FromA")
    (Rendering|Material|SetMaterial :self ({V}GetSurface) :ElementIndex 0 :Material "/Game/Game/Materials/Latte/MI_LatteSurface_B.MI_LatteSurface_B")
    (else
      (Rendering|DrawMaterialtoRenderTarget :TextureRenderTarget {A} :Material "/Game/Game/Materials/Latte/MI_LatteSim_FromB.MI_LatteSim_FromB")
      (Rendering|Material|SetMaterial :self ({V}GetSurface) :ElementIndex 0 :Material "/Game/Game/Materials/Latte/MI_LatteSurface_A.MI_LatteSurface_A")))
  ({V}SetFlipA (not ({V}GetFlipA)))
  ({V}SetFill (+ ({V}GetFill) (* Dt (select Low 0.04 0.045))))
  (if Low
    ({V}SetLowTime (+ ({V}GetLowTime) Dt))
    ({V}SetCutDist 0.0)
    (if (> ({V}GetLowGap) 0.15)
      ({V}SetBlobs (+ ({V}GetBlobs) 1))
      ({V}SetLowSince 0.0))
    ({V}SetLowGap 0.0)
    ({V}SetLowSince (+ ({V}GetLowSince) Dt))
    (if (> (* Dx Dx) 2.0)
      (if (< (* (select (> Dx 0.0) 1.0 -1.0) ({V}GetLastSign)) 0.0)
        ({V}SetWiggles (+ ({V}GetWiggles) 1)))
      ({V}SetLastSign (select (> Dx 0.0) 1.0 -1.0)))
    (else
      (if (and (> ({V}GetBlobs) 0) (> sp2 0.000001))
        ({V}SetCutDist (+ ({V}GetCutDist) Dt))))))
'''


# THE GUIDE ON THE CUP.  Units are the surface picture's: cm / 12, x up the screen.  Dim until the cup is full
# enough to start (Fill 0.55).  The same numbers as the pours in tools/latte_pie.py that made the GOAL pictures,
# so following the guide makes the goal.
G['LatteGuideStep'] = '''
(fn LatteGuideStep ()
  (bind m (select (>= (Variables|Default|GetFill) 0.5) 1.0 0.7))
  (bind done (select (== (Variables|Default|GetPattern) 0) (>= (Variables|Default|GetLowTime) 3.8) (select (== (Variables|Default|GetPattern) 1) (>= (Variables|Default|GetWiggles) 12) (and (>= (Variables|Default|GetBlobs) 3) (> (Variables|Default|GetLowGap) 0.15)))))
  (bind idx (select (> (Variables|Default|GetLowGap) 0.15) (Variables|Default|GetBlobs) (- (Variables|Default|GetBlobs) 1)))
  (if (== (Variables|Default|GetPattern) 0)
    (Rendering|Material|SetVectorParameterValue :Collection "/Game/Game/Materials/Latte/MPC_Latte.MPC_Latte" :ParameterName "GuideA" :ParameterValue (Utilities|Struct|MakeLinearColor :R 0.04 :G 0.0 :B 0.2 :A (select done 0.0 m)))
    (Rendering|Material|SetVectorParameterValue :Collection "/Game/Game/Materials/Latte/MPC_Latte.MPC_Latte" :ParameterName "GuideB" :ParameterValue (Utilities|Struct|MakeLinearColor :R 0.375 :G -0.375 :B 0.0 :A (select done 1.0 0.0)))
    (elif (== (Variables|Default|GetPattern) 1)
      (Rendering|Material|SetVectorParameterValue :Collection "/Game/Game/Materials/Latte/MPC_Latte.MPC_Latte" :ParameterName "GuideA" :ParameterValue (Utilities|Struct|MakeLinearColor :R 0.275 :G 0.0 :B 0.05 :A (select done 0.0 m)))
      (if done
        (Rendering|Material|SetVectorParameterValue :Collection "/Game/Game/Materials/Latte/MPC_Latte.MPC_Latte" :ParameterName "GuideB" :ParameterValue (Utilities|Struct|MakeLinearColor :R 0.38 :G -0.28 :B 0.0 :A 1.0))
        (else
          (Rendering|Material|SetVectorParameterValue :Collection "/Game/Game/Materials/Latte/MPC_Latte.MPC_Latte" :ParameterName "GuideB" :ParameterValue (Utilities|Struct|MakeLinearColor :R -0.217 :G 0.25 :B 0.167 :A m))))
      (else
        (Rendering|Material|SetVectorParameterValue :Collection "/Game/Game/Materials/Latte/MPC_Latte.MPC_Latte" :ParameterName "GuideA" :ParameterValue (Utilities|Struct|MakeLinearColor :R (select (<= idx 0) -0.125 (select (== idx 1) 0.04 0.19)) :G 0.0 :B (select (<= idx 0) 0.15 (select (== idx 1) 0.1 0.065)) :A (select done 0.0 m)))
        (Rendering|Material|SetVectorParameterValue :Collection "/Game/Game/Materials/Latte/MPC_Latte.MPC_Latte" :ParameterName "GuideB" :ParameterValue (Utilities|Struct|MakeLinearColor :R 0.38 :G -0.3 :B 0.0 :A (select done 1.0 0.0)))))))
'''

G['LatteJudge'] = f'''
(fn LatteJudge ()
  (bind made (select (== ({V}GetPattern) 0) (>= ({V}GetLowTime) 3.8) (select (== ({V}GetPattern) 1) (>= ({V}GetWiggles) 12) (>= ({V}GetBlobs) 3))))
  ({V}SetEndWin (and made (>= ({V}GetCutDist) 0.3)))
  ({V}SetEnding true)
  (Rendering|Material|SetVectorParameterValue :Collection "/Game/Game/Materials/Latte/MPC_Latte.MPC_Latte" :ParameterName "GuideA" :ParameterValue (Utilities|Struct|MakeLinearColor :R 0.0 :G 0.0 :B 0.07 :A 0.0))
  (Rendering|Material|SetVectorParameterValue :Collection "/Game/Game/Materials/Latte/MPC_Latte.MPC_Latte" :ParameterName "GuideB" :ParameterValue (Utilities|Struct|MakeLinearColor :R 0.0 :G 0.0 :B 0.0 :A 0.0))
  ({V}SetEndTimer 2.4)
  (Rendering|SetVisibility :self ({V}GetStream) :bNewVisibility false)
  (if ({V}GetEndWin)
    (Rendering|Components|TextRender|SetText :self ({V}GetStatus) :Value (Utilities|Text|MakeLiteralText :Value "Beautiful!   E: done    R: pour it again"))
    (else
      (Rendering|Components|TextRender|SetText :self ({V}GetStatus) :Value (Utilities|Text|MakeLiteralText :Value "Spilled it. Fresh cup, try again.")))))
'''

G['LatteFinish'] = f'''
(fn LatteFinish ()
  ({V}SetLatteActive false)
  (CallFunction|LatteShow :Show false)
  (Game|Player|SetViewTargetwithBlend :self (Game|GetPlayerController 0) :NewViewTarget ({V}GetLattePlayer) :BlendTime 0.5)
  ({V}SetShift 3)
  ({V}SetShiftT 0.0)
  (Rendering|SetVisibility :self ({V}GetWorldText) :bNewVisibility true)
  {say("The latte is ready<br>Press E at the cup when you want to serve it")}
  (Class|PlayerController|SetShowMouseCursor :self (Game|GetPlayerController 0) :bShowMouseCursor false)
  (Input|SetInputModeGameOnly :PlayerController (Game|GetPlayerController 0) :bFlushInput false)
  {WALK})
'''

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'JumpCut', 'Saved', 'latte_graphs.json')
json.dump({k: v.strip() for k, v in G.items()}, open(out, 'w', encoding='utf-8'), indent=1)
print('wrote', os.path.normpath(out), list(G))
