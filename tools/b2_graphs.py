# Packet C1d + B2 graphs, written with the Unreal MCP's write_graph_dsl and kept here as text so they can be rebuilt.
# See docs/FIRST_BUILD_DESIGN.md sections 2 (WBP_HUD, BP_JumpCutGameMode) and 7 (BP_PlazaGate, C1d).
# `python tools/b2_graphs.py` writes JumpCut/Saved/b2_graphs.json ({"<graph refPath>": "<dsl>"}).
#
# C1d (the entry gate never lands on the player and never leaves them outside):
#   BP_PlazaGate: new variables GateSafeDepth (float 120, T: 20 cm half slab + 42 cm capsule + 58 cm spare),
#     GateRescueReach (float 400, T: how far outside the gate line a player is still pulled in),
#     GateRescueHalfWidth (float 600, T: how far sideways from the gate's centre), GateGuardingClose (bool).
#   New functions GateKeepPlayerInside and GatePushPlayerInside. When the close-behind branch fires it sets
#     GateGuardingClose and pushes at once; GateTickStep then calls GateKeepPlayerInside every tick, so while the slab
#     drops (and on the frame it reaches the bottom) a player less than GateSafeDepth inside the gate line, within
#     GateRescueReach outside it and GateRescueHalfWidth sideways, is moved along the gate's forward axis to exactly
#     GateSafeDepth inside (sideways position and height kept; SetActorLocation, sweep off, teleport on). The guard
#     switches off when the slab reaches the bottom or the gate opens. Only gates whose close-behind branch fired
#     (Gate_PlazaEntry) ever set the guard: Gate_PlazaExit, PlazaGateOpen/Close/OpenForGood/ResetToStart unchanged.
#   Backups of the graphs before C1d: GateCheckTrigger in tools/d2_graphs.py, GateTickStep in tools/c1_graphs.py.
import json
import os

G = '/Game/Game/Blueprints/BP_PlazaGate.BP_PlazaGate'
V = 'Variables|Default|'

GATE = {}

GATE['GateTickStep'] = f'''
(fn GateTickStep (DeltaSeconds)
  (bind rel (Class|SceneComponent|GetRelativeLocation :self ({V}GetGateMesh)))
  (bind target (select ({V}GetGateIsOpen) ({V}GetGateOpenHeight) 0.0))
  (bind nz (Math|Interpolation|FInterptoConstant :Current (.z rel) :Target target :DeltaTime DeltaSeconds :InterpSpeed ({V}GetGateMoveSpeed)))
  (Transformation|SetRelativeLocation :self ({V}GetGateMesh) :NewLocation (Math|Vector|MakeVector :X (.x rel) :Y (.y rel) :Z nz))
  (CallFunction|GateKeepPlayerInside))
'''

GATE['GateKeepPlayerInside'] = f'''
(fn GateKeepPlayerInside ()
  (if ({V}GetGateIsOpen)
    ({V}SetGateGuardingClose false))
  (if ({V}GetGateGuardingClose)
    (Utilities|IsValid ({V}GetPlayerRef)
      (:"Is Valid"
        (CallFunction|GatePushPlayerInside))
      (:"Is Not Valid"))))
'''

GATE['GatePushPlayerInside'] = f'''
(fn GatePushPlayerInside ()
  (bind here (Transformation|GetActorLocation))
  (bind tr (- (Transformation|GetWorldLocation :self ({V}GetTriggerSphere)) here))
  (bind into (Math|Vector|Normalize (Math|Vector|MakeVector :X (.x tr) :Y (.y tr) :Z 0.0)))
  (bind pl (Transformation|GetActorLocation :self ({V}GetPlayerRef)))
  (bind pd (- pl here))
  (bind pflat (Math|Vector|MakeVector :X (.x pd) :Y (.y pd) :Z 0.0))
  (bind depth (Math|Vector|DotProduct :A pflat :B into))
  (bind side (Math|Vector|VectorLength (- pflat (* into depth))))
  (bind safe ({V}GetGateSafeDepth))
  (bind near (and (and (< depth safe) (> depth (* -1.0 ({V}GetGateRescueReach)))) (< side ({V}GetGateRescueHalfWidth))))
  (if near
    (Transformation|SetActorLocation :self ({V}GetPlayerRef) :NewLocation (+ pl (* into (- safe depth))) :bSweep false :bTeleport true))
  (if (<= (.z (Class|SceneComponent|GetRelativeLocation :self ({V}GetGateMesh))) 0.0)
    ({V}SetGateGuardingClose false)))
'''

