# The walk was wide because only the arms were ever corrected

*Sat 14 Nov 2026, 10:14 PM Pacific — GameStation*

The report was that the main character "still looks like the old model" after the V2 body landed. He
does not: `BP_Player` reads `SK_CafeWalkerV2`, the material and texture chain resolves, and the editor
had loaded assets newer than the mesh. What reads as "the old model" is the **stance**, because V1 and
V2 bind to the same skeleton, and that skeleton's reference pose is Meshy's auto-rig stance rather than
a neutral one. That is [#73](https://github.com/Waffle-Widgets/jump-cut/issues/73).

## First, numbers, because the ticket was written off thumbnails

#73 said so itself: the angles in it were read off asset thumbnails, and it asked for
`tools/_arm_check.py` to be pointed at the walk and given legs. `_arm_check.py` measures the arms only,
on one attack frame, so instead there is now `tools/stance_check.py`. It evaluates the mannequin's
source clip and the retargeted clip at the same twelve times across the cycle, in each rig's **own**
body frame, and reports scale-free numbers — angles, or lengths divided by that rig's leg length — so a
1.8 m mannequin and a Meshy body of any height compare directly. It measures each rig's **reference
pose** as well, which is what actually tests the ticket's claimed cause.

Bone roles come from topology, not names, because a Meshy Smart Rig calls every bone `Bone_NNN`. Two
things had to be right for that to work and were not at first:

- Limb paths follow the child with the **deepest subtree** at each step. `straight()` — which
  `_arm_check.py` uses — stops at the first branch, and the mannequin's thigh and upperarm both carry
  twist bones, so it reports the thigh itself as the ankle.
- `get_all_socket_names()` returns **sockets as well as bones**, and a socket's parent can come back
  empty. `weapon_r_muzzle` was picked as the skeleton root and the hierarchy vanished. The bone list
  now comes from a clip's own `AnimPose`, which carries bones only.

## What the measurement said, including the parts that contradict the ticket

On `MF_Unarmed_Walk_Fwd`, player against mannequin:

| | mannequin | player | delta |
|---|---|---|---|
| stance width | 0.195 | **0.751** | **+0.556** |
| stagger | 0.703 | 0.671 | −0.032 |
| spine lean | 6.9° | 3.8° | −3.1° |
| head drop | 23.9° | 25.9° | +2.1° |
| upper-arm out | 26.3° | 27.2° | +0.9° |
| arm lateral | 0.273 | 0.273 | +0.000 |
| elbow bend | 30.8° | 19.4° | −11.4° |

One defect, not five. The ticket's "stooped" is wrong — the player is **more** upright than the
mannequin. "Head dropped" is 2° and the mannequin's own walk drops its head the same amount. "Arms
splayed out and away from the body" is wrong: the arms match the mannequin to 0.9° and the lateral
component is identical to three decimals. "Staggered, left foot forward" is wrong too — in the
reference pose both ankles sit at the same fore/aft offset, 0.071, exactly level.

What is right is **wide**, and badly: the feet stand 3.85× as far apart as the mannequin's. The
reference pose is 0.880 against the mannequin's 0.330, a +0.550 offset that arrives in the clip as
+0.556. A retarget applies rotations relative to each rig's reference pose, so that offset is added to
every frame of every clip. The ticket's mechanism was right even though most of its symptom list was not.

## The cause is one argument, and it has been there since the set was built

`unreal_retarget_meshy.py` ran with `ALIGN=arms`, which calls `auto_align_bones(CHAIN_TO_CHAIN)` on the
arm and finger bones **and nothing else**. The legs were never aligned, so they kept the raw Meshy rest
pose. That is exactly why the arms measure within 0.9° of the mannequin while the legs are 0.556 out —
the call did its job on everything it was given.

Re-running the old settings into a scratch folder reproduced the shipped clip on every metric to three
decimals, which is what made the rest of this a controlled comparison rather than a guess.

## Four alignment methods, and why the obvious one is wrong

The obvious fix is to add the leg bones to the same `CHAIN_TO_CHAIN` call. It fixes the width and it is
still the wrong answer. One clip per variant, into its own scratch folder:

| legs aligned by | stance width | stagger | toe-out | toe asym | knee bend |
|---|---|---|---|---|---|
| *nothing (shipped)* | +0.556 | −0.032 | +16.2° | +20.5° | −23.6° |
| CHAIN_TO_CHAIN | +0.034 | +0.005 | **+35.8°** | −1.3° | −7.5° |
| **MESH_TO_MESH** | **−0.007** | +0.027 | **+16.7°** | −11.6° | −26.6° |
| GLOBAL_ROTATION_AXES | +0.047 | **+1.015** | −82.9° | +162.8° | −5.4° |
| LOCAL_ROTATION_AXES | −0.096 | **−0.589** | +20.0° | +53.8° | +3.7° |

Chain-to-chain aligns a bone to its **chain's** overall direction, and a leg chain points down the leg,
so the whole leg is rotated and the foot yaws out with it: toe-out goes from 21.3° to 40.9° against the
mannequin's 5.1°. Dropping the foot and toe from the align set changes **nothing** — identical to three
decimals — because the foot is a child of the thigh and inherits its rotation. The two axis methods are
not close: one doubles the stride, the other collapses it to a sixth.

`MESH_TO_MESH` is what shipped. It lands stance width within 0.007 of the mannequin, leaves toe-out
where it already was, improves left/right symmetry, and is one documented engine call that generalises
to any rig. A hybrid (mesh on the leg, chain re-applied to the knee and shin) recovers 7° of knee bend
for 4.9° more toe-out; it was rejected because it depends on a `ch[1:3]` slice that assumes a leg bone
count, which the goon's rig need not share.

## The toe-angle metric had to be fixed before any of that could be read

The first pass had the mannequin's own walk at 22.3° of toe-out, which is absurd. Mid-stride the
swinging foot is plantar-flexed, its shadow on the ground plane is almost nothing, and the **direction**
of that shadow is numerical noise — one sample read 126.9°. `foot_flat` is now the fraction of the foot
that survives the projection, and toe angles are averaged only over samples above 0.6. The mannequin's
real toe-out is **5.1°**. Without that fix the comparison above would have picked the wrong method.

## The trap that cost the most time was not animation at all

Overwriting the 40 clips in place is the right move — the paths stay, so the anim blueprint, the blend
space, `BP_Player` and all five hand-authored `AM_CafeWalker_*` montages keep resolving with nothing
repointed. It stalled for six minutes on a modal nobody could see from the MCP side:

> This file is read-only on disk: … `BS_Idle_Walk_Run_CWM.uasset`. Delete it anyway?

LFS keeps `.uasset` files read-only, and the engine's normal overwrite is *create `_CWM1` → delete the
original → rename*. Every delete hit a read-only file and raised a dialog that blocks the game thread,
and with it every MCP call. Clearing the read-only flag on the destination folder first makes the whole
run finish in about two minutes with no dialog at all. The `_CWM1` names in `CLAUDE.md`'s warning are
the engine's **intermediate step**, not corruption in themselves — what makes them dangerous is a run
that is interrupted part way, which is precisely what a read-only file does.

Answering **No** to that dialog is correct while it is up: Yes deletes the original and leaves only the
`_CWM1` copy, which is the "a folder of 42 clips came back as 3" story. The two assets declined that way
were left stale and their strays were cleaned up before the real run.

## What this fixed, and what it did not

Idle is the pose on screen most of the time, and it is the clearest result: stance width **1.075 →
0.512** against the mannequin's 0.471. The before/after was also rendered side by side in the level,
same clip frame, and the old pose is an unmistakable wide straddle where the new one stands normally.
Which figure was which was settled with `WorldPosToScreenCoords` rather than by reasoning about axes,
because this project has already lost a day to a left/right inversion.

Still out, and deliberately not chased here:

- **Toe-out is unchanged at ~21.8° against the mannequin's 5.1°.** The reference poses differ by only
  4°, so roughly 12° is added by the retarget itself. Fixing it needs an explicit rotation offset on
  the foot in the retarget pose, not an alignment method.
- **Elbow bend is 11.4° short** and **knee bend 26.6° short** — both clips are straighter-limbed than
  the mannequin's. The knee figure is the least trustworthy number here, because it depends on which
  `Bone_NNN` is treated as the knee on a 5-bone leg.
- `SK_StreetGoon` and the boss came through the same pipeline with `ALIGN=arms` and were **not**
  touched. They almost certainly stand the same way.

**Nobody has played it.** This is geometry and two editor renders. The 40 clips carry the attacks, the
hit reacts and the deaths as well as locomotion, and none of those has been seen in motion.
