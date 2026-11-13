# Splice (power 2, beat 4) on BP_Player, plus the HUD box for it.
#
# WHY THIS FILE IS THE SOURCE OF TRUTH RIGHT NOW
# ----------------------------------------------
# All of this was built and VERIFIED in Play-In-Editor on GameStation on Fri Nov 13 2026,
# 17:28-17:40 UTC (measurements in docs/devlog/2026-11-13-splice-the-blink-that-ignores-people.md).
# It was then LOST before it reached disk: the editor's "Save Content" dialog was clicked through
# and Unreal quit (log: QUIT_EDITOR at 17:44:13 UTC) while BP_Player and WBP_HUD were still dirty
# in memory. The compiled assets survive only as autosaves, kept outside git at
#   JumpCut/Saved/jcpy/recovered/BP_Player_Auto2.uasset   (17:37:17 UTC - has all of the below)
#   JumpCut/Saved/jcpy/recovered/WBP_HUD_Auto2.uasset     (17:37:17 UTC - has the four widgets,
#                                                          but PRE-dates the HudRefresh edit)
# Restoring from those is one option. Re-running the recipe below is the other, and it is the one
# known to reproduce exactly what was tested.
#
# THE RECIPE, in order. Every id here compiled with warnings_as_errors and was read back.
#
# 1. BP_Player variables (BlueprintTools.add_variable on /Game/Game/Blueprints/BP_Player.BP_Player):
#       float: SpliceDistance SpliceCooldown SpliceCooldownLeft SpliceTraceRadius
#              SpliceWallBackoff SpliceFlashTime SpliceFlashLeft
#       bool:  SpliceDownNow SpliceWasDown
# 2. add_function_graph(graph_name="SpliceStart"), then write SPLICE_START below.
# 3. Overwrite PlayerTickInput with TICK_INPUT and PlayerTickTimers with TICK_TIMERS below.
# 4. compile_blueprint(warnings_as_errors=True), then ObjectTools.set_properties on
#    /Game/Game/Blueprints/BP_Player.Default__BP_Player_C with DEFAULTS below.
# 5. HUD: HUD_WIDGETS and HUD_REFRESH_PATCH at the bottom.
#
# DESIGN NOTES WORTH KEEPING
#  - Direction is (Transformation|GetActorForwardVector) flattened to XY, the SAME forward that
#    PlayerPunch uses for its arc test. You blink where you punch.
#  - The trace is Collision|SphereTraceByChannel on TraceTypeQuery1 (Visibility), bIgnoreSelf
#    true; every pin was checked with get_node_infos. Visibility is the whole point: the Pawn
#    collision preset IGNORES the Visibility channel, so the blink passes THROUGH characters and
#    stops only on world geometry. That is what makes the Team Owner's beat-5 call work - "Splice
#    lets the user get past the attack Stunt Double and attack the boss directly" - with no
#    special case for the stand-in anywhere. Measured: the full 600 cm through a goon (capsule
#    r=34) and through the cleaver boss (r=45), with neither of them shoved.
#  - On a blocked trace we land at ImpactPoint - dir * SpliceWallBackoff, NOT at the impact point,
#    so the capsule never ends up inside the wall. Measured against the street building face at
#    y=500, starting from y=0: ended at y=455.0, i.e. 455 cm travelled instead of 600.
#  - DO NOT use SetActorLocation with bSweep true instead of the trace. Sweeping blocks on pawns,
#    which breaks the one thing this power exists to do.
#  - Velocity is deliberately NOT touched. A first attempt zeroed the Z component, but
#    `Class|MovementComponent|SetVelocity` silently resolved to `Class|ABPUnarmed|SetVelocity`
#    (the anim blueprint's own Velocity variable) with the movement component wired into it.
#    If anyone wants a momentum-killing blink later, check the resolved id in the read-back.

SPLICE_START = r'''
(fn SpliceStart ()
  (if (not (or (not (Variables|Default|GetHasSplice)) (> (Variables|Default|GetSpliceCooldownLeft) 0.0)))
    (bind canact (CallFunction|PlayerCanAct))
    (if canact
      (bind start (Transformation|GetActorLocation))
      (bind raw (Transformation|GetActorForwardVector))
      (bind dir (Math|Vector|Normalize (Math|Vector|MakeVector (.x raw) (.y raw))))
      (bind goal (+ start (* dir (Variables|Default|GetSpliceDistance))))
      (bind (hit ok) (Collision|SphereTraceByChannel :Start start :End goal :Radius (Variables|Default|GetSpliceTraceRadius) :TraceChannel "TraceTypeQuery1" :bTraceComplex false :bIgnoreSelf true))
      (bind (bb io tm dist loc ip nrm inrm pm hitactor comp hbn bn hi ei fi ts te) (Collision|BreakHitResult hit))
      (bind stopshort (- ip (* dir (Variables|Default|GetSpliceWallBackoff))))
      (bind land (select ok stopshort goal))
      (Variables|Default|SetSpliceCooldownLeft (Variables|Default|GetSpliceCooldown))
      (Variables|Default|SetSpliceFlashLeft (Variables|Default|GetSpliceFlashTime))
      (Transformation|SetActorLocation :NewLocation land :bSweep false :bTeleport true))))
'''

