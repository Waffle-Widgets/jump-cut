# 2026-11-13 — The last grey boxes get models (M Station)

- **What we asked for:** the art still missing for the first half of the demo, found from the tickets.

- **Prompt(s) we gave the agent:** the actual words, quoted:

  > check the tickets to see what art we still need to create any missing assets and get to work on them. I
  > would like to get everything up to and including the Slicer boss out of gray boxes and mannequins.

- **What happened.**

  **The tickets said the art was finished, and for the characters that was true.** Every `art` ticket for
  beats 1 to 3 (#5 the coworker, #6 the goon, #7 the player) is a model that already exists and is waiting
  to be imported by the builder. Read literally, there was nothing to make.

  **So we read the level instead of the tickets**, and the level disagreed. `tools/c1_layout.py` is the list
  of boxes the first build was made from, and `city_layout.json` records which of them the city replaced:
  eight. That left, between the cafe and the far side of the boss fight, with no model and **no ticket**:

  - the crashed car — two red boxes, in the first room of the game
  - the shrapnel — "a red bar", the object the whole tutorial is about
  - all six walls of the boss lot, and both walls of the run beyond it
  - both plaza gates — one scaled cube
  - the checkpoint — a post and a green sign
  - the floor, everywhere — one grey slab

  Nobody had written a ticket for any of them because the board was built from the roadmap, and the roadmap
  tracks work by beat and by character. Scenery that belongs to a Blueprint or to the first build's box list
  fell between the two.

  **Eleven models, built the way the city was** (`Art/Blender/jumpcut_city_kit.py`, a new `set` group):
  geometry from numbers, flat `MS_City*` slots, 4,332 triangles in all, 0 credits. The decisions worth
  recording:

  - **The car is right-hand drive with its door open on the side the body is on.** The driver was placed at
    (−380, 220) long before there was a car to fall out of. A door hanging open next to him is beat 1's
    story told by the set. It is also the right car for a Tokyo lane.
  - **Every wall has the footprint of the box it replaces**, to the centimetre on the arena side. The fight
    was tuned in those boxes. The layout script now refuses a replacement that reaches more than 16 cm past
    its box, and we proved the refusal works by moving a wall 30 cm and watching it fail.
  - **The gate is centred on its origin** and thin on X, unlike everything else in the kit, because that is
    how the cube inside `BP_PlazaGate` sits. Swapping it is then a mesh and a scale, not a re-placement.
  - **The checkpoint is a film-set light stand with a slate.** The game is called Jump Cut; the place a take
    restarts should be set equipment.
  - **The floor is paint, not a floor.** Paving, crossings and road lines sit 1 cm up with collision off, so
    the footing the fight was tuned on does not change. The real slabs get dark asphalt from the placer.

  **Two things went wrong on the way.** The first sheet render put a 30 m floor and a 78 cm shard in one
  row and showed only the floor — the car was off the edge of the frame — so the set pieces got their own
  close-up renderer. And the road lines were first drawn at ±2.4 m, which is *under* the kerb stones (they
  stand at ±2.44): found by reading the kerb's measured footprint, not by looking, because in a render a
  white line under a grey kerb is simply absent.

  **What a suspicious render turned out not to be:** the shrapnel looked half-transparent. We assumed two
  materials on one plane and "fixed" it; the picture did not change. It was the sun on a flat red face. The
  fix stayed in, because the teeth really were two materials on one plane and would have flickered in
  Unreal, but it was not the thing we were looking at.

- **What we learned:**
  - **A board built from a roadmap only contains what the roadmap thought of.** The level's own box list was
    the honest inventory, and it had been in the repo since day one.
  - Scale decides what a check render shows. One row of everything is a picture of the biggest thing.
  - **None of this is in Unreal.** M Station is a maker. The placer's new `add` mode and `set_ground()` have
    never been run, and four of the eleven go inside Blueprints by hand. Steps: `docs/CITY.md`, "Set pieces".

- **Media:**

  ![The crashed car in the hole in the cafe's west wall, seen from inside](../media/2026-11-13-set-crash-car.jpg)
  ![The boss lot from just inside the entry gate: yard walls, paving, and the ring where he stands](../media/2026-11-13-set-boss-lot.jpg)
  ![The plaza gate and the checkpoint stand](../media/2026-11-13-set-gate-checkpoint.jpg)
  ![The run past the exit gate, between demolition hoardings](../media/2026-11-13-set-exit-run.jpg)
