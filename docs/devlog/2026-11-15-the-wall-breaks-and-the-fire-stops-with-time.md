# The wall breaks, the fire waits for its shot, and the driver lands on the right side

**Sun Nov 15, 06:20 UTC (Sat Nov 14, 10:20 PM Pacific) — Justin's Mac mini**

## What we asked for

Feedback after playing the beat-1 opening, five items:

1. *"The initial wall is still just a block. I think we should replace that structure with one that
   is the complete building, then uses the chaos extensions to make the wall breakable so the car
   plows through."*
2. *"There's a third camera cut that's just looking at the car. That's when it should burst into
   flames."*
3. *"The fire should also be frozen during the freeze frame ability. That's the main focus that
   time has stopped."*
4. *"Let's have the driver on the right side of the car and do some ragdolling to get him into
   position."*
5. *"The main character has some movement right at the beginning of the clip like he just loaded
   in. Should be standing there like it's just another day at work."*

## What happened

The Mac lost power mid-session on the 14th. The *scripts* for items 1-4 survived on disk and were
committed as `db3b823`, but everything that lived in the editor — the placed wall, the director's
new variables, the rewritten graphs — died with the machine. This session rebuilt all of it, which
is exactly why these beats are script-driven.

**The wall is a Geometry Collection now.** `B1_Cine_WallPatch` — a grey cube standing 4 cm proud
of the cafe's west wall, which popped in and out and was the whole of complaint #1 — is deleted.
In its place `B1_Cafe_WallPanel_GC` stands in the hole: 299 cm wide, 255 cm tall, 19 cm thick, cut
from `SM_CafeWallPanel` through the same Dataflow template that made `GC_CrashCar`, drawing the
kit's real `M_CityBrick` / `M_CafeWall` / `M_CityWood`. The director breaks it on the frame the
car reaches it (`CineWallTime` 4.70) with the four-step recipe a kinematic collection needs.

**The fire waits for its own shot.** Cut C runs 6.20 → 8.80 and is the shot of the car on its own,
so `CineFireTime` is **7.00** — inside it. Before that the fire is hidden *and* stopped, so its
particle system has not advanced a single frame when it is lit: the burst is real rather than a
plume that has been burning off screen since the crash.

**And it stops when time stops.** `CineFireTimeStep` runs every tick and sets the fire's Niagara
component to `CustomTimeDilation` 0 while `FreezeFrameActive` is true, 1 otherwise. Freeze Frame
freezes the fire with everything else, which is the point of the power.

**The driver comes out of the car's right side and lands as a ragdoll.** `ObjDriverLoc` moved from
`(-380, +220)` to `(-395, -215)` — the car drives in heading +X, so its right is -Y, which is also
screen-right from where the player stands. The thrown body's keyframed arc is mirrored to match,
and on the frame it lands the real `BP_CrashDriver` takes over simulating physics, so the pose it
settles in is physics rather than a hand-set rotation. It is behind `DriverRagdoll`, one checkbox.

**Item 5 turned out to be ours after all, and it is one word.** `PlayerRefreshMoveLock` released a
move lock with `SetMovementMode(MOVE_Falling)`. The title screen's lock is released on the first
tick of every game, so the player entered a fall-and-land on frame 1 — which on a Meshy rig with
`force_root_lock` is also a 90 cm hover. `MOVE_Walking` is the correct release; the movement
component drops to falling by itself on the next update if there is no floor. The *other* half of
item 5 — the wide-legged stance and the odd arm angle — is #73, the retarget base pose, and
GameStation is regenerating all 48 `_CWM` clips for it right now. That half is not fixed here.

## What we learned

**`Variables|Actor|SetCustomTimeDilation` has no `self` pin.** It is the actor's *own* dilation and
nothing else's: `write_graph_dsl` refuses `:self` outright with
*"Input pins: ['CustomTimeDilation']"*. To slow something else down, reach its component —
`Niagara|SetCustomTimeDilation`, whose pins are **`self`** and **`Dilation`** (not
`CustomTimeDilation`, which is the spelling that fails).

