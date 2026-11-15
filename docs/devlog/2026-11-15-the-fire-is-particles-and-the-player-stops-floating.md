# The fire is particles, and the player stops floating

**When:** Sat 14 Nov 2026, evening Pacific (Sun 15 Nov UTC)
**Who:** Justin's Mac mini (builder)
**Branch / PR:** `Justin/beat1-opening-cinematic` -> PR #116

## What was asked for

Playtest feedback on the beat 1 opening, four items, in the Team Owner's words:

> 1. Player levitates at the begining of the cinematric. Should be grounded. 2. We opened an issue
> for the fire assets, we should be able to use the Niagra extention for fire. 3. We also have the
> double car again because of using the new asset that explodes. And it's missing it's textures.
> 4. We need some kind of effect to give life to the fact that we've received a new power up when we
> walk up to that first objective.

## 1. The levitation, and why it was never about the cinematic

Measured first, in PIE, sampling the player every 0.05 s from the frame `JumpCutStartPlay` runs
(`tools/b1y_float.py`). The capsule was **never** off the floor: `actor_z` held 94.2 and the gap
under the capsule held 2.2 cm for the whole six seconds. What moved was the **mesh** - bone 0 rose
to **90.6 cm** at t=0.21, held, and blended back to 0 by t=1.03.

90.6 is not an arbitrary number: it is this rig's **reference-pose root height** (CafeWalker 90.58).

The trigger is the project's own unlock path. `PlayerRefreshMoveLock` releases a lock with
`SetMovementMode(MOVE_Falling)`, and at the start of the game that fires once - so the player enters
the falling state on the first tick. Forcing `MOVE_Falling` by hand at t=2.0 reproduced it exactly,
and a real `jump()` at t=4.0 reproduced it a third time (`tools/b1y_fall.py`). One defect, three
triggers: the opening, every jump, and every unlock.

**The cause is two properties on three clips.** An `AnimSequence` with `force_root_lock = True` and
`root_motion_root_lock = REF_POSE` has its root pinned to the skeleton's reference pose - and on a
Meshy Smart Rig that pose puts the root at pelvis height. `7ef73e1` fixed the locomotion clips by
moving them to `ANIM_FIRST_FRAME` and **missed the jump / fall / land clips**, which is why he only
floated while airborne.

Four dead ends on the way, all of which looked right:
- the clips' own root tracks read **0.0** at every sample, so the clips looked innocent;
- they all carry a real `bone_000` track, so "no track, falls back to ref pose" was out;
- none of them is marked additive;
- the Jump state in `ABP_Unarmed_CWM` is correctly wired to `MM_Jump_CWM`.

Every one of those is true *and* irrelevant - the root lock is applied after the clip is sampled.

Fixed on six clips (`tools/b1y_rootlock.py`): `MM_Jump/Fall_Loop/Land` for the player (`_CWM`) and
the goons (`_SGN`). Deliberately **not** Epic's own mannequin clips, which share the combination and
are correct - the mannequin's reference pose has its root on the floor. Of 85 clips matching the
pattern, 60 are Epic's and 19 are the unused legacy `_CW` set; the 6 in use were confirmed by
reading each anim blueprint's asset references.

Re-ran the same test afterwards: **max root 0.0 cm** across the whole run - at startup, on forced
falling, and on a real jump, where the capsule now rises to 115 and comes back with the mesh on it.

This should also close #71 (the post-landing A-pose) and the jump half of #69.

## 3. Two cars, and a car with no textures

**Two cars** was a straight regression and the project's own trap, for the second time.
`CineImpactTime` - the moment the director reveals the real wreck - was back at **4.70 s**, where
the cinematic car is still in the air at x=-900. It was set to 6.20 live on Nov 14 and
`tools/b1_opening_wire.py`'s `DEFAULTS` still said 4.70, so the next run of that script put it
straight back. Fixed on the CDO, on the placed actor, **and in the script's defaults** with a
comment saying why, which is the only part that stops it happening a third time.

