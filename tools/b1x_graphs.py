# Beat 1's explosion-and-pan cinematic, and the objective chain that carries the player from the
# cafe out to the goons and on to the boss. Written with the Unreal MCP's write_graph_dsl and kept
# here as text so it can be rebuilt. `python tools/b1x_graphs.py` writes JumpCut/Saved/b1x_graphs.json
# ({"vars": [...], "fns": [...], "graphs": {"<graph refPath>": "<dsl>"}}).
#
# The explosion is NOT a Level Sequence. The rescue that precedes it is already director-driven, the
# camera move is four poses and three lerps, and a sequence would add a second asset to keep in step
# with the actors it photographs. The director owns the camera, the card and the wreck instead.
import json
import os

D = '/Game/Game/Blueprints/BP_OpeningDirector.BP_OpeningDirector'
V = 'Variables|Default|'
GOON = '"/Game/Game/Blueprints/BP_Goon.BP_Goon_C"'

# ---------------------------------------------------------------- new member variables
VARS = [
    # the explosion cinematic's own clock and state
    ('ExplCine', 'bool', None), ('ExplDone', 'bool', None), ('ExplSaid', 'bool', None),
    ('ExplT', 'float', None),
    ('ExplTB', 'float', None), ('ExplTC', 'float', None), ('ExplTD', 'float', None),
    ('ExplFlashSecs', 'float', None), ('ExplSayAt', 'float', None),
    ('ExplCardMin', 'float', None), ('ExplCardMax', 'float', None),
    ('ExplBlastStrain', 'float', None), ('ExplBlastImpulse', 'float', None),
    # the four camera poses it lerps between
    ('ExplCamALoc', 'struct', 'Vector'), ('ExplCamBLoc', 'struct', 'Vector'),
    ('ExplCamCLoc', 'struct', 'Vector'), ('ExplCamDLoc', 'struct', 'Vector'),
    ('ExplCamARot', 'struct', 'Rotator'), ('ExplCamBRot', 'struct', 'Rotator'),
    ('ExplCamCRot', 'struct', 'Rotator'), ('ExplCamDRot', 'struct', 'Rotator'),
    # the actors it drives
    ('ExplCam', 'object', '/Script/Engine.Actor'),
    ('ExplCard', 'object', '/Script/Engine.StaticMeshActor'),
    ('ExplCarGC', 'object', '/Script/GeometryCollectionEngine.GeometryCollectionActor'),
    # beats 2 and 3: the goons, then the boss
    ('ObjGoonLoc', 'struct', 'Vector'), ('ObjBossLoc', 'struct', 'Vector'),
    ('ObjBossDoneX', 'float', None), ('GoonZoneMaxX', 'float', None),
    ('GoonsSeen', 'bool', None), ('GoonsLeftNow', 'int', None),
]

# ---------------------------------------------------------------- new functions (name, params, outputs)
FNS = [
    ('CineExplBegin', [], []),
    ('CineExplFire', [], []),
    ('CineExplCardOn', [], []),
    ('CineExplCardStep', [], []),
    ('CineExplCamStep', [], []),
    ('CineExplStep', [('DeltaSeconds', 'float')], []),
    ('CineExplEnd', [], []),
    ('CineGoonsLeft', [], [('Count', 'int')]),
    ('CineObjGoons', [], []),
    ('CineObjBoss', [], []),
    ('CineRescueRun', [('DeltaSeconds', 'float')], []),
]

G = {}

# A multi-exec node (IsValid, Cast, any latent call) TERMINATES the exec flow it sits in, so it
# must be the LAST statement in its scope. That one rule is why the bang is split across
# CineExplFire / CineExplCardOn and the camera move lives in its own CineExplCamStep, rather than
# all three being one function with three guards in the middle of it.

# The bang: the wreck comes apart.
G['CineExplFire'] = f'''
(fn CineExplFire ()
  (bind gc ({V}GetExplCarGC))
  (Utilities|IsValid gc
    (:"Is Valid"
      (bind comp (Class|GeometryCollectionActor|GetGeometryCollectionComponent :self gc))
      (bind at (Transformation|GetActorLocation :self gc))
      (Class|GeometryCollectionComponent|SetObjectType :self comp :ObjectType "Chaos_Object_Dynamic")
      (ChaosPhysics|RemoveAllAnchors :self comp)
      (ChaosPhysics|ApplyExternalStrain :self comp :ItemIndex 0 :Location at :Radius 500.0
        :PropagationDepth 0 :PropagationFactor 1.0 :Strain ({V}GetExplBlastStrain))
      (ChaosPhysics|CrumbleActiveClusters :self comp)
      (Physics|AddRadialImpulse :self comp
        :Origin (- at (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z 70.0))
        :Radius 700.0 :Strength ({V}GetExplBlastImpulse) :Falloff "RIF_Linear" :bVelChange true))))
'''

