# The death reaches the game, and the viewport shows something nobody can explain

**Sat 14 Nov 2026 · Justin's Mac mini · UE 5.8 · issues #103 and #14**

Yesterday's devlog ended with the clip authored and merged but **not in the game**: the FBX existed, the import
script existed and had never been run, and `BP_Player` had no death variable. Both halves are done now. The
player's own authored death plays when he loses, on the live pawn, verified in Play mode.

And while looking at it — which is the entire argument of #103 — the level viewport showed the player as a
crumpled ball. That part is **not explained**, and the rest of this entry is as much about what it is not.

## The import

`tools/unreal_import_authored_clip.py` ran against the committed
`Art/Blender/export/Characters/CafeWalker/SK_CafeWalker_Death.fbx`, pinned to
`/Game/Game/Imported/CafeWalker/Meshy/SK_CafeWalker_Skeleton` — the skeleton the player actually wears, which
the script checks **by object identity** and refuses to continue without. It held: one AnimSequence came out,
no second skeleton, no skeletal mesh, nothing stray in the folder.

| measured | value |
|---|---|
| clip length | 1.967 s |
| frames | 59 (`AnimationLibrary.get_num_frames`) |
| `enable_root_motion` | False |
| `root_motion_root_lock` | `ANIM_FIRST_FRAME` |
| montage slot | `DefaultSlot`, 1 segment, pointing at our clip |
| `enable_auto_blend_out` | False — the body holds its last pose |

Two API traps cost two runs, and both are in `CLAUDE.md` now. UE 5.8's `AnimSequence` has neither
`get_number_of_sampled_keys` nor `get_sampling_frame_rate`; the first run died **while logging its own
success** and left the clip on `RefPose` — the float defect of `7ef73e1`, reintroduced by a print statement.
And `FAnimSegment.StartPos` is read-only to Python, so the hand-built montage track could never work; giving
`AnimMontageFactory` a `source_animation` (the recipe `tools/unreal_fight_anims.py` has always used) does.

## The Blueprint half, and a regression the printed graph hid

`PlayerLose` is the single funnel: `PlayerHealthHitZero` calls it when there is no Rewind left, `PlayerTickDowned`
calls it when the grace timer runs out, and `PlayerTickFall` reaches it through health. So the montage goes
there once, guarded so a second call cannot restart the clip:

```
(fn PlayerLose ()
  (if (not (Variables|Default|GetIsLost))
    (Animation|PlayAnimMontage :AnimMontage (Variables|Default|GetPlayerAnimDeath)))
  (Variables|Default|SetIsLost true)
  (CallFunction|PlayerFreezeFrameEnd)
  (CallFunction|PlayerStopAllEnemies :Stopped true))
```

**The DSL does not round-trip a bool parameter, and that is worth more than the feature.** `read_graph_dsl`
prints the existing call as `(CallFunction|PlayerStopAllEnemies true)` — positionally. Writing that back binds
the literal to nothing, the pin falls to its default, and the read-back prints `false`: `PlayerLose` had
quietly stopped stopping the enemies. Nothing failed, nothing warned, and the printed graph is what lied.
Naming the pin (`:Stopped true`) fixes it. Everything here was then verified at **pin level** rather than from
the printed DSL: 9 nodes, no duplicate append, Branch true → `PlayAnimMontage` → `SetIsLost`, Branch false →
`SetIsLost`, `AnimMontage` fed by `PlayerAnimDeath`, `Stopped = true`.

## It plays

In Play mode, on the live pawn, `PlayerLose` called directly: active montage becomes
`AM_CafeWalker_Death_Authored`, `playing=True`, position 0.0000. Read again later: position **1.9666 of
1.9667**, `playing=False`, still the active montage — it runs to the end and holds the final pose instead of
blending out or standing back up. Read again 4.4 game seconds later: identical. The actor's Z never moved
(94.15 throughout), so he neither sinks nor floats.

## And then we looked at it

The clip's own asset preview — real mesh, real clip — reads as a clean backward fall: reeling, one arm up,
legs folding. Beside it, the retargeted `AM_CafeWalker_Death` reads as a hunched fold with the arms wrapped
across the body. That contrast is the case for #103 in one picture.

**The level viewport is another story.** Every `CaptureViewport` of the player in the cafe — alive, dead, mid-
clip — shows a ~50 cm crumpled ball of his clothing at the component origin, while the coworker standing three
metres away renders correctly. It is **not** the authored clip: the retargeted clip, and the reference pose
with no animation at all, look exactly the same.

What was ruled out, each by test rather than by argument:

- **The pose.** All 69 bones measured in Play mode span `z 4.2 … 164.6`, `x ±27`, `y ±43` — a standing human.
- **The mesh and its material.** `SK_CafeWalker`'s own thumbnail renders a correctly clothed standing figure.
- **The material instance.** Swapping every slot to `WorldGridMaterial` on the live component changed nothing
  on screen — which is also the one result that does not fit, and the reason this is filed rather than fixed.
- **The GPU skin cache** (`r.SkinCache.Mode 0`): no change.
- **Hardware ray tracing** (`r.RayTracing.Enable 0`), turned on by `940065c` yesterday: the lighting changed
  completely, the ball did not.
- **A stale frame:** every capture hashes differently, so each is a fresh render.

Filed as its own issue. It may yet be an artefact of capturing an editor viewport on Metal rather than
anything a player would see — and that question is settled by a person looking at the screen, which is exactly
the check this project keeps finding it cannot automate.

## Housekeeping

`EditorLoadingAndSavingUtils.reload_packages` was called to discard an actor package my own Play-mode test had
dirtied. With anything dirty it opens a modal through `FMessageDialog`, the game thread stops, and every MCP
call times out; `osascript` cannot answer it without Accessibility permission. The editor had to be killed.
Everything in this entry was already saved to disk at that point, nothing was restored on the next check, and
the only thing discarded was the test leak — but the rule is in `CLAUDE.md` now: never call it from the MCP.