**No textures** was more interesting. `GC_CrashCar` draws `MS_CityAccent`, `MS_CityTrim`,
`MS_CityGlass`, `MS_CityMetal`, `MS_CitySignA`, `MS_CityWall`, `MS_CityCloth` - all seven of which
are `MaterialInstanceConstant`s of **`FBXLegacyPhongSurfaceMaterial` with DiffuseColor 0.8**: the
flat grey placeholders Unreal makes at import. The real look materials are `M_City*` under
`Materials/City/`, and every placed `City_*` **static** actor overrides to them per slot. Measured:
**0** static actors draw an `MS_` directly. Nothing ever told the geometry collections.

So the fix is on the collection **asset**, slot for slot, `MS_<Name>` -> `M_<Name>`. That also
fixes the cafe tables, the barriers and the crate stacks, which shatter in beats 2-3 and were all
grey the same way - **13 geometry-collection actors in total**, read back off the live components.

## 2. The fire is Niagara now

`NS_CarFire`: two CPU sprite emitters, Flames and Embers, built from the Niagara plugin's Fountain
emitter template through the MCP's Niagara toolset. It rides on the **existing** `B1_Cafe_Fire`
actor as a NiagaraComponent rather than as a new actor, so `BP_Coworker` lights it at exactly the
right moment with **no Blueprint change at all**. Two details make that safe: the component is set
absolute location/rotation/scale, so the coworker's per-tick `(2.9, 2.9, 2.1 +/- wobble)` scaling of
the cone cannot touch the particles; and the cone's own mesh component is set invisible, which
`SetActorHiddenInGame(false)` does not undo.

Two rounds of looking at it, which is the whole point of the `niagara-fx` skill:
- **Round 1 was dark grey coins.** A Smoke emitter on the masked flame material gave hard-edged
  opaque discs stacked over the car. Confirmed they were mine by switching the system off and
  re-capturing from the same camera. Smoke removed.
- **Round 2 was orange coins.** Better colour, still discs - exactly the failure the skill
  predicts for round sprites. The silhouette is the problem, not the colour.
- **Round 3 works.** `M_FlameTuft` (`tools/unreal_make_flame_tuft_mat.py`) varies the mask radius
  with angle (five soft lobes), rotates the lobes per particle with `ParticleRandom`, runs the
  colour bands on `d/r` so they follow the lobes, and drops the near-black outer rim that was
  drawing the coin's edge. It reads as a ragged orange plume with embers coming off it.

It is **not** photo-real fire and it is not Niagara Fluids. The Fluids route (a Grid3D gas sim,
tuned through Slate and baked to a flipbook) is hours of work and volumetric at runtime; #121 stays
open for it. This is the cel-shaded version, which is what the rest of the game looks like.

## 4. The power-up has a pop

`NS_PowerPop`: a cyan burst (Shards) plus a slower rising column (Rise), spawned by **one new line**
in `DriverTryTouch` - `Niagara|SpawnSystemAtLocation` at the driver +55 cm, auto-destroy on. No new
variable, no new component, no new actor. Verified at pin level rather than from the printed DSL
(this project has been bitten by that), compiled with warnings-as-errors, and then measured in PIE:
before the touch there is one NiagaraComponent in the world, after it there are two, the new one
carrying `NS_PowerPop`, visible and active.

First take came out **white**, not cyan: `(0.15, 1.85, 2.00)` clips through the posterising look,
exactly the way `M_FireHot` did at emissive 3.0. `(0.08, 0.95, 1.15)` reads cyan. Shard speed also
came down from 620 to 400 cm/s - at 620 over a 0.75 s life the spray reached 4.6 m, which reads as
an explosion rather than a pickup.

## What nobody has played

Every result above is a script measuring live actors, plus six captures I looked at myself. Nobody
has played beat 1 end to end since these changes. In particular the *feel* of the fire and the pop,
and whether the burst is now the right size, are the Team Owner's call.