# The bang: the fireball card appears, at frame 0 and at its smallest.
G['CineExplCardOn'] = f'''
(fn CineExplCardOn ()
  (bind card ({V}GetExplCard))
  (bind cmin ({V}GetExplCardMin))
  (Utilities|IsValid card
    (:"Is Valid"
      (Transformation|SetActorScale3D :self card :NewScale3D (Math|Vector|MakeVector :X cmin :Y cmin :Z cmin))
      (Rendering|Material|SetScalarParameterValueonMaterials
        :self (Class|StaticMeshActor|GetStaticMeshComponent :self card)
        :ParameterName "Frame" :ParameterValue 0.0)
      (Rendering|SetActorHiddenInGame :self card :bNewHidden false))))
'''

# The card is a flat sheet, so it is turned to face the camera every frame. MakeRotFromZ was the
# obvious way and it is wrong: it leaves the roll about the view axis free, and PIE measured the
# card sitting at roll -83 deg - the fireball drawn on its side. Taking the camera's own rotation
# and pitching it 90 deg puts the plane's +Z down the lens with the roll pinned at zero.
G['CineExplCardStep'] = f'''
(fn CineExplCardStep ()
  (bind card ({V}GetExplCard))
  (bind t ({V}GetExplT))
  (bind flash ({V}GetExplFlashSecs))
  (Utilities|IsValid card
    (:"Is Valid"
      (if (> t flash)
        (CallFunction|CineHideActor :Target card :Hide true)
        (else
          (bind a (/ t flash))
          (bind lo ({V}GetExplCardMin))
          (bind s (+ lo (* a (- ({V}GetExplCardMax) lo))))
          (Transformation|SetActorScale3D :self card :NewScale3D (Math|Vector|MakeVector :X s :Y s :Z s))
          (bind raw (* a 36.0))
          (Rendering|Material|SetScalarParameterValueonMaterials
            :self (Class|StaticMeshActor|GetStaticMeshComponent :self card)
            :ParameterName "Frame" :ParameterValue (select (> raw 35.0) 35.0 raw))
          (bind cam ({V}GetExplCam))
          (Utilities|IsValid cam
            (:"Is Valid"
              (bind cr (Transformation|GetActorRotation :self cam))
              (Transformation|SetActorRotation :self card
                :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch (+ (.pitch cr) 90.0) :Yaw (.yaw cr))
                :bTeleportPhysics true))))))))
'''

# A -> B holds on the wreck while it comes apart; B -> C swings off it; C -> D settles looking
# straight out of the cafe door, which is where the player is being sent next.
G['CineExplCamStep'] = f'''
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
          (bind b (/ (- t tb) (- tc tb)))
          (Transformation|SetActorLocationAndRotation :self cam
            :NewLocation (Math|Vector|Lerp(Vector) :A ({V}GetExplCamBLoc) :B ({V}GetExplCamCLoc) :Alpha b)
            :NewRotation (Math|Rotator|Lerp(Rotator) :A ({V}GetExplCamBRot) :B ({V}GetExplCamCRot) :Alpha b :bShortestPath true)
            :bSweep false :bTeleport true)
          (else
            (bind raw (/ (- t tc) (- td tc)))
            (bind c (select (> raw 1.0) 1.0 raw))
            (Transformation|SetActorLocationAndRotation :self cam
              :NewLocation (Math|Vector|Lerp(Vector) :A ({V}GetExplCamCLoc) :B ({V}GetExplCamDLoc) :Alpha c)
              :NewRotation (Math|Rotator|Lerp(Rotator) :A ({V}GetExplCamCRot) :B ({V}GetExplCamDRot) :Alpha c :bShortestPath true)
              :bSweep false :bTeleport true)))))))
'''

# Takes the frame off the player at the moment the car goes up. Freeze Frame is ended first, so the
# explosion is always seen at normal speed however the player got here.
G['CineExplBegin'] = f'''
(fn CineExplBegin ()
  (bind pl ({V}GetPlayerRef))
  ({V}SetExplCine true)
  ({V}SetRescueCine false)
  ({V}SetExplT 0.0)
  ({V}SetExplSaid false)
  ({V}SetObjectiveState 0)
  ({V}SetBarTarget 1.0)
  (Class|BPPlayer|SetInputLocked :self pl :InputLocked true)
  (Class|BPPlayer|SetMoveLocked :self pl :MoveLocked true)
  (if (Class|BPPlayer|GetFreezeFrameActive :self pl)
    (Class|BPPlayer|PlayerFreezeFrameEnd :self pl))
  (CallFunction|CineExplFire)
  (CallFunction|CineExplCardOn)
  (bind cam ({V}GetExplCam))
  (Utilities|IsValid cam
    (:"Is Valid"
      (Transformation|SetActorLocationAndRotation :self cam :NewLocation ({V}GetExplCamALoc)
        :NewRotation ({V}GetExplCamARot) :bSweep false :bTeleport true)
      (Game|Player|SetViewTargetwithBlend :self (Game|GetPlayerController :PlayerIndex 0)
        :NewViewTarget cam :BlendTime 0.35 :BlendFunc "VTBlend_EaseInOut" :BlendExp 2.0
        :bLockOutgoing false))))
'''

