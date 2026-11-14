# The player and the goons floated on the same reference pose

**Fri Nov 14, 2026, 00:0x Pacific — M Station.** The Team Owner, mid-playtest on GameStation: *"fix the issue
where people float whenever they do anything."* They do, it is the bug the mob boss had, and the note telling us
to fix it on everyone else had been sitting in `docs/CHARACTERS.md` for a day.

## What was actually happening

Ticket [#69](https://github.com/Waffle-Widgets/jump-cut/issues/69) led with the wrong suspect. Its title says
*"the capsule lifts on every attack"* and its leading theory was that the retarget root receives the mannequin's
pelvis world height, so root-motion **translation** is handed to the capsule. Both halves of that are wrong, and
measuring took five minutes:

- Extracted root-track Z on all 14 attack clips: **0.00 on every one.** No Z translation exists to hand anywhere.
- In PIE, `actor_z` stayed at **94.15 for all four seconds** of a punch. The capsule never moves.

What moves is the **skeleton**. Sampling every bone's world Z through a punch:

| phase | lowest bone | `bone0_z` | `actor_z` |
|---|---|---|---|
| idle | 4.15 | 4.15 | 94.15 |
| punch | → **94.73** | → **94.73** | 94.15 |
| punch ends | back to 4.15 | 4.15 | 94.15 |

The lift is **90.58 cm**, and that is not an arbitrary number: it is exactly where `Bone_000` sits in the
**reference pose** of `SK_CafeWalker_Skeleton`. Meshy's Smart Rig keeps its root at pelvis height in the reference
pose while the retargeted clips animate it on the floor, and a root-motion clip's default
`RootMotionRootLock = RefPose` pins the root to the reference pose while the clip plays. So the root jumps to
90.58 and carries the whole body with it. Per rig: CafeWalker **90.58**, StreetGoon **92.46**, CleaverBoss 87.26.

## Why it survived a day

`tools/unreal_boss_root_lock.py` already existed, already diagnosed this, already fixed the boss, and
`docs/CHARACTERS.md:1073` already said in bold *"Any other Meshy Smart Rig character (the street goon) needs the
same setting on its root-motion clips."* Two things stopped that happening:

1. **Its docstring was half true and read as all true.** It said *"The player's CafeWalker clips came through the
   same retarget... They read 0."* True of the `_CW` clips, which ride our own Blender skeleton whose root really
   is on the floor. False of the `_CWM` clips — the ones `ABP_Unarmed_CWM` actually plays — which measure **90.6**.
   One sentence conflating two clip sets left the player floating.
2. **Its folder list was hand-written.** Four folders, and `StreetGoon/Loco` (the goon's 16 locomotion clips) and
   `StreetGoon/MeshyLoco` were not among them, so no run of it could ever have found them. The scan is now the
   whole of `/Game/Game/Imported`, recursive. Never hand-list the folders again.

The tool's own detection was never broken: run today it reported 90.6 on the `_CWM` clips immediately.

## The fix

`root_motion_root_lock = RefPose -> AnimFirstFrame` on **44 clips**: 20 CafeWalker (16 locomotion + 4 attack),
16 StreetGoon locomotion, 4 goon attacks, 4 orphaned `_SGL` attacks. Max lift **90.6 -> 0.0** on all 44. The 16
`_CW` clips measured 0.0 and were correctly left alone — the `> 5.0` gate protects floor-rooted rigs.

**It shifted the pose and reshaped nothing.** Each clip's lowest-to-highest spread is identical before and after,
on all 44 of 44. That matters because several clips now show feet dipping below the floor plane — worst on an
actually-used clip is `MM_Attack_02_SG` at -9.9 cm and `MF_Unarmed_Jog_Bwd_CWM` at -10.1 cm. Those dips are
pre-existing; they were simply hidden under a 90 cm lift. The three deepest (-12 to -19 cm) are all `_SGL` clips,
which `get_referencers` reports as having **no referencers at all** — nothing in the game plays them.

Verified by A/B in PIE, the same way PR #46 proved the boss: `bone0_z` now holds **4.15 constant** through a
punch, and through walking at full speed 600 (`JumpCutStartPlay` first, or the title screen holds input *and*
movement and every test reads zero).

## The jump is a second, different bug — diagnosed, not fixed

#69 bundles a jump hang with the float. They are not the same defect and the jump is **not** fixed.

The capsule's arc is clean: `vel_z` 447 → 347 → 262 → 177 → 77 → -8 → -103 → -295 → -472, a constant ~980 cm/s²,
no hang anywhere. What hangs is the mesh, and the hang is **after** landing, not at the top:

| t | mode | `bone0_z` | bone spread |
|---|---|---|---|
| 2.90 | FALLING | 147.2 (= ref height) | 152.8 |
| 3.07-3.52 | WALKING (landed) | **94.73, held 0.45 s** | → 159.5 |
| 3.58-3.92 | WALKING | 84.8 → **4.15** | 161.1 |

The spread converges on **161.1** against the reference pose's **162.0**, with `bone0` at exactly the ref-pose
height. So during the fall and for ~0.45 s after landing the anim blueprint is outputting the **reference pose**,
then blending into idle over ~0.35 s. To a player: you land, your body stays up in an A-pose for half a second,
then sinks. That is what "stops dead in mid air for a moment before dropping" is.

It is not the clips: `MM_Jump_CWM`, `MM_Fall_Loop_CWM` and `MM_Land_CWM` all have root motion **off**, all sit on
the correct `SK_CafeWalker_Skeleton`, and all evaluate to a real pose with `Bone_000` at 0.0. It is the
`MainStates` state machine inside `ABP_Unarmed_CWM` — 183 nodes — not reaching those clips. Left for a dedicated
pass: that asset is Justin's most recent commit (`31aa693`, 6 hours before this work) and editing a state machine
blind during a live playtest is the wrong trade on a jam clock.

## Lessons

- **A note saying "someone else needs this too" is not a fix.** The boss write-up named the goon in bold and the
  goon floated for a day anyway. Either do it in the same pass or file a ticket; a sentence in a doc is neither.
- **Never hand-list asset folders in a sweep tool.** Scan the root recursively. Two folders missing from a list of
  four is invisible, and the tool reports complete success over the subset it was given.
- **"The capsule lifts" and "the mesh lifts" look identical in a screenshot and need opposite fixes.** Log
  `actor_z` beside the bone heights; one number separates them.
