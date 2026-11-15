# The shoes were tipped up in the model, and the shoulders fell with the arms

*Sun 15 Nov 2026, about 12:30 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** after the new idle went in, two things still looked wrong on the player.

- **Prompt we gave the agent:**

  > Yes and fix the rest of the player, it looks like his shoulders are droopy and his feet are looking oddly
  > folded upwards.

- **What happened:**

  **Both were looked at in the rest pose first**, because a part that is wrong there is the model and a part that
  is only wrong in the idle is the clip. The picture below has the idle on top and the rest pose underneath.

  ![Shoulders and feet: the idle (top) against the rest pose (bottom)](../media/2026-11-15-player-shoulders-and-feet-idle-vs-rest.png)

  **The feet were the model.** In the rest pose each shoe is pitched toes-up, measured from the mesh at **11.3 and
  13.0 degrees**, with the toe cap several centimetres off the ground. Every clip plants the foot *bone* the way
  the rig rests, so every clip showed a tipped-up shoe: the new idle and all 40 retargeted ones. Fixing one clip
  would have left it in the other forty. `Art/Blender/flatten_feet.py` turns each foot about its ankle until the
  sole is level, bakes that shape into the vertices and puts the rig back: 4,310 vertices moved (5.3 cm at most),
  no bone moved, UVs unchanged. One shoe also rests a centimetre higher than the other in the model; the idle now
  measures each sole and lowers that ankle so both touch the floor (lowest vertex 0.04 cm).

  ![One shoe after flattening](../media/2026-11-15-player-shoe-flat.png)

  **The shoulders were the clip.** In the rest pose they are square. Bringing the arms down from the A-pose
  dragged them into a slope, because the collarbones never answered. Three settings were rendered side by side;
  the idle now lifts each collarbone 14 degrees, draws it back 3 and hangs the hands a little further from the
  hips (7 cm, was 3.5).

  **Re-importing a clip over itself needed its own tool.** The first import script imports under the file's name
  and renames, which cannot work once the name is taken by the asset the anim blueprint points at.
  `tools/unreal_reimport_authored_clip.py` hands Interchange the existing asset instead, and proves the content
  changed by reading six bones before and after (the wrists moved 5.5 cm; a no-op would read 0).

  **Checked in the running game** from the front, settled: square shoulders, feet flat on the floor.

- **What we learned:**
  - Look at the rest pose before fixing a clip. It splits "the model is wrong" from "the animation is wrong" in
    one picture.
  - A fault in the rest pose is in every clip at once, so fix it in the mesh, once.

- **Not done:** nobody has played it. The feet were not captured close up in the game, only in Blender and by the
  body's bounds moving (lowest point -0.11 to 0.31 cm). The retargeted walk, run and punches bring the arms down
  the same way and may show the same shoulder slope; they have not been changed.
