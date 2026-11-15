# "This looks worse": the elbow pumped with every breath, and the shoulders I could not level

*Sun 15 Nov 2026, about 5:38 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** the previous pass (arms, and the cartoon look's brightness on the player) made it worse.

- **Prompt we gave the agent:**

  > this looks worse, his shoulders are not even and his arms are bent inwards when they should be straighter.

- **What happened:**

  **Measured in the running game first.** A new `sym` step in the Play helper prints each joint on both sides, in
  his own frame. Shoulders, elbows, wrists and hips were the same height left and right to a millimetre. So the
  skeleton is level and the picture is not.

  ![Before, in the game: hands turned out and curled back in](../media/2026-11-15-idle-front-before.png)

  **The arms. Three causes, all in `clip_idle.py`.**
  - *The elbow pumped.* The wrist was placed 99 % of the arm's length from the shoulder, plus 0.6 cm of breath. On
    an arm that close to straight, 0.6 cm is 20 degrees of elbow: it swung between **3 and 24 degrees** every
    breath. The last pass was checked on frame 1 only. The breath is off the wrist now; the hand rides the shoulder
    and the elbow reads 9 degrees on frames 1, 30, 60 and 90.
  - *16 degrees was still a bend.* The wrist now sits at 99.7 % of the arm's length: 9 degrees.
  - *The hands.* They hung turned out from the forearm with the fingers curled back in, which is what "bent
    inwards" was. The wrist is tipped 15 degrees so the hand continues the line of the forearm, and the fingers are
    looser (25 % curl, was 36 %). Tipping it the other way was rendered too and was worse.

  ![After, in the game](../media/2026-11-15-idle-front-after.png)

  **The shoulders. Not fixed, and here is what was tried.** `posture_check.py` gained a measure of the cloth, not
  the joint: the top of the shoulder at four distances from the centre line. His right shoulder's surface is about
  1 cm higher than his left with the joints level. The model is not symmetric; his right sleeve is 3 to 4 cm
  fatter as well.

  Tipping the two collarbones opposite ways to level the cloth was built at 2.5, 4, 9 and 13 degrees. It does not
  work: at 9 degrees the joints are 4 cm apart, the hands hang at different heights, and he visibly leans the other
  way, while the cloth measure moved less than its own noise. It is left at 0 with the reason beside it.

  One thing the last pass may have made more visible: with the look's brightness at 0.6 instead of 0.95, the
  two-tone shading on him shows, and its key light comes from one side. One shoulder gets the light tone and the
  other the shadow tone. That is inferred from the picture, not tested.

- **Known flaws:**
  - The shoulders are level in the skeleton and about 1 cm uneven in the cloth. Fixing it means editing the mesh.
  - Only the idle changed. The stance the other twelve clips end in still has the old hand.
  - Stills. A person has to watch it breathe.

- **What we learned:**
  - A loop checked on one frame is not checked. The elbow was right on frame 1 and wrong on most of the others.
  - Near a straight limb, a distance is the wrong thing to animate. A centimetre of reach is tens of degrees.
  - Level joints do not make level shoulders on a generated model. Measure what is seen.
  - When a correction moves the thing you can measure (joints, 4 cm) more than the thing you want (cloth, under
    1 cm), it is the wrong correction.