# PlayerTickInput: the ONLY changes from what was there are the SpliceDownNow poll, the
# SpliceStart edge-detect branch, and the SpliceWasDown write. Left Shift / gamepad B.
TICK_INPUT = r'''
(fn PlayerTickInput ()
  (bind _returnvalue (Game|GetPlayerController 0))
  (Variables|Default|SetAttackDownNow (or (Game|Player|IsInputKeyDown _returnvalue "LeftMouseButton") (Game|Player|IsInputKeyDown _returnvalue "Gamepad_FaceButton_Left")))
  (Variables|Default|SetRewindDownNow (or (Game|Player|IsInputKeyDown _returnvalue "Q") (Game|Player|IsInputKeyDown _returnvalue "Gamepad_LeftShoulder")))
  (Variables|Default|SetFreezeDownNow (or (Game|Player|IsInputKeyDown _returnvalue "E") (Game|Player|IsInputKeyDown _returnvalue "Gamepad_RightShoulder")))
  (Variables|Default|SetInteractDownNow (or (Game|Player|IsInputKeyDown _returnvalue "F") (Game|Player|IsInputKeyDown _returnvalue "Gamepad_FaceButton_Top")))
  (Variables|Default|SetSpliceDownNow (or (Game|Player|IsInputKeyDown _returnvalue "LeftShift") (Game|Player|IsInputKeyDown _returnvalue "Gamepad_FaceButton_Right")))
  (if (and (and (Variables|Default|GetAttackDownNow) (not (Variables|Default|GetAttackWasDown))) (<= (Variables|Default|GetPunchIntervalLeft) 0.0))
    (Variables|Default|SetPunchIntervalLeft (Variables|Default|GetPunchInterval))
    (CallFunction|PlayerPunch))
  (if (and (Variables|Default|GetRewindDownNow) (not (Variables|Default|GetRewindWasDown)))
    (CallFunction|RewindStart))
  (if (and (Variables|Default|GetFreezeDownNow) (not (Variables|Default|GetFreezeWasDown)))
    (CallFunction|FreezeFrameStart))
  (if (and (Variables|Default|GetInteractDownNow) (not (Variables|Default|GetInteractWasDown)))
    (CallFunction|PlayerInteract))
  (if (and (Variables|Default|GetSpliceDownNow) (not (Variables|Default|GetSpliceWasDown)))
    (CallFunction|SpliceStart))
  (Variables|Default|SetAttackWasDown (Variables|Default|GetAttackDownNow))
  (Variables|Default|SetRewindWasDown (Variables|Default|GetRewindDownNow))
  (Variables|Default|SetFreezeWasDown (Variables|Default|GetFreezeDownNow))
  (Variables|Default|SetInteractWasDown (Variables|Default|GetInteractDownNow))
  (Variables|Default|SetSpliceWasDown (Variables|Default|GetSpliceDownNow)))
'''

# PlayerTickTimers: the only change is the last two clauses.
TICK_TIMERS = r'''
(fn PlayerTickTimers (DeltaSeconds)
  (if (> (Variables|Default|GetComboTimeLeft) 0.0)
    (Variables|Default|SetComboTimeLeft (Math|Float|Max(Float) 0.0 (- (Variables|Default|GetComboTimeLeft) DeltaSeconds))))
  (if (> (Variables|Default|GetPunchIntervalLeft) 0.0)
    (Variables|Default|SetPunchIntervalLeft (Math|Float|Max(Float) 0.0 (- (Variables|Default|GetPunchIntervalLeft) DeltaSeconds))))
  (if (> (Variables|Default|GetHitFlashLeft) 0.0)
    (Variables|Default|SetHitFlashLeft (Math|Float|Max(Float) 0.0 (- (Variables|Default|GetHitFlashLeft) DeltaSeconds))))
  (if (> (Variables|Default|GetHitSafeLeft) 0.0)
    (Variables|Default|SetHitSafeLeft (Math|Float|Max(Float) 0.0 (- (Variables|Default|GetHitSafeLeft) DeltaSeconds))))
  (if (> (Variables|Default|GetRewindCooldownLeft) 0.0)
    (Variables|Default|SetRewindCooldownLeft (Math|Float|Max(Float) 0.0 (- (Variables|Default|GetRewindCooldownLeft) DeltaSeconds))))
  (if (> (Variables|Default|GetFreezeCooldownLeft) 0.0)
    (Variables|Default|SetFreezeCooldownLeft (Math|Float|Max(Float) 0.0 (- (Variables|Default|GetFreezeCooldownLeft) DeltaSeconds))))
  (if (> (Variables|Default|GetSpliceCooldownLeft) 0.0)
    (Variables|Default|SetSpliceCooldownLeft (Math|Float|Max(Float) 0.0 (- (Variables|Default|GetSpliceCooldownLeft) DeltaSeconds))))
  (if (> (Variables|Default|GetSpliceFlashLeft) 0.0)
    (Variables|Default|SetSpliceFlashLeft (Math|Float|Max(Float) 0.0 (- (Variables|Default|GetSpliceFlashLeft) DeltaSeconds)))))
'''

