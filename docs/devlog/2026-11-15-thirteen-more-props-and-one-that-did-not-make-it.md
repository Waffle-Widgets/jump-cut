# 2026-11-15 — thirteen more props, and one that did not make it (M Station)

- **What we asked for:** the same treatment for the rest of the block models, after the sakura tree, the van,
  the hatchback, the bicycle and the scooter went into the level and read well.
- **Prompt(s) we gave the agent:**
  > "can you create models for the rest of the assets that are blocky"

  The agent answered with the clock again (1:32 PM, 4 h 27 m left, the final build already packaging on
  GameStation) and with the count: the kit has 86 models, so "the rest" could not mean all of them. It offered
  nine free-standing street props, or those plus the cafe interior, or stopping. The Team Owner picked:
  > "Props plus cafe interior"
- **What happened:**
  - **What was left out on purpose,** before anything was drawn: every building, everything bolted to a wall
    (air conditioners, signs, ducts, fire escapes), the utility poles (the cables hang off them at fixed
    heights), and every prop the physics tool owns (chairs, cones, trash bags, crates, cafe tables, the road
    barrier). Swapping the mesh on a knockable or breakable prop also swaps its collision, and that is not a
    thing to find out at 2 PM on deadline day.
  - **14 prompts, one style block** ([`prompts_batch2.json`](../../Art/Refs/Street/prompts_batch2.json)),
    sent to Gemini as 14 tabs. The style block gained "no writing in any language, no numbers": a vending
    machine and a cash register are the two objects most likely to come back covered in text.
  - **Gemini's "Download full size" button stopped working after the third picture.** No error; the click
    simply produced no download, and the script waited 90 seconds on each of the other eleven before giving
    up. The way round it: read each picture off its own page into a canvas and hand it straight to Meshy's
    upload box inside the browser, never touching the disk. Eight of those pages had already swapped the
    picture for a link that a canvas may not read; opening Gemini's image viewer puts a readable copy back.
  - **Meshy, 14 models, 490 credits, all first takes.** Downloading 14 from a grid that also holds 14 grey
    untextured twins: click every card and skip the ones whose toolbar still offers a "Texture" button.
  - **Blender.** 13 of 14 baked clean in 2 minutes 15 seconds. **The gas-bottle cage did not**: a wire mesh
    cage is exactly what image-to-3D cannot do. 2.1 million triangles, a door hanging open that the picture
    did not have, and it would not reduce below 28,545. Dropped; the kit's own cage stays.
  - **Three fixes after looking at the renders,** all by measuring against the kit model each one replaces:
    - The A-frame sign came in side-on (turned 90 degrees).
    - The bench is 78 cm deep where the kit's is 50, and it stands against a shopfront. Centred, its back
      would be 14 cm inside the wall. `PROP_BACK` puts the new model's back where the kit model's back is,
      so the extra depth goes toward the street. Same for the vending machine, dumpster, planter and pot row.
    - The kit's pot row has its origin 24 cm off its middle. The new one is shifted to match.
  - The street lamp keeps its origin under the column (`PROP_ORIGIN=base`), not in the middle of a box that
    is mostly arm, and is turned so the arm points the way the kit's does.
- **What we learned:**
  - A parallel batch is only fast if every step fails fast. Eleven 90-second timeouts in a row cost more
    than the whole first batch took to draw.
  - Size and place a replacement against the thing it replaces, not against the real world. "A bench is
    1.8 m" was already true of both; what mattered was where its back was.
  - Know what a generator cannot do before paying for it: wire, mesh, spokes on a small wheel. (The bicycle
    was luck.)
- **Not done:** none of the 13 is in the game. `tools/unreal_street_models.py` was extended for them and the
  new part has not been run.
- **Media:**
  ![The thirteen baked models, front and three-quarter view, beside a 1.75 m figure](../media/2026-11-15-street-and-cafe-props-meshy-bake.jpg)
