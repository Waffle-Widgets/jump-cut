# 2026-11-13 — Splice: the blink that ignores people (GameStation)

- **What we asked for:** the work-order rule. The Team Owner set it on Nov 13: *"We should work on things in
  order of how we are playing through the game, so if we still have work to be done on earlier beats we should
  do that."* By that rule beat 4 — **destroyed buildings** — is the earliest unfinished beat, and `ROADMAP.md`
  says plainly what is missing from it: *"Nothing built. The Splice power itself, and the platforming section
  that needs it."* Beat 4 is also where the Team Owner's beat-5 decision has been waiting:

  > We can let Splice allow the user to get past the attack Stunt Double and attack the boss directly.

- **What Splice is, now that it exists.** A short forward blink: **600 cm**, on a **1.2 s** cooldown, bound to
  **Left Shift** (or the gamepad's **B** / right face button). It is gated on `HasSplice`, which the cleaver
  boss has been handing over since Nov 12 to no effect at all — `PlayerGrantSplice` set a flag that nothing in
  the project ever read. It now opens a power.

- **The direction is the punch direction.** `SpliceStart` takes `GetActorForwardVector`, flattens it to XY and
  blinks along it. That is deliberately the *same* forward vector `PlayerPunch` uses for its arc hit test, so
  there is one rule to learn: you blink where you punch. No separate aim, no camera-relative special case.

- **The one decision that matters, and it is a collision channel.** The blink is a
  `SphereTraceByChannel` on **Visibility**, not a swept move. Unreal's **Pawn** collision preset *ignores* the
  Visibility channel, so the trace sees walls and does not see people. That single choice is what delivers the
  Team Owner's beat-5 call for free: the player blinks straight **through** the stunt double the boss tags in
  and lands on the boss, and there is no special case for the stand-in anywhere in the code. The obvious
  alternative — `SetActorLocation` with `bSweep` true — would have been three words shorter and would have
  stopped dead on the first body in the way, which is the exact opposite of the power.

- **It still cannot go through a wall.** On a blocked trace the player lands at
  `ImpactPoint - direction * SpliceWallBackoff` (45 cm), not at the impact point, so the capsule never finishes
  inside geometry. Backing off is also why the blink can't be used to clip out of the level.

- **Verified by playing it, five ways, with numbers.** Every run drove the real `SpliceStart` on the live PIE
  pawn after `JumpCutStartPlay` (the title screen locks all input until then — see below):

  | Test | Result | Expected |
  |---|---|---|
  | No power yet (`HasSplice` false) | moved **0.0 cm** | 0 — the gate holds |
  | Open plaza, facing +X | moved **600.0 cm** | ~600 |
  | Second blink immediately after | moved **0.0 cm**, cooldown read **0.80** | 0 — on cooldown |
  | Facing a street building whose face is 500 cm away | moved **455.0 cm**, ended at y=455.0 | ~455, *not* 600 |
  | A goon 250 cm directly in front (capsule r=34) | moved **600.0 cm** | ~600 = passed through, not ~205 |
  | The cleaver boss 250 cm directly in front (capsule r=45) | moved **600.0 cm** | ~600 = passed through |

  Neither the goon nor the boss was shoved by the blink. Both drifted ~120 cm during the half-second window
  because they are alive and were walking at the player; that is the chase AI, not the teleport.

- **The HUD gained a third power box.** `SpliceBox` sits third along the bottom-left row (Rewind at 40, Freeze
  at 124, Splice at 208), violet, labelled **SHIFT**, collapsed until `HasSplice` is true, with a bar that
  fills as the cooldown runs down and an icon that dims to 0.35 while it is not ready. It mirrors `FreezeBox`
  exactly.

- **Two traps worth writing down.**
  - `HudShowIf(Target, Show)` is printed **positionally** by `read_graph_dsl`. Writing that back makes the
    writer try to connect `RewindBox` to the function's `self` pin and the whole graph write is rejected
    (*"Could not connect pin RewindBox to self"*). Every `HudShowIf` call has to be written in the
    `:Target` / `:Show` keyword form, not only the new ones.
  - `unreal.Rotator` in Python is **(roll, pitch, yaw)**. Writing `Rotator(0.0, yaw, 0.0)` sets *pitch*, which
    points the forward vector at the sky and gives an XY forward of `(0, 0)`. The first test run reported every
    blink as 0 cm because of this, in my own harness rather than in the game.

- **How it was lost, and where it is.** None of the Unreal work reached disk. The editor's **"Save Content"**
  dialog opened at 17:38:18 UTC, stood for six minutes, and was then clicked through and the editor quit
  (`QUIT_EDITOR`, `UUnrealEdEngine::CloseEditor()`, 17:44:13 UTC) with `BP_Player` and `WBP_HUD` still dirty in
  memory. The likely reason is a good one: the editor was holding ~29 GB of the 5090 and the ComfyUI renders
  needed the card. The compiled assets survive as autosaves, copied out of the rotation to
  `JumpCut/Saved/jcpy/recovered/` (outside git). **`tools/splice_graphs.py` carries the whole recipe** — every
  variable, every graph verbatim, the defaults, the HUD widgets and both traps — so this is a few minutes to
  put back rather than a day to rediscover.

- **What is still not built.** The **platforming section** of beat 4: Splice is the power the gaps are for, and
  there are no gaps yet. Beat 4 is half done. And the Team Owner's other beat-5 decision — *"a timer starts on
  him to disappear once he has nothing in range to attack"* for the tagged-in stand-in — is still unbuilt on
  `BP_StuntStandIn`.

- **Unrelated but undocumented:** the game opens on a title screen that locks input, and nothing moves until
  `JumpCutStartPlay` runs. Any script that drives the player has to press start first or it will read a build
  that looks completely dead. (Recorded once before; it cost time again here.)