DEFAULTS = {
    "SpliceDistance": 600.0,    # cm per blink
    "SpliceCooldown": 1.2,      # s
    "SpliceCooldownLeft": 0.0,
    "SpliceTraceRadius": 30.0,  # the player capsule is r=34; 30 lets him through where he fits
    "SpliceWallBackoff": 45.0,  # how far short of a wall he lands
    "SpliceFlashTime": 0.35,    # HUD pulse; stored and ticked, not yet read by the HUD
    "SpliceFlashLeft": 0.0,
    "SpliceDownNow": False,
    "SpliceWasDown": False,
}

# --- HUD ---------------------------------------------------------------------------------
# WBP_HUD gains a SpliceBox mirroring FreezeBox/RewindBox exactly, violet (0.62, 0.35, 1.0),
# sitting third along the bottom-left row: RewindBox Left=40, FreezeBox Left=124, SpliceBox 208.
# UMGToolSet.AddWidget under WidgetTree.HudRoot, then ToggleWidgetAsVariable TRUE on SpliceBox
# and SpliceKey -- AddWidget leaves panels and text blocks as non-variables, while images and
# progress bars come out as variables already, and HudRefresh cannot reference a non-variable.
HUD_WIDGETS = [
    # (name, class, parent, slot offsets, extra properties)
    ("SpliceBox", "/Script/UMG.CanvasPanel", "HudRoot",
     {"Left": 208.0, "Top": -124.0, "Right": 64.0, "Bottom": 84.0},
     {"Visibility": "Collapsed",
      "_anchors": {"Minimum": {"X": 0.0, "Y": 1.0}, "Maximum": {"X": 0.0, "Y": 1.0}}}),
    ("SpliceIcon", "/Script/UMG.Image", "SpliceBox",
     {"Left": 0.0, "Top": 0.0, "Right": 64.0, "Bottom": 64.0},
     {"ColorAndOpacity": {"R": 0.62, "G": 0.35, "B": 1.0, "A": 1.0}}),
    ("SpliceKey", "/Script/UMG.TextBlock", "SpliceBox",
     {"Left": 0.0, "Top": 18.0, "Right": 64.0, "Bottom": 32.0},
     {"Text": "SHIFT", "Justification": "Center", "Font": {"Size": 15.0},
      "ColorAndOpacity": {"SpecifiedColor": {"R": 0.05, "G": 0.05, "B": 0.05, "A": 1.0}}}),
    ("SpliceBar", "/Script/UMG.ProgressBar", "SpliceBox",
     {"Left": 0.0, "Top": 72.0, "Right": 64.0, "Bottom": 10.0},
     {"Percent": 1.0, "FillColorAndOpacity": {"R": 0.62, "G": 0.35, "B": 1.0, "A": 1.0}}),
]

# Three lines added to WBP_HUD:HudRefresh, immediately after the FreezeBox line, plus one bind
# with the other cooldown binds at the top of the function.
#
# TRAP: HudShowIf takes a Target parameter, and read_graph_dsl prints it POSITIONALLY. Writing
# it back positionally makes the writer try to connect RewindBox to the `self` pin and the whole
# write is rejected ("Could not connect pin RewindBox to self"). Use the :Target / :Show keyword
# form for EVERY HudShowIf call in the function, not only the new ones.
HUD_REFRESH_PATCH = r'''
  (bind _splicecooldownleft (Class|BPPlayer|GetSpliceCooldownLeft _hudplayerref))
  ...
  (Progress|SetPercent (Variables|WBP_HUD|GetSpliceBar) (- 1.0 (/ _splicecooldownleft (Math|Float|Max(Float) (Class|BPPlayer|GetSpliceCooldown _hudplayerref) 0.01))))
  (Widget|SetRenderOpacity (Variables|WBP_HUD|GetSpliceIcon) (select (<= _splicecooldownleft 0.0) 1.0 0.35))
  (CallFunction|HudShowIf :Target (Variables|WBP_HUD|GetSpliceBox) :Show (Class|BPPlayer|GetHasSplice _hudplayerref))
'''

if __name__ == '__main__':
    import json
    print(json.dumps({'defaults': DEFAULTS,
                      'widgets': [w[0] for w in HUD_WIDGETS],
                      'graphs': ['SpliceStart', 'PlayerTickInput', 'PlayerTickTimers',
                                 'WBP_HUD:HudRefresh']}, indent=1))
