# The plaza is paved, and the lamps face the road

**Sun Nov 15, about 4:15 PM, GameStation (builder). After the noon cut-off; the Team Owner asked while playing.**

## What we asked for

> the props are fine but we need to do something about the floor in the plaza

> make sure lamp posts and other assets are not obviously facing the wrong way.

## What happened

**The floor.** The plaza's floor is one mesh in three flat colours (a cream and grey checker inside a brick border),
and those three materials are shared with half the city, so they could not be changed. But the kit gives every
face real-scale UVs, 1 unit = 1 m, so a tiling texture needs no new geometry.

- `Art/Blender/plaza_pavers.py` draws the texture: stone setts in a running bond, 2 m square, near-white so it can
  be tinted. Sized against the 2-pixel rule in CLAUDE.md: setts 50 x 25 cm, a 3 cm joint, and low contrast so the
  ink pass does not outline every stone.
- `tools/jc_plaza_floor.py apply` imports it, makes one material (texture x tint) and three instances (border,
  stone A, stone B), and overrides the three slots on `City_PlazaPaving` only. `revert` puts the kit colours back.
- The script failed on its first run with a syntax error: a `'\'` in a Bash heredoc. Nothing had been changed.

**The lamps.** There was no time to look at 150 swapped props one by one, so `tools/jc_facing_audit.py` measures
instead: for each prop with a front, how much open ground is in front of it and behind it; for each lamp, which
side its arm overhangs and how much room is on that side.

- First version flagged 17 and most were wrong. It cast its rays from the middle of each prop, and the kit sets
  ducts, meter boxes and air-conditioners INTO the wall (a duct is 42 cm deep with 35 cm of it inside the building),
  so the ray started inside the wall. Rays now start just outside the prop's own front and back faces.
- Second version: **12 lamps** flagged, and they were all really wrong. Every street lamp on the north and south
  pavements and all six plaza lamps had the arm on the side with LESS room: over the shopfronts and into the plaza
  walls, not over the road. Turned 180 about their columns.
- It also flags three box props (an air-conditioner, a dumpster, a meter box). Each has another prop standing in
  front of it, which is not the same as facing the wrong way. Left alone. `fix lamps` exists so that a sweep cannot
  turn those too.

**My screenshots went blank twice** while checking this: `HighResShot` started returning empty sky with an axis
gizmo, in a running game whose world (547 actors) and camera both read back correctly. `CaptureEditorImage` showed
the real picture, and that the boss had killed the test player while I stood in his arena. Cause not found.

![The plaza after](../media/2026-11-15-plaza-paving-and-lamps.png)

## Checked, and not checked

- Checked by eye from the game camera: the paved plaza with the boss in it.
- Checked by script: 12 lamps turned and saved; a re-run of the audit is the proof they now point at the open side.
- **Not checked by eye:** each street lamp, and the three lamps the audit could not judge (avenue, crossing, alley:
  open on both sides). The joints in the paving at a distance, for shimmer. A packaged build.

## What we learned

- **A measurement that flags most of what it looks at is measuring itself.** Seventeen flags, and the pattern in
  them (everything set into a wall) said where the ray was starting.
- **Give a fix a narrower door than the report.** The report may be wrong about three things; `fix lamps` cannot be.
