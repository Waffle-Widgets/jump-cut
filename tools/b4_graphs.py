# Packet B4 graphs (Rewind on BP_Player), written with the Unreal MCP's write_graph_dsl and kept here as text so they
# can be rebuilt. See docs/FIRST_BUILD_DESIGN.md section 4. `python tools/b4_graphs.py` writes
# JumpCut/Saved/b4_graphs.json ({"<graph refPath>": "<dsl>"}), which an execute_tool_script reads and writes.
import json
import os

P = '/Game/Game/Blueprints/BP_Player.BP_Player'
V = 'Variables|Default|'
A = 'Utilities|Array|'

PLAYER = {}

PLAYER['PlayerTrailAddSample'] = f'''
(fn PlayerTrailAddSample ()
  ({A}Add :TargetArray ({V}GetTrailPos) :NewItem (Transformation|GetActorLocation))
  ({A}Add :TargetArray ({V}GetTrailHealth) :NewItem ({V}GetHealth))
  ({A}Add :TargetArray ({V}GetTrailTime) :NewItem ({V}GetTrailClock)))
'''

PLAYER['PlayerTrailReset'] = f'''
(fn PlayerTrailReset ()
  ({A}Clear :TargetArray ({V}GetTrailPos))
  ({A}Clear :TargetArray ({V}GetTrailHealth))
  ({A}Clear :TargetArray ({V}GetTrailTime))
  ({V}SetTrailSampleLeft 0.0)
  (CallFunction|PlayerTrailAddSample))
'''

# The drop check is two nested ifs, not one `and`: a Blueprint AND reads both sides, and TrailTime[1] on a
# one-sample trail logs an out-of-bounds warning. An empty trail (never expected) just gets a first sample.
PLAYER['PlayerTickTrail'] = f'''
(fn PlayerTickTrail (DeltaSeconds)
  ({V}SetTrailClock (+ ({V}GetTrailClock) DeltaSeconds))
  (if (not (or (or ({V}GetIsRewinding) ({V}GetIsLost)) (<= ({V}GetHealth) 0.0)))
    (if (< ({A}Length :TargetArray ({V}GetTrailPos)) 1)
      (CallFunction|PlayerTrailAddSample)
      (else
        (if (>= ({A}Length :TargetArray ({V}GetTrailTime)) 2)
          (if (<= ({A}Get(acopy) ({V}GetTrailTime) 1) (- ({V}GetTrailClock) ({V}GetTrailSeconds)))
            ({A}RemoveIndex :TargetArray ({V}GetTrailPos) :IndexToRemove 0)
            ({A}RemoveIndex :TargetArray ({V}GetTrailHealth) :IndexToRemove 0)
            ({A}RemoveIndex :TargetArray ({V}GetTrailTime) :IndexToRemove 0)))
        ({V}SetTrailSampleLeft (- ({V}GetTrailSampleLeft) DeltaSeconds))
        (if (<= ({V}GetTrailSampleLeft) 0.0)
          ({V}SetTrailSampleLeft ({V}GetTrailSampleInterval))
          (bind last ({A}LastIndex :TargetArray ({V}GetTrailPos)))
          (bind moved (Math|Vector|Distance(Vector) (Transformation|GetActorLocation) ({A}Get(acopy) ({V}GetTrailPos) last)))
          (if (or (> moved ({V}GetTrailMinMove)) (!= ({V}GetHealth) ({A}Get(acopy) ({V}GetTrailHealth) last)))
            (CallFunction|PlayerTrailAddSample)))))))
'''

PLAYER['RewindStart'] = f'''
(fn RewindStart ()
  (if (not (or (or (or (not ({V}GetHasRewind)) ({V}GetIsRewinding)) (> ({V}GetRewindCooldownLeft) 0.0)) (or (or ({V}GetIsLost) ({V}GetHasWon)) ({V}GetInputLocked))))
    (CallFunction|PlayerFreezeBreak)
    ({V}SetIsDowned false)
    (CallFunction|PlayerTrailAddSample)
    (bind count ({A}Length :TargetArray ({V}GetTrailPos)))
    ({V}SetRewindSlideDuration (Math|Float|Max(Float) ({V}GetRewindSlideMin) (/ (* ({V}GetRewindSlideTime) count) (/ ({V}GetTrailSeconds) ({V}GetTrailSampleInterval)))))
    ({V}SetRewindAlpha 0.0)
    ({V}SetIsRewinding true)))
'''

# F = (1 - alpha) x (count - 1); I = floor(F); J = min(I + 1, count - 1); position = lerp(TrailPos[I], TrailPos[J], F - I).
PLAYER['PlayerTickRewindSlide'] = f'''
(fn PlayerTickRewindSlide (DeltaSeconds)
  (if ({V}GetIsRewinding)
    ({V}SetRewindAlpha (+ ({V}GetRewindAlpha) (/ DeltaSeconds ({V}GetRewindSlideDuration))))
    (if (>= ({V}GetRewindAlpha) 1.0)
      (CallFunction|PlayerRewindFinish)
      (else
        (bind last ({A}LastIndex :TargetArray ({V}GetTrailPos)))
        (bind f (* (- 1.0 ({V}GetRewindAlpha)) last))
        (bind i (Math|Float|Floor f))
        (bind j (Math|Integer|Min(Integer) (+ i 1) last))
        (bind pos (Math|Vector|Lerp(Vector) ({A}Get(acopy) ({V}GetTrailPos) i) ({A}Get(acopy) ({V}GetTrailPos) j) (- f i)))
        (Transformation|SetActorLocation :NewLocation pos :bSweep false :bTeleport true)))))
'''

PLAYER['PlayerRewindFinish'] = f'''
(fn PlayerRewindFinish ()
  (Transformation|SetActorLocation :NewLocation ({A}Get(acopy) ({V}GetTrailPos) 0) :bSweep false :bTeleport true)
  ({V}SetHealth (Math|Float|Max(Float) ({V}GetHealth) ({A}Get(acopy) ({V}GetTrailHealth) 0)))
  ({V}SetIsRewinding false)
  ({V}SetRewindCooldownLeft ({V}GetRewindCooldown))
  ({V}SetHitSafeLeft ({V}GetRewindSafeTime))
  (CallFunction|PlayerTrailReset))
'''


def build():
    return {f'{P}:{name}': code.strip() for name, code in PLAYER.items()}


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    dst = os.path.join(here, '..', 'JumpCut', 'Saved', 'b4_graphs.json')
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(build(), f, indent=1)
    print('wrote', os.path.normpath(dst), len(build()), 'graphs')
