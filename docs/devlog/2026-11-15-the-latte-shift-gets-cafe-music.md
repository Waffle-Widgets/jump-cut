# 2026-11-15 — The latte shift gets cafe music, and the crash starts the game's track (Justin's Mac mini)

- **What we asked for:** "There's a latte mini game before our car crash now. We should have some different music
  during that part. Then the current music can play once the car smashes through the wall."

- **Prompt(s) we gave the agent:** the message above, relayed with the boss-camera fix.

- **What happened:**

  **Before:** the latte shift (merged an hour earlier in PR #134) counted as "playing", so the gameplay track
  started the moment you left the title and ran under the whole shift, then went silent for the opening and came
  back when it ended.

  **The track.** `MUS_LatteCafe`, generated from code by `tools/make_sfx.py <folder> latte`: 84 BPM, 16 bars,
  **45.7 s**, D major, Dmaj7 - Bm7 - Em7 - A7 on a soft electric piano, a walking bass, brushes on a lazy swing, and
  a sparse vibes-like melody in the second half. Rendered into the same wrap-around buffer as our other loops, so
  the loop point has no seam, and levelled to the same **0.22 peak** as `MUS_Title` / `MUS_Gameplay` (about 12 dB
  under the sound effects). Imported by the auto-import watcher, `bLooping` set and read back true. **Ours: no
  credit needed, and it counts as scored work.**

  **The wiring, in `BP_OpeningDirector`, still one music component and one track at a time:**
  - New `CineMusicLatte` finds the `BP_LatteGame` in the level and reads its `LatteDone` - read only, so the latte
    Blueprint was not touched.
  - `CineMusicApply` now picks: title track on the title; **cafe track** while the shift is on **and on into the
    opening until the wall breaks**; then the gameplay track (or the boss track once the intro has run), with the
    existing ducks under the cinematics and silence on the end screens unchanged.
  - **The choice asked for: cut dead at the wall break, not a fade at the start of the opening.** The cafe plays
    on through the calm first 4.7 s of the opening, so the crash interrupts it - and the cut lands exactly under the
    crash sound, which masks it. The gameplay track then comes in with the player's usual 0.8 s fade-in. It no
    longer waits for the opening to end.
  - `UseGeneratedMusic` still swaps tracks 1-3; the cafe track is ours in both modes.

  **One bug found by the test and fixed before committing:** on the single frame between clocking out and the
  opening starting, the rule said "gameplay", so the gameplay track started for one frame and the cafe track
  restarted from bar one. Now "before the wall breaks and before the opening has finished" counts as cafe.

  **Measured in PIE** (`tools/c3_pie.py music`: title, the real `JumpCutStartPlay`, `LatteClockOut`, the real
  opening, then a whole-level restart), music component on every frame:
  - title: `MUS_TitleMystery`, playing, level 1.0
  - latte shift: `MUS_LatteCafe`, playing, level 1.0 (switched on the first frame of the shift)
  - clock-out and the first 4.7 s of the opening: still `MUS_LatteCafe` - **no restart** (second run)
  - wall break at opening t = **4.696 s**: next frame (t = 4.72) `MUS_Gameplay_Sourced`
  - after the opening and in play: `MUS_Gameplay_Sourced`, level 1.0
  - `UseGeneratedMusic` on: track 2 -> `MUS_Gameplay`, cafe -> `MUS_LatteCafe`; off again -> `MUS_Gameplay_Sourced`
  - whole-level restart: back to `MUS_TitleMystery` with the shift reset
  - never two tracks: there is only one music component, and every switch replaces its sound

- **Not checked:** **nobody has heard any of it.** The boss track and the ducks were not re-run (that code did not
  change). A restart from the lose screen was not run separately; it reloads the level, which is what was tested.

- **Justin, listen for:** the cafe loop under the shift (and its loop point at 45.7 s if you linger), whether it is
  too loud or too quiet against the pour sounds, and the moment the car hits the wall - the cafe music should stop
  on the crash and the game's track come in right after.

- **What we learned:**
  - A rule built from flags that change on different frames (clocked out, opening running) has a gap one frame
    wide. Sampling every frame found it; sampling at "the moments that matter" would not have.
