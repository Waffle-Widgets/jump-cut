# The arms were on the wrong sides

**Sat Nov 14, 2026, ~04:20 UTC (Fri Nov 13 evening Pacific) — Justin's Mac mini**

## What we asked for

> The main character and goons arms are mangled looking

## What it actually was

Not the hands, and not the models. **Every arm and leg on both Meshy characters was labelled with the
wrong side**, so the retargeter played the mannequin's *right* arm animation on the character's *left*
arm, and the other way round.

`tools/unreal_retarget_meshy.py` has to work out which limb is which on a rig whose bones are called
`Bone_000` to `Bone_082`. It did it by reading the sign of a chain tip's X against the hip's:

```python
faces_plus_y = (pos[toe][1] - pos[ankle][1]) > 0
right_sign = 1.0 if faces_plus_y else -1.0
side = 'Right' if (tip_x - hip_x) * right_sign > 0 else 'Left'
```

That is inverted. Unreal is left-handed (+X forward, +Y right, +Z up), so a rig facing **+Y** has its
right side at **−X**, not +X. Both Meshy characters face +Y, so every label came out backwards.

**Then the alignment pass made it much worse than a mirror.** With `ALIGN=arms` the script calls
`auto_align_bones(..., CHAIN_TO_CHAIN)`, which rotates each target chain's retarget pose to point the
way its *mapped source chain* points. Mapped to the opposite arm, it rotated each arm's rest pose onto
the other arm's. That is the difference between "he punches with the wrong hand" (which reads as odd)
and limbs folded across the body (which reads as mangled).

Measured on `MM_Attack_01` at t = 0.3 s, in each character's own body frame
(`tools/_arm_check.py`, `AnimPoseExtensions`, no PIE):

| | upper arm (right, fwd, up) | bend at the shoulder |
|---|---|---|
| mannequin, right arm (the source) | `[0.92, -0.34, 0.20]` | **1.1°** |
| street goon, right arm — before | `[-0.22, -0.96, 0.17]` | **141.6°** |
| cafe walker, right arm — before | `[0.27, 0.96, 0.13]` | **148.3°** |
| street goon, right arm — after | `[0.93, -0.34, 0.17]` | matches |
| cafe walker, right arm — after | `[0.93, -0.34, 0.13]` | matches |

Before the fix the two characters' right arms pointed in *opposite* directions (one forward, one back)
and neither matched the mannequin. After it, both agree with the source to within 0.07 on every axis.

## Why nothing caught it

This failure has no internal tell-tale. Every chain still got a unique name, so the script's existing
duplicate-name guard stayed quiet. All **19 of 19** chains still mapped. `auto_align_bones` still ran.
The batch still retargeted. The logs said `mapped 19 of 19` and `saved ok True` both before and after.
Reading the assets back cannot find it either, because the assets are exactly what the script intended
to build — the *intent* was wrong.

Swapping left for right is self-consistent. The only check that can catch it is an **external** one.

## The fix

`side()` now computes the character's right axis from its own geometry rather than guessing a sign:

```python
up    = chest - hip
fwd   = toe - ankle, flattened against up
right = up x fwd          # Unreal is left-handed
side  = 'Right' if dot(tip - hip, right) > 0 else 'Left'
```

And `check_side_rule()` runs that same rule on the **mannequin** at the start of every run, where the
answer is known from the `_l` / `_r` bone names, and refuses to retarget if it disagrees. It logs:

```
  side check hand_r Right 45.87
  side check hand_l Left -49.03
  side check thigh_r Right 9.88
  side check thigh_l Left -9.92
  side check foot_r Right 14.76
  side check foot_l Left -13.23
side rule verified against the mannequin bone names, 6 of 6
```

## What was rebuilt

Three folders, all with `ONLY=clips` so no anim blueprint was touched:

| folder | suffix | clips |
|---|---|---|
| `CafeWalker/MeshyAnims` | `_CWM` | 39 (fight + locomotion) |
| `StreetGoon/MeshyAnims` | `_SG` | 18 (fight) |
| `StreetGoon/Loco` | `_SGN` | 21 (locomotion) |

Checked afterwards with `tools/_montage_refs.py`, because a re-run of
`IKRetargetBatchOperation.duplicate_and_retarget` into a folder that already holds its own output has
silently discarded assets in this project twice: **23 montages, 1 segment each, 0 missing references,
2 blend spaces at 27 of 27 samples, 0 bad.** Folder counts came back 48 / 39 / 25 with no stray
`_1` rename copies.

## The other half, from the run before this one

The same session had already found that the Meshy rigs had **no finger chains at all**, so all ten of
the mannequin's finger chains were dropped and the hands held their reference pose in every clip — a
permanently splayed claw. `finger_chains()` names the five branches off each hand the way Epic's auto
definition names the mannequin's. Both halves are in these rebuilt clips: the chain count went from
9 to **19**.

## What we learned

- **Unreal is left-handed: right = up × forward.** Writing it as a sign test on one axis is where this
  went wrong, and the shortcut saved nothing.
- **A left/right swap is invisible to every internal check.** Name uniqueness, chain-mapping counts and
  asset read-back all pass. Verify a geometric rule against a rig whose answer you already know.
- **A symmetric animation hides it.** The goons' walk was signed off as working the day before, and it
  was: a walk cycle with the legs swapped is a walk cycle with a phase shift. It took an *asymmetric*
  clip — a punch — for anyone to see it, and what they saw was the arms.

## Still not checked by a person

Nobody has played this. Every number above is the editor evaluating a clip, not someone watching the
goons throw a punch. The thumbnails changed from both arms balled up in front of the chest to a
readable punch, which is a good sign and is not a playtest.
