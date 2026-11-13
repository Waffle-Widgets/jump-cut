# 2026-11-13 — The boss was walking on the wrong axis (GameStation)

- **What we asked for:** the Team Owner played the build and reported the same fault he had reported the night
  before. In his words:

  > Let's get ready to move work over to M_Station for tonight. 1. Boss 3 will only be in if we can finish
  > everything else. 2. We should use meshy where we can, Trellis can be a backup if we run out of credits.
  > 3. Go ahead and merge to main. I played the fight and the boss is still missing animations.

- **The night before, this was called fixed.** Commit `5920c65` gave the mob boss an anim blueprint, four
  retargeted montages and a walk blend space, and it was signed off with a Play-In-Editor check that read back
  *which montage was playing*. Everything that check looked at was true. The boss still stood still.

- **The bug was one wire.** `BS_Idle_Walk_Run_CB` is a two-axis blend space: **X is Direction** (-180 to 180)
  and **Y is Speed** (0 to 600). `ABP_CleaverBoss`'s AnimGraph had `BossAnimSpeed` plugged into **X**, and left
  **Y at its literal 0**. So the boss's speed was being read as a compass heading, and his speed was always
  zero — which samples the bottom row of the blend space, where every cell is `MM_Idle_CB`. He played a perfect
  idle at 380 cm/s, in every direction, for ever. The montages were never affected, because the Slot node sits
  *downstream* of the blend space: his cleave, his hit react and his death all worked the whole time. It was
  only the walk, which is exactly the half the Team Owner kept reporting.

  The fix: `BossAnimSpeed` → **Y (Speed)**, and **X (Direction)** pinned to the literal `0.0`. Direction 0 is
  correct for this enemy because `EnemyFacePlayer` turns him to face the player every frame before
  `EnemyWalkToPlayer` moves him, so he is always walking forward.

- **How it was checked this time, and why the old check could not have caught it.** Reading back the playing
  montage says nothing about a blend space, and reading back `BossAnimSpeed = 380.0` says nothing about which
  pin it reached. So this time the test measured the **skeleton**: a `register_slate_post_tick_callback` loop
  sampled all 83 bones in component space every frame and reported the largest per-frame movement.

  | | per-frame max bone movement | reading |
  |---|---|---|
  | standing still | **0.03 – 0.06 cm** | idle breathing |
  | walking at 380 cm/s | **2 – 6 cm** | a walk cycle |
  | mid-cleave | **6 – 15 cm** | a montage |

  Fifty to a hundred times more motion while walking than while standing is a walk cycle, measured rather than
  claimed. Before the fix the walking number *was* the standing number — that is the whole defect in one line.
  Nobody has still played this with a controller in their hands.

- **Two traps worth passing on.**

  **A montage can report "playing" for sixty straight frames while the skeleton does not move at all.** That
  happened here, in a session where the game world had stopped ticking: `get_current_active_montage()` happily
  returned `AM_CleaverBoss_Cleave` on every one of those frames with **0.00 cm** of bone movement. It is the
  clearest demonstration yet of why a montage name is not evidence. Bone deltas are.

  **PIE stops advancing after the first script you run in it.** Driving a `py` script through the console box
  takes focus away from the game viewport, and from then on the world stops: actors hold position, `is_game_paused`
  reports `False`, slate ticks keep firing at 120 Hz, and bone movement drops to exactly zero. Only the *first*
  script run after `StartPIE` sees a live world. Every test above was therefore one script, started once, with
  a per-frame tick callback doing the work — stop PIE and start it again for each measurement.

  A third, smaller one: `EnemyTimeStopped` was left `True` on the boss by an earlier freeze in the same session,
  which silently halted his tick. `EnemySetTimeStopped(False)` clears it.

- **What is in:** `ABP_CleaverBoss` (one pin moved, one literal set), compiled with warnings as errors and
  saved. No other asset was touched; the twelve Blueprints that were already dirty in the editor are still
  dirty and still unsaved.

- **What is not:** the player and the goons are still Epic's `SKM_Quinn_Simple` and `SKM_Manny_Simple`, and the
  boss is still the only character in the game wearing one of our models.
