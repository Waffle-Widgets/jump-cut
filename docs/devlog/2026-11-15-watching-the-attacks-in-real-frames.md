# Watching the attacks in real gameplay frames, for the first time

*Sun 15 Nov 2026, about 3:50 AM Pacific — GameStation · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** "The attacks look very stiff still." (owner, after playing)

- **What happened:**

  **Every judgement of an attack so far had been a contact sheet rendered in Blender.** The game was never the
  thing being looked at, because a hit lasts a third of a second and one capture through the MCP takes longer.

  **The recipe that works.** In the Play-mode console: `slomo 0.04`, then `r.DumpingMovie 150`, then trigger the
  hits 11 real seconds apart. The dump itself slows the editor to about 3 frames a second; at a twenty-fifth of
  game speed that puts consecutive PNGs about 0.013 game-seconds apart, 37 frames across one punch. The side
  camera has to be at exactly 90 degrees to his facing: at 70 it sat behind a door frame. `slomo 1` afterwards, and
  delete the frames (150 of them is half a gigabyte).

  ![The lunge in the running game, every third dumped frame](../media/2026-11-15-lunge-real-gameplay-frames.png)
  ![The front kick in the running game](../media/2026-11-15-kick-real-gameplay-frames.png)

  **What the frames show.** The poses are fine. The lunge is fully out within a twentieth of a second, holds for
  about a tenth, reverses straight back to the stand it left, and then he is dead still. And every clip's first
  frame is a rigid neutral stand, so a chained hit - blended in over 0.03 s - cut from the last hit's recovery to
  that stand and only then into the strike. The stiffness is in the joins, not the moves.

  **Changed:** the montages' blend times. In 0.03 -> 0.08 s, so the previous pose carries into the strike (the
  hit still lands by frame 3-4). Out 0.10 -> 0.22 s (0.25 for the finisher), so the settle melts into the idle
  instead of arriving at it. `tools/unreal_player_authored_wire.py` carries the numbers and the reason.

- **Not verified:** the new blend times have not been dumped and watched yet, and nobody has played them.

- **What we learned:**
  - If the instrument is slower than the thing it measures, slow the thing down. Game time is a console command.
  - A clip that starts from a neutral pose is only half authored; the other half is what it is blended in from.
