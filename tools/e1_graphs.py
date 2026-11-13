# Packets G1 + E1 graphs, written with the Unreal MCP's write_graph_dsl and kept here as text so they can be rebuilt.
# See docs/FIRST_BUILD_DESIGN.md sections 6, 7 and 8 and their "As built (G1/E1)" notes.
# `python tools/e1_graphs.py` writes JumpCut/Saved/e1_graphs.json ({"<graph refPath>": "<dsl>"}).
#
# G1 (the Team Owner's design change, Nov 12 afternoon):
#   BP_Player: class default HasRewind = false (no graph changed: RewindStart, PlayerHealthHitZero and the HUD already
#     read it, so Rewind is parked whole and 0 health goes straight to PlayerLose).
#   BP_SceneMarker: new instance-editable bool MarkerGrantsFreezeFrame (default false) and a component GiftMesh
#     (engine Sphere, M_WarnFreeze unlit cyan, 0.6 scale, 100 cm up, no collision, no shadow, hidden by default).
#     MarkerTickStep now just calls MarkerWinStep (C1's old body, unchanged) then MarkerGiftStep (new): while the marker
#     grants and the player hasn't got Freeze Frame, the sphere shows; the player inside the trigger gets
#     PlayerGrantFreezeFrame (once: after that HasFreezeFrame is true and the sphere hides).
#   BP_BossFreeze: new bool BossUsesFreeze (default false). BossThinkFight only starts the freeze wind-up when it is
#     true (BossStartFreezeWindup itself is unchanged, so a checker can still call it).
#   BP_PlazaGate.GatePushPlayerInside: "slab at the bottom" is now <= 0.01 (was <= 0.0; the slab could rest at 0.00009).
#   Level: Marker_RewindGiven -> Marker_FreezeFrameGiven (MarkerGrantsFreezeFrame true, by the driver), the plaza's old
#     Marker_FreezeFrameGiven -> Marker_BossDefeated, and a new Marker_FreezeFrameDoor at (560, 0, 0), TriggerSphere
#     radius 200 on the instance, MarkerGrantsFreezeFrame true: it covers the whole door gap (x 600..630, |y| < 150), so
#     nobody leaves the cafe without the power (JumpCut/Saved/e1_editor.py markers door 560 200).
#   The placed markers' GiftMesh came in blank (component added after they were placed): set per instance by
#     e1_editor.py gifts / gifts2.
# E1 (screens, losing, restart): BP_Player.PlayerRespawnAtCheckpoint and the whole flow on BP_JumpCutGameMode.
#   New game mode variables FlowState (int), ShowTitleOnStart (bool, default true), RestartDownNow, RestartWasDown,
#   RestartPressedNow (bool; added so "pressed" is stored before RestartWasDown is overwritten), TitleWidget,
#   LoseWidget, WinWidget. Helper functions besides the note's: JumpCutFlowStep, JumpCutTitleStep, JumpCutPlayStep.
#   Widgets WBP_Title / WBP_Lose / WBP_Win (UMGToolSet): ScreenRoot canvas, ScreenBg (full screen), ScreenTitle,
#   KeyBox (240 x 72 light box) and ScreenKey ("R  /  (A)").
#   WBP_HUD: RewindBox and FreezeBox now start Collapsed (designer default), because the HUD doesn't tick while the
#   game mode keeps it Collapsed on the title, and it would otherwise show both icons for its first visible frame.
# Trap hit: BossThinkFight was doubled by write_graph_dsl (17 -> 35 nodes); deleted all but the entry and rewrote (19).
import json
import os

B = '/Game/Game/Blueprints/'
V = 'Variables|Default|'
PL = 'Class|BPPlayer|'
G = {}

# ---------------- BP_SceneMarker
MK = B + 'BP_SceneMarker.BP_SceneMarker:'
G[MK + 'MarkerTickStep'] = '''
(fn MarkerTickStep ()
  (CallFunction|MarkerWinStep)
  (CallFunction|MarkerGiftStep))
'''
G[MK + 'MarkerWinStep'] = f'''
(fn MarkerWinStep ()
  (if ({V}GetMarkerEndsGame)
    (bind inside (CallFunction|MarkerInTrigger))
    (if inside
      ({PL}PlayerReachWin :self ({V}GetPlayerRef)))))
'''
G[MK + 'MarkerGiftStep'] = f'''
(fn MarkerGiftStep ()
  (bind want (and ({V}GetMarkerGrantsFreezeFrame) (not ({PL}GetHasFreezeFrame :self ({V}GetPlayerRef)))))
  (Rendering|SetVisibility :self ({V}GetGiftMesh) :bNewVisibility want)
  (if want
    (bind inside (CallFunction|MarkerInTrigger))
    (if inside
      ({PL}PlayerGrantFreezeFrame :self ({V}GetPlayerRef)))))
'''

