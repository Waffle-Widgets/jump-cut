# Three props from Tripo, made on the builder

**Sun Nov 15, about 3:40 PM, GameStation (builder). After the noon cut-off; the Team Owner asked.**

## What we asked for

> Tripo looks similar to Meshy and we have credits we need to use there. Can we pick up any tickets for assets that
> M_Station isn't working on and make them here using Tripo?

and, when the built-in browser turned out not to be signed in:

> use the browser that is logged in already not your internal browser

## What happened

Picked three alley tickets M Station was not doing and that are not physics props: gas bottles (#89, the one Meshy
failed on), the meter box (#86) and the duct run (#85). Told M Station so nothing was made twice.

Tripo's home page only takes a picture. Its workspace has a text box behind a pencil icon, so no reference picture
was needed. 55 credits and about two minutes each, on the HD model. The prompts, as typed:

- *Two red propane gas cylinders standing upright side by side inside a simple black steel rack frame, on the
  ground. Stylized anime background prop, clean simple shapes, flat painted colors, slightly worn, no text, no logos.*
- *A wall-mounted electricity meter cabinet for a Japanese back alley: a tall flat grey metal box with three round
  glass meter dials in a row, a small hinged door, and two conduit pipes running down from the bottom. Flat against
  a wall, shallow depth.* (same style ending)
- *A tall vertical rectangular galvanized steel ventilation duct that runs straight up the outside wall of a
  building, about five metres tall and narrow, with four evenly spaced wall brackets and a curved elbow hood at the
  very top.* (same style ending)

Each came back first time at about 1.9 million triangles. Export as GLB, then M Station's own
`Art/Blender/meshy_prop_bake.py` unchanged: it does not care which generator made the file. Then the same
`unreal_street_models.py import / plan / lock / swap` as the Meshy batches, with three new lines in `MODELS`.

- **Gas bottles:** sized to the kit's 114 cm height they were 155 cm wide (two bottles in a wide rack) against the
  kit's 94, and would have stood 34 cm into the vending machine beside them. `tools/jc_scale_by_mesh.py` scales the
  three placed actors to 0.7 (109 x 64 x 80 cm) rather than re-baking and forcing a re-import.
- **Meter box and duct:** fitted exactly into the kit piece's own box with `PROP_KITBOX`, read off the kit mesh in
  Unreal, and turned 180 so the front faces away from the wall. The kit meter box runs from y = -22.5 to 0 in
  Unreal, which is Blender +Y: for these wall props the front is Blender **+Y**, the opposite of the note in the
  bake script. That is also why the Meshy register came in backwards.

![In game](../media/2026-11-15-tripo-props-in-game.png)

## Checked, and not checked

- Checked by script: 3 imported, 13 actors changed (3 gas, 4 meter, 6 duct), all saves `ok=True`; the meter box and
  duct measure 158 x 22.5 x 188 and 93 x 42.7 x 486 cm, the kit pieces' sizes.
- Checked by eye: the gas bottles beside the vending machines, from the game camera. The bake's own check render
  shows the meter box's BACK from Blender -Y, which is what "front to +Y" should look like.
- **Not checked by eye in the game: the meter boxes and the ducts.** Two tries at a capture did not frame them
  (the camera ended up inside other props). If a meter box shows a blank grey face, it is backwards:
  `unreal_street_models.py revert MeterBoxM` puts the kit one back.
- Not made: the fire stair (#93). Stopped to leave time for a build and a playthrough.

## What we learned

- **The bake and import pipeline is generator-agnostic.** A second generator cost one new CREDITS line and three
  lines in a table.
- **Text-to-3D is enough for a background prop.** No Gemini step, so about four minutes from prompt to baked FBX.
- **Which way is "front" is a property of each kit piece, not of the kit.** Read the kit mesh's box before baking.
