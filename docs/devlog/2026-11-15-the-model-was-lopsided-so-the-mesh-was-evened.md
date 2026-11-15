# The model was lopsided, so the mesh was evened

*Sun 15 Nov 2026, about 5:45 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** the uneven shoulders the last entry measured and could not fix by posing.

- **Prompt we gave the agent:**

  > Fix it so it looks right, do whatever you need to.

- **What happened:**

  The skeleton was already level. The surface was not: Meshy's model has its right sleeve 3 to 4 cm fatter than its
  left and the cloth on that shoulder higher. No pose hides that, so the mesh had to change.

  `Art/Blender/even_sides.py` does it in the bind pose. Each vertex of the shoulders and arms is mirrored across
  the body's centre plane, and the nearest point of the surface on the other side is found. Mirrored back, that is
  where this vertex would be if its side were shaped like the other. Every vertex moves **half** way, so the two
  sides meet in the middle. The move is capped at 3 cm, smoothed across the mesh, and faded out toward the chest,
  the chin and the hands. Faces, UVs, weights and bones are untouched.

  One pass closes half the gap, so it runs three times:

  | | sleeve radius, one side | the other |
  |---|---|---|
  | before | 12.0 cm | 10.1 cm |
  | pass 1 | 11.8 | 10.4 |
  | pass 2 | 11.6 | 10.6 |
  | pass 3 | 11.3 | 10.8 |

  In the standing pose the outer edge of each arm, shoulder to wrist, went from 20-21-21-21 against 23-25-25-24 cm
  to 21-22-22-21 against 21-23-22-21.

  The first version left the head out by BONE, and the neck's bones carry the collar and the slope from neck to
  shoulder, which is where the sides differ most. It keeps the head out by height now.

  About 7,900 vertices moved, 0.4 cm on average and 1.5 cm at most on the first pass. No animation was rebuilt:
  the clips do not depend on the shape of a sleeve. Only the body was re-imported.

  ![In the game: level shoulders, matching sleeves, straight arms](../media/2026-11-15-shoulders-even-in-game.png)

  ![The reshaped body in its bind pose](../media/2026-11-15-even-sides-bind.png)

- **Known flaws:**
  - The shirt collar is still not symmetric (about 1 cm, 10 to 13 cm from the centre). It is a collar; one wing
    sits higher. Left alone.
  - The rolled cuffs sit at slightly different heights on the two arms. Also left alone: averaging them would blur
    the rolls.
  - Seen in the idle only. Nobody has looked at the reshaped sleeves in a punch or the sprint.
  - Stills, one room. A person has to play it.

- **What we learned:**
  - A generated character is not symmetric, and a level skeleton inside it proves nothing about what is seen.
  - Moving both sides half way needs no decision about which side is right, and it converges: three passes.
  - Check what a mask is made of. "Not the head" by bone also meant "not the collar".