G['CineExplStep'] = f'''
(fn CineExplStep (DeltaSeconds)
  (bind t (+ ({V}GetExplT) DeltaSeconds))
  ({V}SetExplT t)
  (CallFunction|CineExplCamStep)
  (CallFunction|CineExplCardStep)
  (if (not ({V}GetExplSaid))
    (if (> t ({V}GetExplSayAt))
      ({V}SetExplSaid true)
      (CallFunction|CineSay :Msg "That was meant for you. There are more of them out on the street - go and put them down." :Secs 5.0)))
  (if (>= t ({V}GetExplTD))
    (CallFunction|CineExplEnd)))
'''

G['CineExplEnd'] = f'''
(fn CineExplEnd ()
  (bind pl ({V}GetPlayerRef))
  ({V}SetExplCine false)
  ({V}SetExplDone true)
  ({V}SetBarTarget 0.0)
  (CallFunction|CineHideActor :Target ({V}GetExplCard) :Hide true)
  (Class|BPPlayer|SetInputLocked :self pl :InputLocked false)
  (Class|BPPlayer|SetMoveLocked :self pl :MoveLocked false)
  (Game|Player|SetViewTargetwithBlend :self (Game|GetPlayerController :PlayerIndex 0)
    :NewViewTarget pl :BlendTime 0.6 :BlendFunc "VTBlend_EaseInOut" :BlendExp 2.0 :bLockOutgoing false)
  ({V}SetObjectiveState 3))
'''

# Counts goons on the beat-2 stretch of street only. Spawner_Beat4 stands at x = 12900 and fills
# its own group at BeginPlay, so an unfiltered count never reaches zero. A defeated goon destroys
# itself, so presence is the test - no cast and no IsDefeated read.
G['CineGoonsLeft'] = f'''
(fn CineGoonsLeft ()
  ({V}SetGoonsLeftNow 0)
  (bind all (Actor|GetAllActorsOfClass :ActorClass {GOON}))
  (for g all
    (if (< (.x (Transformation|GetActorLocation :self g)) ({V}GetGoonZoneMaxX))
      ({V}SetGoonsLeftNow (+ ({V}GetGoonsLeftNow) 1))))
  (return ({V}GetGoonsLeftNow)))
'''

G['CineObjGoons'] = f'''
(fn CineObjGoons ()
  (bind n (CallFunction|CineGoonsLeft))
  (if (> n 0)
    ({V}SetGoonsSeen true)
    (else
      (if ({V}GetGoonsSeen)
        ({V}SetObjectiveState 5)
        (CallFunction|CineSay :Msg "That is the welcome party dealt with. The one with the cleaver is still waiting - keep going east." :Secs 5.0)))))
'''

G['CineObjBoss'] = f'''
(fn CineObjBoss ()
  (if (> (.x (Transformation|GetActorLocation :self ({V}GetPlayerRef))) ({V}GetObjBossDoneX))
    ({V}SetObjectiveState 0)))
'''

# ---------------------------------------------------------------- edits to existing graphs
G['CineObjStreet'] = f'''
(fn CineObjStreet ()
  (if (> (.x (Transformation|GetActorLocation :self ({V}GetPlayerRef))) ({V}GetObjStreetDoneX))
    ({V}SetObjectiveState 4)))
'''

G['CineObjectiveAdvance'] = f'''
(fn CineObjectiveAdvance ()
  (bind s ({V}GetObjectiveState))
  (if (== s 1)
    (CallFunction|CineObjDriver))
  (if (== s 2)
    (CallFunction|CineObjRescue))
  (if (== s 3)
    (CallFunction|CineObjStreet))
  (if (== s 4)
    (CallFunction|CineObjGoons))
  (if (== s 5)
    (CallFunction|CineObjBoss)))
'''

