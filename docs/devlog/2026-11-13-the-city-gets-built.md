# 2026-11-13 — The city gets built, and it isn't generated (M Station)

- **What we asked for:** a city and a coffee shop to put the game in — somewhere between Tokyo and New York
  — plus the clutter that makes a street look lived in, laid out so it makes sense once you are walking
  down it.

- **Prompt we gave the agent:**

  > create the models for the city and coffee shop. The city should look like something between Tokyo and
  > New York. Also create assets to make the city feel alive. The layout of the city should make sense once
  > it is in game. If generating clothing and humans separately makes more sense then do so, otherwise
  > continue with how we have been working. If any characters need to be remade for consistency then do so.
  > Then push changes so Justin can use the new models in game.

- **What happened:**

  **The first decision was not to use Meshy.** Every character in this game has come out of ComfyUI and
  Meshy, and the Nov 13 decision says to keep it that way for consistency — so the obvious move was to
  draw some buildings and generate them. We didn't, and the reason is worth writing down: image-to-3D is
  the right tool when one believable silhouette matters and nobody walks along the inside of it. A city is
  the opposite job. The player walks down it, so walls have to be flat and vertical, floors have to be at
  z = 0, a doorway has to be the width a character capsule actually fits through, and the cafe has to be
  *exactly* 12.6 × 10.3 m because a car, a dead driver, a coworker and a piece of shrapnel are already
  placed inside it at fixed coordinates. Those are numbers, not pictures. So the city is built from
  numbers, in `Art/Blender/jumpcut_city_kit.py`. The cast is untouched and still comes from ComfyUI and
  Meshy; this changes nothing about that decision.

  It cost **0 credits** and the whole city is **20,615 triangles** — fewer than the single goon model
  (18,000), which is the part that genuinely surprised us.

  **Tokyo and New York blend by zoning, not by averaging.** Averaging two cities gives you one that is
  neither. The street the player walks is 10 m wide, which in New York is an alley and in Tokyo is an
  ordinary shopping street — so the lane is Tokyo (4–8 m plots, a shop on every ground floor, signage
  stacked vertically because the plot is too narrow to put it sideways, air conditioners and cable worn on
  the outside, a utility pole every 11 m) and everything above and behind it is New York (masonry setback
  towers and curtain-wall slabs at 42–62 m, water tanks, fire escapes).

  **The crossing is the piece the story actually required.** The car hits the cafe's *west* wall — its box
  spans x −720..−320, which crosses the x = −615 wall line. A car cannot arrive from the west unless there
  is a road to the west, and there wasn't one. There is now: an avenue at x = −1900, New York in scale,
  with a corner block on each side. It is what the player stares at through the hole for all of beat 1.

  **Three things were wrong and only a render caught them.** The windows were all modelled correctly and
  all invisible — each floor's wall was drawn as one quad across the full band, coplanar with the openings,
  burying every pane behind it. The cafe ceiling faced *up*, so from the only side anybody ever sees it
  from, it wasn't there. And the cafe's shopfront was glazed onto the **north** wall, which looks at the
  neighbouring building a metre away; the street only exists *east* of the cafe, which is the wall the
  player faces for the whole beat. All three fixed.

  **And one thing a render could never have caught.** After adding a floor band round the building sides —
  itself a fix for the towers reading as featureless 46 m slabs from the plaza — the layout script put
  eleven buildings down overlapping their neighbours, because the band widened every building by 14 cm
  while the script was still using a width table kept by hand. So the kit now writes its own measured
  footprints to `city_models.json`, and `tools/jumpcut_city_layout.py` checks all 216 placements against
  them: nothing in the player's road, the cafe, the boss arena, either gate opening or the exit run, and no
  two lane buildings overlapping. It found **17 real collisions** on its first run. It now reports none.

  **The characters were measured rather than eyeballed.** The brief said to remake anything that needed it
  for consistency, so we ran the full colour audit over all ten models. Eight are clean. Two are not, and
  they are the two the player looks at most: **`CafeWalker`, the player himself, leaks 6.13% front / 3.94%
  back**, and **`CafeCoworker` leaks 4.46% / 5.27%** — clothing within dE 14 of their own skin tone, which
  is the exact thing the Team Owner's standing colour rule forbids. Neither is wired into Unreal yet
  (`BP_Player` still wears Epic's mannequin and `BP_Coworker` is still a green box), so this is the
  cheapest moment there will ever be to redo them. **They have not been redone in this pass** — that is
  the next job, not a finished one.

- **What we learned:**
  - A render shows you what the camera happens to point at. A checked footprint looks at all of it. The
    renders here were genuinely useful for the three visual defects and completely blind to the eleven
    overlaps.
  - A hand-kept table that duplicates a measurement is a bug with a delay fuse. The widths were right when
    they were written and wrong forty minutes later, and nothing complained.
  - Detail belongs in geometry when a cel shader is going to flatten your lighting into bands and outline
    every edge. Flat material slots plus recessed windows beat a photographic facade texture, and they cost
    nothing to bake.
  - "Alive" is not more buildings. It is evidence that somebody was here five minutes ago and will be back
    — and it wants to be in clumps, because a prop every two metres reads as a shop display, not a street.

- **Media:**

  ![The lane, looking east from the cafe door at eye height](../media/2026-11-13-city-lane.jpg)

  ![The coffee shop, dressed, with the ceiling and the south wall cut away](../media/2026-11-13-cafe-interior.jpg)

  ![The nine building types](../media/2026-11-13-city-buildings.jpg)
