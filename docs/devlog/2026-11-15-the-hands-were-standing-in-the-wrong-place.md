# The hands were standing in the wrong place

*Sun 15 Nov 2026, 00:55 UTC — M Station*

The player's hands read as paddles. The obvious reading was that the skin weights were broken, and
they were: 16 of his 40 finger bones carried no weight at all and 13 more carried between one and
six vertices. So the obvious fix was to rebuild the weights. That was written, measured, and it made
the model **worse**.

The weights were a symptom. A skinned mesh has to be modelled in its skeleton's rest pose, and V2
was not. `reskin_to_existing_rig.py` checks that the two bodies agree on height, feet-at-zero and
arm span before it transfers anything — and all three matched while the limbs did not. Meshy's own
rig for the same body, measured against the 69-bone rig we animate on, puts the **elbow 8.3 cm out,
the wrist 12.7 cm and the knee 8.2 cm**. V1's A-pose splays the legs and hangs the forearms down and
back. Meshy stood him up straight.

Which means the rig's twenty finger bones were sitting in **empty space** — 11 to 17 cm from the
nearest vertex of the hand they are supposed to drive. A proximity weight transfer had nothing
sensible to find. It dumped the fingers into the palm and produced an asset with the right vertex
count, the right skeleton, the right material and zero unweighted vertices.

And re-weighting genuinely cannot fix that. A bone 15 cm from the finger it drives does not curl the
finger, it swings it. The geometric re-weight took 33 articulating finger bones down to 29, because
concentrating weight onto a bone in the wrong place just makes the wrong motion more confident.

So the mesh had to move, not the weights. `Art/Blender/conform_rest_pose.py` poses Meshy's own rig
to match the target rig's rest pose joint by joint and bakes the result, before any weight is
transferred. Three details in it were each separately necessary:

- The root is seated by the **leg roots and the soles**, not the hip bone. Meshy's `Hips` sits 9.7 cm
  above its own leg roots where `Bone_001` sits 2.1 cm above its — they are not the same anatomical
  point, and matching them put the whole body **11.9 cm through the floor**.
- The hand's axis is wrist → **the middle of the fingertips**. Matching `Bone_020 → Bone_019` instead
  looks right and is not: that is a 5 cm wrist-to-palm stub pointing somewhere else, and using it
  rolled the hand down and cost the arm 9 cm of reach.
- Each hand gets a slide and a **roll search against the finger bones themselves**. Joint-direction
  matching leaves roll undetermined, and roll is exactly what decides whether the finger bones land
  along the fingers or across them. Meshy's rig has no fingers to align against, so the fingers are
  the objective function.

Afterwards the fingertip bone that had been 17.5 cm from the mesh is 0.8 cm from it.

| | finger bones that move | weak | dead | whole-hand swing |
|---|---|---|---|---|
| as shipped yesterday | 18 | 5 | **17** | 14.1 / 14.9 cm |
| now | **32** | 6 | 2 | 13.3 / 13.6 cm |
| V1, the best we had | 32 | 7 | 1 | 15.5 / 14.3 cm |

A light weight smooth over the hands only (factor 0.25, two passes) takes a shard off the curled
fist; at 0.5 it cost five articulating bones, which is why it is 0.25.

`Art/Blender/reweight_verify.py` is what produced that table: it poses each of the 40 finger bones on
its own and measures how far the mesh actually moves. Counting weights is what let "18 of 21 finger
bones carry weight" stand as a reassuring sentence about a hand where most of those bones moved
between one and six vertices.

## Two things that would have silently wasted the next person's evening

**The re-import was a no-op and reported success.** `unreal_import_char_v2.py` imports the FBX and
renames whatever came out to `SK_<Name>`. That is right the first time. Every time after, Interchange
names the new asset after the FBX (`SK_CafeWalkerV2_oldrig`), the rename is skipped because
`SK_CafeWalkerV2` already exists, and the script then validates — and reports a clean bill of health
on — the **old** asset, while the new geometry sits in a duplicate nobody references. Re-posing a
mesh changes neither vertex count, skeleton, bone count nor material slot, so every check passes
either way. The only thing that moves is the **bounds**. `tools/unreal_reimport_char_v2.py` re-imports
over the real asset and proves it landed by reading the bounds back against numbers measured in
Blender.

**The animation editor was previewing the wrong body.** `SK_CafeWalker_Skeleton`'s preview mesh was
still V1 — the skirt apron, forty working finger bones. Open any clip, montage or blend space and
that is what you pose against, while the game runs V2.

Forty of the seventy-two animation assets also hold a soft reference to the V1 body, which looks
exactly like a per-clip preview override when you read the `.uasset` name tables — and that is what
it was first called. Asked directly, every one of them reports `preview_pose_asset = None` and
exposes no preview-mesh property at all. The reference is **`RetargetSourceAsset`**: the mesh whose
proportions the clip was authored against. It is correct, and repointing it would have changed how
all 38 of those clips are interpreted. One asset needed changing, not forty-one.

## What is still wrong

Meshy's 365k high-poly already has the fingers **fused** — shallow grooves, no gaps, a stub thumb.
Adjacent fingers share vertices and will always drag on each other, and a full fist folds into a
wedge rather than closing. Two bones stay dead: `Bone_037` and `Bone_061`, the outermost segment of
one finger per hand, whose bones extend past the end of the mitten.

**Nobody has played it.** Every number here is Blender measuring the committed FBX or Unreal
reporting on the saved asset. No in-engine picture was taken.
