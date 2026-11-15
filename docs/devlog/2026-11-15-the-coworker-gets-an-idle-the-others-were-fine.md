# The coworker gets an idle; the goons and the boss were fine

*Sun 15 Nov 2026, about 8:35 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** the same care the player got this morning, for everybody else.

- **Prompt we gave the agent:**

  > Can we fix the rest of the models that need fixing and add animations

  The agent pushed back: it is Sunday (bug fixes only), the build was not packaged, and the player alone had
  taken all morning. It measured the four other bodies first and offered a smaller job. The answer:

  > Coworker plus goons and boss

- **What happened:**

  **Measure before fixing.** `Art/Blender/body_audit.py` reads any body's surface with no bone names: how far the
  head sits from the chest, arm thickness left against right, and a front render. The goon, the boss and the
  crash driver came out symmetric and solid. Only the coworker had the player's faults: thin arms, and a pose
  with the arms held out.

  **A wrong guess, caught by reading the game.** The agent had told the owner the coworker "has no idle animation
  at all". She has one. Her placed actor plays `SK_CafeCoworkerArmature_Idle` in Single Node mode; the clip just
  holds the pose she was sculpted in, so it looks like no animation. The fix was a new clip, not a missing wire.
  `BP_Coworker` was locked by Justin, and nothing in it had to change.

  **The coworker.**
  1. Arms 25 % thicker with `model_tuneup.py` (`THICK=1.25 HAND=1.0 HEAD_MAX=0`). Her arm bones have the same
     names as the player's, so the tool ran unchanged. Length, head and skeleton untouched:
     `rest_delta.py` reads 0.0 degrees against the old body, so her other clips still fit.
  2. `Art/Blender/coworker_idle.py`: her A-pose with the arms lowered and the hands hanging, breathing once
     every 4 seconds. Root and hip bones stay at rest, so she stands exactly where she stood.
  3. Imported onto her existing skeleton as `A_CafeCoworker_Idle_Authored`, and
     `tools/unreal_coworker_idle.py apply` pointed the placed `Coworker_Cafe` at it and saved her actor file.

  ![Before: the pose she was sculpted in](../media/2026-11-15-coworker-before.png)
  ![The new idle, front, side and back](../media/2026-11-15-coworker-idle-sheet.png)
  ![In the game](../media/2026-11-15-coworker-idle-in-game.png)

  **The goons and the boss: looked at, not changed.** The first try at photographing them failed twice. An MCP
  round trip is 5-8 seconds and three goons kill the player in about ten, so every capture was either a fist in
  the lens or the "CUT!" screen. What worked: a callback inside the editor's own tick that takes a `HighResShot`
  every 0.35 s (`Saved/npc_pie.py shoot2`). Twelve frames each:
  - Goons: the right anim blueprint is live on all five, feet on the floor, they jog in and drop into a fighting
    stance.
  - Boss: walks with his feet on the floor, cleaver in hand, and swings it.

  Nothing was visibly broken, so nothing was touched. New attack animations for them stay on the cut list.

  ![Goons running in](../media/2026-11-15-goons-run-in.png)
  ![The boss walks and swings](../media/2026-11-15-boss-walks-and-swings.png)

- **Known flaws:**
  - Nobody on the team has played this yet. The coworker was seen standing in Play; her breathing was seen only
    in Blender.
  - Her head still sits about 2 cm off her chest. Moving it changes the skeleton and every clip she has.
  - Her apron straps cross at the back. That is the model, not this change.
  - The boss walks into the player's body when he attacks. That is his reach, not his animation; not changed.

- **What we learned:**
  - "It doesn't animate" and "it plays a clip that doesn't move" look the same on screen. Read the component
    before saying which.
  - When the thing you want to photograph is faster than your camera, put the camera inside the game's own tick.
  - Measuring four bodies took five minutes and took three of them off the list.
