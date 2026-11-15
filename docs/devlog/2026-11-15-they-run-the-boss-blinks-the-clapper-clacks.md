# 2026-11-15 — They run, the boss blinks, the clapper clacks (Justin's Mac mini)

- **What we asked for:** three things, on the morning of the deadline:
  1. the rescue: "They just slide over right now and should hold hand (if possible) and be running."
  2. "The boss doesn't use the splice ability. It needs to be shown off, and have some kind of warp
     effect/animation."
  3. "When we freeze frame I wonder if we can have a clapperboard appear and clack! To give some more
     pizzazz to the ability triggering."

- **Prompt(s) we gave the agent:** the three sentences above, with one instruction from the project: for
  each item, check first whether the assets exist, and say early if a piece is not possible.

- **What happened:**

  **What exists was checked before anything was built.** The player has run clips (16 retargeted locomotion
  clips and an authored `Run`). The coworker has exactly two clips, `Idle` and `Walk`. Nobody has a
  hand-hold clip, and her hands are a fused mitten with the finger bones folded away, so there is nothing
  to hold with. The boss had no Splice code at all: `BP_BossFreeze` carried a Freeze attack that is
  switched off and a chase-and-punch. The clapperboard already existed as our own code-drawn art
  (`tools/make_clapperboard.py`, blank slate, drawn for the title animation) and had never been imported.

  **1. The rescue is a run now. The hand-hold was left out.** The slide had a plain cause: the director
  moved the player with `SetActorLocation` while the animation blueprint picks its pose from the movement
  component's velocity, which stayed zero. The first attempt kept the teleport and added a velocity for the
  animation to read, and the player crossed the cafe at **900 cm/s instead of 520**: the movement component
  was never off. `MoveLocked` is only acted on when it *changes*, and the director sets it directly, so he
  had been in walking mode all along and the teleport and the walk were adding up. The teleport is gone;
  the director now sets his velocity and feeds movement input, he turns to face the way he runs, and if he
  has not made it by the time the fuse ends he is placed at the safe spot the way she already was.
  The coworker used to chase his position from behind at a walk pose that never played. She now takes a
  spot half a metre behind his left shoulder, catches up fast when she is far, and plays her `Walk` clip at
  1.9x while either of them is moving. Measured in play: he holds 520 cm/s for 1.4 s and stops on the
  spot, she ends 62 cm from him. **They do not hold hands** - the caption still says "You grab her hand and
  run", and what you see is two people running shoulder to shoulder.

  **2. The boss uses Splice, twice over.** A blink is 0.4 s: his body pinches to a sliver and stretches
  upward for 0.2 s, he moves, and he opens back out, with the Splice sound and a burst of the cyan stars
  the player's own power pickup uses at both ends. No new art.
  - *In his intro*, on the line "Let me show you how a scene gets cut", he cuts **out of his own close-up**
    and lands 350 cm nearer the player, so the camera comes home to find him closer than it left him. The
    first version moved him 110 cm toward the lens and filled the frame with his chest and no face.
  - *In the fight* he blinks every 6 seconds, first one 2.5 s in. The first version put him behind the
    player, which is exactly where the camera is: he materialised inside it. He now lands at the player's
    side, alternating left and right, 1.8 m away, and cannot swing for 0.45 s after he lands.
  - The first fight test showed **no blink in 16 seconds**. The on-switch was a new variable defaulting to
    true, and the boss already placed in the level read it as false and its cooldown as zero. The same
    stale-instance trap as last night. It is now written so that every new variable is correct at false and
    zero: the switch is `BossSpliceOff`, and the timings are literals.

  **3. The clapperboard.** Our own drawing, imported for the first time, with a new `SFX_Clapper` made in
  code. It appears open and tilted, snaps shut at 0.16 s with the clack and a 28% pop, holds, and is gone by
  one second. It fires when a power is granted *and* every time the player triggers Freeze Frame himself,
  by watching the player's state from the director, so `BP_Player` was not touched. First try nothing
  appeared: the "was it on last frame" value was read after it had been overwritten, because a Blueprint
  getter is re-read every time it is used.

  **The whole demo was then played start to finish by script** and still reaches the ending card.

- **What we learned:**
  - Read whether the movement component is really off before adding to a scripted move. `MoveLocked` being
    true says nothing about it.
  - A screenshot hitches the game about 0.3 s, which is longer than a 0.4 s effect. The test slows the
    world while the boss is mid-blink so the frames can be told apart.
  - A new Blueprint variable should be right at false and zero, because an actor already placed in the
    level may not pick up any other default.
  - Teleporting an enemy "behind the player" in a third-person game teleports it into the camera.

- **Not checked by a person.** Everything above was played by a script in the editor on the Mac. Nobody has
  held the controller: whether the blink is fair, whether the clack is too loud under the power sting, and
  whether her sped-up walk reads as a run are all for a player to say. Not tested in a packaged Windows build.

- **Media:**
  ![Both of them running out of the cafe](../media/2026-11-15-rescue-both-run.jpg)
  ![The boss pinched to a sliver as he cuts out of his close-up](../media/2026-11-15-boss-cuts-out-of-his-shot.jpg)
  ![The boss arriving at the player's side in the fight](../media/2026-11-15-boss-splice-flank.jpg)
  ![The clapperboard open on the Freeze Frame moment](../media/2026-11-15-clapperboard-on-freeze-frame.jpg)
  ![The clapperboard snapped shut](../media/2026-11-15-clapperboard-shut.jpg)
