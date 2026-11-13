# 2026-11-12 — The fight gets its animation (GameStation)

- **What we asked for:**

  > "Let's stick to using the same tools we have been using unless we say otherwise. Install what is needed here
  > to do work or push the work over to M_Station if needed, or split the work between workstations. I play tested
  > the game and none of enemies or the player have attack animations and the boss doesn't even have walk animations."

- **What happened:**

  The playtest was right, and the cause was simpler and worse than expected. **Nothing in the project ever played
  an animation for a fight.** `PlayerPunch` and `EnemyPunchPlayer` did damage, knockback and stun and stopped
  there; `git grep -i montage` over `docs/` and `tools/` returned **nothing**, and the only `AnimMontage` asset in
  the whole project was Epic's `MM_Pistol_Fire_Montage`. Epic's `MM_Attack_01/02/03`, `MM_HitReact_*` and
  `MM_Death_*` were sitting in `Content/Characters/Mannequins/Anims/` the entire time, unreferenced.

  The boss was a second, separate failure. `BP_BossFreeze`'s mesh was in **`AnimationSingleNode`** mode with
  `AnimClass = None`, playing `BS_Idle_Walk_Run_CB` as a single node. A blend space in single-node mode has
  nothing driving its axis, so he stood at the idle corner of it forever — and single-node mode **cannot play a
  montage at all**, so no amount of Blueprint work would have given him an attack.

  What we built:

  - Nine `AnimMontage` assets — `AM_Human_Punch_01/02/03`, `AM_Human_HitReact`, `AM_Human_Death` on the mannequin
    skeleton, and `AM_CleaverBoss_Punch/Cleave/HitReact/Death` on our own boss skeleton — made by a new script,
    `tools/unreal_fight_anims.py`. The boss's four are retargeted from the same mannequin motion capture through
    the `RTG_Mannequin_to_SK_CleaverBoss` retargeter we already had.
  - `ABP_CleaverBoss`, a small anim blueprint for the boss: `BS_Idle_Walk_Run_CB` → `Slot 'DefaultSlot'` →
    Output Pose, with the blend space's X driven by a `BossAnimSpeed` float the event graph sets from his pawn's
    velocity each frame. `BossDriveAnim` — which used to push the blend space by hand — is now empty.
  - Three `AnimMontage` variables on `BP_EnemyBase` (`EnemyAnimPunch`, `EnemyAnimHitReact`, `EnemyAnimDeath`) and
    four on `BP_Player`, so each class picks its own clips and the code path is identical for everyone.
  - `EnemyPunchPlayer` plays the punch. `EnemyTakeHit` plays the hit react while health is above zero and the
    death when it hits zero. `PlayerPunch` plays punch 1, 2 or finisher by combo step; `PlayerTakeHit` plays the
    hit react.
  - `EnemyDefeatLinger` 0.6 s → **1.2 s**, because the death animation is 1.1 s and the body was being removed
    two-thirds of the way through it. The two death montages have auto blend-out switched off so the last pose
    holds for the rest of the linger.

  Verified in Play-In-Editor by calling the real Blueprint functions on the live actors and reading back which
  montage was playing: `PlayerPunch` ×4 gave `AM_Human_Punch_01` → `02` → `03` → `01` with `ComboStep`
  1 → 2 → 0 → 1; a goon hit for 5 played `AM_Human_HitReact` and dropped to 35 health; a goon hit for 999 played
  `AM_Human_Death` with `EnemyIsDefeated true`; the boss's punch played `AM_CleaverBoss_Cleave`; and with the
  player stood 1,200 cm away the boss walked at **380 cm/s with `BossAnimSpeed` reading 380.0** — his move speed,
  straight into the blend space.

- **What we learned:**

  - **`ABP_Unarmed` already has a `Slot 'DefaultSlot'` node.** We nearly duplicated and rebuilt the whole anim
    blueprint before checking. `BlueprintTools.list_graphs` only lists sub-graphs, so the slot is invisible there;
    `find_nodes` on `:AnimGraph` is what shows it. Nothing had to change in Epic's anim blueprint at all.
  - **`ACharacter::PlayAnimMontage` is null-safe**, so a montage variable that is still `None` costs a branch and
    nothing else. That is what lets one function body serve the player, the goons and the boss.
  - **A new variable's default does not reach an existing child Blueprint.** `EnemyAnimPunch` was set on
    `BP_EnemyBase`'s class defaults and `BP_Goon` still read `None` after a recompile. Set the child's defaults too.
  - **A placed actor is worse.** The boss actor in `Lvl_JumpCut` kept `AnimationSingleNode` / `AnimClass None`
    after the class defaults changed, and lives in its own external-actor package, so `AssetTools.save_assets` on
    the `.umap` does not save it — `EditorLoadingAndSavingUtils.save_packages` on the actor's own package does.
  - **The DSL reader does not round-trip.** It prints `Math|Vector|vector-vector`, `(bind _x 1.0)` and
    `(Character|LaunchCharacter v true true)`; the writer rejects the first two and puts the third's first
    argument in the `self` pin. Use `-`, fold literals, and name the pins (`:LaunchVelocity`).
  - **`unreal.Rotator` takes `(roll, pitch, yaw)` positionally.** `Rotator(0, 180, 0)` stood the boss on his head
    in the first screenshot.

- **Media:** ![the player mid-punch and the mob boss with his cleaver, both driven by montages](../media/FIGHT-ANIMATION.png)

  Both figures are held at 1/8 play rate so the pose is readable. The player is still Epic's `SKM_Quinn_Simple` —
  swapping him for `CafeWalker` is the next job, and it needs this same montage set retargeted onto that skeleton.
