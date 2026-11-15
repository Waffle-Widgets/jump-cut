# Beat 1 feedback round 4 (2026-11-15): the breakable wall, the fire that lights in the third cut
# and freezes with the power, and the driver thrown out of the RIGHT side of the car as a ragdoll.
# Written with the Unreal MCP's write_graph_dsl and kept here as text so it can be rebuilt.
# `python tools/b1z_graphs.py` writes JumpCut/Saved/b1z_graphs.json.
#
# WHY THE FIRE IS DRIVEN BY TIME DILATION. NS_CarFire rides B1_Cafe_Fire as a NiagaraComponent, and
# the graph DSL has no clean way to reach a component on ANOTHER actor. Setting the fire ACTOR's
# CustomTimeDilation does both jobs the Team Owner asked for with one lever: 0 before it is lit
# means the system has never advanced, so unfreezing it at the third cut is a real burst from
# nothing rather than a plume that has been burning off screen for seven seconds; and 0 again while
# Freeze Frame is active is the fire stopping dead with the rest of the world.
import json, os

D = '/Game/Game/Blueprints/BP_OpeningDirector.BP_OpeningDirector'
C = '/Game/Game/Blueprints/BP_CrashDriver.BP_CrashDriver'
V = 'Variables|Default|'

G = {}

# ---------------------------------------------------------------- BP_CrashDriver: the ragdoll
# The body is thrown by the cinematic as a keyframed spawnable and handed over to the REAL
# BP_CrashDriver on the frame it lands. From that frame the real one is a ragdoll, so the pose it
# comes to rest in is physics, not a hand-set rotation - which is what "do some ragdolling to get
# him into position" asks for. It is behind BP_OpeningDirector.DriverRagdoll so it can be switched
# off in one checkbox if the auto-generated physics asset misbehaves.
G[C + ':DriverRagdollStart'] = f'''
(fn DriverRagdollStart ()
  (if (not ({V}GetRagdollLive))
    ({V}SetRagdollLive true)
    (Physics|SetAllBodiesSimulatePhysics :self ({V}GetDriverMesh) :bNewSimulate true)
    (Physics|SetAllPhysicsLinearVelocity :self ({V}GetDriverMesh)
      :NewVel (Math|Vector|MakeVector :X 210.0 :Y -260.0 :Z -40.0) :bAddToCurrent false)))
'''

# Stopping is NOT SetAllBodiesSimulatePhysics(false): that hands the mesh back to its animation and
# the settled sprawl snaps to the reference pose. Killing the velocities keeps the physics pose and
# leaves him lying still.
G[C + ':DriverRagdollStop'] = f'''
(fn DriverRagdollStop ()
  (if ({V}GetRagdollLive)
    (Physics|SetAllPhysicsLinearVelocity :self ({V}GetDriverMesh)
      :NewVel (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z 0.0) :bAddToCurrent false)
    (Physics|SetAllPhysicsAngularVelocityinDegrees :self ({V}GetDriverMesh)
      :NewAngVel (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z 0.0) :bAddToCurrent false)))
'''

# ---------------------------------------------------------------- BP_OpeningDirector
# The wall comes apart on the frame the car reaches it. Same four-step recipe GC_CrashCar needs:
# a KINEMATIC collection cannot be broken and says nothing about it.
G[D + ':CineBreakWall'] = f'''
(fn CineBreakWall ()
  (bind gc ({V}GetCineWallGC))
  (Utilities|IsValid gc
    (:"Is Valid"
      (bind comp (Class|GeometryCollectionActor|GetGeometryCollectionComponent :self gc))
      (bind at (Transformation|GetActorLocation :self gc))
      (Class|GeometryCollectionComponent|SetObjectType :self comp :ObjectType "Chaos_Object_Dynamic")
      (ChaosPhysics|RemoveAllAnchors :self comp)
      (ChaosPhysics|ApplyExternalStrain :self comp :ItemIndex 0 :Location at :Radius 400.0
        :PropagationDepth 0 :PropagationFactor 1.0 :Strain ({V}GetWallBreakStrain))
      (ChaosPhysics|CrumbleActiveClusters :self comp)
      (Physics|AddRadialImpulse :self comp
        :Origin (- at (Math|Vector|MakeVector :X 180.0 :Y 0.0 :Z 0.0))
        :Radius 600.0 :Strength ({V}GetWallBreakImpulse) :Falloff "RIF_Linear" :bVelChange true))))
'''

# One guarded place where the fire actor's clock is written, so no other function has to risk a
# call on a null reference.
G[D + ':CineFireDilate'] = f'''
(fn CineFireDilate (Rate)
  (bind f ({V}GetCineFireActor))
  (Utilities|IsValid f
    (:"Is Valid"
      (Variables|Actor|SetCustomTimeDilation :self f :CustomTimeDilation Rate))))
'''