**That refusal is the cheapest documentation in the project.** `write_graph_dsl` names the valid
pins in its error and rolls the whole graph back, so guessing a pin name costs one call and teaches
you the right one. `get_node_type_pins` returns pin *values*, not names, so it cannot answer this.

**Order matters between two scripts that both look standalone.** `b1_opening_cine.py` reads the
**placed** `BP_CrashDriver`'s location to key the last two frames of the thrown body, so rebuilding
the sequence before moving the driver lands the arc on the old left-hand spot — mid-air tumble to
y -118, then a snap to y +220. The sequence was built, the driver moved, and the sequence rebuilt;
it now lands at `(-395, -215)`, exactly where the body stands.

**A `Package` has no `is_dirty()` in UE 5.8 Python.** The obvious name, and it raises.

**Python runs on the game thread, so you cannot wait for a cinematic — drive it.** An 11 s sequence
is long over before a second MCP round trip (5-8 s) arrives, and `time.sleep` stops the very world
it is waiting for. `tools/b1z_pie.py open` calls `CineDirectorStep` with a fixed delta itself: the
director's own Tick cannot run while the script holds the thread, so the loop is the only thing
advancing it and every trigger is exercised through the real function. What it *cannot* show is
physics — no ticks means no falling debris and no settling ragdoll — so it proves each trigger
fired and each physics state was applied, and a later sample shows where things came to rest.

**`FreezeFrameActive` is not instance-editable**, so the fire-freeze test drives the real power:
`PlayerGrantFreezeFrame` → `FreezeFrameStart` → step → `PlayerFreezeFrameEnd` → step. That is
better evidence than writing the flag would have been, because it goes through the gates.

## What was measured

Stepped through the director's own clock in PIE, with the real functions:

| trigger | fired at | wanted |
|---|---|---|
| wall breaks | **4.700** | `CineWallTime` 4.70 |
| real wreck revealed | **6.200** | `CineImpactTime` 6.20 |
| ragdoll takes over | **6.400** | `CineBodyTime` 6.45 |
| car catches fire | **7.000** | `CineFireTime` 7.00, inside cut C (6.20-8.80) |
| ragdoll settles | **8.100** | 6.40 + `RagdollSettle` 1.8 |
| control handed over | **11.000** | `CineLength` 11.0 |

The wall genuinely came apart: its bounds went from the intact slab's extent **(9.5, 149.6, 127.3)**
to **(170.1, 240.9, 133.9)** — 19 cm thick to 340 cm across — with `object_type` switched to
`Chaos_Object_Dynamic`. The driver finished at `(-395, -215, 0)`, `RagdollLive` true, mesh
simulating. The fire read `CustomTimeDilation` **1.0** lit, **0.0** with Freeze Frame running, and
**1.0** again after it ended.

All three Blueprints compile with warnings-as-errors. `b1_beat1_audit.py` reports **0** labels
appearing more than once, and `b1x_orphans.py` reports **477 actors / 477 packages / 0 orphans** —
the old director, beacon and wall-patch packages were `git rm`-ed in this commit, because World
Partition loads every file in `__ExternalActors__` and a stale director would run beat 1 twice.

## What is NOT done

- **Nobody has played it.** Every number above is a script driving the real functions, not a person
  watching a car come through a wall. The feel of an 11 s opening is not ours to call.
- **The debris has not been watched falling.** The break is proven applied and the bounds prove it
  spread, but no one has seen the pieces land.
- **Item 5's stance half is GameStation's** (#73) and is still open.
- `SM_CafeWallPanel`'s own material slots are null — harmless, because the placed actor is the
  Geometry Collection and that carries the right materials, but it means the static mesh renders
  grey if anyone ever places it directly.
