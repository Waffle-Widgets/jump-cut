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
  (bind startPlayer (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter 0))
    (:then
      (Class|BPPlayer|PlayerSetInputLocked :self startPlayer :Locked true))
    (:CastFailed)))

(event EventTick (DeltaSeconds)
  (if ({V}GetLatteActive)
    (CallFunction|LatteStep :Dt DeltaSeconds)))
'''

G['LatteShow'] = f'''
(fn LatteShow (Show)
  (Rendering|SetVisibility :self ({V}GetPitcher) :bNewVisibility Show)
  (Rendering|SetVisibility :self ({V}GetPrompt) :bNewVisibility Show)
  (Rendering|SetVisibility :self ({V}GetStatus) :bNewVisibility Show)
  (Rendering|SetVisibility :self ({V}GetFillBar) :bNewVisibility Show)
  (Rendering|SetVisibility :self ({V}GetFillMark) :bNewVisibility Show)
  (Rendering|SetVisibility :self ({V}GetStream) :bNewVisibility false))
'''

G['LatteTryBegin'] = f'''
(fn LatteTryBegin (Player)
  ({V}SetLattePlayer Player)
  (if ({V}GetLatteDone)
    (Class|BPPlayer|PlayerSetInputLocked :self Player :Locked false)
    (else
      (Class|BPPlayer|PlayerSetInputLocked :self Player :Locked true)
      ({V}SetLatteActive true)
      (Game|Player|SetViewTargetwithBlend :self (Game|GetPlayerController 0) :NewViewTarget self :BlendTime 0.6)
      (CallFunction|LatteShow :Show true)
      (CallFunction|LatteReset))))
'''

P1 = '1. Hold LEFT mouse: pour from high until the bar reaches the mark'
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
  ({V}SetPattern (Math|Random|RandomIntegerinRange 0 2))
  (if (== ({V}GetPattern) 0)
    (Rendering|Components|TextRender|SetText :self ({V}GetPrompt) :Value (Utilities|Text|MakeLiteralText :Value "LATTE ART: HEART<br>{P1}<br>2. Hold RIGHT mouse in the middle: pour close and let the white circle grow<br>3. Let go. Hold LEFT and drag straight through the circle"))
    (elif (== ({V}GetPattern) 1)
      (Rendering|Components|TextRender|SetText :self ({V}GetPrompt) :Value (Utilities|Text|MakeLiteralText :Value "LATTE ART: ROSETTA<br>{P1}<br>2. Hold RIGHT mouse and wiggle left and right while you pull slowly back<br>3. Let go. Hold LEFT and drag straight through the middle"))
      (else
        (Rendering|Components|TextRender|SetText :self ({V}GetPrompt) :Value (Utilities|Text|MakeLiteralText :Value "LATTE ART: TULIP<br>{P1}<br>2. Hold RIGHT mouse three separate times, each pour pushing into the last<br>3. Hold LEFT and drag straight through the stack"))))))
'''