G[D + ':CineLightFire'] = f'''
(fn CineLightFire ()
  ({V}SetCineFireLit true)
  (CallFunction|CineHideActor :Target ({V}GetCineFireActor) :Hide false)
  (CallFunction|CineHideActor :Target ({V}GetCineFireLight) :Hide false)
  (CallFunction|CineFireDilate :Rate 1.0))
'''

# Freeze Frame stops every enemy by setting its CustomTimeDilation to 0; the fire now stops the
# same way, because "time has stopped" is the whole point of the power.
G[D + ':CineFireTimeStep'] = f'''
(fn CineFireTimeStep ()
  (if ({V}GetCineFireLit)
    (bind frozen (Class|BPPlayer|GetFreezeFrameActive :self ({V}GetPlayerRef)))
    (CallFunction|CineFireDilate :Rate (select frozen 0.0 1.0))))
'''

G[D + ':CineDriverRagdoll'] = f'''
(fn CineDriverRagdoll ()
  (bind d ({V}GetCineRealDriver))
  (Utilities|IsValid d
    (:"Is Valid"
      (Class|BPCrashDriver|DriverRagdollStart :self d))))
'''

G[D + ':CineDriverRagdollStop'] = f'''
(fn CineDriverRagdollStop ()
  (bind d ({V}GetCineRealDriver))
  (Utilities|IsValid d
    (:"Is Valid"
      (Class|BPCrashDriver|DriverRagdollStop :self d))))
'''

# The wall patch is gone: B1_Cafe_WallPanel_GC is the wall now, and it is SHOWN here rather than
# hidden. The fire starts hidden AND stopped, so its particle system has not advanced a frame when
# the third cut lights it.
G[D + ':CineSceneBeforeCrash'] = f'''
(fn CineSceneBeforeCrash ()
  (CallFunction|CineHideActor :Target ({V}GetCineWallGC) :Hide false)
  (CallFunction|CineHideActor :Target ({V}GetCineRealCar) :Hide true)
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
  (CallFunction|CineFireDilate :Rate 0.0))
'''

G[D + ':CineShowWreck'] = f'''
(fn CineShowWreck ()
  (CallFunction|CineHideActor :Target ({V}GetCineRealCar) :Hide false))
'''

G[D + ':CineShowBody'] = f'''
(fn CineShowBody ()
  (CallFunction|CineHideActor :Target ({V}GetCineRealDriver) :Hide false)
  (if (and ({V}GetDriverRagdoll) (not ({V}GetRagdollOn)))
    ({V}SetRagdollOn true)
    ({V}SetRagdollT 0.0)
    (CallFunction|CineDriverRagdoll)))
'''

# Two new triggers inside the opening's own clock, and two steps that run in every state: the
# ragdoll's settle timer and the fire's clock (which has to keep working through the rescue and
# the explosion, where Freeze Frame is still being used).
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
  (CallFunction|CineFireTimeStep)
  (CallFunction|CineBeaconStep :DeltaSeconds DeltaSeconds))
'''

# ---------------------------------------------------------------- BP_Player
# The player's "he just loaded in" twitch at the start of the cinematic: releasing a move lock put
# him into MOVE_Falling, so the anim blueprint ran a fall and a landing on the first tick of every
# game (and after every freeze, rewind and cinematic). MOVE_Walking is the correct release - the
# movement component drops to falling by itself on the next update if there is no floor under him.
G['/Game/Game/Blueprints/BP_Player.BP_Player:PlayerRefreshMoveLock'] = f'''
(fn PlayerRefreshMoveLock ()
  (bind cm (Variables|Character|GetCharacterMovement))
  (bind busy (or (or (or ({V}GetIsRewinding) ({V}GetIsFrozenbyBoss)) (or ({V}GetIsDowned) ({V}GetIsLost)))
                 (or ({V}GetHasWon) ({V}GetInputLocked))))
  (if (and busy (not ({V}GetMoveLocked)))
    (Pawn|Components|CharacterMovement|DisableMovement cm)
    (Components|Movement|StopMovementImmediately cm)
    ({V}SetMoveLocked true))
  (if (and (not busy) ({V}GetMoveLocked))
    (Pawn|Components|CharacterMovement|SetMovementMode cm "MOVE_Walking")
    ({V}SetMoveLocked false)))
'''


def build():
    out = {k: v.strip() + '\n' for k, v in G.items()}
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'JumpCut', 'Saved', 'b1z_graphs.json')
    with open(p, 'w') as fh:
        json.dump(out, fh, indent=1)
    print('wrote %s: %d graphs' % (p, len(out)))
    return out


if __name__ == '__main__':
    build()
