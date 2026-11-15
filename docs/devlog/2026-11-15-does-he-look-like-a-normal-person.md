# "Does he look like a normal person?" No. Three reasons, and none of them was the animation tool

*Sun 15 Nov 2026, about 3:30 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`), one Fable 5.2 helper on the sprint*

- **What we asked for:** after playing the sprinter run, the front kick and the freed apron.

- **Prompt we gave the agent** (with two photographs of real sprinters in the drive phase):

  > The apron clips into him when he is standing still and during some attacks. If you look at this character and
  > then look at a normal person, do they look the same? Do they give off the same vibes? After he get's the first
  > power he should be able to sprint like an actual sprint. His clothes shouldn't stretch out in weird ways when he
  > attacks or moves. The attacks look very stiff still. His arms look bent, almost broken, when standing still.
  > From the side when standing still his legs look bowed weird.

- **The honest answer first:** no, he did not look like a normal person, and the agent had been answering a
  different question for hours. Every check so far was "does this CLIP look right on a contact sheet". Nobody had
  stood him still and compared him with a person.

- **What happened:**

  **Standing still was the oldest clip, and it had been left behind.** `idle_clip.py` was written before the shared
  clip tool existed. So the pose on screen more than any other had none of what came after it:
  - *Arms "almost broken":* its elbows were bent 30 degrees, and the whole 62 degree forearm roll sat on the elbow
    alone. Every other clip has shared that twist across three joints since this morning.
  - *Apron clipping while he stands:* the idle never drove the apron bones at all. The skirt hung at zero while his
    thighs sat forward of where the model rests them.
  - *Legs bowed from the side:* this one is the MODEL. It rests with its ankles 6 cm behind its hip joints. Stand a
    figure like that and the legs slant back and bow. Four stances were rendered side by side; the one with the
    ankles under the hips is the one that reads as a person.

  ![Four stances from every side: the top row is what the game had](../media/2026-11-15-stance-study.png)

  `Art/Blender/clip_idle.py` replaces it, on the shared tool. The feet stay exactly where every other clip plants
  them, so nothing slides on a blend; the PELVIS moves back 6.5 cm over the ankles instead. Elbows straightened to
  16 degrees. The apron hangs 13 degrees forward, in front of his thighs.

  ![The new idle, full body and arms](../media/2026-11-15-idle-standing-straight.png)

  **Clothes stretching: his waist was tied to his thighs.** The generator's skin weights (and the smoothing we ran
  over them) gave the thigh bones influence up to 127 cm - the waistband, the bottom of his shirt, the apron's tie.
  Every time a leg lifted, his waist went with it. `Art/Blender/waist_weights.py` hands leg weight above the hip
  joints to the hip bone, ramped across 10 cm at the joint: 6,612 vertices. Stretched edges, same clips, same
  poses:

  | clip | before | after |
  |---|---|---|
  | front kick | 133 | 62 |
  | run | 128 | 44 |
  | lunge | 68 | 41 |
  | uppercut | 152 | 135 |

  **Apron clipping in attacks:** each apron bone watched only the leg on its own side, but the two bones share the
  middle 30 cm of the skirt, so the far leg could come through the centre. Each now watches the shared strip too.

  **The sprint.** The owner sent two photographs of sprinters in the drive phase, and the brief to the helper
  was the photographs described: one straight line from the rear foot through the hips and spine to the head at
  40-45 degrees, front hand open at face height, rear hand thrown back and up behind the hip, front thigh level,
  rear leg long. `Art/Blender/clip_sprint.py`: 16 frames a cycle, 36 degrees of lean measured hip to neck with the
  rear leg at 39 so they read as one line, feet on the ball with three frames of contact and five of flight,
  authored for 850 cm/s with the speed as one number at the top.

  ![The sprint from four sides](../media/2026-11-15-sprint-four-sides.png)

  **The sprint exposed the apron's last weakness, so the apron got a fold.** One stiff panel per side stuck straight
  out like a plank whenever a thigh came up level. `apron_bones.py` now adds a second pair of bones half way down
  (`Apron_L2` / `Apron_R2`, skeleton 71 -> 73), and `cw_clip.py` solves the two panels separately: the upper one
  lies on the thigh, the lower one hangs from the knee. Both also feel gravity now - when he leans forward the
  skirt hangs toward the ground instead of staying glued to his hips.

  **In the game, standing:** upright from the side, arms straight, apron in front of his legs.

  ![In the game: the new idle from the side and the front](../media/2026-11-15-idle-in-game.png)

  **A first try at watching the attacks in real frames failed, usefully.** `r.DumpingMovie` writes every frame as
  a PNG but slows the game to about 3 frames a second, so each dumped frame skipped most of a punch. Slowing game
  time with `slomo 0.1` brought the frames closer together, but the combo window ran out between presses (it is
  measured in game time too) and the camera had ended up behind a door frame. The recipe that should work next:
  `slomo 0.04`, the side camera at 90 degrees, and the three presses 11 real seconds apart.

- **Not done:**
  - "The attacks look very stiff still." Not touched in this entry. They have only ever been judged from still
    sheets; the next step is to dump real gameplay frames and watch them move before changing anything.
  - Making him FASTER after the first power is a gameplay change after feature freeze. The sprint clip is authored
    and imported (`A_CafeWalker_Sprint_Authored`) but NOTHING PLAYS IT: his speed is unchanged until the owner says go.
  - The uppercut still stretches a patch at his right hip where the towel tucks into the waistband.

- **What we learned:**
  - Check the thing the player looks at longest first. The idle is on screen more than every attack together and
    it was the one clip nobody had re-opened.
  - "Compare him with a normal person" is a better test than any number we had. A stance study took four minutes.
  - When a fix lands in a shared tool, list what does NOT use the tool.
