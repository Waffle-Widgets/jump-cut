# The idle is the A-pose, lowered

*Sun 15 Nov 2026, about 5:55 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** a simpler way to get the idle, from the owner.

- **Prompt we gave the agent:**

  > What was wrong with the original A pose? We could just straighten out the legs a bit and bring the arms down a
  > bit from that pose to have our idle pose.

- **What happened:**

  **What was wrong with the A-pose: nothing, from the front.** Read off the skeleton, the pose the model was
  sculpted in has the arms 30 degrees out from straight down, the feet 60 cm apart and the knees 3 degrees bent.
  It is the one pose where the mesh has no skinning damage at all, because it is the pose it was made in.

  So it was built exactly as asked: arms lowered, feet brought in, nothing else. From the front it looked more
  relaxed than anything from the last six rounds. From the side it showed the two things that ARE wrong with it:

  ![The A-pose with only the arms lowered and the feet in](../media/2026-11-15-a-pose-lowered-untouched.png)

  - his hips sit ahead of his ankles, so he leans back;
  - his head hangs 12 degrees down and he stares at the floor.

  And bringing the feet in from 60 cm bends the knees 19 and 26 degrees unless the hips rise 1.4 cm, since legs
  that were spread are now under him.

  **The idle now.** The A-pose's own upper body, with those three side-view corrections kept:
  - collarbones near where they were sculpted (lift 14, was a squared 36);
  - arms 12 degrees out from straight down (30 in the A-pose), elbows 16 degrees, steady through the loop;
  - palms part-way in, hands open;
  - feet 20 cm apart, knees 10 and 11 degrees.

  ![The idle: the A-pose lowered, standing upright](../media/2026-11-15-idle-from-the-a-pose.png)
  ![In the game](../media/2026-11-15-idle-a-pose-in-game.png)

  **Why this was not the first thing tried.** Every earlier round started from the previous round's pose and added
  a correction on top: squared shoulders, pushed-out arms, a wide stance, rolled wrists. Each one moved the mesh
  further from the pose it was sculpted in. The owner's suggestion throws all of that away and keeps only what the
  side view proves is needed.

- **Known flaws:**
  - The earlier complaint "his shoulders are drooping" was answered with the collarbone lift this removes. If they
    read as droopy again, `SH_UP` is the one number (14 now; 24 is halfway).
  - His arms are still 10 cm short in the model.
  - The other 12 clips still end in the old stance; a blend back to standing moves his feet and hands.
  - Stills, one room. A person has to play it.

- **What we learned:**
  - Start from the pose the model was made in and change as little as possible. Each extra rotation is skin being
    bent somewhere it was not sculpted to bend.
  - Ask "what was wrong with the original?" before the sixth correction, not after.
