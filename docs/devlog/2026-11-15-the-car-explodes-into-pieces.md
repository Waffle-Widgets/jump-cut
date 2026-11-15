# The car explodes into pieces, and the camera turns to point at the goons

**Sat 14 Nov 2026, late evening (Sun 15 Nov, 02:00 UTC).** Justin played the beat that
landed an hour earlier and sent six more pieces of feedback. Four of them are built;
two of them are issues he asked to be filed rather than fixed.

## What he asked for

> 1. Lets use that explosion sheet to have the car explode after she's saved (and
>    freeze frame ends) 2. There's a box object blocking the hole in the wall? Is that
>    supposed to be the before wall? lol If we need assets for that wall peice to then
>    break into peices then create a github issue for that. 3. create a github issue to
>    get the fire asset too. 4. Can we make the car explode into peices using the chaos
>    stuff that is used for the small objects that break? Then it can break into peices
>    in the explosion. 5. The car exploding and then panning around to point the camera
>    to the next goal. Should be a cinematic. And we should have a text box for
>    progressing the story from the voice in our head to defeat the goons coming for
>    the player 6. Once goons are defeated the voice should tell us to head to the next
>    objective, the boss.

## The wreck is a Geometry Collection now

`City_CafeCrashCar` is hidden for good and `B1_Cafe_CrashCar_GC` stands in its place -
`GC_CrashCar`, cut from `SM_CrashCar` through the same Dataflow template that produced
`GC_CrateStack`, `GC_CafeTable` and `GC_Barrier`. All seven of the kit's material slots
came across in order.

Two things had to be learned the hard way.

**A GeometryCollectionActor spawns Dynamic, and a car-sized one falls out of the
world.** The cafe tables use Dynamic and are fine, so the setting looked safe. Measured
in PIE, this wreck's bounds reached **z -19405 within four seconds of BeginPlay** - it
was gone before the player could look at it. The component is **Kinematic** now, which
is how a destructible building is set up: it holds its place, ignores gravity, and
damage still releases its clusters.

**But a kinematic collection cannot be broken.** The first blast ran
`ApplyExternalStrain` and `AddRadialImpulse` and the wreck's bounds came back
**identical to the intact mesh** - no error, nothing in the log, just a car that did
not move. `CineExplFire` now switches the component to Dynamic, calls `RemoveAllAnchors`
and `CrumbleActiveClusters`, and then applies the strain and the impulse.

**And Chaos debris does not collide with the city kit's floors.** The kit is set to
collision-trace *complex-as-simple*, and geometry-collection particles do not collide
with triangle-mesh collision: the first successful break fell straight through the cafe
to **z -44289**. `B1_Cafe_DebrisFloor` - a hidden 1600 x 1200 box collider with its top
face at z = 0 - is what stops it. Most of the wreck now rests on the cafe floor where it
broke. A few pieces still escape past its edge and keep falling; that is cosmetic and
off camera by the time it happens.

The impulse went from 900 to **350 cm/s**: at 900 the debris crossed 30 m of room and
went out through the walls.

## The fireball is the explosion sheet nobody had used

`T_FX_Explosion_6x6` has been in `Content/Game/FX/Textures` since PR #53 and had never
been attached to anything. `M_FXExplosion` is an unlit **additive** material that reads
one cell of that 6 x 6 sheet from a `Frame` scalar: `row = floor(Frame / 6)`,
`col = Frame - row * 6`, UV = `TexCoord / 6 + (col, row) / 6`. Additive because the sheet
is drawn on black, so no alpha channel is needed.

**Frame has to be floored inside the material.** A fractional `Frame` lands between two
cells of the sheet and draws half of each. The first build did the clamp in the
Blueprint and passed a float straight through.

`B1_Cafe_Explosion` is a camera-facing card the director grows from 600 to 1100 cm while
walking `Frame` 0 to 35 over 1.6 s, then hides.

**`MakeRotFromZ` is the wrong way to billboard a card.** It points the plane's normal at
the lens and leaves the roll about the view axis free - PIE measured the card sitting at
**roll -83 degrees**, the fireball drawn on its side. Taking the camera's own rotation
and pitching it 90 degrees pins the roll at zero.

## The explosion and the pan are one director-driven cinematic

Not a Level Sequence. The rescue that precedes it is already director-driven, the camera
move is four poses and three lerps, and a sequence would have added a second asset to
keep in step with the actors it photographs.

`CineExplBegin` fires the moment the coworker is clear, ends Freeze Frame if it is still
running (so the explosion is always seen at normal speed), takes the camera, and breaks
the car. `CineExplCamStep` holds on the wreck for 1.8 s, swings off it, and settles
looking straight out of the cafe door - which is where the player is being sent next. At
2.6 s the voice says *"That was meant for you. There are more of them out on the street -
go and put them down."* At 5.2 s the bars go out and control comes back.

**The rescue used to run on for another 1.8 s after the blast with the camera on
nothing.** It now hands straight over, and `RescueT` freezes at 2.98.

**A soft-lock found by measurement.** With the old `RescueEndAt` tail gone, a rescue
started *after* the explosion had nothing left to end it: PIE sat with the player's input
locked and `RescueT` climbing past 140 s. `CineRescueStep` refuses to run once `ExplDone`
is set and hands control straight back.

## The objective chain reaches the boss

`ObjectiveState` 3 (out to the street) now advances to **4** (the goons) when the player
passes x = 1200, and to **5** (the boss) when the last goon on the beat-2 stretch is gone
- with the voice saying *"That is the welcome party dealt with. The one with the cleaver
is still waiting - keep going east."* The beacon walks from the cafe door to
Spawner_Street at (4600, 0, 0) to Boss_Freeze at (8120, 0, 0), then switches off.

**The goon count has to be fenced.** `Spawner_Beat4` stands at x = 12900 and fills its
group at BeginPlay, so an unfiltered `GetAllActorsOfClass(BP_Goon)` never reaches zero.
`GoonZoneMaxX` is 6500.

## A change that was only ever made in a live session

The beacon went back to being a **sphere**. Justin asked for a downward cone yesterday and
that change was made on the placed actor and never written into
`tools/b1_opening_wire.py`, so the next run of that script put the sphere straight back -
caught in a PIE capture. The cone lives in the script now, roll 180, scale 0.45/0.45/0.75.

## What is filed rather than built

**#120** - the wall patch is a grey cube that pops. The hole and the rubble are modelled
into `SM_CafeShell`, so there is no intact state to show; a real wall panel plus a
`GC_CafeWallPanel` would let the car break through it instead.

**#121** - the fire is still an orange cone. The flipbook material recipe exists
(`tools/unreal_make_fire_flipbook_mat.py`) but the atlas it reads was baked in the
practice repo and is not in this project, and there is no looping flame sheet here.

## What nobody has watched

Every number above is a script reading live actors in PIE, and four captures were looked
at: the rescue with its letterbox and caption, the broken wreck lying in the cafe, the
end of the pan with the goon line on screen, and the fireball card held open on frame 8.
Nobody has played the beat with a controller in their hands.

Two things are known-imperfect. A few debris pieces escape the debris floor and fall
forever. And the fireball comes out of `MI_AnimeLook_JumpCut` with a white core and a
lavender fringe - `Glow` is down from 1.6 to 1.1 to reduce it, but the posteriser is what
makes the fringe and that is the look working as designed.
