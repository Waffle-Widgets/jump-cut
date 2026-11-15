# A hole in his waist, a head the model tilts, and hands with rigor mortis

*Sun 15 Nov 2026, about 8:45 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** four things about the idle after the hero stand went in.

- **Prompt we gave the agent:**

  > Let's make sure the arms and hands look natural and not bent up and riddled with rigor mortis. The shoulders
  > need to be straight not higher on one side than the other. The head needs to be straight not slanted. I noticed
  > there is a gap in his waist right beneath where the apron is tied, this needs to be fixed because you can see
  > right through him.

- **What happened:**

  **The hole.** A tight close-up of his waist showed it at once: a jagged slit under the apron tie, white
  background through it. The cause is what the model is. It is one skin; where the apron covers his waist there
  are no trousers underneath, the apron IS the surface. Cutting the skirt free and swinging it even 12 degrees
  opens the cut, and there is nothing behind.

  ![The slit under the tie, front and both sides](../media/2026-11-15-waist-gap-before.png)

  Two cures were tried and thrown out, each on its picture:
  - *Leave the top of the skirt joined to the body as a hinge.* No hole, but 21 cm webs of stretched cloth at the
    waist in a run (264 stretched edges; the clean skirt has 44).
  - *Keep the skirt's sides on his hips and let only the front swing.* It shredded the skirt: ragged edges, half
    of it left behind.

  The third fills the hole instead of avoiding it. `apron_bones.py` duplicates the top 18 cm of the skirt, pushes
  the copy 0.8 cm toward the body and leaves it with the weights the surface always had. It stays on his hips when
  the skirt swings, and what shows in the gap is cloth. The clean skirt comes back unchanged. (The copy then counted
  as a leg pushing the skirt out - the idle's swing went from 13 degrees to 23 - until the clearance check was told
  to ignore anything within 1.5 cm of the skirt.)

  ![After: cloth behind the tie](../media/2026-11-15-waist-gap-after.png)

  **The head.** `posture_check.py` gained two numbers: how much higher one shoulder is than the other, and how far
  the head leans. The shoulders came out level to a millimetre. The head's BONE leaned 2.7 degrees with a
  perfectly symmetric pose. A close-up in world axes settled it: the model's head is not upright in any level
  pose. It was rendered at three corrections; 4 degrees stands it up, 7 leans it the other way. The correction
  lives in `cw_clip.neck()` so every clip has it, not just the idle.

  ![The head at two strengths of correction: 4 degrees (top) and 7](../media/2026-11-15-head-upright.png)

  **Shoulders.** Level already by the numbers, but the pose around them was not: a turned-out foot, a slight lean,
  one hand drifting. Everything one-sided is gone from the resting pose.

  **Arms and hands.** The hero stand had fists at 85 % curl on arms bent 27 degrees with the elbows pushed out:
  held, not hanging. Now the elbows bend 16 degrees and point back, the hands are open and relaxed (36 %), the
  palms face the thighs.

  ![In the game: front, hands, and the waist from each side](../media/2026-11-15-idle-level-in-game.png)

- **Known flaws:**
  - The backing layer keeps the model's old weights, so in the sprint it stretches under the skirt (206 stretched
    edges, up to 17 cm). It is behind the skirt; nobody has looked for it in the game.
  - From the side its lower edge is a little ragged where the selection ends.
  - Movement and feel: still only stills. A person has to watch the idle.

- **What we learned:**
  - A model that is one skin has nothing under its clothes. Cut any layer free and plan what fills the hole.
  - Three numbers said "level" and the picture said "slanted". When they disagree, find what the numbers are
    measuring: here, a bone, not a face.
  - Two failed cures in a row both tried to stop the gap OPENING. The one that worked let it open and put something
    behind it.
