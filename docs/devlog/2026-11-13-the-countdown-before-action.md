# 2026-11-13 — The countdown before "Action" (GameStation)

- **What we asked for:** the Team Owner read the beat-1 build back and changed the shape of the quick time
  event. In his words:

  > the explosion should go off a couple seconds after picking up the first power. The explosion should trigger
  > a quick time event that puts the user into bullet time for a short duration allowing them to activate their
  > Freeze Frame in time, this way they are given a chance to learn how to use the power. We can have a timer
  > show at 5 seconds remaining on Freeze Frame and an audio countdown like they do when filming just before
  > "Action". We can start working on the latte art minigame after we complete the sequences up until we defeat
  > the Splice boss and add the assets into the game. We should have GameStation create more assets if we aren't
  > making any here. We should also install ComfyUI here in case we need to start generating here so the art
  > stays consistent.

- **The tutorial was teaching the wrong lesson, and that is the whole point of this change.** An hour earlier
  the explosion *froze time for you*: `AutoFreezeOnExplosion` called `FreezeFrameStart` on the player's behalf,
  and you woke up already inside stopped time. That reads well and teaches nothing. The player never presses
  the button, so beat 1 — the demo's only tutorial — never actually shows them that **E** is the power. The new
  shape fixes exactly that: the world slows down *instead of* stopping, and the player has to finish the move
  themselves.

  `AutoFreezeOnExplosion` is gone. `BulletTimeOnExplosion` replaces it and calls the new
  **`PlayerBulletTimeStart`**, which sets global time dilation to **0.25** and starts a window counted in
  **real** seconds, not game seconds — `BulletTimeRealLeft` is decremented by `DeltaSeconds / GetGlobalTimeDilation()`,
  so slowing the world does not also slow the clock that governs how long the slowdown lasts. The window is
  3.5 real seconds. Press **E** inside it and `FreezeFrameStart` calls `PlayerBulletTimeEnd`, dilation snaps
  back to 1.0, and the ten-second freeze takes over. Miss it and dilation returns on its own and the shrapnel
  finishes its flight at full speed.

  The explosion delay moved **1.2 s → 2.0 s**, which is the "couple of seconds" the scene asks for and also
  enough time to notice that something has gone wrong before the world drops into slow motion.

- **The countdown is the film convention, not a generic timer.** `PlayerTickFreezeCountdown` watches the live
  freeze and, once `FreezeFrameTimeLeft` falls to `FreezeCountdownAt` (5 s, against a 10 s freeze), takes
  `Ceil` of the remaining time and plays a pop each time that whole number changes: 5, 4, 3, 2, 1. The **HUD**
  shows the same number as a 140-point outlined figure at the top of the screen (`CountdownText` on
  `WBP_HUD`), and a cyan **PRESS E** sits in the middle of the screen for exactly as long as bullet time is
  running (`QtePrompt`). Both are driven from `HudRefresh` off the player's own state, so neither can drift out
  of sync with the thing it is reporting.

  The "Action" cue deliberately does **not** come from the countdown function. A countdown that ends at zero
  never fires its own zero — by the time `TimeLeft` reaches 0 the freeze has already ended and the tick that
  would have announced it sees an inactive power. So the cue is fired from `PlayerFreezeFrameEnd` itself, which
  is the honest place for it: time resuming *is* "Action". It is also gated behind the existing
  lost/won check, so it does not play over a death.

- **The game had no sound at all, which nobody had written down.** `JumpCut/Content/Game/Audio/` did not
  exist. `tools/make_sfx.py` — a pre-jam script carried in from an earlier project — was still full of a frog
  game's hops and splashes and had never been pointed at this one. It gained `make_jumpcut()`, which
  synthesizes three sounds from sine/square/noise with nothing but the standard library:
  `SFX_CountdownBeep` (a dry 1 kHz pop, the Academy leader's), `SFX_CountdownAction` (a clapperboard crack and
  a rising two-tone) and `SFX_BulletTime` (a tone bending *down* a fifth, so it can never be mistaken for the
  countdown's pops). They are ours, so there is nothing to credit. They imported into Unreal by the editor's
  own auto-import simply by being copied into `Content/` — worth knowing, because this project had previously
  recorded that auto-import *ignores* `.glb` and apparently concluded it was off.

- **Checked by playing it, with one honest gap.** Four Play-In-Editor runs. Touching the driver sets
  `HasFreezeFrame`; 2 s later the explosion fires, the shrapnel spawns, and bullet time engages **on its own**
  with the world measured at **exactly 0.25** dilation and the freeze still unused — the window is genuinely
  open and waiting for the player. Driving the real `FreezeFrameStart` from inside it flipped
  `FreezeFrameActive` true, `BulletTimeActive` false and dilation back to **1.0** in the same frame, with 10 s
  on the freeze. The countdown then stepped down and was caught at `FreezeCountdownLast = 1` with 0.146 s left,
  and reset itself to 0 when the freeze ended and the 20 s cooldown started. The fail branch was confirmed too,
  by accident: letting the window lapse killed the coworker **once**, with `RescueTriesUsed = 1` and no
  restart. The output log has no Blueprint runtime errors.

  The gap: **nobody has heard the sounds and nobody has pressed a key.** `PlaySound2D` is called with assets
  that are assigned and valid, and the countdown's trigger logic is verified by state, but a silent build and a
  working one look identical from here.

- **Two traps, one of them the same one as last time.** The placed `Coworker_Cafe` again read
  `BulletTimeOnExplosion = false` — a variable that had existed for about thirty seconds — and
  `ExplosionDelay = 1.2` after the class default was already 2.0. It was checked because this project had
  written the lesson down, and a reload from disk afterwards confirmed the committed actor package plus the new
  defaults give the right values. The second was mine: the first version of the test hook reset its own trigger
  flag *before* comparing it, and a Blueprint pure getter is re-evaluated at each use, so the comparison read
  back the zero it had just written. Compare first, write second.

- **What is not built, deliberately.** The **latte art minigame** stays cut for now, which is now a sequenced
  decision rather than an open question: the Team Owner's order is to finish the beats up to and including
  the Splice boss and get the assets in, *then* build it. And the **explosion still has no cause** in the
  fiction — it is a 2.0 s timer after the power lands.

- **ComfyUI is being installed on GameStation.** M Station has had ComfyUI + Qwen-Image on its 3090 since the
  cast was drawn; GameStation has the RTX 5090, TRELLIS.2 and Pixal3D but no way to draw the *reference
  pictures* that image-to-3D needs. `tools/install_comfyui.sh` closes that gap, pinned to the exact model
  filenames `tools/gen_images.py` already asks for (`qwen_image_2512_fp8_e4m3fn`,
  `qwen_2.5_vl_7b_fp8_scaled`, `qwen_image_vae`) so the art stays consistent rather than merely local. It is
  running as a background job as this is written; it is idempotent and resumable, because ~45 GB of weights on
  feature-freeze night is exactly the kind of thing that gets interrupted.
