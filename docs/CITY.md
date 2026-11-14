# The city — buildings, the coffee shop, and the clutter that makes it look lived in

> **Builder, start here:** [How to put it in the game](#how-to-put-it-in-the-game). Everything is committed
> and waiting; nothing in this file needs a decision first.

Made Fri Nov 13 on M Station. **44 models, 20,615 triangles for the whole city**, 1.2 MB of FBX, **0 Meshy
credits and nothing uploaded anywhere.** 216 placements are worked out and checked against the real level.
**Since then:** eleven set pieces for beats 1 to 3 (the crashed car, the boss lot's walls and floor, the
gate, the checkpoint) — see [Set pieces](#set-pieces--the-last-grey-boxes-up-to-the-cleaver-boss-fri-nov-13-evening).
The kit is now **55 models, 24,947 triangles**, and the layout **245 placements**.

For scale: the entire city — every building, the coffee shop and its fittings, every sign, pole and vending
machine — costs **fewer triangles than one character** (`SK_StreetGoon` is 18,000 on its own).

---

## Why it is modelled and not generated

Meshy and TRELLIS are image-to-3D. That is the right tool for a character, where one believable silhouette
matters and nobody ever walks along the inside of it. A city is the opposite job:

- the player **walks down it**, so walls have to be flat and vertical and floors have to be at z = 0
- a doorway has to be the width a character capsule actually fits through
- the same facade has to repeat fifteen times without reading as a repeat
- the cafe has to be **exactly** 12.6 × 10.3 m, because a car, a dead driver, a coworker and a piece of
  shrapnel are already placed inside it at fixed coordinates

Those are numbers, not pictures, so the city is built from numbers — `Art/Blender/jumpcut_city_kit.py`. It
also costs nothing and re-runs in seconds when a size turns out wrong, which is the thing that actually
happens on a jam. **This is not a change to the Nov 13 "use ComfyUI and Meshy for consistency" decision:**
that decision is about the **cast**, and the cast is still drawn in ComfyUI and modelled on Meshy. No
character was made by this kit.

## Tokyo and New York, blended by zoning

The two cities do not blend by averaging — averaging them gives a city that is neither. They blend by
**zoning**, which is also what makes the layout legible to play:

| Where | Which city | Why |
|---|---|---|
| **The lane** (the 60 m the player walks) | **Tokyo** | The street is 10 m wide. In New York that is an alley; in Tokyo it is an ordinary shopping street. So: plots of 4–8 m, a shop on the ground floor of *every* building, flats above, signage stacked vertically because the plot is too narrow to put it sideways, and the services worn on the outside — air conditioners, overhead cable, a utility pole every 11 m. Nothing on the lane is over 18 m, so the player can always see sky |
| **The skyline** (behind and above) | **New York** | Masonry setback towers and curtain-wall slabs, 42–62 m, with timber water tanks and fire escapes. Never reachable. They are what the lane is seen *against* |
| **The crossing** (west of the cafe) | **Where they meet** | A wide avenue running north–south at x = −1900, New York in scale, with a corner block each side |

**The crossing is the one piece of layout the story actually requires.** The car hits the cafe's **west**
wall — its box spans x −720..−320, which crosses the x = −615 wall line. A car cannot arrive from the west
unless there is a road to the west. So there is one. It is why the crash is possible, it is what the player
sees through the hole for the whole of beat 1, and it is the handover between the two halves of the city.

## What is in the kit

**The coffee shop (10).** `SM_CafeShell` is the whole room as one mesh — floor, four walls, the door, the
east shopfront, the hole the car made, and a ceiling — and it replaces **five** grey boxes on its own. Then
`SM_CafeCounter` (5.00 × 0.80 × 1.10 m, the exact size of the grey box it replaces), `SM_CafeEspresso`,
`SM_CafePastryCase`, `SM_CafeShelf`, `SM_CafeTable`, `SM_CafeChair`, `SM_CafeAwning`, `SM_CafeMenuBoard`,
`SM_CafeSign`.

**The city (9).** `SM_ShopHouse_A` (6 m, 4 storeys — the workhorse), `SM_ShopHouse_B` (4 m, 5 storeys — the
Tokyo pencil building), `SM_ShopHouse_C` (8 m, brick, shutter down — a lane of *open* shops needs a closed
one to read as a set), `SM_CornerBlock` (L-shaped, for the crossing), `SM_BlockFiller`, `SM_SetbackTower`
(46 m), `SM_CurtainTower` (62 m), `SM_PlazaTower` (42 m, colonnaded base), `SM_FireEscape`.

**Beat 4's ruins (5).** `SM_RuinSlab_A` (5 × 5 m), `SM_RuinSlab_B` (7 × 3.2 m), `SM_RuinBeam` (8 m I-beam),
`SM_RuinWall`, `SM_Rubble`. See [the note below](#beat-4-pieces-made-not-placed).

**The clutter (20).** `SM_VendingMachine`, `SM_SignVertical`, `SM_SignBlade`, `SM_ACUnit`, `SM_UtilityPole`,
`SM_CableSpan`, `SM_StreetLamp`, `SM_TrafficCone`, `SM_Bollard`, `SM_Barrier`, `SM_CrateStack`,
`SM_TrashBags`, `SM_Planter`, `SM_Bicycle`, `SM_Noren`, `SM_Awning`, `SM_RoofTank`, `SM_Manhole`,
`SM_Bench`, `SM_Kerb`.

"Alive" is not more buildings. It is evidence that somebody was here five minutes ago and will be back: a
machine that sells something, a bike leaning where it should not be, bags out for collection, a cone round a
hole nobody has filled. The lane is dressed in **clumps with gaps between them** — a prop every two metres
reads as a shop display, not as a street.

## No textures, on purpose

The level wears a cel-shaded post-process (`MI_AnimeLook_JumpCut`) that flattens lighting into bands and
draws an outline on every depth and normal edge. Under that, a photographic facade texture is mostly thrown
away and a flat colour is not. So the kit ships **12 flat material slots** (`MS_CityWall`, `MS_CityBrick`,
`MS_CityConcrete`, `MS_CityTrim`, `MS_CityMetal`, `MS_CityGlass`, `MS_CitySignA`, `MS_CitySignB`,
`MS_CityAccent`, `MS_CityWood`, `MS_CityRoof`, `MS_CityCloth`) and puts its detail in **geometry** —
recessed windows, mullions, sills, parapets, balconies, fire escapes — where the outline pass can find it.

The variety a texture would normally give is baked into **vertex colour** instead: every window pane gets its
own brightness, so one material produces a facade of lit and dark rooms.

`tools/jumpcut_city_place.py` creates one flat material per slot if it does not already exist, using the same
colours the check renders used, so the level should come out looking like the sheets.

## No trademarks (MegaJam §15d)

Every sign in this kit is a **blank lit panel or an invented abstract glyph block**. No real shop name, no
real logo, nothing readable, nothing traced off a photograph of a real street. This was a design constraint
from the start, not a cleanup pass — it is also why the signage is shapes rather than text.

---

## How to put it in the game

**On the builder** (GameStation, or Justin's Mac — M Station is a maker and must not save Unreal files):

1. **`git pull` with Unreal CLOSED.** This moves binaries; that is the trap this project has already hit.
2. Copy `Art/Blender/export/City/` into `JumpCut/Content/Game/Imported/City/` **with Unreal open**, and let
   Interchange auto-import the FBXs. Same route the characters came in by — auto-import is on for FBX here
   (it is only `.glb` that it ignores).
3. In the editor, Play mode stopped:
   ```
   py C:/Users/thecl/code/jump-cut/tools/jumpcut_city_place.py hide
   ```
   `hide` also hides the eight grey boxes the city replaces. Leave it off and you get the city with the grey
   boxes still there, which is a useful way to check alignment first.
4. **Look at it, then save the level yourself.** The script does not save, on purpose.

It only ever adds or removes actors tagged `JC_City`, so running it twice gives you one city and not two. It
never touches a `C1_Layout` actor, the player, the floor, the sun, the gates, the boss or any marker, and the
grey boxes are **hidden, not deleted** — `jumpcut_city_place.py show` puts them back.

### Conventions, if you move things by hand

- **Units:** the FBXs are centimetres in Unreal, and every model stands on its own origin at z = 0. The
  exceptions are deliberate: wall-mounted pieces (`SM_CafeAwning`, `SM_CafeSign`, `SM_Awning`,
  `SM_FireEscape`, `SM_CableSpan`) have their geometry start at mounting height, so you place them at the
  **foot of the wall** and they appear where they belong.
- **Buildings face +Y with their body running to −Y.** So on an east–west street, **yaw 0 = the south side**
  and **yaw 180 = the north side**, and the street line is a single y value to snap to.
- **The cafe floor top is at z = +0.02**, 2 cm above `Floor_Base`, so it reads as a tiled threshold instead
  of z-fighting the level floor it stands on.

## What is checked, and what is not

**Checked.** All 44 exported FBX were **re-imported into a clean Blender and re-measured**, rather than
trusting the exporter: every one comes back as a single mesh, within 1.5 cm of its intended size on both
axes, with its triangle count exact and every material slot named `MS_City*`. Then every model was built,
measured and looked at — the check sheets are in `Art/Blender/cache/`
(`city_cafe.png`, `city_cafe_interior.png`, `city_city.png`, `city_ruins.png`, `city_props.png`) and the
layout was assembled in Blender and rendered from eye height at the player's own start point
(`city_layout_lane.png`, `city_layout_lane_back.png`, `city_layout_cafe_west.png`,
`city_layout_plaza.png`, `city_layout_overview.png`). `tools/jumpcut_city_layout.py` then checks every one of
the 216 placements against the real footprints the kit measured, and reports anything standing in the
player's road, the cafe, the boss arena, either gate opening or the exit run, plus any two lane buildings
overlapping. **It currently reports nothing.**

That check is not decoration. It caught **17 real collisions** that none of the renders showed, all from one
cause: a floor band added to the building sides widened every building by 14 cm while the layout script was
still using a hand-kept width table. Widths are now read from the kit's own measured footprints.

~~**Not checked.** `tools/jumpcut_city_place.py` has never been run.~~ **Run for the first time on Justin's
Mac mini, Fri Nov 13, 23:55 UTC**, and the prediction held exactly: **one line** needed fixing
(`set_editor_property('hidden_in_game', ...)` is not an `AActor` property; it is `set_actor_hidden_in_game()`),
and the layout itself needed none. 37 models imported, **224 actors placed and saved**, 8 grey boxes hidden,
verified after a reload from disk. It also gained a `prepare_meshes()` step it never had: Interchange turns
Nanite **on** and builds one auto convex hull, and both are wrong for this kit.

**The layout itself needed two fixes, and neither was visible.** The committed `city_layout.json` was **eight
actors out of date** — it predated the `City_Avenue*` block, so the New York avenue the car crashes in from
existed in the generator and nowhere else. And `City_Landmark` stood at (12600, 0), which is inside beat 4's
platforming run; beat 4 was placed after this layout was authored, so the checker had never heard of it. The
checker now carries a `beat 4 run` no-go box and the tower is at x = 16200. See ROADMAP, "The city is in the
level".

**Still not seen by a person.** Everything above is traces, counts and one editor screenshot — nobody has
played it.

## Set pieces — the last grey boxes up to the cleaver boss (Fri Nov 13, evening)

> **In the game as of Sat Nov 14, 02:10 UTC** (issue #40, Justin's Mac mini). All eleven are imported; the
> seven that are level geometry are placed as 21 `JC_City` actors by `jumpcut_city_place.py add`, and the
> four Blueprint meshes are swapped in at scale (1,1,1). 18 grey boxes hidden, asphalt on both floors, both
> gates still block, and the player still reaches the driver with 134 cm to spare. Nobody has played it.
>
> **Keep `SIMULATED` in `tools/jumpcut_city_place.py` in step with `KNOCK` in `tools/unreal_chaos_props.py`.**
> `SM_CafeChair`, `SM_TrafficCone` and `SM_TrashBags` must keep simple collision or the chaos props stop
> being knockable, and the placer used to overwrite them.

The Team Owner asked for everything up to and including the Splice boss to come out of grey boxes and
mannequins. The characters for that were already made (and are waiting on the builder: issues #5, #6, #7).
What had **no model at all** was the scenery the first build left as boxes after the city went in. Eleven
more models, same kit, same rules — **4,332 triangles, 0 credits, nothing uploaded**:

| Model | Replaces | Notes |
|---|---|---|
| `SM_CrashCar` | `C1_Cafe_Car`, `C1_Cafe_CarCab` (two red boxes) | 3.88 × 1.76 × 1.43 m, nose east, bonnet sprung, front bumper hanging. **Right-hand drive with the driver's door open on the +Y side** — the side his body lies on at (−380, 220) |
| `SM_Shrapnel` | the red bar in `BP_Shrapnel` | 79 cm torn strip of the car's own bodywork, long axis X, centred |
| `SM_YardWall_1250` ×4, `SM_YardWall_3040` ×2 | the six `C1_Plaza_Wall*` boxes | brick yard wall, 4 m, dressed on the arena face only: shutters, barred windows, blank posters, bulkhead lamps |
| `SM_Hoarding_990` ×2 | `C1_Run_WallN`, `C1_Run_WallS` | demolition-site hoarding — the run leads to beat 4 |
| `SM_PlazaGate` | the scaled cube in `BP_PlazaGate` | 0.4 × 5 × 4 m roller gate, **origin at its centre** like the cube |
| `SM_CheckpointPost`, `SM_CheckpointTaken` | `PostMesh` and `TakenSign` in `BP_Checkpoint` | a film-set light stand carrying a slate; the "taken" sign is the slate lit, with a tick |
| `SM_PlazaPaving` | nothing — the boss lot had a grey floor | 30 × 30 m, two-tone slabs, a ring where the boss stands. **No collision** |
| `SM_Crosswalk` ×4, `SM_RoadLines` ×8 | nothing — the lane had a grey floor | paint, 1 cm above the floor. **No collision** |

**Every wall keeps the footprint of the box it replaces.** The plaza fight was tuned inside those boxes, so
a prettier wall that stands 20 cm further in is a different arena. `jumpcut_city_layout.py` now carries a
`REPLACES` table — label, the grey box, its centre and size from `tools/c1_layout.py` — and fails the layout
if any replacement reaches more than 16 cm past its box into the play space. The check was proved by moving
a wall 30 cm in and watching it fail. The car's open door is the one allowed overhang (it swings 83 cm out
of the red box, towards the body) and is checked separately so it cannot cover the driver.

**The ground.** `Floor_Base` and `C1_Floor_RunExtra` still wear `M_GreyFloor`. The placer's `hide` and `add`
modes now put `M_CityRoof` (dark asphalt) on them, and `show` puts the grey back. Without that the white
road paint and the paving have nothing to read against.

**To put them in** (builder; the city is already placed and saved, so use `add`, which leaves the 224
existing actors and their packages alone):

1. `git pull` with Unreal **closed**, then copy the eleven new FBX from `Art/Blender/export/City/` into
   `JumpCut/Content/Game/Imported/City/` with Unreal open.
2. `py C:/Users/thecl/code/jump-cut/tools/jumpcut_city_place.py add` — places the 21 new actors, hides ten
   more grey boxes (18 in all), and sets the asphalt. Look, then save.
3. **Four meshes go inside Blueprints and the script does not touch Blueprints.** It prints them; they are
   also in `city_layout.json` under `blueprint_meshes`:
   - `BP_PlazaGate.GateMesh` → `SM_PlazaGate`, **relative scale back to (1, 1, 1)** (the cube was 0.4 × 5 × 4)
   - `BP_Checkpoint.PostMesh` → `SM_CheckpointPost`, scale (1, 1, 1), z = 0
   - `BP_Checkpoint.TakenSign` → `SM_CheckpointTaken`, scale (1, 1, 1); keep `M_CheckGreen` on its
     `MS_CitySignB` slot if the checkpoint should stay green
   - `BP_Shrapnel`'s bar → `SM_Shrapnel`, scale (1, 1, 1)

**Checked:** all eleven FBX re-imported into a clean Blender — one mesh each, within 1.5 cm, triangle counts
exact, every slot an existing `MS_City*` name, so **no new material is needed**. Layout regenerated: 245
actors, no problems. Rendered from where the player stands (`city_layout_cafe_car.png`,
`city_layout_plaza_in.png`, `city_layout_exit_run.png`, and `city_set_*.png` close-ups).

**Not checked:** none of it has been in Unreal. `set_ground()` and the `add` mode were written on M Station
and have never been run. The hidden grey boxes **keep their collision** — that is deliberate for the walls
and the car (identical arena), but it means the car's open door has the mesh's own collision on top; if the
player snags on it reaching the driver, switch the car to `WALK_THROUGH` and let the red box do the blocking.
`BP_Shrapnel`'s and `BP_Checkpoint`'s current component transforms are not written down anywhere, so the
scales above are the intent, not a measurement.

## Beat 4 — pieces made, not placed

The five ruin pieces are built and committed but **not in the layout**, because beat 4 has no level yet and
laying out beats 4–6 is the builder's job. They are sized against the one number that matters: **Splice
blinks 600 cm on open ground** (measured on Justin's Mac, Nov 13). So:

- a gap the player **must** blink is **6.5–8.5 m** — past a run-and-jump, inside a blink
- a gap they **may** jump is **under 3 m**
- platform tops are flat and at least 3 m across, because landing a blink on a narrow or sloped surface is
  where this kind of section stops being fun

## Cafe dressing and street life (Fri Nov 13)

Nineteen models were added on the note "the cafe should look like an anime cafe" and "everything outside
the play area looks barren". They are two groups in the kit, `cafedeco` and `life`.

**Cafe** — `SM_CafeFloorBoards`, `SM_CafeRug`, `SM_CafePendant`, `SM_CafeWallArt`, `SM_CafeChalkboard`,
`SM_CafeClock`, `SM_CafePlantTall`, `SM_CafePlantSmall`, `SM_CafeTableTop`, `SM_CafeStool`,
`SM_CafeBarCounter`, `SM_CafeBanquette`. Placed from `CAFE_DECO_CM` in `tools/jumpcut_city_layout.py`,
which is checked against `CAFE_DECO` in the Blender kit on every run, the same way `CAFE_DRESS` is.

**Street** — `SM_StreetTree`, `SM_Hedge`, `SM_LanternString`, `SM_BannerFlag`, `SM_LaundryRack`,
`SM_Scooter`, `SM_RoofBillboard`, placed by `street_life()`.

Four material slots are new: **MS_CafeWall** (cream plaster) and **MS_CafeFloor** (honey boards), so the
cafe can be warm without the street being warm; **MS_CityLantern** (emissive warm red); and **MS_CityLeaf**,
which is the first green in the project — every plant in the kit before this was painted `MS_CityCloth`,
which is beige.

### Rules this group added, all learned the hard way

- **Foliage is solid blocks, never crossed cards.** A card is one quad, so Unreal culls its back and the
  canopy vanishes from one side. Two-siding the material is worse: a back face renders with the FRONT
  face's normal, so the half of the canopy facing away from the sun lights as if it faced the ground and
  comes out black. Blocks have outward normals on every face. See `build_street_tree`'s docstring.
- **You cannot make a card two-sided by emitting it twice.** `B.finish()` welds coincident verts and the
  duplicate face is dropped, so the mesh comes out byte-identical and the tri count does not move.
- **Leaf green must be a LIGHT green.** The look bands `sceneColour / baseColour` and the shadow band is
  about 0.6x the base, so a realistic leaf green is black on the shadow side.
- **`street_life()` must run after `plaza()` and `exit_run()`.** It places with `put_clear()`, which nudges
  a prop along x until it stops standing inside something - and it can only avoid what is already in the
  list. Run earlier, it put six hedges through the plaza tower.
- **`put_clear()`, not `put()`, for anything standing on the ground.** The lane already has 246 things on
  it; there is no free hand-picked x left.

### The trap in `add` mode

`tools/jumpcut_city_place.py add` decides what is already placed **by actor label**. The cafe's labels are
positional, so inserting one prop renumbers every prop after it and `add` then places a second copy of each
renumbered actor on top of the first. That happened on this pass: seven duplicates, invisible in the
viewport, two coincident surfaces each. Run **`tools/jumpcut_city_dedupe.py`** (report) after any `add`,
and `... dedupe.py fix` if it finds any. It matches on mesh and position, not on names.

## The back alley, and the pass that stopped the props being boxes (Sat Nov 14)

Two notes from the Team Owner, which turned out to be one gap seen twice: *"a lot of things on that street
look very blocky"*, and *"make sure the scene makes sense — a car comes bursting through the back wall of
the store leading to the alley… the player then goes out to the alley and the thugs get in the way."*

### Chamfers, not triangles

Under `MI_AnimeLook` an axis-aligned cuboid renders as **three flat fields of colour meeting at three black
lines**, because the outline pass draws every normal break. That is a picture of a box however it is
painted, and gluing more small boxes to the front of it does not help — detail only counts where the
outline pass looks, which is **the silhouette and the corners**.

The builder gained `B.poly`, `B.loft`, `B.prism` and `B.cbox`. **`cbox` cuts INWARD**, which is the whole
reason this could be a sweep over finished models: a chamfered prop keeps the exact footprint the layout
checker measured, so ten props were rebuilt without moving any of the 316 things already in the level.

| Prop | tris | What it gained |
|---|---|---|
| `SM_ACUnit` | 48 → 398 | a **round** fan guard and louvres. There are more of these on the lane than anything else |
| `SM_VendingMachine` | 216 → 962 | chamfered body, bevelled top, recessed kick, and a display that is a real recess with a reveal |
| `SM_StreetLamp` | 130 → 426 | a tapered column and a tapered lantern head with a lit underside, instead of a stick with a plate on it |
| `SM_CrateStack` | 96 → 1,152 | slats **with gaps**, which is what tells a crate from a wooden cube |
| `SM_TrashBags` | 320 → 628 | lobed sacks that bulge low and gather at a knotted neck, not cylinders |
| `SM_Bench` | 132 → 572 | cast ends, which is the shape that says "bench" from across the street |
| `SM_Barrier`, `SM_Bollard`, `SM_Planter`, `SM_Awning` | — | chamfers, a taper, a lamp, a scalloped valance |

Whole city: **29,683 → 41,299 triangles**. One street goon is 18,000.

### The alley, and the geography call behind it

The crash is on the cafe's **west** wall and what was on the other side of it was a wide avenue with a zebra
crossing. A car coming off a main road through the back of a shop is a different accident from a car coming
down the alley the shop puts its bins in.

**The decision, because it is a judgement call and may be reversed:** the expensive reading is that the
player should leave through the hole, which relocates 60 m of lane, the plaza, both gates and the boss. The
reading taken is that **the cafe is a corner unit on an L-shaped back lane** — the alley runs down its west
(back) side and turns the corner along its east front. The car came off the avenue, down the alley, through
the back wall; the player leaves by the front door into the **same lane**, one corner along. Nothing moves.

Ten models, because every building in this kit is a shopfront and a service alley is defined by what is
**not for sale** in it: `SM_KeiVan`, `SM_Dumpster`, `SM_DuctRun`, `SM_MeterBox`, `SM_GasBottles`,
`SM_PotRow`, `SM_AFrameSign`, `SM_ShopDisplay`, `SM_DrainGrate`, `SM_FireStair`. Same rules as the rest of
the kit — procedural, **0 credits, nothing uploaded**.

### Three things measured here that are worth not re-deriving

- **The alley had only one wall.** `City_CornerSW`'s origin is at its own corner, so at yaw 90 it occupies
  x −2632…−1000, **y −1500…−100** — the south side is solid building for the alley's whole length, and the
  north side had nothing at all past x = −607. Two building backs (`City_AlleyBackN0/N1`) close it and set
  the corridor at y −100…560, i.e. **6.6 m**. Anything standing against the south wall must therefore sit
  at y > −100, not at y ≈ −470 where an 11 m alley would have put it.
- **The south wall is a flank, so it is blank.** This kit puts a building's detail on its facade only, so
  the alley's south side was 16 m of featureless 22 m slab. Two `SM_Hoarding_990` cover it at eye height.
- **Vans park at y = ±345.** The road keep-clear ends at 260 and a van is 150 wide, so that spans 270…420:
  wholly on the pavement side, fight lane untouched, and none within 9 m of the goon spawner at x = 4600.

### Traps this pass added to the list

- **Rewriting a prop's RNG loop moves the prop.** Changing how many times `rng` is called per bin bag
  reshuffled every bag and grew the pile's footprint from 1.20 × 1.00 m to 1.57 × 1.31 — a real collision on
  a 2.6 m pavement, invisible in a render, caught only by diffing `city_models.json`.
- **Never chamfer a 2.4 cm board.** Chamfering the crate slats cost 1,400 triangles on a prop placed twelve
  times, for a bevel nobody can see. `cbox` for the posts, plain `box` for the slats.
- **`put_clear` outcomes depend on footprints.** Shrinking `SM_TrashBags` moved `City_Hedge_S5` by 30 cm,
  40 m away, because the nudge search runs against whatever is already placed. **Diff the layout
  actor-by-actor against the committed one before running `add`** — that diff (0 removed, 71 added, 1 moved)
  is what proved `add` was safe here.

## Known gaps

- **No people.** The city has no pedestrians. See `docs/CHARACTERS.md` → *Crowds* for the cheap route
  (recolour instances of the two models we already own) and why no new character was generated for it.
- **Buildings carry their detail on the facade.** Sides and backs get a floor band every 3.4 m — enough to
  read as a building from any angle — but not windows. That was a deliberate trade and it is visible if you
  stand in the plaza and look at the back of a lane building.
- **The lane is fixed-width.** It is one straight 60 m corridor because that is the level that exists. If
  beats 4–6 add a second street, the kit tiles the same way.
