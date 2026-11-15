# Every action now starts and ends on the measured stand

*Sun 15 Nov 2026, about 5:00 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** the idle had been tuned against photographs of people standing, but every attack still
  began and ended on the older stand and blended to it.

- **Prompt we gave the agent:**

  > Yes, fix attack stance

- **What happened:**

  **Eight scripts, three different pose-table formats, one stand.** The lunge, the kick, the uppercut and the hit
  react share one engine; jump, land and the two power casts share another; each has its own "neutral" written in
  as numbers, and each action's settle keys are written RELATIVE to those numbers. Changing the neutral in eight
  places would have shifted every key that inherits from it and left the ones that do not.

  **So the difference is added, not the stand replaced.** `cw_clip.py` now holds the gap between the old stand and
  the measured one in one table (`STANCE`: pelvis 6.5 cm back and 5 degrees forward, spine, head 12 degrees up,
  hands in and a little forward, collarbones). `author()` takes `stance=(a, b)` and adds that gap to whatever the
  script poses: in full on the first frame, fading out by the time the action takes over, fading back in for the
  settle. The feet are never touched; both stands plant them in the same place. Each script changed by one
  argument.

  | clip | fades out by | fades back in from |
  |---|---|---|
  | lunge, kick | 14 % | 55 % |
  | uppercut | 12 % | 72 % |
  | hit react | 12 % | 55 % |
  | jump | 20 % | (ends in the air) |
  | land | (starts crouched) | 45 % |
  | Freeze Frame cast, Splice blink | 15-18 % | 55-60 % |

  **Measured.** `posture_check.py` on the lunge's first and last frames: hips and shoulders within 2 cm of the
  ankle line (were 6 and 13 cm off it), head 6 degrees from level (was 12 down), hands 9 cm outside the hips (were
  17). Same as the idle to within a centimetre or two.

  **And watched in the game,** with the slow-motion frame dump from the previous entry: he leaves an upright stand,
  there is one in-between frame from the longer blend-in before the lunge is fully out, the recovery is graded
  over six frames, and he arrives back on the idle with no pop. That is also the first look at the softer montage
  blends, which went in an entry ago unwatched.

  ![The lunge in the running game, every third dumped frame](../media/2026-11-15-lunge-from-and-to-the-measured-stand.png)

- **Not verified:** only the lunge was dumped and watched. The other seven clips were rebuilt and re-imported with
  the same mechanism and their numbers read, but not looked at in the game.

- **What we learned:**
  - When eight files each hold a copy of one fact, do not edit eight copies: put the CORRECTION in the one place
    they all pass through.
  - An additive fix that fades with time leaves the authored action alone, which is the part people already
    signed off.
