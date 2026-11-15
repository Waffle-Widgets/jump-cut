# Arms that hang straight, and a face that is not bleached white

*Sun 15 Nov 2026, about 5:50 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** two things seen in the game after the level idle went in.

- **Prompt we gave the agent:**

  > From the front his arms look oddly bent. Also the lighting looks wrong, can you fix the lighting?

- **What happened:**

  **The arms.** The last pass made the elbows soft (16 degrees) and called that relaxed. From the side it was. From
  the front the upper arm ran down beside the ribs and the forearm then flared out to a hand 15 cm outside the hip:
  a bow, out at the elbow and out again at the wrist.

  ![Before: the forearms flare away from the hips](../media/2026-11-15-idle-arms-before.png)

  Two numbers in `clip_idle.py` did it. `ELBOW_OUT` 0.3 pointed the elbow a little sideways, so part of its bend
  showed in the front view; it is 0 now, the elbow points straight back and the bend is fore-and-aft only. `ARM_OUT`
  put the wrist 8.5 cm outside the shoulder; three values were rendered from the front (3.0, 4.5, 4.5 with the
  elbow turned IN) and 4.5 is the one where the arm is one line from shoulder to hand and the hand still clears the
  hip. Turning the elbow in made it worse.

  ![After: one line from shoulder to hand](../media/2026-11-15-idle-arms-hang-straight.png)

  Only the idle was rebuilt. The stance the other twelve clips start and end in was not changed.

  **The lighting.** "The lighting" could have meant the room or him, so the first step was a picture from Play,
  cropped to him. His face and arms were flat white with no eyes, and his khaki shirt was nearly white too. The
  coworker standing in the same frame, in the same light, kept her skin tone. So it is not the room's lights.

  ![Before: bleached. The coworker behind him is lit normally](../media/2026-11-15-player-washed-out-before.png)

  This is the cause ticket #72 already names: the cartoon look (`MI_AnimeLook_JumpCut`) shades anything that writes
  custom depth with its own `Char*` numbers, the player is the only thing that does, and `CharLevel` was 0.95. On
  top of that the room's brightness multiplies it by up to 1.21 (`CharEnv` 0.35), so his lit colour was pushed to
  about 1.15 times its texture and anything pale clipped.

  Two values were photographed in Play:
  - **0.6:** the shirt is khaki, the apron is its own green, the face has eyes.
  - **0.5:** the skin is no better and the apron and trousers go muddy.

  0.6 is saved. `tools/unreal_look_char.py` reads and sets these numbers on the material that is really in the
  level (not `MI_AnimeLook`, which is a different asset and the trap that cost a day earlier).

  ![After, CharLevel 0.6](../media/2026-11-15-player-lit-right-after.png)

- **Known flaws:**
  - His skin is still very pale. That is his texture: it is that pale in Blender too, where nothing of ours shades
    it. Turning the level down further only darkens his clothes. A warmer skin means repainting the texture.
  - The hands still read as flat shapes at game distance (#72's other half, the smoothing width). Not touched.
  - Checked in one room only, the cafe. Nobody has looked at him at this level on the street or in beat 4.
  - Stills only. A person has to watch the idle move and say whether the light on him looks right now.

- **What we learned:**
  - "The lighting looks wrong" was answered by one cropped picture with a second character in it. The control was
    already in the frame.
  - A pose that is right from the side can be wrong from the front. The check for a stand is both views, every time.
  - When turning one number stops helping (0.6 to 0.5), the rest of the problem is somewhere else. Stop turning it.