GATE['GateCheckTrigger'] = f'''
(fn GateCheckTrigger ()
  (if (and (and ({V}GetGateClosesBehindPlayer) ({V}GetGateTriggerArmed)) ({V}GetGateIsOpen))
    (Utilities|IsValid ({V}GetGateEnemyToWake)
      (:"Is Valid"
        (bind inside (CallFunction|GateInTrigger))
        (bind past (CallFunction|GateIsPastGateway))
        (if (or inside past)
          (CallFunction|PlazaGateClose)
          ({V}SetGateTriggerArmed false)
          ({V}SetGateGuardingClose true)
          (CallFunction|GatePushPlayerInside)
          (Class|BPEnemyBase|EnemyWake :self ({V}GetGateEnemyToWake))
          (Class|BPPlayer|PlayerTrailReset :self ({V}GetPlayerRef))
          (CallFunction|GateSendGoonsHome)))
      (:"Is Not Valid"))))
'''


# ---------------- WBP_HUD (B2). Widget tree (built with UMGToolSet, all "Is Variable"), in draw order on the root
# canvas HudRoot: HitFlash (red 0.25), DownedTint (dark red 0.45), FrozenTint (pale blue 0.25), FreezeFrameTint
# (grey 0.35), FreezeFrameEdges (canvas holding four 18 px cyan bars round the screen edge: FreezeFrameEdgeTop/Bottom/
# Left/Right), RewindTint (amber 0.3) (all full screen, Collapsed at start), RewindBox (canvas 64 x 84, bottom left at 40,-124: RewindIcon amber 64 px square, RewindKey "Q",
# RewindBar 64 x 10), FreezeBox (same at 124,-124: FreezeIcon cyan, FreezeKey "E", FreezeBar), HealthBar
# (400 x 28 at 40,40, red fill). Additions to the note: RewindBox (so "Q" and the bar collapse with the icon),
# DownedTint, FreezeFrameTint + FreezeFrameEdges, RewindTint, HudShowIf, and the Rewind icon also blinks while frozen
# by the boss when Rewind is ready. The Rewind icon blinks 1 / 0.2 four times a second (t*4 - 2*floor(t*2) < 1).
W = '/Game/Game/UI/WBP_HUD.WBP_HUD'
WV = 'Variables|WBP_HUD|'
PL = 'Class|BPPlayer|'
HUD = {}

HUD['EventGraph'] = f'''
(event UserInterface|EventTick (MyGeometry InDeltaTime)
  (Utilities|IsValid ({V}GetHudPlayerRef)
    (:"Is Valid"
      (CallFunction|HudRefresh))
    (:"Is Not Valid"
      (CallFunction|HudFindPlayer))))
'''

HUD['HudFindPlayer'] = f'''
(fn HudFindPlayer ()
  (bind pl (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter :PlayerIndex 0))
    (:then
      ({V}SetHudPlayerRef pl))
    (:CastFailed)))
'''

HUD['HudShowIf'] = '''
(fn HudShowIf (Target Show)
  (if Show
    (Widget|SetVisibility :self Target :InVisibility "HitTestInvisible")
    (else
      (Widget|SetVisibility :self Target :InVisibility "Collapsed"))))
'''

