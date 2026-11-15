# The apron's fold had no reach, the idle had no life, and the run was a bound

*Sun 15 Nov 2026, about 6:40 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** three things after playing the sprint and the measured stand.

- **Prompt we gave the agent:**

  > something still looks off about the run. He looks way too stiff in his idle stance and his clothes are clipping
  > through the apron.

- **What happened:**

  **Looked first, all three.** Close-ups of the hips and apron in the idle, the run and the kick; the run dumped
  from the running game in slow motion, from the side and from behind.

  **Clothes through the apron: the fold added last night could not see a leg.** When the skirt got its second pair
  of bones, the solver's "length of the skirt" was still measured from the vertices of the UPPER bones only. So the
  skirt's length came out equal to the upper panel's, the lower panel's reach was that minus itself - zero - and
  it never looked for a leg at all. It hung at whatever gravity gave it, straight down through the thigh
  underneath. The debug line that found it: `leg points within reach 0` for both sides in every pose.

  Fixed, and one more thing came out with it. Each apron bone had been made to answer for the whole 30 cm strip the
  two share, which was safe and wrong: both swung to the same angle and the skirt moved as one board. Now each
  bone answers for the points that are mostly its own, swinging far enough that the sheet there clears them given
  that the other bone follows 45 % of the way.

  | pose | upper L / R | lower L / R |
  |---|---|---|
  | standing | 9 / 9 | 5 / 6 |
  | left knee up | 62 / 28 | 67 / 30 |
  | right leg kicking | 40 / 89 | 28 / 61 |

  ![Close-ups: the run and the kick, the skirt draped over the raised leg](../media/2026-11-15-apron-drapes-over-the-leg.png)

  **The idle: measured into place and then left motionless.** The stand tuned against photographs was the same
  pose on both sides with a breath of 0.9 degrees. A person standing still is never symmetric and never still.
  `clip_idle.py` now puts his weight on his right leg with the free hip dropped 3 degrees and the shoulders tipped
  back the other way, the free foot a little forward and turned out, the two hands at slightly different places;
  the chest rises 2 degrees on a breath and takes the collarbones and hands with it, the weight drifts 1.3 cm, the
  head wanders 5 degrees on its own clock, and a faster, smaller settle runs twice per loop. Still on the plumb
  line: head 3 degrees from level, standing hip and shoulder within a centimetre of the ankle.

  ![The idle: both sides and the front](../media/2026-11-15-idle-with-a-weight-shift.png)

  **The run: in real frames it was a bound.** Dumped from the game, the torso was close to upright - 11 degrees hip
  to head, where the script said 20 - while the legs made a huge split and the front foot landed 28 cm ahead of the
  hip joint on a straight leg. That is braking on every step. The stance moved 9 cm back so he lands close under
  his hips, the lean went to 28 degrees in the script (18 measured hip to neck), the rear hand goes further back.

  ![The run in the running game before the change: side](../media/2026-11-15-run-real-frames-before.png)
  ![The run after, four sides](../media/2026-11-15-run-leaning-and-landing-under-the-hips.png)

- **Not verified:**
  - The run after the change was measured in Play (head 22 cm ahead of the hips at 600, was 15) and seen on the
    Blender sheet. It was NOT dumped and watched in the game again; the captures taken caught his first step.
  - The rear foot leaves the floor about a centimetre early at push-off (the leg is 1.7 cm short of the target).
  - Whether the idle now reads as relaxed or as restless is a matter of feel. Every amplitude is a number at the
    top of `clip_idle.py`.

- **What we learned:**
  - A feature added on top of a measurement has to re-check the measurement. The fold doubled the bones and left
    "how long is the skirt" counting half of them.
  - "0 of N within reach" is a better debug line than any picture: it says the code is not looking, not that it
    is looking and getting it wrong.
  - Tuning a pose against a still reference gives a still pose. Measure it, then make it move.
