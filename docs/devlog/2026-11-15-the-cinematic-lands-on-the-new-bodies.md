# The cinematic lands on the new bodies

*Sun 15 Nov 2026, 04:45 UTC — GameStation*

Two lanes finished within an hour of each other and collided on one file. M_Station landed the remade
character bodies ([#122](https://github.com/Waffle-Widgets/jump-cut/pull/122),
[#123](https://github.com/Waffle-Widgets/jump-cut/pull/123),
[#124](https://github.com/Waffle-Widgets/jump-cut/pull/124)); Justin had beat 1's opening cinematic in
flight on `Justin/beat1-opening-cinematic`. [#116](https://github.com/Waffle-Widgets/jump-cut/pull/116)
went from MERGEABLE to CONFLICTING the moment #124 landed, and the whole conflict is one binary asset:
`JumpCut/Content/Game/Blueprints/BP_Coworker.uasset`. Everything else — 93 files, including `CLAUDE.md` —
auto-merged.

A `.uasset` has no textual resolution. One side's work has to be redone by hand, so the only question
worth answering is **which side is cheaper to redo**, and the answer was sitting in the blob sizes.

| side | bytes | what it is |
|---|---|---|
| Justin's branch | **961,298** | the whole cinematic graph |
| `main` (M_Station) | **480,840** | the pre-cinematic Blueprint plus one changed pointer |

Justin's side carries `CoworkerLightFire`, `CoworkerFireStep`, `CoworkerTryRescue`, `CoworkerBlastNow`,
`CoworkerHideThing`, the blast ring, the fuse and the follow behaviour. M_Station's side is, per the
commit message on `65ae320`, exactly one property: `BP_Coworker.CoworkerBody` now points at
`SK_CafeCoworkerV2`. So **keep Justin's asset and re-apply M_Station's one property on top** — the
opposite of the resolution proposed before the sizes were read.

The re-application did not need to be done by hand either. `tools/unreal_coworker_body_v2.py swap` is
M_Station's own tool for exactly this write, and it verifies more than a hand edit would: it writes
**every** SCS handle (the subsystem lists each node twice, and setting only the first leaves the other
holding V1 while the read-back still says V2), then refuses to save unless `anim_class`,
`override_materials` and all three relative transform components are unchanged.

```
found 2 handle(s) for CoworkerBody
BEFORE  mesh /Game/Game/Imported/CafeCoworker/SK/SK_CafeCoworker
AFTER   mesh /Game/Game/Imported/CafeCoworkerV2/SK_CafeCoworkerV2
SAVED /Game/Game/Blueprints/BP_Coworker ok=True
```

The asset came out at **961,301** bytes — three more than Justin's, which is what one longer soft object
path costs. The graph is intact: the CDO still exposes `blastRing`, `useFireHazard`,
`bulletTimeOnExplosion` and `rescueRequiresFreeze`, and all eleven of Justin's `B1_*` actors are in the
level (`B1_Cine_Director`, `B1_Cafe_Fire`, `B1_Cafe_BlastRing`, `B1_Cafe_CrashCar_GC`, `B1_Cine_Seq` …).

## The editor viewport says she is a heap on the floor, and it is wrong

After the merge the coworker renders in the level viewport as a crumpled shape at floor level. A tight
capture from 120 cm away at torso height shows bare wall where she should be standing. That is alarming
and it is **not** a defect.

`BP_Coworker.CoworkerBody` has `bUpdateAnimationInEditor = false` on Justin's version, so the editor does
not evaluate her single-node `SK_CafeCoworkerArmature_Idle` clip and the viewport draws something that is
not her posed body. Nothing else differs: the instance reads the V2 mesh, `AnimationSingleNode`, the Idle
clip, `bVisible` true, `bHiddenInGame` false, relative transform zero and scale one.

**In PIE she is fine.** Press R at the title, and the peaceful cafe opens with the player in
`SK_CafeWalkerV2` — khaki shirt, green apron — and the coworker standing behind the counter in
`SK_CafeCoworkerV2`, white shirt, green apron, dark hair. That is the only view that settles it, and it is
the general rule: *do not judge a skeletal mesh from the level viewport when the component does not
update animation in editor.*

## Also worth knowing

- Justin's level dressing is authored in the **post-crash** state: the wrecked car, `B1_Cafe_Fire`,
  `B1_Cine_WallPatch` and `B1_Cafe_DebrisFloor` all sit in the cafe in the editor, and the director hides
  them until the beat runs. The editor view of `Lvl_JumpCut` no longer resembles the opening shot.
- `0 of 482` assets under `/Game/Game` are dirty after the swap, but the status bar still reads
  `1 Unsaved`. Whatever it is, it is not a `/Game/Game` asset and it did not reach `git status`.
- The merge brings in the hazard change from
  [#18](https://github.com/Waffle-Widgets/jump-cut/issues/18): beat 1's threat is no longer one piece of
  shrapnel but a car fire with a 700 cm blast ring and a 9-second fuse that only burns while time runs.
  That revises the Freeze Frame tutorial as previously specified.

## Not done

Nobody has played the beat end to end on this merge. The PIE run above was the title screen and the first
seconds of the peaceful cafe — enough to prove both bodies render and stand, not enough to prove the
rescue, the fuse or the explosion still behave now that the coworker is a different mesh on the same rig.