# ---------------- BP_BossFreeze
BO = B + 'BP_BossFreeze.BP_BossFreeze:'
G[BO + 'BossThinkFight'] = f'''
(fn BossThinkFight (DeltaSeconds)
  ({V}SetBossFreezeCooldownLeft (- ({V}GetBossFreezeCooldownLeft) DeltaSeconds))
  (bind d (CallFunction|EnemyDistToPlayer))
  (if (and (and ({V}GetBossUsesFreeze) (and (<= ({V}GetBossFreezeCooldownLeft) 0.0) (not ({V}GetEnemyIsWindingUp)))) (<= d ({V}GetBossFreezeRadius)))
    (CallFunction|BossStartFreezeWindup)
    (else
      (CallFunction|EnemyChasePunchStep :DeltaSeconds DeltaSeconds))))
'''

# ---------------- BP_PlazaGate (b2_graphs.py's GatePushPlayerInside with the 0.01 bottom test)
GA = B + 'BP_PlazaGate.BP_PlazaGate:'
G[GA + 'GatePushPlayerInside'] = f'''
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
  (if (<= (.z (Class|SceneComponent|GetRelativeLocation :self ({V}GetGateMesh))) 0.01)
    ({V}SetGateGuardingClose false)))
'''

# ---------------- BP_Player: the respawn (design note section 6, step 1)
PP = B + 'BP_Player.BP_Player:'
_zero = ['RewindCooldownLeft', 'FreezeCooldownLeft', 'HitSafeLeft', 'ComboTimeLeft', 'HitFlashLeft', 'DownedTimeLeft',
         'PunchIntervalLeft']
G[PP + 'PlayerRespawnAtCheckpoint'] = f'''
(fn PlayerRespawnAtCheckpoint ()
  (CallFunction|PlayerFreezeFrameEnd)
  (CallFunction|PlayerStopAllEnemies :Stopped false)
  (CallFunction|PlayerFreezeBreak)
  ({V}SetIsDowned false)
  ({V}SetIsRewinding false)
  ({V}SetIsLost false)
  ({V}SetHasWon false)
  (Transformation|SetActorLocationAndRotation :NewLocation (+ ({V}GetCheckpointLocation) (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z 20.0)) :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw ({V}GetCheckpointYaw)) :bSweep false :bTeleport true)
  (Pawn|SetControlRotation :self (Game|GetPlayerController :PlayerIndex 0) :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw ({V}GetCheckpointYaw)))
  (Components|Movement|StopMovementImmediately :self (Variables|Character|GetCharacterMovement))
  ({V}SetHealth ({V}GetMaxHealth))
''' + '\n'.join(f'  ({V}Set{z} 0.0)' for z in _zero) + f'''
  ({V}SetComboStep 0)
  (CallFunction|PlayerTrailReset))
'''

# ---------------- BP_JumpCutGameMode (design note section 8)
GM = B + 'BP_JumpCutGameMode.BP_JumpCutGameMode:'
SCREENS = (('TitleWidget', 'WBP_Title'), ('LoseWidget', 'WBP_Lose'), ('WinWidget', 'WBP_Win'))
ENEMY = '"/Game/Game/Blueprints/BP_EnemyBase.BP_EnemyBase_C"'
SPAWNER = '"/Game/Game/Blueprints/BP_GoonSpawner.BP_GoonSpawner_C"'
GATECLS = '"/Game/Game/Blueprints/BP_PlazaGate.BP_PlazaGate_C"'


def vis(var, how):
    return f'(Widget|SetVisibility :self ({V}Get{var}) :InVisibility "{how}")'


G[GM + 'JumpCutFindPlayer'] = f'''
(fn JumpCutFindPlayer ()
  (bind pl (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter :PlayerIndex 0))
    (:then
      ({V}SetPlayerRef pl))
    (:CastFailed)))
'''

_setup = [f'''  (bind pc (Game|GetPlayerController :PlayerIndex 0))
  (Input|SetInputModeGameOnly :PlayerController pc)
  (bind hud (UserInterface|CreateWidget "/Game/Game/UI/WBP_HUD.WBP_HUD_C" :OwningPlayer pc))
  ({V}SetHudWidget hud)
  (UserInterface|Viewport|AddtoViewport :self hud :ZOrder 0)
  (Widget|SetVisibility :self hud :InVisibility "Collapsed")''']
for i, (var, wbp) in enumerate(SCREENS):
    _setup.append(f'''  (bind s{i} (UserInterface|CreateWidget "/Game/Game/UI/{wbp}.{wbp}_C" :OwningPlayer pc))
  ({V}Set{var} s{i})
  (UserInterface|Viewport|AddtoViewport :self s{i} :ZOrder 10)
  (Widget|SetVisibility :self s{i} :InVisibility "Collapsed")''')
G[GM + 'JumpCutFlowSetup'] = '(fn JumpCutFlowSetup ()\n' + '\n'.join(_setup) + f'\n  ({V}SetFlowState 0))\n'

