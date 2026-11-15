# A sprinter, a front kick, and an apron that clears his legs

*Sun 15 Nov 2026, about 4:15 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`), two Fable 5.2 helpers on the run and the kick*

- **What we asked for:** four notes after playing the freed apron and the re-timed attacks.

- **Prompt we gave the agent:**

  > Let's make sure the apron does not clip into the character. Can we give him a better run since the Naruto run
  > looks lame. Maybe more of a sprinter run. In the attack animations it looks like his arms are having that same
  > thin issue. His leg looks very odd when he kicks.

- **What happened:**

  **Looked before touching anything.** `shoulder_sheet.py` grew a `scale=` and an `aim=hips`, so the same close-up
  tool can show a whole arm or a whole leg. Three different causes came out of two pictures.

  **Thin arms in the attacks: the fix from the last round put two halves on one joint.** Last round split the upper
  arm's spin between shoulder and elbow, and the forearm roll between elbow and wrist. The elbow got half of each:
  about 70 degrees in a punch, which leaves 82 % of the arm's thickness. The three joints carry two twists, T and P,
  and the split that minimises the squares is the same angle on all three: (T + P) / 3. A punch with T 49 and P 90
  now puts 46 on each (92 %), and where the two oppose they cancel. `cw_clip.py` reports it per clip as
  `arm_joint_twist_deg`: the lunge went from about 70 to 39, the walk and run sit at 32-39.

  **The same sharing now happens inside the solver, for legs too.** A thigh spun at the hip pinches exactly like an
  upper arm spun at the shoulder; `ik2` now leaves half at the top joint and hands half to the knee or elbow.

  **The apron clipped because the clearance check was watching the wrong thing, twice.**
  - Version one watched two guessed points per leg, pushed out by a guessed radius. It let a knee through at full
    drive and threw the skirt straight out in FRONT while a kicking leg went out to the SIDE.
  - Version two samples the real front surface of both legs (848 points) and asks, per point, that it come no closer
    to the skirt than it sits at rest. It reported that a deep lunge needed no room at all. Two bugs: a thigh raised
    to level has its front surface ABOVE the hinge, which the check threw away as "not under the skirt"; and the
    "most forward third of the thigh's vertices" was mostly waistband - the model weights the waistband to the
    thighs, and it swings BACK when the knee comes up.
  - Sampling only below the hip joint: a stand needs 6 degrees, a crouch 25, a raised knee 53. That is the right
    shape.

  At a full knee drive the skirt lies along the top of the thigh, which is what a short apron does.

  **The run: a sprinter.** The owner's three verdicts in order were "Forrest Gump" (upright, tight pump), "lame"
  (the ninja dash), and now "maybe more of a sprinter run". 20 degrees of lean with the head level, a big arm drive
  from behind the hip to the chin with open blade hands, thigh near level at the knee drive, heel tucked under the
  hip, rear leg nearly straight at toe-off, shoulders counter-rotating 13 degrees against 7 at the hips. The
  planted foot still travels exactly 20 cm a frame.

  ![The sprinter from four sides](../media/2026-11-15-sprinter-four-sides.png)
  ![In the game: from behind, the game camera](../media/2026-11-15-sprinter-in-game.png)

  **The kick: the pose was asking for a hip this model does not have.** The roundhouse turned his hips 84
  degrees and rolled the foot 72. Close up, the thigh tapered where it left the body, the knee pointed at the floor
  and the shirt pulled open at his side.

  ![The roundhouse, close up: front, back, his left, his right, above](../media/2026-11-15-roundhouse-leg-close-up.png)

  Sharing the thigh's spin with the knee helped the pinch and not the pose. So the MOVE changed: the second hit is
  now a front thrust kick. Knee up in front on frames 2-3, leg straight out with the heel leading on 4, held on 5,
  torso leaning back 15 degrees as a counterweight, the shin folding back under a knee that stays high for a
  frame. It is a hinge the rig is good at: the thigh's spin went from 64 degrees to 23, and the standing foot does
  not move for all 15 frames. Same length, same impact frame.

  ![The front kick, close up](../media/2026-11-15-front-kick-close-up.png)

  **In the game** the combo plays through all three hits. A hit lasts a third of a second and a capture through the
  MCP takes longer, so the pictures caught the frames around the kick and the uppercut in the air, not the kick at
  full stretch. That was checked in Blender only.

- **Known flaws:**
  - From directly behind, the arm drive is foreshortened; the knee lift and heel kick carry the read.
  - In the front kick the skirt lies over the kicking thigh and hangs below it as a green triangle, because the
    other half only swings part of the way. From directly behind, the kick's lean-back barely shows.
  - The skirt is still two rigid boards sharing a twist. It clears the legs now, but at a level thigh it sticks out
    as a flat panel instead of folding over the knee.
  - The Freeze Frame cast still leaves 72 degrees on one arm's joints (a 140 degree forearm roll for the open palm).
    Nothing plays that clip yet.
  - Nobody has played this round with a keyboard.

- **What we learned:**
  - Sharing a load between neighbours is not the same as sharing it between everyone: check the joint in the
    middle.
  - A sampling rule ("the front third of the vertices on this bone") is a guess about the model. Print three
    poses whose answer you already know before trusting it.
  - When a pose fights the rig, change the move, not the rig, with nine hours to the build.
