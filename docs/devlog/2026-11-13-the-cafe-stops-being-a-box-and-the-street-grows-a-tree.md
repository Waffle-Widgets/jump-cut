# The cafe stops being a box, and the street grows a tree

**Fri Nov 13 2026, late (Pacific) — M Station**

The note was two lines: *the cafe should look like something you'd see in an anime*, and *everything
outside the play area looks barren*. Both were right, and the second one was right about something I did
not expect.

## What the cafe actually was

A counter, a register, an espresso machine, a pastry case, two shelves, three tables and six chairs, in a
grey-white box. That is not a short list — it is most of a cafe. What was missing was everything that is
not furniture: no light fitting (the ceiling had Unreal's light-bulb icon and nothing else), nothing on a
wall, nothing on a table, nothing growing, and a floor that was one untextured quad the colour of the
street outside it.

Nineteen models later it has a plank floor, four pendant lamps, a chalk menu board behind the counter, two
groups of framed pictures and a clock on the long wall, a padded corner banquette with a rug, a window bar
with two stools along the shopfront glass, two floor plants and two small pots, and a cup-and-saucer set on
each of the three tables. Two new material slots carry the warmth the room never had: **MS_CafeWall**
(cream plaster) and **MS_CafeFloor** (honey boards), so the cafe can be warm without repainting the whole
city with it.

The floorboards and the rug are laid 2 cm over the shell's concrete slab with **no collision**, the same
arrangement the plaza paving and the road markings already use. The player still stands on the slab every
fight in beat 1 was tuned on.

## The street had no living thing in it

This is the part worth writing down. The lane has buildings, vertical signage, utility poles, cable spans,
air conditioners, fire escapes, balconies, crates, bin bags, bicycles, vending machines, barriers and cones
— and it still read as empty, because **not one of those is alive**. Nothing was parked anywhere in sixty
metres of shopping street. The air over the road between first-floor height and the cables was completely
empty. And there was no green anywhere: the kit's only foliage was the shrub inside `SM_Planter`, and it
was painted **MS_CityCloth**, which is beige.

So: street trees mid-pavement, paper-lantern strings across the road, shop banners off the facades, washing
out on the balconies, parked delivery scooters, clipped hedges round the boss lot, and billboards on the
lane roofs. The shrub is green now.

The avenue got the same treatment, deliberately, because **it is the only thing the player sees through the
hole in the west wall for the whole of beat 1** — two trees, a hedge row and a lantern string, all placed
inside the cone that hole actually admits.

## Four things that were not obvious

**A single quad has one side, and nothing tells you.** The first street trees used crossed leaf cards, the
standard cheap tree. From the south: a full canopy. From the north: a bare trunk. Correct materials,
correct placement, no warning, no error. Marking the material two-sided fixed the culling and produced a
worse bug — Unreal renders a back face with the **front** face's normal, so every card pointing away from
the sun lit as though it faced into the ground, and half the canopy came out pure black *before* the cel
pass. Two-sided foliage shading and a self-lit term both failed to shift it. The canopy is **solid blocks**
now, which have outward normals on every face by construction. `SM_Hedge` was built from blocks from the
start and never had the problem, which was the clue.

**Doubling the geometry does not make a card two-sided.** I tried emitting each leaf twice with reversed
winding. The tri count did not move: `finish()` welds coincident verts and bmesh drops the duplicate face.
An hour's work that produced a byte-identical mesh. The helper is gone; the note is in the kit.

**A believable leaf green is black under this look.** The post-process bands `sceneColour / baseColour`,
and the shadow band is roughly 0.6× the base. A realistic `(0.29, 0.46, 0.22)` comes out of the shadow side
as near-black. `MS_CityLeaf` is `(0.46, 0.64, 0.30)` — a light green, chosen so both bands still read as
green rather than so the leaf is accurate.

**`ensure_materials()` could not change a colour.** It returned early for any material that already
existed, so editing `COLOURS` did nothing at all on a machine where the material had been made once. It now
reconciles the existing material with `COLOURS`, `TWO_SIDED` and `FOLIAGE` every run.

## And a bug the dressing uncovered

Running the placer's `add` mode created **seven duplicate actors** in the cafe: a shelf, three tables and
three chairs, each a second mesh at the identical transform.

`add` decides what is already in the level **by actor label**, and the cafe's labels are positional
(`City_Cafe_%02d_%s`). Inserting the register at index 1 on Nov 13 renumbered everything after it; four of
those actors were renamed by hand at the time and eleven were not. So `add` looked for
`City_Cafe_09_CafeTable`, could not find it, and made one — standing inside the table that was already
there under its old name. Nothing looks wrong in the viewport. What you get is double the draw calls and
two coincident surfaces fighting for the depth buffer, which is worth knowing about while
[#67](https://github.com/Waffle-Widgets/jump-cut/issues/67) is open on exactly that kind of shimmer.

`tools/jumpcut_city_dedupe.py` matches on `(mesh, position, yaw)` instead of on names, which is the thing
that cannot drift. It reports by default and only acts on `fix`. The seven duplicates are gone and the four
stale labels are corrected, so `add` is honest again.

## What is not done

**Nobody has played any of this.** Everything above is the editor rendering its own level from a camera I
positioned. Whether the cafe reads as somewhere a person works is the one question measurement cannot
answer.

The plaza trees stand **outside** the lot and hang over its wall, because there is no room for one inside:
the gap between the arena keep-clear and the wall is 200 cm and a street tree is 255 cm across. The lane
still has no pedestrians (`docs/CHARACTERS.md` → *Crowds*). And the laundry racks hang at a fixed 3.8 m
rather than on a measured balcony, so a couple of them sit in front of blank wall.
