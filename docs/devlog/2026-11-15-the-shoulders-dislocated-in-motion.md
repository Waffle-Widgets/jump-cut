# The shoulders "dislocated" in motion, and it was our own fix from an hour before

*Sun 15 Nov 2026, about 2:15 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** after playing the anime dash and the new combo.

- **Prompt we gave the agent:**

  > The biggest issue is still the shoulders during animation, they look like they dislocate. Fix it so they look
  > normal like in his idle pose

- **What happened:**

  **The four-side clip sheets could not show it.** A shoulder is a few pixels in a 230 px tile. So first a new
  check: `Art/Blender/shoulder_sheet.py` renders the chest close up from front, back, both sides and above, for
  chosen frames of any clip, with the camera turning with the torso.

  ![Before: idle on top, then the dash and the three attacks](../media/2026-11-15-shoulders-in-motion-before.png)

  The idle (top row) is fine. In the punch the shoulder line falls steeply away from the neck and the sleeve
  pinches where the arm leaves the body.

  **Two guesses were tested and thrown out.** That the collarbone should travel *with* the arm (drawn back when
  the arm sweeps back, forward when it punches): rendered at six settings each way, every one of them was worse
  than leaving it alone - it drags the apron bib across the chest. And that the swept-back arm was simply past
  what a shoulder can do: measured, it is only 23 degrees behind the line of the torso.

  **The cause was the rule written an hour earlier.** A hanging arm needs 28 degrees of collarbone lift or the
  shoulder slopes. When that lift ballooned the first dash, `hand()` was changed to fade it to nothing for a
  level or raised arm. So every time an arm came up, the shoulder JOINT sank about 6 cm below where the idle
  holds it, and came back up when the arm dropped. In a still it reads as sloped shoulders. In motion it reads as
  a shoulder leaving its socket.

  **The fix is to hold the shoulder at the idle's height in every pose.** Rendered with the arms forward, back and
  overhead, a lifted collarbone looks natural in all three. The lift is now 28 for a hanging arm, eases to 24 for
  a level one and rises to 34 overhead, the way a real shoulder does. All eleven clips were rebuilt and
  re-imported.

  ![After: the same frames](../media/2026-11-15-shoulders-in-motion-after.png)

  ![In the game: idle from behind, three frames around the punches, and the dash](../media/2026-11-15-shoulders-in-game.png)

- **Not verified:** a punch lasts a third of a second and a capture through the MCP takes longer than that, so
  the in-game pictures show the frames around the punches, not the impact frames. Those were checked in Blender
  only. A person has to watch it move.

- **What we learned:**
  - A joint that MOVES between poses is a different defect from a joint that looks wrong in one pose, and a
    contact sheet only shows the second kind. Compare the same body part across frames, close up.
  - The quick fix for "it balloons" was to remove the thing; the right question was why the idle looked right.
  - Test the plausible theory before building on it. Two reasonable ideas about collarbones cost five minutes of
    rendering to rule out, and would have cost every clip if built first.
