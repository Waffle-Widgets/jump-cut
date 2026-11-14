# The street stops being boxes, and the alley starts existing

*Sat Nov 14, 2026, 3:30 – 5:10 AM Pacific. M Station.*

The Team Owner gave two notes at once and they turned out to be the same note:

> "A lot of things on that street look very blocky."
>
> "Consider the layout of the city streets we are on and make sure it makes sense and that the scene
> makes sense. Two baristas are working a coffee shop in the city… a car comes bursting through the back
> wall of the store leading to the alley… The player then goes out to the alley to see what is going on
> and the thugs get in the way."

The first is a modelling note. The second is a geography note. Both of them are about the same gap: the
city kit knows how to make a **shopping street** and nothing else, so everywhere the story needs somewhere
that is *not* a shopping street, the level has either a box or a main road.

---

## Part one: why everything was blocky, and what actually fixes it under this shader

Every prop in the kit is built from `B.box()`, which emits an axis-aligned cuboid with six flat faces and
twelve hard 90° edges. That is the single worst shape to put under this project's look. `MI_AnimeLook`
flattens lighting into two bands and draws an outline on every depth and normal break, so a cuboid renders
as **three flat fields of colour meeting at three black lines** — which is a drawing of a box, no matter
what colour you paint it or how many small boxes you glue to the front of it.

The fix is not more triangles in general. It is triangles **on the silhouette and on the corners**, because
those are the only two places the outline pass looks. So the builder gained four methods:

| Method | What it gives |
|---|---|
| `B.poly(pts2d, z, …)` | one horizontal n-gon |
| `B.loft(prof0, z0, prof1, z1, …)` | side walls between two profiles — a taper is just a smaller second profile |
| `B.prism(prof, z0, z1, …)` | the two above, with caps |
| `B.cbox(p0, p1, …, ch, top, bot)` | a cuboid with its vertical corners cut in by `ch`, and optionally a bevelled top and a recessed kick |

**`cbox` cuts INWARD**, and that is the detail that made this a sweep over finished models rather than a
re-layout. A chamfered prop keeps the exact footprint the layout checker already measured, so ten props
could be rebuilt without moving one of the 316 things standing in the level.

Ten props were rebuilt. The ones that mattered most were the ones the player passes closest to:

- **`SM_ACUnit` — 48 → 398 tris.** There are more of these on the lane than any other prop, and at 48
  triangles each one was forty-eight triangles of "box", twenty times over. It now has the two things that
  make a condenser readable at a glance: a **round fan guard** and horizontal louvres, both of which the
  outline pass draws for free.
- **`SM_VendingMachine` — 216 → 962.** Chamfered corners, a bevelled top, a recessed kick, and a display
  that is a real **recess** rather than a decal on the front, so the reveal gives the ink line a frame.
- **`SM_StreetLamp` — 130 → 426.** Six metres of constant-radius stick with a flat plate on the end became
  a tapered column with a raking bracket and a proper tapered lantern head with a lit underside.
- **`SM_CrateStack` — 96 → 1,152.** Slats with gaps between them, because the gap is what distinguishes a
  crate from a wooden cube.
- **`SM_TrashBags` — 320 → 628.** Lobed sacks that bulge at the bottom and gather at a knotted neck,
  instead of a 7-sided cylinder with a smaller cylinder on top, which reads as a bucket.
- Plus **`SM_Bench`, `SM_Barrier`, `SM_Bollard`, `SM_Planter`, `SM_Awning`** (which gained a scalloped
  valance and ribs under the canvas, the treatment `SM_CafeAwning` already had).

The whole city went from **29,683 to 41,299 triangles**. For scale, one street goon is 18,000, so the
entire city — every building, every sign, every bin — still costs less than two and a half characters.

### Three measurement bugs this pass produced, all caught by re-measuring rather than by looking

1. **The bin bags escaped their own base plate.** Rewriting the bag loop changed how many times the RNG was
   called per bag, which moved every bag, and the pile's footprint grew from 1.20 × 1.00 m to **1.57 × 1.31**
   — on a 2.6 m pavement that is a real collision. Clamped back.
2. **The dumpster's castors were centred on z = 0**, so half of each wheel was under the floor
   (`z_min = −0.055`). Caught by the kit's own off-ground report.
3. **The crate stack cost 1,920 triangles** because every 2.4 cm slat was being chamfered — a chamfer
   nobody can see on a 2.4 cm board, on a prop placed twelve times. Slats are plain boxes again; only the
   corner posts are chamfered. 1,920 → 1,152.

---

## Part two: the scene did not make sense, and here is exactly where

Beat 1 as the Team Owner describes it is: two baristas, a customer, latte art, a car through **the back
wall**, which leads to **an alley**; then the player goes **out into that alley** and the thugs are in the
way.

