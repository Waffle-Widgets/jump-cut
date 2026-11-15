# The coworker's hands were tied to her hips

*Sun 15 Nov 2026, about 1:55 PM Pacific — GameStation · Blender 5.3.0 · UE 5.8 · by Fable 5.2 (`claude-fable-5-2`) · on `main`*

- **What we asked for:** first a check, then a fix.

- **Prompt we gave the agent:**

  > did we apply the fixes for the twisted hands and other body parts on the other characters? If not do so.

  The agent checked and answered: player, coworker and goons yes, the boss partly, and recommended leaving it. The
  owner sent a screenshot from behind the coworker:

  > the coworker's hands still look all twisted up, we need to fix this

- **What happened:**

  **The agent's "yes" for the coworker was wrong, and the screenshot said so.** She had been given the same body
  fix as the player early this morning, and a new idle at 8:30 AM. Both were real. Neither had been looked at
  from behind with her arms down.

  **Fault one: the palms faced backward.** `coworker_idle.py` lowers each arm by the shortest turn, which keeps
  whatever roll the sculpt had, and hers has the palms facing back. Measured: the thumbs sat **61 and 58 degrees**
  off pointing forward. The idle now measures that roll from the hand's own bones and shares it across the upper
  arm, forearm and hand (this rig has no twist bones). Left over afterwards: 0.1 degrees.

  **Fault two, found only by fixing fault one: pieces of her hands belonged to her hips.** With the palms turned,
  a chunk of each hand stayed behind on the trousers and a bite of trouser left with the hand. On her rig the
  rest pose hangs the forearms beside the hips, so when the skin was bound a hand was centimetres from the
  cloth, and `collapse_hand_weights.py`'s prune pass gives any vertex that lost everything to the *nearest* bone,
  which for a fingertip beside a hip is the hip. Nothing shows in the pose she was sculpted in.

  `Art/Blender/hand_body_untangle.py` separates them. It took four tries:
  1. *Nearer the hand's line or a body bone?* Shattered the hands. A splayed fingertip is as far from the hand's
     centre line as trouser cloth is from the thigh bone.
  2. *What colour is it?* Her hands are bare skin and everything they touch is navy or teal. Better, but a shard
     tore off along every finger: **the grooves between her fingers are painted as dark lines**, and a vertex on
     one read as cloth.
  3. *Let each vertex take the majority of its neighbours.* The shards went, and a patch of hand that touches the
     hip was voted into the trousers.
  4. *One way only: dark may become skin, never the reverse.* Skin is never misread here, so only the grooves
     need filling. Clean.

  Result: 2,395 hand vertices put wholly on the palm bone, 408 arm-skin vertices freed from body bones, 3,076
  cloth vertices freed from an arm. `rest_delta.py` reads 0.0 degrees against the old body, so her other clips
  still fit.

  ![Before: left hand back, front, side; right hand back, front, side](../media/2026-11-15-coworker-hands-before.png)
  ![After](../media/2026-11-15-coworker-hands-after.png)
  ![In the game](../media/2026-11-15-coworker-hands-in-game.png)

- **Known flaws:**
  - **Checked in Blender up close and in the game only from across the room.** Two attempts to put the game
    camera behind her failed. The owner's own view from behind is the real test.
  - A pale spot remains on each hip where the hand touched it when she was sculpted: skin colour painted onto
    the trousers. It is a texture fault, not fixed here.
  - Her hand is one rigid piece (she has no separate fingers to bend).
  - The boss's animations are still the hand-mapped ones from Thursday, and the crash driver's skin is still
    weighted to his root bone. Neither was touched.

- **What we learned:**
  - "It has the fix" is a statement about history. "It looks right from where the player stands" is the one
    that matters, and only looking answers it.
  - A fault can be hidden by another fault. The backward palms were covering the torn hands.
  - A painted line is not a material boundary. Classify by colour, then fill the thin gaps.
