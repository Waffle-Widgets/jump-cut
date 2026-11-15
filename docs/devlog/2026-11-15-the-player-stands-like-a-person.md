# The player stands like a person

*Sun 15 Nov 2026, about 2:15 AM Pacific — GameStation · Blender 5.3.0 · authored and fixed by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** the models looking right, then animation. "The models should look and move like normal
  people."

- **Prompt we gave the agent:**

  > Yes, continue. We need the models looking right. We also need to start working on animations once the models
  > look right. The models should look and move like normal people.

- **What happened:**

  **The first clip is a standing idle, authored on the player's own rig** (`Art/Blender/idle_clip.py`, issue
  #103's route, the second clip made this way after the death). Feet under the hips with the toes a little out,
  weight a touch on his right leg, arms hanging at his sides, fingers loosely curled, one breath every four
  seconds with a slow sway. 121 frames at 30 fps; frame 121 is frame 1, so it loops with no seam.

  ![The idle in Blender: front, three-quarter, side, back](../media/2026-11-15-player-authored-idle-blender.png)

  **Posing him like a person tore his skin, and that was the real find.** With his arms down and feet together
  the body showed 1,581 edges stretched to more than 2.5 times their length, the longest 31 cm: a flap of forearm
  left hanging at the hip, fingertips in shards, flecks through the apron and towel. In the A-pose it was built
  in, nothing shows. The cause is the new body's weights: they were projected from another mesh, and where cloth
  lies in layers a few millimetres apart, or parts are thin, next-door vertices came away following different
  bones. This is also what the speckled patch at his waist tie was.

  `Art/Blender/smooth_weights.py` averages each vertex's weights with its neighbours' along the surface. Six
  passes left 396 torn edges, sixteen left 121, **forty left 4** (5 with the final foot placement), the longest
  2 cm. The hands came out clean with the fingers still separate. Geometry, UVs, rig and texture were checked
  unchanged (27,791 vertices, none moved more than 0.00004 cm).

  ![The hands in the idle pose, after smoothing](../media/2026-11-15-player-idle-hands-after-smoothing.png)

  **Two ways to make the idle, and only one blends.** The death clip keys the pelvis on the root bone, which is
  fine for a clip played alone. This one plays next to the retargeted walks and jogs, which keep the root on the
  floor and let the hip bone carry the pelvis. Mixing the two would sink him by up to 90 cm halfway through a
  blend. So every frame is solved on the pelvis and then re-expressed with the root on the floor.
  `tools/unreal_player_idle_swap.py` reads both clips back in Unreal and refuses to swap unless the roots agree:
  they differ by 0.00 cm and 0.00 degrees.

  **The blend space was the wrong place, and a number said so.** The idle was swapped into the 9 speed-zero
  samples of `BS_Idle_Walk_Run_CWM`, read back correctly, saved, and the game looked the same. Measured live:
  ankles 35.9 cm apart, the old idle's figure, not 21.6. The anim blueprint has its own **Idle state that plays
  the idle clip directly**; the blend space's idle samples are only used on the way into a walk. Pointing that
  state's sequence player at the new clip is what changed the game.

  **Then he hung in the air, and it was the float again.** With the new idle in, a capture one second after the
  start showed him a metre up in a falling pose. Not the idle: the game begins in the falling state, and the
  jump, fall and land clips had lost their root lock in the same rebuild that broke the walks (see
  `2026-11-15-the-float-came-back-with-the-new-legs.md`, which fixed the 20 clips with root motion and missed
  these three, which have root motion off and Force Root Lock on). `tools/b1y_rootlock.py apply` fixed them, and
  `unreal_retarget_meshy.py` now sets the lock for both kinds.

  **In the running game, settled:** ankles 21.6 cm apart (the retargeted idle: 35.9; the rest pose: 60.2), wrists
  43.9 cm apart (was 59.4), hip 84.9 cm above the root, feet on the floor.

  ![The idle in the game](../media/2026-11-15-player-authored-idle-in-game.png)

- **What we learned:**
  - A body can pass every check in the pose it was built in and tear in every other one. Pose it like a person
    and count stretched edges before calling it done.
  - Read the anim blueprint's states before replacing a clip. An asset can be referenced in two places and only
    one of them is on screen.
  - Measure settled, not one second in. The first second of this game is a fall.

- **Not done:** nobody has played it with a keyboard. It takes several seconds after the start to settle into the
  idle (the land-to-idle blend); that was not changed. His soles sit 1 cm above the floor in the clip. The walk,
  jog, jump and punches are still the retargeted clips. Only the player was smoothed: the coworker, goons and boss
  have not been posed and counted.
