# The coworker's hands became fists, and her face got its shading back

**Sun Nov 15, about 2:15 PM, GameStation (builder). After the noon cut-off: the team said go.**

## What we asked for

> her hands still look crumpled up. Her face also looks weird. Is this the model, the skeletal structure, or an
> issue with the shader?

and, after the answer (hands: the model; face: the shader; skeleton: fine):

> go ahead with both. Make sure the hands aren't clipping into her body.

## What happened

**The face was one checkbox.** The cel look only treats a pixel as a character if its mesh writes custom depth,
and the player was the only mesh that did. The coworker was being shaded as scenery. `tools/unreal_coworker_idle.py
apply depth` sets `render_custom_depth` on the placed `Coworker_Cafe`. Her face now reads as a drawn face.

**The clipping was real: 0.1 cm.** `Art/Blender/coworker_idle.py` now measures the nearest distance from her hands
to her body at two frames of the idle and opens the arms 2 degrees at a time until there are 2.5 cm of air. It
stopped at 21 degrees (2.6 cm).

**The hands took five tries, and four of them were the same mistake.**

1. Smoothing the hand vertices: the jags went, the claw stayed.
2. Drawing every vertex onto an egg fitted to the hand, from the average of the vertices: still a hook.
3. Pinning only the wrist ring: no change at all, which was the clue that pinning was never the problem.
4. Projecting from the deepest point inside the hand instead: still a hook. A colour-coded render finally showed
   why. Meshy's mitten is a thin, curled shell. There is no point inside it from which the whole skin can be seen,
   so any projection covers only part of the egg, and the uncovered part is the gap between thumb and fingers.
5. Stop reshaping it. `Art/Blender/hand_smooth.py` now builds the convex hull of each hand's own vertices,
   smooths it, skins it wholly to the palm bone, paints it with one clean skin texel, and deletes the curled faces
   inside. She has no finger bones in use, so a loose closed fist is the honest shape.

**A second bug hid under the first.** The clip import "worked" at 1:46 PM and reported the new clip's length. It
had not: `unreal_import_authored_clip.py` renames the imported clip onto the name the game uses, the rename fails
silently when that name exists, and the tool then loads the OLD clip by that name and describes it. The new idle
sat unsaved in memory beside the old one. Measured: the game's clip had the upper arm at pitch 9.4, the new one at
17.6. `tools/unreal_reimport_authored_clip.py` already exists for exactly this and says so in its docstring; I
did not use it. So the palm fix committed earlier today (`d8207aa`) may never have been on screen either.

![Her hands in Blender after the fist pass](../media/2026-11-15-coworker-hands-rounded.png)
![In the running game](../media/2026-11-15-coworker-fists-in-game.png)

## Checked, and not checked

- Checked by script: hand-to-body gap 2.6 cm at frames 0 and 60; body re-import kept the skeleton (68 bones) and
  the material slot, bounds moved 0.97 cm; the clip in the game is the new one (bone pose read back).
- Checked by eye, one capture from the running game: closed hands, clear of the body, face shaded as a character.
- **Not checked:** the whole idle loop in motion, her explosion and rescue beats with the new body, and a packaged
  build played by a person.
- Left out: her arms now hang 21 degrees out, wider than a relaxed stance. The hands are one flat skin colour.
  The pale spot on each hip (texture) is still there.

## What we learned

- **When three fixes change nothing, the thing you are fixing is not what you think it is.** Render it with the
  suspect vertices coloured before trying a fourth.
- **A thin curled shell cannot be projected onto a ball.** Replace it (convex hull) instead of reshaping it.
- **A second import of an authored clip must go through `unreal_reimport_authored_clip.py`.** The first-import
  tool reports success over the old asset.
- **A character that looks flat in the cel look: check `render_custom_depth` before the texture.**