G['LatteStep'] = f'''
(fn LatteStep (Dt)
  (bind pc (Game|GetPlayerController 0))
  (if ({V}GetEnding)
    ({V}SetEndTimer (- ({V}GetEndTimer) Dt))
    (if (<= ({V}GetEndTimer) 0.0)
      (if ({V}GetEndWin)
        (CallFunction|LatteFinish)
        (else
          (CallFunction|LatteReset))))
    (else
      (bind (dx dy) (Game|Player|GetInputMouseDelta :self pc))
      ({V}SetLowGap (+ ({V}GetLowGap) Dt))
      (bind nx (+ ({V}GetPitX) (* dy 0.012)))
      (bind ny (+ ({V}GetPitY) (* dx 0.012)))
      ({V}SetPrevX ({V}GetPitX))
      ({V}SetPrevY ({V}GetPitY))
      ({V}SetPitX (select (< nx -5.2) -5.2 (select (> nx 5.2) 5.2 nx)))
      ({V}SetPitY (select (< ny -5.2) -5.2 (select (> ny 5.2) 5.2 ny)))
      (bind low (Game|Player|IsInputKeyDown :self pc :Key "RightMouseButton"))
      (bind high (and (Game|Player|IsInputKeyDown :self pc :Key "LeftMouseButton") (not low)))
      ({V}SetPitH (Math|Interpolation|FInterpTo :Current ({V}GetPitH) :Target (select low 1.5 8.0) :DeltaTime Dt :InterpSpeed 10.0))
      (if (or low high)
        (CallFunction|LattePour :Dt Dt :Low low :Dx dx))
      (Transformation|SetRelativeLocation :self ({V}GetPitcher) :NewLocation (Math|Vector|MakeVector :X ({V}GetPitX) :Y (+ ({V}GetPitY) 3.85) :Z (+ ({V}GetPitH) 1.8)))
      (Transformation|SetRelativeLocation :self ({V}GetStream) :NewLocation (Math|Vector|MakeVector :X ({V}GetPitX) :Y ({V}GetPitY) :Z (/ ({V}GetPitH) 2.0)))
      (Transformation|SetRelativeScale3D :self ({V}GetStream) :NewScale3D (Math|Vector|MakeVector :X (select low 0.012 0.005) :Y (select low 0.012 0.005) :Z (/ ({V}GetPitH) 100.0)))
      (Rendering|SetVisibility :self ({V}GetStream) :bNewVisibility (or low high))
      (Transformation|SetRelativeLocation :self ({V}GetFillBar) :NewLocation (Math|Vector|MakeVector :X (+ -6.0 (* ({V}GetFill) 6.0)) :Y -10.0 :Z 0.0))
      (Transformation|SetRelativeScale3D :self ({V}GetFillBar) :NewScale3D (Math|Vector|MakeVector :X (* ({V}GetFill) 0.12) :Y 0.008 :Z 0.004))
      (if (>= ({V}GetFill) 1.0)
        (CallFunction|LatteJudge)))))
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
      (Rendering|Material|SetVectorParameterValue :Collection "/Game/Game/Materials/Latte/MPC_Latte.MPC_Latte" :ParameterName "Vel" :ParameterValue (Utilities|Struct|MakeLinearColor :R vx :G vy :B 0.9 :A 0.6))
      (Rendering|Material|SetVectorParameterValue :Collection "/Game/Game/Materials/Latte/MPC_Latte.MPC_Latte" :ParameterName "Misc" :ParameterValue (Utilities|Struct|MakeLinearColor :R 0.035 :G 0.0 :B 0.25 :A 0.0))))
  (if ({V}GetFlipA)
    (Rendering|DrawMaterialtoRenderTarget :TextureRenderTarget {B} :Material "/Game/Game/Materials/Latte/MI_LatteSim_FromA.MI_LatteSim_FromA")
    (Rendering|Material|SetMaterial :self ({V}GetSurface) :ElementIndex 0 :Material "/Game/Game/Materials/Latte/MI_LatteSurface_B.MI_LatteSurface_B")
    (else
      (Rendering|DrawMaterialtoRenderTarget :TextureRenderTarget {A} :Material "/Game/Game/Materials/Latte/MI_LatteSim_FromB.MI_LatteSim_FromB")
      (Rendering|Material|SetMaterial :self ({V}GetSurface) :ElementIndex 0 :Material "/Game/Game/Materials/Latte/MI_LatteSurface_A.MI_LatteSurface_A")))
  ({V}SetFlipA (not ({V}GetFlipA)))
  ({V}SetFill (+ ({V}GetFill) (* Dt (select Low 0.07 0.045))))
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

G['LatteJudge'] = f'''
(fn LatteJudge ()
  (bind made (select (== ({V}GetPattern) 0) (>= ({V}GetLowTime) 1.5) (select (== ({V}GetPattern) 1) (>= ({V}GetWiggles) 6) (>= ({V}GetBlobs) 3))))
  ({V}SetEndWin (and made (>= ({V}GetCutDist) 0.3)))
  ({V}SetEnding true)
  ({V}SetEndTimer 2.4)
  (Rendering|SetVisibility :self ({V}GetStream) :bNewVisibility false)
  (if ({V}GetEndWin)
    (Rendering|Components|TextRender|SetText :self ({V}GetStatus) :Value (Utilities|Text|MakeLiteralText :Value "Beautiful. Order up!"))
    (else
      (Rendering|Components|TextRender|SetText :self ({V}GetStatus) :Value (Utilities|Text|MakeLiteralText :Value "Not quite. Fresh cup, try again.")))))
'''

G['LatteFinish'] = f'''
(fn LatteFinish ()
  ({V}SetLatteActive false)
  ({V}SetLatteDone true)
  (CallFunction|LatteShow :Show false)
  (Game|Player|SetViewTargetwithBlend :self (Game|GetPlayerController 0) :NewViewTarget ({V}GetLattePlayer) :BlendTime 0.0)
  (Class|BPPlayer|PlayerSetInputLocked :self ({V}GetLattePlayer) :Locked false))
'''

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'JumpCut', 'Saved', 'latte_graphs.json')
json.dump({k: v.strip() for k, v in G.items()}, open(out, 'w', encoding='utf-8'), indent=1)
print('wrote', os.path.normpath(out), list(G))