HUD['HudRefresh'] = f'''
(fn HudRefresh ()
  (bind pr ({V}GetHudPlayerRef))
  (Progress|SetPercent :self ({WV}GetHealthBar) :InPercent (/ ({PL}GetHealth :self pr) (Math|Float|Max(Float) ({PL}GetMaxHealth :self pr) 0.01)))
  (bind rcd ({PL}GetRewindCooldownLeft :self pr))
  (Progress|SetPercent :self ({WV}GetRewindBar) :InPercent (- 1.0 (/ rcd (Math|Float|Max(Float) ({PL}GetRewindCooldown :self pr) 0.01))))
  (bind ready (<= rcd 0.0))
  (bind t (Utilities|Time|GetGameTimeinSeconds))
  (bind blinkon (< (- (* t 4.0) (* 2.0 (Math|Float|Floor (* t 2.0)))) 1.0))
  (bind wayout (and ready (or ({PL}GetIsDowned :self pr) ({PL}GetIsFrozenbyBoss :self pr))))
  (Widget|SetRenderOpacity :self ({WV}GetRewindIcon) :InOpacity (select wayout (select blinkon 1.0 0.2) (select ready 1.0 0.35)))
  (CallFunction|HudShowIf :Target ({WV}GetRewindBox) :Show ({PL}GetHasRewind :self pr))
  (bind ffa ({PL}GetFreezeFrameActive :self pr))
  (bind ffcd ({PL}GetFreezeCooldownLeft :self pr))
  (bind ffdrain (/ ({PL}GetFreezeFrameTimeLeft :self pr) (Math|Float|Max(Float) ({PL}GetFreezeFrameDuration :self pr) 0.01)))
  (bind ffcharge (- 1.0 (/ ffcd (Math|Float|Max(Float) ({PL}GetFreezeFrameCooldown :self pr) 0.01))))
  (Progress|SetPercent :self ({WV}GetFreezeBar) :InPercent (select ffa ffdrain ffcharge))
  (Widget|SetRenderOpacity :self ({WV}GetFreezeIcon) :InOpacity (select (or ffa (<= ffcd 0.0)) 1.0 0.35))
  (CallFunction|HudShowIf :Target ({WV}GetFreezeBox) :Show ({PL}GetHasFreezeFrame :self pr))
  (CallFunction|HudShowIf :Target ({WV}GetFrozenTint) :Show ({PL}GetIsFrozenbyBoss :self pr))
  (CallFunction|HudShowIf :Target ({WV}GetHitFlash) :Show (> ({PL}GetHitFlashLeft :self pr) 0.0))
  (CallFunction|HudShowIf :Target ({WV}GetDownedTint) :Show ({PL}GetIsDowned :self pr))
  (CallFunction|HudShowIf :Target ({WV}GetFreezeFrameTint) :Show ffa)
  (CallFunction|HudShowIf :Target ({WV}GetFreezeFrameEdges) :Show ffa)
  (CallFunction|HudShowIf :Target ({WV}GetRewindTint) :Show ({PL}GetIsRewinding :self pr)))
'''

# ---------------- BP_JumpCutGameMode (B2's frame; E1 fills JumpCutFlowSetup's screens and JumpCutFlowTick)
GM = '/Game/Game/Blueprints/BP_JumpCutGameMode.BP_JumpCutGameMode'
MODE = {}
MODE['EventGraph'] = '''
(event EventBeginPlay
  (CallFunction|JumpCutFlowSetup))

(event EventTick (DeltaSeconds)
  (CallFunction|JumpCutFlowTick :DeltaSeconds DeltaSeconds))
'''
MODE['JumpCutFlowSetup'] = f'''
(fn JumpCutFlowSetup ()
  (bind hud (UserInterface|CreateWidget "/Game/Game/UI/WBP_HUD.WBP_HUD_C" :OwningPlayer (Game|GetPlayerController :PlayerIndex 0)))
  ({V}SetHudWidget hud)
  (UserInterface|Viewport|AddtoViewport :self hud :ZOrder 0))
'''
MODE['JumpCutFlowTick'] = '''
(fn JumpCutFlowTick (DeltaSeconds))
'''
# Writing this empty body over a graph that had nodes left one orphan pure node: delete_node it (count with find_nodes).

GRAPHS = {G: GATE, W: HUD, GM: MODE}


def build():
    out = {}
    for base, graphs in GRAPHS.items():
        for name, code in graphs.items():
            out[f'{base}:{name}'] = code.strip()
    return out


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    dst = os.path.join(here, '..', 'JumpCut', 'Saved', 'b2_graphs.json')
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(build(), f, indent=1)
    print('wrote', os.path.normpath(dst), len(build()), 'graphs')
