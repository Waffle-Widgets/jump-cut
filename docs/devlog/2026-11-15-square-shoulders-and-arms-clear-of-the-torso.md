# Square shoulders and arms clear of the torso: the third reference for one standing pose

*Sun 15 Nov 2026, about 7:50 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** the idle again, against a line drawing of an anime hero standing.

- **Prompt we gave the agent:**

  > He looks very stiff and his shoulders are drooping making his arms look weird. His shoulders should be straight
  > while his arms hang down not touching his torso. Similar to the pose in this image.

- **What happened:**

  **Three references in one night, each asking for a different stand.** Photographs of people from the side (stack
  the ear, shoulder, hip and ankle); a school character sheet (plain, arms straight down); and now a hero drawing.
  Each was followed literally, and the second one produced exactly what this prompt complains about: arms hung
  straight down against the body.

  **Why that droops on this model.** He is modelled in an A-pose. Bring the arms all the way down to the ribs and
  two things happen: the shoulder's cap slides down with the arm, so the shoulder line slopes, and the arm presses
  into the torso. The earlier fix was more collarbone lift; the better one is the drawing's: do not bring the arm
  all the way down.

  **Read off the drawing, then set as numbers** at the top of `Art/Blender/clip_idle.py`:
  - the wrist hangs 9.5 cm OUTSIDE the shoulder joint, so there is daylight between arm and ribs (it was 2);
  - the elbow points out and back and is softly bent, 27 degrees (the arm's length is held to 97 % whichever way it
    hangs; a first try that moved the wrist out AND kept it as far down locked the elbow straight);
  - loose fists, the back of the hand facing out;
  - collarbone lift 36 with the shoulders left wide rather than drawn back. On an arm held away from the body 36
    reads as level; on an arm against the body it had read as a shrug;
  - feet 14 cm either side of centre, wider than the shoulders, one turned out; chest up 5 degrees;
  - and more movement than before: a 2.2 degree breath, the weight drifting 1.2 cm, the head turning 4 degrees.

  ![The stand: his left side, his right side, front](../media/2026-11-15-hero-stand.png)
  ![In the game: front, three-quarter, side, back](../media/2026-11-15-hero-stand-in-game.png)

  **The other clips follow through one table.** `STANCE` in `cw_clip.py` carries the difference between the old
  neutral stand and this one, added at the ends of every action clip. It gained the fists and the wider feet. Three
  attack scripts place their own feet and needed one line each. Checked from the numbers: every action clip's
  first and last frame has the feet at 14 cm, the idle's.

- **Not verified:** the idle and the other clips were seen in the game as stills and read from their numbers. Whether
  he still "looks very stiff" is about motion over several seconds, and only a person watching can say.

- **What we learned:**
  - A model built in an A-pose has a stand it does well, and it is not "arms at the sides". Pose with the model,
    not against it.
  - Three references for one pose is the owner finding the words. The pose that satisfied the second was the
    complaint in the third; keep the earlier measurements (the plumb line still holds) and change only what the
    new picture changes.