G['CineObjectiveSpot'] = f'''
(fn CineObjectiveSpot ()
  (bind s ({V}GetObjectiveState))
  (if (== s 1)
    (return ({V}GetObjDriverLoc))
    (elif (== s 2)
      (return ({V}GetObjSafeLoc))
      (elif (== s 3)
        (return ({V}GetObjStreetLoc))
        (elif (== s 4)
          (return ({V}GetObjGoonLoc))
          (elif (== s 5)
            (return ({V}GetObjBossLoc))
            (else
              (return (Math|Vector|MakeVector 0.0)))))))))
'''

# The explosion cinematic is checked before the rescue, and both before the opening, so only one
# of the three ever drives the frame.
G['CineDirectorStep'] = f'''
(fn CineDirectorStep (DeltaSeconds)
  (bind nt (+ ({V}GetCineTime) DeltaSeconds))
  (if ({V}GetExplCine)
    (CallFunction|CineExplStep :DeltaSeconds DeltaSeconds)
    (elif ({V}GetRescueCine)
      (CallFunction|CineRescueStep :DeltaSeconds DeltaSeconds)
      (elif ({V}GetCineRunning)
        ({V}SetCineTime nt)
        (if (>= nt ({V}GetCineImpactTime))
          (CallFunction|CineShowWreck))
        (if (>= nt ({V}GetCineBodyTime))
          (CallFunction|CineShowBody))
        (if (>= nt ({V}GetCineLength))
          (CallFunction|CineFinishOpening))
        (elif ({V}GetCineDone)
          (CallFunction|CineObjectiveAdvance)
          (elif (not (Class|BPPlayer|GetInputLocked :self ({V}GetPlayerRef)))
            (CallFunction|CineBeginOpening))))))
  (CallFunction|CineBeaconStep :DeltaSeconds DeltaSeconds))
'''

# The rescue now hands straight to the explosion rather than running on for another 1.8 s with the
# camera on nothing. The old RescueEndAt tail is gone: CineExplEnd returns control instead - which
# means a rescue started AFTER the explosion has nothing left to end it. PIE soft-locked exactly
# that way (input locked, RescueT climbing past 140 s), so CineRescueStep now refuses to run once
# ExplDone is set and hands control straight back.
G['CineRescueStep'] = f'''
(fn CineRescueStep (DeltaSeconds)
  (bind pl ({V}GetPlayerRef))
  (if ({V}GetExplDone)
    ({V}SetRescueCine false)
    ({V}SetBarTarget 0.0)
    (Class|BPPlayer|SetInputLocked :self pl :InputLocked false)
    (Class|BPPlayer|SetMoveLocked :self pl :MoveLocked false)
    (else
      (CallFunction|CineRescueRun :DeltaSeconds DeltaSeconds))))
'''

# The run itself, split out only because CineRescueStep's ExplDone guard has to be the whole of
# that function's top level.
G['CineRescueRun'] = f'''
(fn CineRescueRun (DeltaSeconds)
  (bind pl ({V}GetPlayerRef))
  (bind cw ({V}GetCoworkerRef))
  (bind here (Transformation|GetActorLocation :self pl))
  (bind safe ({V}GetObjSafeLoc))
  (bind d (- safe here))
  (bind flat (Math|Vector|MakeVector :X (.x d) :Y (.y d) :Z 0.0))
  (bind t (+ ({V}GetRescueT) DeltaSeconds))
  ({V}SetRescueT t)
  (if (> (Math|Vector|VectorLength flat) 60.0)
    (Transformation|SetActorLocation :self pl
      :NewLocation (+ here (* (Math|Vector|Normalize flat) (* ({V}GetRescueMoveSpeed) DeltaSeconds)))
      :bSweep false :bTeleport true))
  (if (> t ({V}GetRescueBlastAt))
    (if (not (Class|BPCoworker|GetBlown :self cw))
      (if (< (Math|Vector|VectorLength (- (Transformation|GetActorLocation :self cw) (Class|BPCoworker|GetBlastOrigin :self cw)))
             (+ (Class|BPCoworker|GetBlastRadius :self cw) 80.0))
        (Transformation|SetActorLocation :self cw
          :NewLocation (+ safe (Math|Vector|MakeVector :X -140.0 :Y -90.0 :Z 0.0))
          :bSweep false :bTeleport true))
      (Class|BPCoworker|CoworkerBlastNow :self cw)
      (CallFunction|CineExplBegin))))
'''


def build():
    out = {'vars': VARS, 'fns': FNS,
           'graphs': {'%s:%s' % (D, k): v.strip() + '\n' for k, v in G.items()}}
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'JumpCut', 'Saved', 'b1x_graphs.json')
    with open(p, 'w') as fh:
        json.dump(out, fh, indent=1)
    print('wrote %s: %d vars, %d new fns, %d graphs' % (p, len(VARS), len(FNS), len(G)))


if __name__ == '__main__':
    build()
