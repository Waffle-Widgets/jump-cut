# Remake the model, or adjust it?

*Sun 15 Nov 2026, about 7:10 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** a straight answer after the A-pose idle went in.

- **Prompt we gave the agent:**

  > Now he looks like he's leaning to his left and his arms look shriveled up. Does this character model need to be
  > remade, or is it fine and we just need to adjust it?

- **What happened:**

  **The lean was mine.** `posture_check.py` now prints where each level of him sits sideways, measured from the
  point between his ankles. With the pelvis roll I added two entries ago (to even out his knees) his chest and
  shoulders sat **2.1 cm to his left** of his feet while his head sat 2.6 cm to his right: an S. The roll is out
  and the hips are centred over the feet. Chest and shoulders now read +0.2 cm. The price is the knees: 3 and 14
  degrees again, inside loose trousers.

  ![After the roll came out, in the game](../media/2026-11-15-idle-no-lean-in-game.png)

  **What is left is the model's.** Everything measured this morning, in one place:

  | What | Measured | A person his height |
  |---|---|---|
  | Shoulder to wrist | 48 cm | 58 cm |
  | Fingertips reach | hip (72 cm) | mid-thigh (65 cm) |
  | Head, sideways from the chest's centre | about 4.5 cm to his right (hair included) | 0 |
  | Head in the sculpted pose | leans about 4 degrees, hangs 12 down | level |
  | Right leg against left | longer: one knee bends 11 degrees more | equal |
  | Sleeves | one was 3 to 4 cm fatter (evened this morning) | equal |
  | Hips against ankles in the sculpted pose | 6 cm ahead | over them |

  "Shriveled" is the first two rows. No pose makes an arm longer.

  **Remake or adjust: adjust.** A remake is a new Meshy generation, and that brings a new set of the same kind of
  faults, a rig with no fingers (CLAUDE.md, Nov 14), and all 13 authored clips to redo. There are five hours to the
  build. The faults above are each a known size, and they can be corrected ONCE in the model's rest pose instead of
  being fought in every clip: lengthen the arms, centre the head, even the legs. That changes the rest pose, so all
  13 clips are rebuilt and re-imported with it.

- **Not done:** that rest-pose pass. It is a bigger change than a pose and waits for a yes.

- **Known flaws:**
  - His head still sits to his right of his chest, so he can still read as tilted.
  - Arms still 10 cm short.
  - Stills, one room.

- **What we learned:**
  - Six rounds of pose fixes were six rounds of compensating for the model. Compensation in a pose shows up
    somewhere else: the knee fix became the lean.
  - Measure the model first and write its faults in one table. It would have turned this morning into one pass.
