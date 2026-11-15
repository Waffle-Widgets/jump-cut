# The coworker gets her own rig back

*Sun 15 Nov 2026, 04:05 UTC — M Station*

The coworker in the game was the V1 body — tan skin, a toothy western-cartoon grin, a full wrap skirt
apron. She had been rejected for exactly those reasons back on Friday, a V2 was generated and committed
the same day, and nothing ever pointed at it. [#101](https://github.com/Waffle-Widgets/jump-cut/issues/101)
said why: her reskin onto the rig her clips are keyed to failed at **13.5 cm per hand**, and posing the
hand bone moved 1,384 vertices on the shipped body against **30** on the reskinned one. That reads as a
dead end.

It is the same dead end the player was in, and the same thing gets out of it.

## The reskin was failing for a reason nobody had named

`reskin_to_existing_rig.py` checks that two bodies agree on height, feet-at-zero and arm span. All three
can match while the elbows, wrists and knees are a hand's width apart — which is exactly what Meshy does,
because it stands a character up straight where our A-pose splays the legs and hangs the forearms down and
back. So the rig's finger bones end up in empty space and a proximity transfer has nothing sensible to find.

`conform_rest_pose.py` fixes it by posing Meshy's own 28-bone rig onto the target rig's rest **first**,
baking, and transferring afterwards. Her V1 rig turns out to use the identical `Bone_NNN` naming as the
player's, so the bone map applied unchanged. After the conform every mapped bone sits **0.08–1.5 cm**
inside her mesh, and `rest_delta.py` reads **0.0°** against the rig `SK_CafeCoworkerArmature_Idle` and
`_Walk` are keyed to. Both clips play with nothing retargeted.

## Her texture was the same self-inflicted damage, and it is gone the same way

Meshy's remesh discards the texture, so her colour map had been **baked** high-poly to low-poly like the
player's. The damage was the same kind and just as visible: a torn fringe through the hair over her right
eye, a shredded collar, ragged sleeve hems, skin-coloured streaks down the trouser sides, navy bleeding
onto the arms and thumbs. Decimating Meshy's 383,852-triangle high-poly to 56,493 instead — it keeps its
own UVs and its own texture — removes every one of them, because every one of them was a bake artefact.

One thing came out differently from the player's build and is worth keeping. On *his* mesh, welding the
high-poly before decimating was the right move. On *hers* it is wrong: her atlas is **538 ragged islands
packed edge to edge**, and collapsing a welded mesh drags UVs across the seams — 5,391 triangles ended up
straddling one, which showed up as dark scratches on both sleeve hems, flecks on the apron and a teal
streak on the trouser seat. Her script decimates **unwelded**, which keeps every island outline, then
stitches the seams shut afterwards and takes normals from the welded copy.

## Two post-passes, each separately necessary

**Her hands are a fused mitten.** Meshy drew no fingers, and the rig has 41 finger bones keyed to a body
that does. Keying five finger chains on one lump of geometry fans it into white shards from the first frame
of `Idle`. So the finger bones are folded into the two palm bones. She cannot articulate fingers she was
not given, and a hand that moves rigidly at the wrist reads correctly at the distance she is ever seen
from. This would be the wrong thing to do to the player, whose fingers separate.

**And one vertex was still shooting a needle out of her hand.** `reskin_to_existing_rig.py` prunes weights
further than 25 cm from their bone, which is generous enough to leave a hand vertex following a *hip* bone
— and a hip bone swinging 25 cm away drags that vertex into a spike several centimetres long. It never
shows in a weight count. It is obvious in a side view. Pruning at 12 cm removes it.

## What is still wrong, and it is Meshy's

The apron straps still **cross in an X with a diamond keeper** on her back, which the character lock
forbids. It is raised geometry as well as texture — the straps stand 3–6 mm proud of the shirt, the keeper
12–14 mm, over about 141 cm² — so no bake or decimate change touches it. Removing it means shrinkwrapping
those vertices onto the shirt and repainting in 3D (the X's texels are scattered over 97 of the atlas's
4,096 cells, so a 2D fill cannot do it), then re-running the rebuild.

![old vs new](../media/2026-11-15-cafecoworker-v1-vs-v2-on-her-rig.jpg)

One last thing, because it cost ten minutes and will cost somebody else more. Straight after the import,
the placed actor rendered as a **crumpled teal lump** in the level viewport — while the asset thumbnail
of the very same mesh was perfect. That is stale skinning on the editor-world actor, the same thing
[#109](https://github.com/Waffle-Widgets/jump-cut/issues/109) chased for a day, and it cleared on the next
editor launch. Restart before filing it as a defect.

**Nobody has played it.**