The level does put the crash on the cafe's **west** wall. What is on the other side of that wall is a wide
New York avenue with a zebra crossing painted across it. **A car coming off a main road through the back of
a shop is a different accident from a car coming down the alley the shop puts its bins in**, and only the
second one is the scene as written.

### The decision, because two readings were possible and they cost very different amounts

**The expensive reading** is that the player should leave through the hole, so the fight belongs west. That
relocates 60 m of lane, the plaza, both gates, the goon spawner and the boss. It is not a Saturday's work
with 38 hours on the clock.

**The reading taken** — and it is also simply truer to a Tokyo corner — is that **the cafe is a corner unit
on an L-shaped back lane**. The alley runs down its west (back) side and turns the corner along its east
front. The car came off the avenue, down the alley beside the cafe, and through the back wall. The player
goes out of the front door into the **same lane**, one corner along, and the thugs are down it.

Nothing moves. The west side stops being a main road and starts being a back lane, and the first 15 m of
the east lane keeps that character before the shops start. This is written down because it is a judgement
call and the Team Owner may want the other one.

### What a back lane needed that the kit had never built

Every building in the kit is a shopfront. A service alley is the opposite — bins, ducts, meters, gas
bottles, a fire stair, **nothing for sale**. That absence is what defines it. So ten new models:

`SM_KeiVan` · `SM_Dumpster` · `SM_DuctRun` · `SM_MeterBox` · `SM_GasBottles` · `SM_PotRow` ·
`SM_AFrameSign` · `SM_ShopDisplay` · `SM_DrainGrate` · `SM_FireStair`

Still procedural geometry from our own Blender script: **0 Meshy credits, nothing uploaded, nothing
generated**. Meshy and Gemini were available and were not used, for the reason `docs/CITY.md` has given
since the kit was written — image-to-3D is the right tool for a character and the wrong tool for a thing
the player walks past at 80 cm, where what matters is a measured footprint and a flat vertical face.

### The alley had only one wall, and nothing said so until something was placed against both of them

`City_CornerSW` is a corner block whose origin is at its own corner, so at yaw 90 it occupies
x −2632…−1000, y −1500…−100 — the alley's **south** side is solid building for its whole length. North of
the cafe there was one `ShopHouse_C` and then **nothing at all** until the avenue's corner block 26 m away.
An alley with one wall is a yard. Two building backs now close it, and they set the corridor at
y −100…560 — **6.6 m, which is an alley**, rather than the 11 m assumed when this was planned.

The south wall is that corner block's **flank**, and this kit deliberately puts a building's detail on its
facade only, so it was 16 m of blank 22 m slab. Two demolition hoardings cover it at eye height — which
also quietly answers why a back lane beside a main road is derelict enough for a car to come down it at
speed.

### Sixty metres of road with nothing on it

The lane's clutter all stands hard against a shopfront or on the kerb edge, and the middle 5.2 m is kept
clear for the fight, so the eye crossed 10 m of street and found nothing between the two facades. Three
**kei vans** are now parked at y = ±345, which is tight against the kerb and **wholly on the pavement
side**: the road keep-clear ends at 260 and a van is 150 wide, so it spans 270…420 and the fight lane is
untouched. None is within 9 m of the goon spawner at x = 4600. Two more are parked on the avenue, which is
what the player stares at through the hole for the whole of beat 1.

Pots, A-boards and produce tables fill the 300…470 band nobody was using, and gullies went in at the kerb
line because the road was 5.2 m of flat grey with nothing but manholes on it.

**The van is off-white, not red.** The first five came out on `MS_CityAccent`, which is the same red as
every awning, barrier and traffic cone on the lane, and five of them turned the street into a fire station.
Body on `MS_CityWall`; `MS_CityAccent` kept for the signwriting panel only.

**Layout: 316 → 387 actors**, checker clean — nothing in the player road, nothing in the cafe, nothing in
the arena, nothing in a gate opening, and nothing left un-placed. Diffed actor-by-actor against the
committed layout before any of it went near Unreal: **0 removed, 71 added, and exactly one existing actor
moved** — `City_Hedge_S5`, by 30 cm, because `put_clear` nudges depend on the footprints of what is already
down and `SM_TrashBags` got smaller. That diff is what made `add` mode safe to run.

---

## What is NOT done

- **Nobody has played it.** Every check above is a Blender render and a layout checker. Whether the street
  still reads as blocky in the cel shader, in motion, at 60 fps, is the Team Owner's call.
- The **alley is scenery, not a place you can stand in** — beat 1 never sends the player through the hole.
  Whether `Floor_Base` even extends west far enough to walk on is unchecked.
- The scene still has **no customer** to make latte art for, and the **ceiling does not collapse** — both
  are in the Team Owner's account of beat 1 and neither exists. Filed rather than faked.