G[GM + 'JumpCutFlowTick'] = f'''
(fn JumpCutFlowTick (DeltaSeconds)
  (Utilities|IsValid ({V}GetPlayerRef)
    (:"Is Valid"
      (CallFunction|JumpCutFlowStep))
    (:"Is Not Valid"
      (CallFunction|JumpCutFindPlayer))))
'''

# RestartPressedNow is stored before RestartWasDown is overwritten (pure nodes re-run on every read).
G[GM + 'JumpCutFlowStep'] = f'''
(fn JumpCutFlowStep ()
  (bind pc (Game|GetPlayerController :PlayerIndex 0))
  ({V}SetRestartDownNow (or (Game|Player|IsInputKeyDown :self pc :Key "R") (Game|Player|IsInputKeyDown :self pc :Key "Gamepad_FaceButton_Bottom")))
  ({V}SetRestartPressedNow (and ({V}GetRestartDownNow) (not ({V}GetRestartWasDown))))
  ({V}SetRestartWasDown ({V}GetRestartDownNow))
  (if (== ({V}GetFlowState) 0)
    (CallFunction|JumpCutTitleStep)
    (else
      (if (== ({V}GetFlowState) 1)
        (CallFunction|JumpCutPlayStep)
        (else
          (if (and (== ({V}GetFlowState) 2) ({V}GetRestartPressedNow))
            (CallFunction|JumpCutRestartFromCheckpoint)
            (else
              (if (and (== ({V}GetFlowState) 3) ({V}GetRestartPressedNow))
                (CallFunction|JumpCutRestartWholeLevel)))))))))
'''

G[GM + 'JumpCutTitleStep'] = f'''
(fn JumpCutTitleStep ()
  (if (not ({V}GetShowTitleOnStart))
    (CallFunction|JumpCutStartPlay)
    (else
      {vis('TitleWidget', 'HitTestInvisible')}
      {vis('HudWidget', 'Collapsed')}
      ({PL}PlayerSetInputLocked :self ({V}GetPlayerRef) :Locked true)
      (if ({V}GetRestartPressedNow)
        (CallFunction|JumpCutStartPlay)))))
'''

G[GM + 'JumpCutPlayStep'] = f'''
(fn JumpCutPlayStep ()
  (if ({PL}GetHasWon :self ({V}GetPlayerRef))
    (CallFunction|JumpCutShowWin)
    (else
      (if ({PL}GetIsLost :self ({V}GetPlayerRef))
        (CallFunction|JumpCutShowLose)))))
'''

G[GM + 'JumpCutStartPlay'] = f'''
(fn JumpCutStartPlay ()
  ({V}SetFlowState 1)
  (Input|SetInputModeGameOnly :PlayerController (Game|GetPlayerController :PlayerIndex 0))
  ({PL}PlayerSetInputLocked :self ({V}GetPlayerRef) :Locked false)
  {vis('TitleWidget', 'Collapsed')}
  {vis('LoseWidget', 'Collapsed')}
  {vis('WinWidget', 'Collapsed')}
  {vis('HudWidget', 'HitTestInvisible')})
'''

G[GM + 'JumpCutShowLose'] = f'''
(fn JumpCutShowLose ()
  ({V}SetFlowState 2)
  {vis('LoseWidget', 'HitTestInvisible')}
  {vis('HudWidget', 'Collapsed')})
'''

G[GM + 'JumpCutShowWin'] = f'''
(fn JumpCutShowWin ()
  ({V}SetFlowState 3)
  {vis('WinWidget', 'HitTestInvisible')}
  {vis('HudWidget', 'Collapsed')})
'''

G[GM + 'JumpCutRestartFromCheckpoint'] = f'''
(fn JumpCutRestartFromCheckpoint ()
  ({PL}PlayerRespawnAtCheckpoint :self ({V}GetPlayerRef))
  (bind foes (Actor|GetAllActorsOfClass {ENEMY}))
  (for foe foes
    (Class|BPEnemyBase|EnemyResetToStart :self foe))
  (bind spawners (Actor|GetAllActorsOfClass {SPAWNER}))
  (for sp spawners
    (Class|BPGoonSpawner|GoonSpawnerRespawn :self sp))
  (bind gates (Actor|GetAllActorsOfClass {GATECLS}))
  (for g gates
    (Class|BPPlazaGate|PlazaGateResettoStart :self g))
  (CallFunction|JumpCutStartPlay))
'''

G[GM + 'JumpCutRestartWholeLevel'] = '''
(fn JumpCutRestartWholeLevel ()
  (Game|OpenLevel(byName) :LevelName (Utilities|String|StringToName (Game|GetCurrentLevelName :bRemovePrefixString true))))
'''


def build():
    return {k: v.strip() for k, v in G.items()}


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    dst = os.path.join(here, '..', 'JumpCut', 'Saved', 'e1_graphs.json')
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(build(), f, indent=1)
    print('wrote', os.path.normpath(dst), len(build()), 'graphs')
