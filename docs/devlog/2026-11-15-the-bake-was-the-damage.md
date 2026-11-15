# The bake was the damage

*Sun 15 Nov 2026, 03:10 UTC — M Station*

The Team Owner uploaded Meshy's own render of the player and said, in as many words, that *that* is
what the game should look like. Standing the two pictures side by side, the difference was not
subtle: a dark blotch smeared across the apron, a sawtooth hem, a mottled white-and-grey collar,
speckled waist ties, and a hand that read as one flat paddle.

Two separate faults sat between those pictures, and only one of them was ever the rig's.

## The texture was damage we inflicted ourselves

Meshy's remesh step regenerates UVs and throws the texture away, so [#112](https://github.com/Waffle-Widgets/jump-cut/pull/112)
baked the 365k high-poly's colour onto the remeshed body's new UVs. That is the textbook move and it
was never necessary. The high-poly keeps its **own** UVs and its **own** clean texture, and a Blender
`DECIMATE COLLAPSE` to the shipped triangle count — 365,038 → 55,679 — keeps both. No bake, no
resampling, no stair-stepped island edges, and 0 Meshy credits.

Every one of those defects is gone, because they were bake artefacts rather than anything in the art.
`T_CafeWalkerV2_BaseColor.png` fell from **3.3 MB to 494 KB** on the way, which turns out to be a
decent smell test: clean art compresses, baked noise does not.

## The obvious fix for the silhouette was wrong, and it looked right

[#117](https://github.com/Waffle-Widgets/jump-cut/pull/117) had fixed the hands by deforming the mesh
into the rig's rest pose, which cost silhouette: the apron gained 7.7 cm of depth and the shoulders
slumped. The obvious answer was to stop deforming the mesh and move the **bones** into it instead.
That was written. It measured better than the conform on every number — bone-to-mesh fit 1.71 cm
against 2.39, better even than the V1 body's 3.07 — and it rendered beautifully.

It is also broken, and the way it is broken is the point. Unreal's `UAnimSequence` tracks are
**absolute local transforms**. Playback puts each bone where the clip says regardless of what the mesh
was bound in, and the mesh is skinned `(clip pose) * (bind)^-1`. So a bind pose that is not the rest
pose the 48 clips were keyed against is extra twist on *every frame*. Measured, the rig-fitted body's
rest pose was **75.7° from the clip rig's on average, 171° at worst, with 47 of 69 bones past 20°**.
It stands perfectly still and shreds the head and one arm the moment `Idle` plays.

A character that is flawless in its bind pose and destroyed in motion is exactly the failure this
project keeps shipping, so it now has a guard: `Art/Blender/rest_delta.py` prints the rest rotation of
a candidate body against the rig its clips were authored on, and **it has to read 0.0°**.

## So the clean geometry was carried into the pose the rig needs

The body in the game and Meshy's low-poly are the **same 27,976 vertices in the same order**, because
the conform only moved them. That makes `conformed[i] - natural[i]` an exact per-vertex displacement
field, already measured, already shipped. Sampling it at the nearest point on the low-poly surface
puts the decimated high-poly into the rig's rest pose with no *new* distortion: applied mean 7.34 cm
and max 23.83 cm, against the conform's own 7.15 and 23.84. Weights come across from the conformed
body by nearest surface, mean source distance **0.25 cm**, all 68 groups carrying weight.
`rest_delta.py` reads 0.0°.

## What it fixes, and what it deliberately does not

Gone: the apron blotch, the sawtooth hem, the mottled collar, the fused paddle hand. Unchanged on
purpose: the wide stance and the apron's depth, because both come from the rig's own splayed rest pose
— that is [#73](https://github.com/Waffle-Widgets/jump-cut/issues/73), and any mesh that skins
correctly on this rig has to stand that way. Still open: the blown-white face,
[#72](https://github.com/Waffle-Widgets/jump-cut/issues/72).

![rebuilt](../media/2026-11-15-cafewalker-v2-rebuilt-no-bake.jpg)

`Idle` and `Walk` were taken off the committed `SK_CafeWalker.fbx` and played on both bodies with the
pose copied bone-for-bone the way Unreal does it, old beside new in the same frame. One trap worth
keeping out of the next person's evening: `pose_bone.matrix` resolves against the parent's *current*
evaluated matrix, so the depsgraph has to be refreshed **between bones**. Leave it to the end of the
loop and the arms and hair tear into streaks that look precisely like a broken bind and are nothing of
the kind — it reported both bodies as broken before it was caught.

**Nobody has played it.** Every picture is Blender rendering the committed files.
