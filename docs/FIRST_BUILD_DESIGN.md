# First build design (Thursday's slice)

> **Read this first: what changed after this note was written** (added Thu Nov 12 evening, after the final audit,
> [`FIRST_BUILD_AUDIT.md`](FIRST_BUILD_AUDIT.md)). The body below is the contract the builders worked from and is
> kept as written; where it disagrees with this box, this box is true. The design change (Team Owner, Nov 12
> afternoon) is in [`ROADMAP.md`](ROADMAP.md), Decisions: Freeze Frame is the first power, Rewind is parked.
>
> - **Rewind is parked.** `BP_Player`'s `HasRewind` default is **false**, not true (section 1.2's table). Every Rewind
>   function and variable is still there, unchanged; with it off, Q does nothing and the HUD's `RewindBox` stays
>   collapsed. Section 4 describes the parked Rewind.
> - **The lose rule is "health 0 = lost".** While Rewind is off there is no downed window: `PlayerHealthHitZero` goes
>   straight to `PlayerLose`. Section 6's "downed" rule, `DownedGraceTime` and the blinking Rewind icon only apply
>   again if a later boss sets `HasRewind`.
> - **The boss's freeze is off.** `BP_BossFreeze.BossUsesFreeze` is false, so he never starts the freeze wind-up; he
>   is a big bruiser who punches with a red warning. Section 5.1's "the answer is Rewind" and "Rewind is the only thing
>   that works" no longer describe the game. Whether this boss stays, and what he becomes, is open (ROADMAP, "Still to
>   decide").
> - **Freeze Frame comes from the driver, not the boss.** `BP_SceneMarker` grants it (`MarkerGrantsFreezeFrame`) at
>   `Marker_FreezeFrameGiven` by the driver, and at a second marker at the cafe door, `Marker_FreezeFrameDoor`, so
>   nobody leaves the cafe without it. The boss's defeat (section 5.1, `EnemyDefeatedHook`) still grants it again,
>   harmlessly, and still opens the exit gate.
> - **Markers renamed** (section 7's list is old): `Marker_RewindGiven` -> `Marker_FreezeFrameGiven` (by the driver);
>   the plaza's old `Marker_FreezeFrameGiven` -> `Marker_BossDefeated`; new `Marker_FreezeFrameDoor`.
> - **Trigger radii on placed copies differ from the class default (250).** The placed checkpoint,
>   `Checkpoint_StreetEnd`, has radius **550** (as wide as the street, C1b); `Marker_FreezeFrameDoor` has **200**.
>   These are instance values in the level, set by `tools/d1_editor.py` and `tools/e1_editor.py`, not class defaults.
> - **The entry gate does more than section 7's first paragraph says** (its C1c and C1d paragraphs are right, and G1
>   finished them): the close-behind check also fires once the player is more than `GatePastDepth` past the gate line
>   (no way round the circle along the wall); while the slab drops, a guard keeps the player `GateSafeDepth` inside so
>   it never lands on them or leaves them outside, and switches itself off once the slab is down; when it shuts,
>   every goon is sent home asleep at full health; and the player's Rewind trail is reset, so a parked-then-revived
>   Rewind can't carry the player back out (C1b).
> - **The anime look is on the level** (packet A3; not in the body at all). An unbound post-process volume
>   `PP_AnimeLook` in `Lvl_JumpCut` uses `MI_AnimeLook_JumpCut` (a child of `M_AnimeLook`), and the character meshes
>   of `BP_Player`, `BP_EnemyBase`, `BP_Goon` and `BP_BossFreeze` (and the placed characters) have Render CustomDepth
>   on, which is how the shader tells characters from the background. Its three changed numbers are in section 12.
> - **Checks and questions that are now moot:** section 10's E1 (2) check through `RewindStart` (G1's check replaced
>   it: health 0 goes straight to lost); section 11's questions 2 to 5 (Rewind's cooldown, the grace window, the
>   boss's freeze reach, the slide), until Rewind comes back. Questions 1 and 6 are still open, and the bigger one is
>   now the game's length: a scripted run takes 25 to 27 s.
> - **Section 12** is completed below with the numbers it lacked; rows marked "off" belong to switched-off features.

The contract between the builder packets in [`FIRST_BUILD_LEDGER.md`](FIRST_BUILD_LEDGER.md). Builders share nothing
but this note: **use every name exactly as written**. If a name here turns out to clash with an engine node, pick a
new one, write it into this file, and say so in your report.

All Blueprints live in `/Game/Game/Blueprints/`, widgets in `/Game/Game/UI/`, the two warning materials in
`/Game/Game/Materials/`. Everything is untested by a person until the ledger says otherwise.

## 0. Rules every builder follows

1. **No timers, no Delay nodes, no Timelines, no input events, no overlap events.** Every countdown is a float
   variable that Tick lowers by `DeltaSeconds`. Every trigger is a distance check in Tick. Every key is polled.
   (The graph tool can't make most of those, and the player's Freeze Frame only stops things that run on Tick.)
2. **No collision queries.** Punches and triggers are plain maths: distance, and a dot product for "in front".
   Nobody has to set a collision channel.
3. **The player is the hub.** Enemies, gates, the checkpoint and markers call functions on the player. The HUD and the
   game mode only *read* the player's variables each tick. The player never holds a reference to the HUD or the game mode.
4. **One cast per Blueprint, in its own tiny function.** A cast ends the exec flow, so each Blueprint has a
   `...FindPlayer` function whose last node is the cast that fills its typed `PlayerRef`
   (`GetPlayerCharacter 0` -> cast to `BP_Player`). Tick calls it while `PlayerRef` is not valid and does nothing
   else that frame. Everything else uses `PlayerRef`. (Watch the two `IsValid` versions.)
5. **B1 creates every `BP_Player` variable and every `BP_Player` function in this note**, the later ones as empty
   stubs, and writes the player's EventGraph once. Later packets (B4, D1, D2, E1) only fill function bodies; they
   never rewrite the player's EventGraph and never add a second Tick. Same for `BP_EnemyBase`: B1 builds all of it.
6. **`BP_Player` has no BeginPlay.** The graph tool can't write a call to the parent's BeginPlay, and the template
   character's must keep running. Setup happens on the first Tick (`PlayerSetupDone`). B1: read the parent's
   EventGraph first; if the parent already has an Event Tick with logic in it, stop and report.
7. **Children of `BP_EnemyBase` never define Tick or BeginPlay.** They override the three hook functions
   (`EnemyThink`, `EnemyDefeatedHook`, `EnemyResetHook`) as events (`add_event`, then `(event ...)`), per the skill.
8. **Reading our own function's result:** `bind` the call, then use the value. Never `(return (OurFunction ...))`.
   Key states and other pure nodes: read once into a variable, then use the variable.
9. Bool variables have no `b` prefix. Actor calls use named pins (`:NewLocation`, `:NewRotation`).
10. A checker reads variables on live actors with `get_editor_property` and calls functions with `call_method`.
    If a variable can't be read that way, add a one-line getter named `<Variable>Get` and report it.

---

## 1. Packet B1: `BP_EnemyBase` and `BP_Player`

### 1.1 `BP_EnemyBase`

**Parent:** Character. **Class defaults:** Auto Possess AI = *Placed in World or Spawned* (default AIController; no
navmesh, it walks in a straight line with `AddMovementInput`), and on CharacterMovement *Run Physics with No
Controller* = true as a second safety. Use Controller Rotation Yaw off. Capsule left at defaults (blocks the player:
that's wanted).

**Components**
- `Mesh` (inherited): the template mannequin with `ABP_Unarmed` so it walks. If that isn't right first try, leave it
  empty and add a grey cylinder static mesh `BodyMesh` (no collision) instead. Don't spend time here.
- `WarnSign`: static mesh (engine sphere, scale 0.4), 130 cm above the capsule centre, material `M_WarnPunch`
  (unlit red), no collision, hidden at start. Shown while winding up a punch.

**Variables** (T = tuning number)

| Name | Type | Default | Notes |
|---|---|---|---|
| `EnemyMaxHealth` | float | 100 | T |
| `EnemyHealth` | float | 100 | set to max in setup |
| `EnemyMoveSpeed` | float | 300 | T, copied to MaxWalkSpeed in setup |
| `EnemyAggroRange` | float | 0 | T. Wakes when the player is nearer than this. 0 = never wakes by itself |
| `EnemyStartsAwake` | bool | false | instance editable |
| `EnemyAttackRange` | float | 130 | T. Stops walking and starts a punch inside this |
| `EnemyHitReach` | float | 200 | T. The punch lands if the player is still inside this when the wind-up ends |
| `EnemyDamage` | float | 8 | T |
| `EnemyWindup` | float | 0.45 | T. Seconds the warning shows before a punch |
| `EnemyAttackCooldown` | float | 1.4 | T |
| `EnemyKnockOnPlayer` | float | 300 | T. How hard its punch pushes the player |
| `EnemyKnockTakenScale` | float | 1.0 | T. Multiplies knockback it receives (bosses lower it) |
| `EnemyStunTakenScale` | float | 1.0 | T. Multiplies stun it receives (0 = can't be interrupted) |
| `EnemyDefeatLinger` | float | 0.6 | T. Seconds between 0 health and being destroyed, so the last knockback is seen |
| `EnemyIsAwake` | bool | false | |
| `EnemyIsDefeated` | bool | false | |
| `EnemyTimeStopped` | bool | false | true during the player's Freeze Frame and on the lose screen |
| `EnemyIsWindingUp` | bool | false | |
| `EnemyWindupLeft`, `EnemyAttackCooldownLeft`, `EnemyStunLeft`, `EnemyDefeatLingerLeft` | float | 0 | countdowns |
| `EnemyPendingKnock` | Vector | 0,0,0 | knockback stored while time is stopped |
| `EnemyHomeLocation` | Vector | | where it stood at BeginPlay |
| `EnemyHomeYaw` | float | | |
| `PlayerRef` | BP_Player ref | | filled by `EnemyFindPlayer` |

**Event BeginPlay** (the base only): `EnemySetup`.

**Event Tick(DeltaSeconds)**, in this order, each step ending the tick when it says "stop":
1. `EnemyTimeStopped` -> stop.
2. `EnemyIsDefeated` -> lower `EnemyDefeatLingerLeft`; at 0 or below `DestroyActor`; stop.
3. `PlayerRef` not valid -> `EnemyFindPlayer`; stop.
4. `EnemyStunLeft` > 0 -> lower it; stop.
5. Lower `EnemyAttackCooldownLeft` (if above 0).
6. If `EnemyIsAwake` -> `EnemyThink(DeltaSeconds)`. Else if `EnemyAggroRange` > 0 and `EnemyDistToPlayer` <
   `EnemyAggroRange` -> `EnemyWake`.

**Functions**

| Name | In / out | What it does |
|---|---|---|
| `EnemySetup` | | `EnemyHealth` = max; MaxWalkSpeed = `EnemyMoveSpeed`; store `EnemyHomeLocation` / `EnemyHomeYaw`; `EnemyIsAwake` = `EnemyStartsAwake`; hide `WarnSign` |
| `EnemyFindPlayer` | | rule 4 |
| `EnemyDistToPlayer` | out `Dist` float | flat (XY) distance to `PlayerRef` |
| `EnemyFacePlayer` | | `SetActorRotation`, yaw only, toward `PlayerRef` |
| `EnemyWalkToPlayer` | | `EnemyFacePlayer`, then `AddMovementInput` with the flat unit direction to the player, scale 1 |
| `EnemyShowWarning` | in `Show` bool | sets `WarnSign` visibility |
| `EnemyPunchPlayer` | in `Damage` float | if `EnemyDistToPlayer` <= `EnemyHitReach`: `PlayerRef.PlayerTakeHit(Damage)`, then `PlayerRef.PlayerKnockFrom(own location, EnemyKnockOnPlayer)` |
| `EnemyChasePunchStep` | in `DeltaSeconds` | The shared "walk up and punch" routine, below |
| `EnemyThink` | in `DeltaSeconds` | **Hook.** Base version: `EnemyChasePunchStep(DeltaSeconds)`. Bosses override it |
| `EnemyWake` | | `EnemyIsAwake` = true |
| `EnemyTakeHit` | in `Damage` float, `FromLocation` Vector, `KnockStrength` float, `KnockUp` float, `StunTime` float | below |
| `EnemyDefeatedHook` | | **Hook.** Base version empty. Called once when health reaches 0 |
| `EnemySetTimeStopped` | in `Stopped` bool | below |
| `EnemyResetToStart` | | if `EnemyIsDefeated` do nothing. Else: teleport to home location and yaw, zero velocity, health = max, `EnemyIsAwake` = `EnemyStartsAwake`, all countdowns 0, `EnemyIsWindingUp` false, hide `WarnSign`, then `EnemyResetHook` |
| `EnemyResetHook` | | **Hook.** Base version empty |
| `EnemyGetHealthNow` | out `Value` float | returns `EnemyHealth` (for checkers) |

`EnemyChasePunchStep`:
1. If `EnemyIsWindingUp`: `EnemyFacePlayer`; lower `EnemyWindupLeft`. When it reaches 0: `EnemyIsWindingUp` false,
   `EnemyShowWarning false`, `EnemyPunchPlayer(EnemyDamage)`, `EnemyAttackCooldownLeft` = `EnemyAttackCooldown`. Return.
2. If `EnemyDistToPlayer` > `EnemyAttackRange`: `EnemyWalkToPlayer`. Return.
3. In range: `EnemyFacePlayer`. If `EnemyAttackCooldownLeft` <= 0: `EnemyIsWindingUp` true, `EnemyWindupLeft` =
   `EnemyWindup`, `EnemyShowWarning true`.

`EnemyTakeHit`:
1. If `EnemyIsDefeated`, return.
2. `EnemyHealth` = max(0, `EnemyHealth` - `Damage`).
3. Knock = (flat unit direction from `FromLocation` to self x `KnockStrength` + up x `KnockUp`) x
   `EnemyKnockTakenScale`. If `EnemyTimeStopped`: add it to `EnemyPendingKnock`. Else `LaunchCharacter` (override XY
   and Z both true).
4. Stun = `StunTime` x `EnemyStunTakenScale`. If stun > 0: `EnemyStunLeft` = max(current, stun), `EnemyIsWindingUp`
   false, `EnemyShowWarning false` (hitting first cancels its punch).
5. Read `EnemyHealth` again (the variable, not a bind). If <= 0: `EnemyIsDefeated` true, `EnemyDefeatLingerLeft` =
   `EnemyDefeatLinger`, hide `WarnSign`, `EnemyDefeatedHook`.

`EnemySetTimeStopped(Stopped)`: `EnemyTimeStopped` = `Stopped`; the actor's `CustomTimeDilation` = 0 if stopped, else
1 (this freezes its movement and animation). When un-stopping and `EnemyPendingKnock` is not zero: `LaunchCharacter`
with it, then zero it. So hits landed during a Freeze Frame all "go off" when time resumes.

### 1.2 `BP_Player`

**Parent:** `/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter`. No new components. Movement, jump and camera are
the template's and untouched. The game mode must keep the template's `BP_ThirdPersonPlayerController` (it adds the
input mappings). One `BP_Player` is **placed in the level** with Auto Possess Player = Player 0; a checker confirms
there is exactly one live `BP_Player_C` in Play mode.

**Variables** (all created by B1)

| Name | Type | Default | Notes |
|---|---|---|---|
| `MaxHealth` | float | 100 | T |
| `Health` | float | 100 | |
| `PunchDamage` | float | 10 | T, hits 1 and 2 |
| `PunchDamageFinisher` | float | 20 | T, hit 3 |
| `PunchRange` | float | 180 | T, flat distance to an enemy's centre |
| `PunchArcDot` | float | 0.3 | T, how far in front counts (1 = dead ahead, 0 = anything in the front half) |
| `PunchInterval` | float | 0.25 | T, shortest time between two button presses |
| `ComboWindow` | float | 0.9 | T, time to press again before the combo starts over |
| `KnockbackLight` | float | 250 | T |
| `KnockbackFinisher` | float | 900 | T |
| `KnockUpFinisher` | float | 300 | T |
| `HitStunLight` | float | 0.25 | T, stun given to the enemy |
| `HitStunFinisher` | float | 0.8 | T |
| `HitFlashTime` | float | 0.2 | T, how long the HUD flashes when hit |
| `ComboStep` | int | 0 | last hit landed: 0, 1 or 2 |
| `ComboTimeLeft`, `PunchIntervalLeft`, `HitFlashLeft`, `HitSafeLeft` | float | 0 | countdowns |
| `PlayerSetupDone` | bool | false | |
| `AttackDownNow`, `AttackWasDown`, `RewindDownNow`, `RewindWasDown`, `FreezeDownNow`, `FreezeWasDown` | bool | false | key polling |
| `InputLocked` | bool | false | set by the game mode on the title screen |
| `MoveLocked` | bool | false | what `PlayerRefreshMoveLock` last applied |
| `IsDowned` | bool | false | at 0 health with Rewind ready (the grace window) |
| `DownedGraceTime` | float | 1.5 | T |
| `DownedTimeLeft` | float | 0 | |
| `IsLost` | bool | false | the game mode watches this |
| `HasWon` | bool | false | the game mode watches this |
| `FallLoseZ` | float | -1000 | T, below this height counts as 0 health |
| `CheckpointLocation` | Vector | | start position until a checkpoint is touched |
| `CheckpointYaw` | float | | |
| **Rewind (B4 fills the functions)** | | | |
| `HasRewind` | bool | true | |
| `TrailSeconds` | float | 10 | T |
| `TrailSampleInterval` | float | 0.1 | T |
| `TrailMinMove` | float | 5 | T, cm; a sample is skipped if the player moved less and health is unchanged |
| `RewindSlideTime` | float | 1.0 | T, slide length for a full trail |
| `RewindSlideMin` | float | 0.25 | T, shortest slide |
| `RewindCooldown` | float | 6 | T |
| `RewindSafeTime` | float | 0.5 | T, no damage for this long after landing |
| `TrailPos` | Vector array | empty | oldest first |
| `TrailHealth` | float array | empty | |
| `TrailTime` | float array | empty | value of `TrailClock` when sampled |
| `TrailClock`, `TrailSampleLeft` | float | 0 | |
| `IsRewinding` | bool | false | |
| `RewindAlpha` | float | 0 | 0 at the start of the slide, 1 at the end |
| `RewindSlideDuration` | float | 0 | worked out when a slide starts |
| `RewindCooldownLeft` | float | 0 | |
| **Boss freeze (D1 fills)** | | | |
| `IsFrozenByBoss` | bool | false | |
| `FrozenTimeLeft` | float | 0 | |
| **Freeze Frame (D2 fills)** | | | |
| `HasFreezeFrame` | bool | false | |
| `FreezeFrameDuration` | float | 10 | T (the pitch's number) |
| `FreezeFrameCooldown` | float | 20 | T, starts when the freeze ends |
| `FreezeFrameActive` | bool | false | |
| `FreezeFrameTimeLeft`, `FreezeCooldownLeft` | float | 0 | |

**EventGraph: Event Tick(DeltaSeconds) only**, written once by B1. It calls, in order:
1. If not `PlayerSetupDone`: `PlayerSetup`.
2. `PlayerTickTimers(DeltaSeconds)`
3. `PlayerTickInput`
4. `PlayerTickTrail(DeltaSeconds)` (stub until B4)
5. `PlayerTickRewindSlide(DeltaSeconds)` (stub until B4)
6. `PlayerTickBossFreeze(DeltaSeconds)` (stub until D1)
7. `PlayerTickFreezeFrame(DeltaSeconds)` (stub until D2)
8. `PlayerTickDowned(DeltaSeconds)`
9. `PlayerTickFall`
10. `PlayerRefreshMoveLock`

**Functions built by B1**

| Name | In / out | What it does |
|---|---|---|
| `PlayerSetup` | | `Health` = `MaxHealth`; `CheckpointLocation` / `CheckpointYaw` = where it stands; `PlayerSetupDone` true; `PlayerTrailReset` |
| `PlayerTickTimers` | `DeltaSeconds` | lowers, when above 0: `ComboTimeLeft`, `PunchIntervalLeft`, `HitFlashLeft`, `HitSafeLeft`, `RewindCooldownLeft`, `FreezeCooldownLeft`. (All cooldowns live here so later packets don't touch it.) |
| `PlayerTickInput` | | below |
| `PlayerCanAct` | out `CanAct` bool | true unless any of `IsRewinding`, `IsFrozenByBoss`, `IsDowned`, `IsLost`, `HasWon`, `InputLocked` |
| `PlayerPunch` | | below |
| `PlayerTakeHit` | in `Damage` float | below |
| `PlayerKnockFrom` | in `FromLocation` Vector, `Strength` float | if `PlayerCanAct`: `LaunchCharacter` away from `FromLocation` (flat) x `Strength`, plus 100 up. Nothing while frozen, downed or rewinding |
| `PlayerHealthHitZero` | | the lose rule, section 6 |
| `PlayerTickDowned` | `DeltaSeconds` | if `IsDowned`: lower `DownedTimeLeft`; at 0 or below: `IsDowned` false, `PlayerLose` |
| `PlayerTickFall` | | if actor Z < `FallLoseZ` and none of `IsDowned`, `IsLost`, `IsRewinding`, `HasWon`: `Health` = 0, `PlayerHealthHitZero` |
| `PlayerLose` | | `IsLost` true; `PlayerFreezeFrameEnd`; `PlayerStopAllEnemies true` (the world holds still behind the lose screen) |
| `PlayerRefreshMoveLock` | | Wanted = `IsRewinding` or `IsFrozenByBoss` or `IsDowned` or `IsLost` or `HasWon` or `InputLocked`. If wanted and not `MoveLocked`: CharacterMovement `DisableMovement` and `StopMovementImmediately`, `MoveLocked` true. If not wanted and `MoveLocked`: `SetMovementMode Falling` (it lands at once), `MoveLocked` false. **This is the only place that locks or unlocks movement**; every state just sets its own bool |
| `PlayerStoreCheckpoint` | in `Location` Vector, `Yaw` float | sets `CheckpointLocation`, `CheckpointYaw` |
| `PlayerReachWin` | | if not `IsLost`: `HasWon` true |
| `PlayerSetInputLocked` | in `Locked` bool | sets `InputLocked` |
| `PlayerStopAllEnemies` | in `Stopped` bool | `GetAllActorsOfClass BP_EnemyBase`, for each: `EnemySetTimeStopped(Stopped)` |
| `PlayerDebugTeleport` | in `Location` Vector, `Yaw` float | `SetActorLocation` (no sweep, teleport) and `SetActorRotation`. For checkers only |
| `PlayerGetHealthNow` | out `Value` float | returns `Health` (for checkers) |

`PlayerTickInput` (player controller 0, `IsInputKeyDown`):
1. `AttackDownNow` = LeftMouseButton or Gamepad_FaceButton_Left. `RewindDownNow` = Q or Gamepad_LeftShoulder.
   `FreezeDownNow` = E or Gamepad_RightShoulder. `InteractDownNow` = **F** or Gamepad_FaceButton_Top.
2. If `AttackDownNow` and not `AttackWasDown` and `PunchIntervalLeft` <= 0: `PunchIntervalLeft` = `PunchInterval`, `PlayerPunch`.
3. If `RewindDownNow` and not `RewindWasDown`: `RewindStart`.
4. If `FreezeDownNow` and not `FreezeWasDown`: `FreezeFrameStart`.
5. If `InteractDownNow` and not `InteractWasDown`: `PlayerInteract`.
6. Copy each `...DownNow` into its `...WasDown`.

There are **four** controls, not three. Nothing drives them through an Input Action asset - there is no
`IA_Punch` and none is needed; it is all polled here with edge detection. A fifth key, **R**, restarts and is
polled by the game mode (`JumpCutFlowStep`), not here.

**Bullet time and the Freeze Frame countdown** (added Fri Nov 13 for beat 1's quick time event):

| Function | Does |
| --- | --- |
| `PlayerBulletTimeStart` | If not already in bullet time: `BulletTimeActive` = true, `BulletTimeRealLeft` = `BulletTimeRealDuration` (3.5), `SetGlobalTimeDilation(max(0.01, BulletTimeDilation))` (0.25), plays `SfxBulletTime` |
| `PlayerBulletTimeEnd` | Clears the flag and the clock, `SetGlobalTimeDilation(1.0)` |
| `PlayerTickBulletTime` | Counts `BulletTimeRealLeft` down in **real** seconds - `DeltaSeconds / GetGlobalTimeDilation()`, because `DeltaSeconds` is already dilated - and ends bullet time when it runs out **or** when `PlayerCanAct` goes false (downed, lost, won), so a slowed world can never be left behind |
| `PlayerTickFreezeCountdown` | While the freeze is live and `FreezeFrameTimeLeft` <= `FreezeCountdownAt` (5), takes `Ceil` of the time left and plays `SfxCountdownBeep` each time that whole number changes: 5, 4, 3, 2, 1. Resets `FreezeCountdownLast` to 0 whenever the window is not open |

`FreezeFrameStart` additionally calls `PlayerBulletTimeEnd` and zeroes `FreezeCountdownLast`, so pressing **E**
inside the window hands straight over from slow motion to stopped time. The **"Action"** cue
(`SfxCountdownAction`) is fired from `PlayerFreezeFrameEnd`, **not** from the countdown: by the time
`FreezeFrameTimeLeft` reaches 0 the power is already inactive, so a tick-based countdown can never announce its
own zero. It is inside the existing not-lost-and-not-won branch, so it does not play over a death.

Both ticks are called from `EventTick`: `PlayerTickBulletTime` early (before input, so the dilation the input
sees is current) and `PlayerTickFreezeCountdown` straight after `PlayerTickFreezeFrame`.

`PlayerPunch` (does **not** check `PunchInterval`, so a checker can call it three times in one script):
1. `bind` `PlayerCanAct`; if false, return.
2. If `ComboTimeLeft` <= 0: `ComboStep` = 0. Then Step = `ComboStep` + 1.
3. Step 3 uses `PunchDamageFinisher`, `KnockbackFinisher`, `KnockUpFinisher`, `HitStunFinisher`. Steps 1 and 2 use
   `PunchDamage`, `KnockbackLight`, 0, `HitStunLight`.
4. `GetAllActorsOfClass BP_EnemyBase`. For each: flat distance <= `PunchRange` **and** dot(player's forward, flat unit
   direction to the enemy) >= `PunchArcDot` -> `EnemyTakeHit(damage, player location, knock, knock up, stun)`.
5. `ComboStep` = 0 if Step was 3, else Step. `ComboTimeLeft` = `ComboWindow`. (A swing that hits nothing still
   advances the combo.)

`PlayerTakeHit(Damage)`:
1. Return if any of `IsRewinding`, `IsDowned`, `IsLost`, `HasWon`, or `HitSafeLeft` > 0. (Being frozen by the boss does
   **not** protect: those are his free hits.)
2. `Health` = max(0, `Health` - `Damage`). `HitFlashLeft` = `HitFlashTime`.
3. Read `Health`; if <= 0: `PlayerHealthHitZero`.

**Stubs B1 creates, filled later:** `PlayerTickTrail`, `PlayerTickRewindSlide`, `PlayerTrailReset`, `PlayerTrailAddSample`,
`RewindStart`, `PlayerRewindFinish` (B4); `PlayerTickBossFreeze`, `PlayerFreezeApply` (in `Duration` float),
`PlayerFreezeBreak`, `PlayerGrantFreezeFrame` (D1); `PlayerTickFreezeFrame`, `FreezeFrameStart`,
`PlayerFreezeFrameEnd` (D2); `PlayerRespawnAtCheckpoint` (E1). Give stubs their parameters now.

---

## 2. Packet B2: `WBP_HUD` (and the game mode's two entry points)

**`WBP_HUD`**, a User Widget. No sentences. Single key letters on the icons are fine.

Widgets (exact names, all "Is Variable"):
- `HealthBar`: Progress Bar, top left, about 400 x 28 px, red fill.
- `RewindIcon`: Image, a 64 px coloured square (amber), bottom left. `RewindKey`: Text "Q" on it. `RewindBar`: thin
  Progress Bar under it.
- `FreezeBox`: a container holding `FreezeIcon` (Image, cyan square), `FreezeKey` (Text "E"), `FreezeBar`
  (Progress Bar). Sits right of the Rewind icon.
- `FrozenTint`: full-screen Image, pale blue, alpha 0.25, not hit-testable.
- `HitFlash`: full-screen Image, red, alpha 0.25, not hit-testable.

Variable: `HudPlayerRef` (BP_Player ref). No property bindings: the widget's **Event Tick** does everything.
- If `HudPlayerRef` is not valid: `HudFindPlayer` (rule 4), stop.
- Else `HudRefresh`:
  - `HealthBar` percent = `Health` / `MaxHealth`.
  - `RewindBar` percent = 1 - `RewindCooldownLeft` / max(`RewindCooldown`, 0.01) (full = ready).
    `RewindIcon` opacity 1 if `RewindCooldownLeft` <= 0, else 0.35. If `IsDowned`: blink it instead (opacity 1 or 0.2,
    switching 4 times a second off `GetGameTimeInSeconds`): that's the wordless "press Rewind now".
    Collapsed if not `HasRewind`.
  - `FreezeBox` Collapsed unless `HasFreezeFrame`. `FreezeBar` percent = `FreezeFrameTimeLeft` /
    `FreezeFrameDuration` while `FreezeFrameActive` (it drains), else 1 - `FreezeCooldownLeft` /
    max(`FreezeFrameCooldown`, 0.01). `FreezeIcon` opacity 1 when ready or active, else 0.35.
  - `FrozenTint` Visible (HitTestInvisible) while `IsFrozenByBoss`, else Collapsed.
  - `HitFlash` visible while `HitFlashLeft` > 0, else Collapsed.

**`BP_JumpCutGameMode`** (B2 creates the frame, E1 fills the rest; see section 7):
- Variables: `PlayerRef` (BP_Player ref), `HudWidget` (WBP_HUD ref).
- EventGraph, written once: BeginPlay -> `JumpCutFlowSetup`. Tick -> `JumpCutFlowTick(DeltaSeconds)`.
- B2's `JumpCutFlowSetup`: create `WBP_HUD`, store it in `HudWidget`, add to viewport. B2's `JumpCutFlowTick`: empty.
- B2 must confirm the game mode's Tick really fires in Play mode (the HUD doesn't depend on it, E1 does). If it
  doesn't, switch on "Start with Tick Enabled" in its class defaults and report.

**As built (B2):** the game mode's Tick fires in Play mode with no setting changed (a temporary counter matched game
time; removed again). Additions, all named here so E1 and checkers can use them: `RewindBox` (canvas holding
`RewindIcon`, `RewindKey`, `RewindBar`; it is what collapses when `HasRewind` is false), `DownedTint` (dark red, while
`IsDowned`), `FreezeFrameTint` (grey 0.35) and `FreezeFrameEdges` (four cyan bars round the screen edge) while
`FreezeFrameActive`, `RewindTint` (amber 0.3, while `IsRewinding`), and a helper `HudShowIf(Target, Show)` that sets
HitTestInvisible or Collapsed. The Rewind icon also blinks while `IsFrozenByBoss` when Rewind is ready (the way out).
`FreezeBox` sits at the same place whether or not the player has Rewind.

---

## 3. Packet B3: `BP_Goon` and `BP_GoonSpawner`

**`BP_Goon`**: child of `BP_EnemyBase`, **no graph at all**. It is only different defaults: the base `EnemyThink`
already walks up and punches.

| Variable | Goon default |
|---|---|
| `EnemyMaxHealth` | 40 (one full combo: 10 + 10 + 20) |
| `EnemyAggroRange` | 1500 |
| others | the base defaults (speed 300, damage 8, wind-up 0.45, cooldown 1.4) |

**`BP_GoonSpawner`**: parent Actor. Components: `SpawnerRoot` (Scene), `SpawnerArrow` (Arrow, editor only: goons line
up across it).

| Variable | Type | Default | Notes |
|---|---|---|---|
| `GoonCount` | int | 3 | T, instance editable |
| `GoonSpacing` | float | 150 | T, cm between goons |
| `SpawnedGoons` | BP_Goon array | empty | |

| Function | What it does |
|---|---|
| `GoonSpawnerSpawnGroup` | for i = 0 .. `GoonCount` - 1: location = actor location + right vector x (i - (`GoonCount` - 1) / 2) x `GoonSpacing` + 100 up; spawn `BP_Goon` there with the spawner's yaw ("AlwaysSpawn"); add to `SpawnedGoons` |
| `GoonSpawnerClear` | destroy every still-valid goon in `SpawnedGoons`; clear the array |
| `GoonSpawnerRespawn` | `GoonSpawnerClear`, then `GoonSpawnerSpawnGroup` |

BeginPlay: `GoonSpawnerSpawnGroup`. No Tick. Goons placed by hand also work, but only spawner goons come back on a restart.

---

## 4. Packet B4: Rewind (on `BP_Player`)

B4 fills these stubs and nothing else.

| Function | What it does |
|---|---|
| `PlayerTrailAddSample` | append actor location to `TrailPos`, `Health` to `TrailHealth`, `TrailClock` to `TrailTime` |
| `PlayerTrailReset` | clear the three arrays, `TrailSampleLeft` = 0, then `PlayerTrailAddSample` (the trail always has at least one sample) |
| `PlayerTickTrail(DeltaSeconds)` | below |
| `RewindStart` | below |
| `PlayerTickRewindSlide(DeltaSeconds)` | below |
| `PlayerRewindFinish` | below |

### The trail
`PlayerTickTrail`:
1. `TrailClock` += `DeltaSeconds` (always: it is the trail's own clock).
2. Return if `IsRewinding`, `IsLost`, or `Health` <= 0. (So no sample ever holds 0 health.)
3. Drop one old sample: if the array has 2 or more entries and `TrailTime[1]` <= `TrailClock` - `TrailSeconds`, remove
   index 0 from all three arrays. Sample 0 is therefore always "how things were 10 seconds ago" (the newest sample
   that is at least 10 s old), or the start point if less time has passed.
4. `TrailSampleLeft` -= `DeltaSeconds`. If <= 0: `TrailSampleLeft` = `TrailSampleInterval`; add a sample **only if**
   the player is more than `TrailMinMove` from the last sample's position or `Health` differs from the last sample's
   health. (Standing still adds nothing, so the slide never pauses on the spot; this also covers time spent frozen.)

Sampling carries on while frozen by the boss and during the player's own Freeze Frame.

### Starting
`RewindStart`:
1. Return if not `HasRewind`, or `IsRewinding`, or `RewindCooldownLeft` > 0, or `IsLost`, or `HasWon`, or `InputLocked`.
   (It does **not** check `PlayerCanAct`: rewinding while frozen or downed is the whole point.)
2. `PlayerFreezeBreak` (ends the boss's freeze; harmless stub until D1).
3. `IsDowned` = false.
4. `PlayerTrailAddSample` (so the slide starts exactly where the player is).
5. `RewindSlideDuration` = max(`RewindSlideMin`, `RewindSlideTime` x sample count / (`TrailSeconds` /
   `TrailSampleInterval`)). A short trail gives a short slide.
6. `RewindAlpha` = 0; `IsRewinding` = true.

### The slide (Tick-driven)
`PlayerTickRewindSlide`: if not `IsRewinding`, return. Otherwise:
1. `RewindAlpha` += `DeltaSeconds` / `RewindSlideDuration`.
2. If `RewindAlpha` >= 1: `PlayerRewindFinish`, return.
3. F = (1 - `RewindAlpha`) x (count - 1). I = floor(F). J = min(I + 1, count - 1).
   Position = lerp(`TrailPos[I]`, `TrailPos[J]`, F - I). `SetActorLocation :NewLocation Position`, sweep off, teleport on.

`PlayerRewindFinish`:
1. `SetActorLocation` to `TrailPos[0]` (sweep off, teleport on).
2. `Health` = max(`Health`, `TrailHealth[0]`). (Rewind never lowers health.)
3. `IsRewinding` = false; `RewindCooldownLeft` = `RewindCooldown` (the cooldown starts on landing);
   `HitSafeLeft` = `RewindSafeTime`.
4. `PlayerTrailReset` (the next rewind can't go back past this landing).

### How movement, collision and gravity behave during it
- `IsRewinding` makes `PlayerRefreshMoveLock` disable movement: no gravity, no walking, no jump, no input fighting
  the slide. On landing the mode goes to Falling and the character settles on the floor in the same frame.
- The slide teleports from sample to sample without sweeping. Every sample is a place the capsule really stood, so it
  never ends inside a wall; it passes through enemies and closed gates on the way.
- Enemies' hits do nothing during the slide and for `RewindSafeTime` after (`PlayerTakeHit` returns early).
  Enemies are **not** rewound (cut list: only the player rewinds); they keep walking toward where the player lands.
- The camera is the template's boom: it follows the slide by itself.

### Edge cases
- **Less than 10 s of trail:** slides to the oldest sample (game start, the last respawn, or the last rewind's
  landing), faster.
- **Only one sample** (stood still for 10 s and nothing changed): a zero-length slide of `RewindSlideMin`; it still
  breaks a freeze, still restores health, and still costs the cooldown.
- **While frozen by the boss:** allowed; step 2 breaks the freeze. Section 5.
- **At 0 health (downed):** allowed during the grace window; health comes back from the oldest sample, which is
  always above 0. Section 6.
- **Falling off the world:** below `FallLoseZ` counts as reaching 0 health. If Rewind is ready the player hangs there
  (movement is locked while downed) and can rewind back onto the floor; otherwise it is a loss.
- **During the cooldown or a slide:** `RewindStart` does nothing at all.

---

## 5. The two freezes

### 5.1 Packet D1: `BP_BossFreeze`, and how the boss freezes the player

**`BP_BossFreeze`**: child of `BP_EnemyBase`. Mesh scaled 1.3 so he reads as the boss. Extra component `FreezeRing`:
static mesh (engine cylinder, flattened to 2 cm, no collision, material `M_WarnFreeze` = unlit cyan), on the floor
under him, hidden at start. Its XY scale is set in his first think so its radius equals `BossFreezeRadius`.

Changed defaults: `EnemyMaxHealth` 240, `EnemyMoveSpeed` 380, `EnemyDamage` 15, `EnemyWindup` 0.7,
`EnemyAttackCooldown` 1.6, `EnemyKnockTakenScale` 0.25, `EnemyStunTakenScale` 0 (combos don't interrupt him),
`EnemyAggroRange` 0 (the gate wakes him).

| Variable | Type | Default | Notes |
|---|---|---|---|
| `BossFreezeRadius` | float | 1200 | T. Most of the plaza: hard to outrun on purpose, the answer is Rewind |
| `BossFreezeWindup` | float | 1.2 | T. The ring shows this long before the freeze |
| `BossFreezeDuration` | float | 3.0 | T. How long the player is stuck |
| `BossFreezeCooldown` | float | 9 | T. **Keep it above the player's `RewindCooldown`** (6), so Rewind can always be ready for the next freeze |
| `BossFirstFreezeDelay` | float | 4 | T. After waking |
| `BossFreeHitDamage` | float | 12 | T |
| `BossFreeHitInterval` | float | 0.8 | T |
| `BossBrokenStun` | float | 1.5 | T. He is dazed this long when Rewind breaks his freeze: the player's opening |
| `BossExitGate` | BP_PlazaGate ref | none | instance editable; set on the placed boss to the far gate |
| `BossState` | int | 0 | 0 = fight, 1 = freeze wind-up, 2 = free hits |
| `BossFreezeCooldownLeft`, `BossFreezeWindupLeft`, `BossHoldLeft`, `BossFreeHitLeft` | float | 0 | |
| `BossRingSized` | bool | false | |

Overrides (events in his EventGraph):

**`EnemyThink(DeltaSeconds)`**
- First time (`BossRingSized` false): scale `FreezeRing`, `BossFreezeCooldownLeft` = `BossFirstFreezeDelay`, set the bool.
- **State 0, fight:** lower `BossFreezeCooldownLeft`. If it is <= 0 and not `EnemyIsWindingUp` and
  `EnemyDistToPlayer` <= `BossFreezeRadius`: `BossStartFreezeWindup`. Otherwise `EnemyChasePunchStep(DeltaSeconds)`
  (his normal punch, with the red `WarnSign` as its warning).
- **State 1, freeze wind-up:** stand still, `EnemyFacePlayer`, lower `BossFreezeWindupLeft`. At 0: hide `FreezeRing`,
  `BossFreezeCooldownLeft` = `BossFreezeCooldown`. If the player is within `BossFreezeRadius`:
  `PlayerRef.PlayerFreezeApply(BossFreezeDuration)`, `BossHoldLeft` = `BossFreezeDuration`, `BossFreeHitLeft` = 0.3,
  state 2. Else state 0 (the player got out: the freeze missed).
- **State 2, free hits:** lower `BossHoldLeft`. If the player's `IsFrozenByBoss` is false: when `BossHoldLeft` > 0.1
  the freeze was broken early, so `EnemyStunLeft` = `BossBrokenStun`; either way state 0. Otherwise: if farther than
  `EnemyAttackRange`, `EnemyWalkToPlayer`; else lower `BossFreeHitLeft` and at 0 `EnemyPunchPlayer(BossFreeHitDamage)`
  and `BossFreeHitLeft` = `BossFreeHitInterval`. No warning: these are the free hits.

**`BossStartFreezeWindup`** (its own function so a checker can call it): `BossState` = 1, `BossFreezeWindupLeft` =
`BossFreezeWindup`, show `FreezeRing`, `EnemyIsWindingUp` false, `EnemyShowWarning false`.

**`EnemyDefeatedHook`**: hide `FreezeRing`; if `BossExitGate` is valid `BossExitGate.PlazaGateOpenForGood`; then
`BossHandOverPower` either way. (The base then destroys him after the linger.)

**`BossHandOverPower`** (Nov 12, the boss ladder decision): if `PlayerRef` is valid, `PlayerRef.PlayerFreezeBreak`
then `PlayerRef.PlayerGrantSplice`. It used to call `PlayerGrantFreezeFrame`; the mob boss is boss 2 and hands over
**Splice**, while Freeze Frame comes from boss 1, the car crash, through the two cafe markers. `HasSplice` gates
nothing yet - the Splice ability is not built and the HUD has no Splice box.

**`EnemyResetHook`**: `BossState` 0, hide `FreezeRing`, `BossFreezeCooldownLeft` = `BossFirstFreezeDelay`, other
countdowns 0.

**Player side (D1 fills these stubs):**

| Function | What it does |
|---|---|
| `PlayerFreezeApply(Duration)` | return if `IsRewinding`, `IsLost`, `HasWon` or `HitSafeLeft` > 0. Else `IsFrozenByBoss` true, `FrozenTimeLeft` = `Duration` |
| `PlayerFreezeBreak` | `IsFrozenByBoss` false, `FrozenTimeLeft` 0 |
| `PlayerTickBossFreeze(DeltaSeconds)` | if `IsFrozenByBoss`: lower `FrozenTimeLeft`; at 0 `PlayerFreezeBreak` |
| `PlayerGrantFreezeFrame` | `HasFreezeFrame` true |
| `PlayerGrantSplice` | `HasSplice` true (nothing reads it yet) |

What "frozen" means for the player: `PlayerRefreshMoveLock` disables movement (he hangs mid-air if he was jumping),
`PlayerCanAct` is false so punches and Freeze Frame do nothing, the HUD shows `FrozenTint`, and hits still land.
The camera still turns. **Rewind is the only thing that works**: `RewindStart` calls `PlayerFreezeBreak`, the slide
carries the player back out, the health lost to free hits returns, and the boss stands dazed for `BossBrokenStun`.

### 5.2 Packet D2: the player's Freeze Frame

**Choice: `CustomTimeDilation` = 0 on each enemy, not global time dilation.** Why:
- Global dilation slows the player, the camera, the HUD's Tick and every countdown in this note; each would need
  compensating, and one missed spot is a bug nobody can see without playing.
- The checkers already use global time dilation to freeze the game for captures. The two would fight.
- Per-enemy needs one loop and no compensation. Every enemy already has `EnemySetTimeStopped`, and the base Tick
  stops at step 1 while it is set, so nothing an enemy does can leak through.

| Function | What it does |
|---|---|
| `FreezeFrameStart` | return if not `HasFreezeFrame`, or `FreezeFrameActive`, or `FreezeCooldownLeft` > 0; `bind` `PlayerCanAct`, return if false. Else `FreezeFrameActive` true, `FreezeFrameTimeLeft` = `FreezeFrameDuration`, `PlayerStopAllEnemies true` |
| `PlayerTickFreezeFrame(DeltaSeconds)` | if `FreezeFrameActive`: lower `FreezeFrameTimeLeft`; at 0 `PlayerFreezeFrameEnd` |
| `PlayerFreezeFrameEnd` | if `FreezeFrameActive`: set it false, `FreezeCooldownLeft` = `FreezeFrameCooldown`, `PlayerStopAllEnemies false` |

During it: enemies don't move, think, wind up or animate. The player moves, punches and can rewind. Punches do their
damage at once; the knockback is stored and released when time resumes. An enemy brought to 0 health stays standing
until time resumes, then flies back and disappears. Gates, the checkpoint and markers are not stopped.

**How new systems must respect it:** anything that should stop is a child of `BP_EnemyBase`, or has its own
`...SetTimeStopped` function that `PlayerStopAllEnemies` is extended to call. Drive everything from Tick's
`DeltaSeconds`; a Delay, timer or Timeline ignores `CustomTimeDilation` and will keep running through a freeze.
Anything spawned mid-freeze must be stopped by whoever spawns it (today nothing spawns mid-freeze).
**As built (D2):** `PlayerTickFreezeFrame` re-applies `PlayerStopAllEnemies true` every tick while the freeze lasts, so
anything spawned mid-freeze (e.g. `GoonSpawnerRespawn`) is stopped within a frame. `PlayerFreezeFrameEnd` also zeroes
`FreezeFrameTimeLeft` and only un-stops enemies when neither `IsLost` nor `HasWon` is set (the lose screen's world stays
still). `FreezeFrameStart` needs `PlayerCanAct`, so it does nothing while frozen by the boss; it works during his warning.

---

## 6. The lose rule and restart

**The rule.** `PlayerHealthHitZero` runs the moment health reaches 0 (a hit, or falling below `FallLoseZ`):
- If `HasRewind` and `RewindCooldownLeft` <= 0: **downed**. `IsDowned` true, `DownedTimeLeft` = `DownedGraceTime`
  (1.5 s). The player can't move or punch and can't be hit again; the HUD's Rewind icon blinks. Pressing Rewind in
  that window saves them (slide back, health restored). If the window runs out: `PlayerLose`.
- Otherwise (Rewind on cooldown, even with 0.1 s left): `PlayerLose` at once.
- Health can't reach 0 during a slide or the `RewindSafeTime` after it.

`PlayerLose` sets `IsLost` and stops every enemy. The game mode sees `IsLost` on its next tick and shows the lose screen.

**Restart** is a soft reset, not a level reload (the checkpoint and the Freeze Frame power would need a save
otherwise). The game mode's `JumpCutRestartFromCheckpoint`, in this order:
1. `PlayerRef.PlayerRespawnAtCheckpoint`: `PlayerFreezeFrameEnd`; `PlayerStopAllEnemies false`; `PlayerFreezeBreak`;
   `IsDowned`, `IsRewinding`, `IsLost`, `HasWon` false; teleport to `CheckpointLocation` + 20 up with `CheckpointYaw`
   (also set the controller's rotation to that yaw so the camera faces forward); zero velocity; `Health` =
   `MaxHealth`; `RewindCooldownLeft`, `FreezeCooldownLeft`, `HitSafeLeft`, `ComboTimeLeft` = 0, `ComboStep` = 0;
   `PlayerTrailReset`. **`HasFreezeFrame` and the stored checkpoint are kept.**
2. Every `BP_EnemyBase`: `EnemyResetToStart` (the boss goes home, asleep, full health; a defeated one is skipped).
3. Every `BP_GoonSpawner`: `GoonSpawnerRespawn` (old goons removed, a fresh group made).
4. Every `BP_PlazaGate`: `PlazaGateResetToStart` (the entry gate reopens and re-arms; a gate opened for good stays open).
5. Hide the lose screen, show the HUD, flow state back to playing.

Goons placed by hand (not by a spawner) that were beaten stay beaten. A beaten boss stays beaten and his gate stays open.

---

## 7. Packet C1: gate, checkpoint, markers, level

All three are parent Actor and find the player by rule 4 (`GateFindPlayer`, `CheckpointFindPlayer`, `MarkerFindPlayer`).
Each has a `TriggerSphere` (Sphere Collision set to **NoCollision**, used only as a visible radius: the Tick check is
"flat distance from the player to `TriggerSphere`'s world location < its scaled radius").

### `BP_PlazaGate`
Components: `GateRoot` (Scene), `GateMesh` (engine cube scaled to fill the opening, BlockAll), `TriggerSphere`
(radius 300; on the entry gate, moved **400 cm into the plaza** so the gate never closes on the player).

| Variable | Type | Default | Notes |
|---|---|---|---|
| `GateOpenHeight` | float | 450 | T. How far `GateMesh` rises when open |
| `GateMoveSpeed` | float | 900 | T, cm/s |
| `GateStartsOpen` | bool | false | instance editable |
| `GateClosesBehindPlayer` | bool | false | instance editable |
| `GateEnemyToWake` | BP_EnemyBase ref | none | instance editable |
| `GateIsOpen` | bool | | |
| `GateLockedOpen` | bool | false | |
| `GateTriggerArmed` | bool | true | |

| Function | What it does |
|---|---|
| `PlazaGateOpen` | `GateIsOpen` true |
| `PlazaGateClose` | if not `GateLockedOpen`: `GateIsOpen` false |
| `PlazaGateOpenForGood` | `GateLockedOpen` true, `GateIsOpen` true |
| `PlazaGateResetToStart` | if `GateLockedOpen` return. `GateTriggerArmed` true; `GateIsOpen` = `GateStartsOpen` |

BeginPlay: `GateIsOpen` = `GateStartsOpen`, and put `GateMesh` straight at that height (no slide at the start).
Tick: (a) move `GateMesh`'s relative Z toward `GateOpenHeight` (open) or 0 (closed) with `FInterpToConstant` at
`GateMoveSpeed`. (b) If `GateClosesBehindPlayer` and `GateTriggerArmed` and `GateIsOpen` and `GateEnemyToWake` is
valid and the player is inside the trigger: `PlazaGateClose`, `GateTriggerArmed` false, `GateEnemyToWake.EnemyWake`.
(No living boss means it doesn't shut.)
**C1c:** "inside" for the close-behind check is the trigger circle **or** more than `GatePastDepth` (float, 120, T) cm
past the gate line on the trigger's side (`GateIsPastGateway`, a flat dot product, so no way round the circle along the
wall; 120 = half the slab + the capsule + spare, so the slab never lands on the player). When it shuts it also calls
`GateSendGoonsHome`: every `BP_Goon` gets `EnemyResetToStart` (home, asleep, full health), so none can punch through.
`EnemyTakeHit` on a sleeping enemy now wakes it first.
**C1d:** from the moment the close-behind branch fires until the slab reaches the bottom (`GateGuardingClose`), a player
less than `GateSafeDepth` (120) inside the gate line, no more than `GateRescueReach` (400) outside it and within
`GateRescueHalfWidth` (600) sideways is moved along the gate's forward axis to `GateSafeDepth` inside (sideways
position and height kept; teleport, no sweep), once in the close branch and every tick after (`GateKeepPlayerInside`
from `GateTickStep`, `GatePushPlayerInside`). So the slab never lands on the player and they can't be left outside.
Only the entry gate ever sets the guard.

In the level: **entry gate** (`Gate_PlazaEntry`): starts open, closes behind the player, wakes the boss.
**Exit gate** (`Gate_PlazaExit`): starts closed; the boss's `BossExitGate` points at it. Keep each opening 5 m wide
or less so one cube fills it.

### `BP_Checkpoint`
Components: `CheckpointRoot`, `PostMesh` (a grey post, no collision), `TakenSign` (a small cube on top, unlit green or
plain, hidden until taken), `RespawnPoint` (Scene; where and which way the player restarts), `TriggerSphere` (radius 250).
Variable: `CheckpointTaken` bool. Tick: if not taken and the player is inside:
`PlayerRef.PlayerStoreCheckpoint(RespawnPoint world location, RespawnPoint world yaw)`, `CheckpointTaken` true, show
`TakenSign`. Place it at the street's end, **outside** the entry gate, with `RespawnPoint` facing the plaza.

### `BP_SceneMarker`
Placeholders for cut scenes, and the finish line. Components: `MarkerRoot`, `MarkerArrow` (Arrow, hidden in game),
`TriggerSphere` (radius 250).

| Variable | Type | Default | Notes |
|---|---|---|---|
| `MarkerId` | Name | None | instance editable; same as the actor's label |
| `MarkerEndsGame` | bool | false | instance editable |

Tick: if `MarkerEndsGame` and the player is inside the trigger: `PlayerRef.PlayerReachWin`. Other markers do nothing yet.
Markers to place: `Marker_Crash` (cafe, by the car box), `Marker_RewindGiven` (by the driver box),
`Marker_FreezeFrameGiven` (plaza centre), and **`Marker_Win`** (`MarkerEndsGame` true, about 6 m beyond the exit gate).

### Level notes for C1
Floor top at Z = 0 everywhere (`FallLoseZ` is -1000). Walls at least 4 m high so a knockback can't clear them. One
`BP_GoonSpawner` (`GoonCount` 3) about 30 m down the street, arrow pointing back at the cafe. The placed `BP_Player`
in the cafe, Auto Possess Player 0. The placed `BP_BossFreeze` at the plaza centre facing the entry gate (D1 places
him and sets `BossExitGate` and the entry gate's `GateEnemyToWake`; after `set_properties` on a placed actor, re-set
its full transform so the level saves).

---

## 8. Packet E1: screens and flow (`BP_JumpCutGameMode`)

**Widgets** (each a full-screen dark panel; these may use words):
- `WBP_Title`: "JUMP CUT" and a small "R / (A)".
- `WBP_Lose`: "CUT!" and "R / (A)".
- `WBP_Win`: "THAT'S A WRAP" and "R / (A)".
No buttons, no mouse: the input mode is always "game only" (`JumpCutFlowSetup` sets it once, which also clears a
"UI only" left over from another level).

**Game mode variables** (added to B2's): `FlowState` int (0 title, 1 playing, 2 lost, 3 won), `TitleWidget`,
`LoseWidget`, `WinWidget`, `ShowTitleOnStart` bool (true; T), `RestartDownNow`, `RestartWasDown` bool.

| Function | What it does |
|---|---|
| `JumpCutFindPlayer` | rule 4 |
| `JumpCutFlowSetup` | input mode game only; create the HUD and the three screens, add all to the viewport, screens Collapsed. `FlowState` 0. (The title is shown from the first `JumpCutFlowTick` that has a player.) |
| `JumpCutFlowTick(DeltaSeconds)` | below |
| `JumpCutStartPlay` | `FlowState` 1; `PlayerRef.PlayerSetInputLocked false`; hide title, lose and win; show HUD |
| `JumpCutShowLose` | `FlowState` 2; show `LoseWidget`; hide HUD |
| `JumpCutShowWin` | `FlowState` 3; show `WinWidget`; hide HUD |
| `JumpCutRestartFromCheckpoint` | section 6, then `JumpCutStartPlay` |
| `JumpCutRestartWholeLevel` | `OpenLevel` with the current level's name (a full reset; used from the win screen) |

`JumpCutFlowTick`:
1. `PlayerRef` not valid -> `JumpCutFindPlayer`; return.
2. `RestartDownNow` = R or Gamepad_FaceButton_Bottom on controller 0. Pressed = now and not `RestartWasDown`. Store
   `RestartWasDown` at the end.
3. `FlowState` 0: if not `ShowTitleOnStart` -> `JumpCutStartPlay`. Else make sure the title is visible, the HUD hidden
   and `PlayerRef.PlayerSetInputLocked true`; on Pressed -> `JumpCutStartPlay`.
4. `FlowState` 1: if `PlayerRef.HasWon` -> `JumpCutShowWin`; else if `PlayerRef.IsLost` -> `JumpCutShowLose`.
5. `FlowState` 2: on Pressed -> `JumpCutRestartFromCheckpoint`.
6. `FlowState` 3: on Pressed -> `JumpCutRestartWholeLevel`.

E1 also fills `PlayerRespawnAtCheckpoint` on `BP_Player` (section 6, step 1) and sets `GameDefaultMap` /
`EditorStartupMap`. The game is never paused (`SetGamePaused` would stop the Ticks that read the restart key).

**As built (G1/E1, Nov 12 design change: Freeze Frame first, Rewind parked).** Graphs in `tools/e1_graphs.py`.
- **Rewind parked:** `BP_Player`'s class default `HasRewind` = false; no Rewind function or variable changed. With it
  false, `RewindStart` returns at once (Q does nothing), the HUD's `RewindBox` stays collapsed, and
  `PlayerHealthHitZero` goes straight to `PlayerLose`: no downed window. The section 6 "downed" rule and the Rewind
  blink only apply again when a later boss sets `HasRewind`.
- **Freeze Frame from the driver:** `BP_SceneMarker` has `MarkerGrantsFreezeFrame` (instance editable, default false)
  and a `GiftMesh` (cyan unlit sphere, 100 cm up, no collision). `MarkerTickStep` = `MarkerWinStep` (the old body) +
  `MarkerGiftStep`: the sphere shows while the marker grants and the player lacks the power; inside the trigger the
  player gets `PlayerGrantFreezeFrame` once and every gift sphere hides. Two markers grant: **`Marker_FreezeFrameGiven`**
  by the driver (re-labelled from `Marker_RewindGiven`, radius 250) and **`Marker_FreezeFrameDoor`** (new, at
  (560, 0), radius 200 on the instance) which covers the whole cafe door, so nobody leaves the cafe without the power.
  (A single circle round the driver can't reach the door without also covering the start point.) The plaza's old
  `Marker_FreezeFrameGiven` is now **`Marker_BossDefeated`**. Nothing looks markers up by label.
- **Boss:** `BP_BossFreeze.BossUsesFreeze` (default false); `BossThinkFight` only starts the freeze wind-up when it is
  true. `BossStartFreezeWindup` itself still works for checkers. His defeat still opens the exit gate (and since the
  Nov 12 ladder decision grants **Splice**, not Freeze Frame).
- **Gate:** `GatePushPlayerInside` clears `GateGuardingClose` at slab height `<= 0.01` (it rested at 0.000091).
- **E1 extras:** game mode variables `RestartPressedNow` (stored before `RestartWasDown` is overwritten) and helper
  functions `JumpCutFlowStep`, `JumpCutTitleStep`, `JumpCutPlayStep`; the HUD is created Collapsed and shown by
  `JumpCutStartPlay`. `JumpCutStartPlay` also sets the input mode to game only. `PlayerRespawnAtCheckpoint` also zeroes
  `HitFlashLeft`, `DownedTimeLeft` and `PunchIntervalLeft`. `WBP_HUD`'s `RewindBox` and `FreezeBox` now start
  Collapsed (the HUD doesn't tick while collapsed on the title). Screens: dark full-screen panel, title text, the key
  as "R / (A)" on a light box. Restart in the cafe (no checkpoint yet) puts the player back at the start; the power is
  kept if taken, and the gift spheres are still there if not.

---

## 9. Who talks to whom

| From | To | How | What |
|---|---|---|---|
| `BP_Player` | every `BP_EnemyBase` | `GetAllActorsOfClass` | `EnemyTakeHit` (punch), `EnemySetTimeStopped` (Freeze Frame, lose screen) |
| `BP_EnemyBase` and children | `BP_Player` | `PlayerRef` | `PlayerTakeHit`, `PlayerKnockFrom`; reads its location |
| `BP_BossFreeze` | `BP_Player` | `PlayerRef` | `PlayerFreezeApply`; reads `IsFrozenByBoss`; on defeat `PlayerFreezeBreak`, `PlayerGrantSplice` |
| `BP_BossFreeze` | exit `BP_PlazaGate` | `BossExitGate` (set in the level) | `PlazaGateOpenForGood` on defeat |
| entry `BP_PlazaGate` | boss | `GateEnemyToWake` (set in the level) | `EnemyWake` when it shuts |
| `BP_Checkpoint` | `BP_Player` | `PlayerRef` | `PlayerStoreCheckpoint` |
| `BP_SceneMarker` (`Marker_Win`) | `BP_Player` | `PlayerRef` | `PlayerReachWin` |
| `WBP_HUD` | `BP_Player` | `HudPlayerRef` | reads variables every tick; calls nothing |
| `BP_JumpCutGameMode` | `BP_Player` | `PlayerRef` | reads `IsLost`, `HasWon`; calls `PlayerSetInputLocked`, `PlayerRespawnAtCheckpoint` |
| `BP_JumpCutGameMode` | enemies, spawners, gates | `GetAllActorsOfClass` | the restart calls in section 6 |

---

## 10. How a checker checks each "Done means" without keys

| Packet | How |
|---|---|
| B1 (2) | `PlayerTakeHit 30`, then `PlayerGetHealthNow` = 70 |
| B1 (3) | `PlayerDebugTeleport` to 120 cm from a placed `BP_EnemyBase`, **yaw facing it**; `PlayerPunch` x 3 in one script; `EnemyGetHealthNow` 100 -> 90 -> 80 -> 60; a second later it is 150 cm or more further away |
| B1 (4) | six more punches (or one `EnemyTakeHit` with 999 damage); it is gone about 0.6 s later, not instantly |
| B3 (5) | as B1 (3) on a goon (40 health): gone 0.6 s after the third hit |
| B4 (2,3) | wait until `IsRewinding` is false again before measuring (the slide takes 0.25 to 1 s) |
| B4 (4) | `RewindCooldownLeft` > 0 and the position doesn't change |
| C1 (3) | `PlazaGateClose` / `PlazaGateOpen`; capture half a second later (the gate slides) |
| C1 (4) | `PlayerDebugTeleport` onto the checkpoint; next tick `CheckpointLocation` = its `RespawnPoint` |
| D1 (2) | `EnemyWake`, then `BossStartFreezeWindup` with the player within 1200 cm; capture the cyan ring; 1.2 s later `IsFrozenByBoss` and `MoveLocked` are true |
| D1 (3) | `RewindStart`: `IsFrozenByBoss` false at once |
| D1 (4) | `EnemyTakeHit` with 999 damage on the boss: `HasFreezeFrame` true, exit gate `GateIsOpen` true |
| D2 (2,3,4) | `FreezeFrameStart` before and after `PlayerGrantFreezeFrame`; compare a waking goon's location over 2 s; `PlayerFreezeFrameEnd` to finish early |
| E1 (2) | `JumpCutStartPlay`, `RewindStart`, wait until `IsRewinding` is false **and 0.5 s more** (`RewindSafeTime`), then `PlayerTakeHit 999` while `RewindCooldownLeft` > 0 |
| E1 (3) | `JumpCutRestartFromCheckpoint` |
| E1 (4) | boss to 0 health, `PlayerDebugTeleport` to `Marker_Win` |

---

## 11. Open questions for the humans

1. **Freeze Frame is 10 s (the pitch's number) with a 20 s cooldown.** Against goons that is most of a fight. Play it
   and say whether 10 stays.
2. **Rewind cooldown: 6 s.** It decides how deadly the lose rule is (0 health during those 6 s is an instant loss).
   This is the first number to tune by feel.
3. **The grace window at 0 health: 1.5 s** to press Rewind, standing helpless. Too generous, too mean?
4. **The boss's freeze reaches 12 m,** so it is nearly unavoidable and Rewind is the answer (the pitch's "counter").
   Should a quick player be able to run out of the ring instead?
5. **The slide plays back at an even speed and skips time spent standing still.** Once it's playable: should it ease
   in and out, and is about a second right?
6. **Winning restarts the whole level** (back to the title); losing restarts at the checkpoint. OK?

---

## 12. All tuning variables

| Name | Default | Blueprint |
|---|---|---|
| `MaxHealth` | 100 | BP_Player |
| `PunchDamage` | 10 | BP_Player |
| `PunchDamageFinisher` | 20 | BP_Player |
| `PunchRange` | 180 cm | BP_Player |
| `PunchArcDot` | 0.3 | BP_Player |
| `PunchInterval` | 0.25 s | BP_Player |
| `ComboWindow` | 0.9 s | BP_Player |
| `KnockbackLight` | 250 | BP_Player |
| `KnockbackFinisher` | 900 | BP_Player |
| `KnockUpFinisher` | 300 | BP_Player |
| `HitStunLight` | 0.25 s | BP_Player |
| `HitStunFinisher` | 0.8 s | BP_Player |
| `HitFlashTime` | 0.2 s | BP_Player |
| `DownedGraceTime` | 1.5 s (**off**: only used with Rewind) | BP_Player |
| `FallLoseZ` | -1000 cm | BP_Player |
| `HasRewind` | false (**Rewind parked**; was true in this note) | BP_Player |
| `TrailSeconds` | 10 s (**off**: Rewind) | BP_Player |
| `TrailSampleInterval` | 0.1 s (**off**: Rewind) | BP_Player |
| `TrailMinMove` | 5 cm (**off**: Rewind) | BP_Player |
| `RewindSlideTime` | 1.0 s (**off**: Rewind) | BP_Player |
| `RewindSlideMin` | 0.25 s (**off**: Rewind) | BP_Player |
| `RewindCooldown` | 6 s (**off**: Rewind) | BP_Player |
| `RewindSafeTime` | 0.5 s (**off**: Rewind) | BP_Player |
| `FreezeFrameDuration` | 10 s | BP_Player |
| `FreezeFrameCooldown` | 20 s | BP_Player |
| `EnemyMaxHealth` | 100 (goon 40, boss 240) | BP_EnemyBase |
| `EnemyMoveSpeed` | 300 (boss 380) | BP_EnemyBase |
| `EnemyAggroRange` | 0 (goon 1500) | BP_EnemyBase |
| `EnemyAttackRange` | 130 cm | BP_EnemyBase |
| `EnemyHitReach` | 200 cm | BP_EnemyBase |
| `EnemyDamage` | 8 (boss 15) | BP_EnemyBase |
| `EnemyWindup` | 0.45 s (boss 0.7) | BP_EnemyBase |
| `EnemyAttackCooldown` | 1.4 s (boss 1.6) | BP_EnemyBase |
| `EnemyKnockOnPlayer` | 300 | BP_EnemyBase |
| `EnemyKnockTakenScale` | 1.0 (boss 0.25) | BP_EnemyBase |
| `EnemyStunTakenScale` | 1.0 (boss 0) | BP_EnemyBase |
| `EnemyDefeatLinger` | 0.6 s | BP_EnemyBase |
| `GoonCount` | 3 | BP_GoonSpawner |
| `GoonSpacing` | 150 cm | BP_GoonSpawner |
| `BossUsesFreeze` | false (the switch for the six rows below) | BP_BossFreeze |
| `BossFreezeRadius` | 1200 cm (**off**: boss freeze) | BP_BossFreeze |
| `BossFreezeWindup` | 1.2 s (**off**: boss freeze) | BP_BossFreeze |
| `BossFreezeDuration` | 3.0 s (**off**: boss freeze) | BP_BossFreeze |
| `BossFreezeCooldown` | 9 s (**off**: boss freeze) | BP_BossFreeze |
| `BossFirstFreezeDelay` | 4 s (**off**: boss freeze) | BP_BossFreeze |
| `BossFreeHitDamage` | 12 (**off**: boss freeze) | BP_BossFreeze |
| `BossFreeHitInterval` | 0.8 s (**off**: boss freeze) | BP_BossFreeze |
| `BossBrokenStun` | 1.5 s (**off**: only when Rewind breaks his freeze) | BP_BossFreeze |
| `GateOpenHeight` | 450 cm | BP_PlazaGate |
| `GateMoveSpeed` | 900 cm/s | BP_PlazaGate |
| `GatePastDepth` | 120 cm (how far past the gate line counts as "in", C1c) | BP_PlazaGate |
| `GateSafeDepth` | 120 cm (where the guard holds a player who turns back, C1d) | BP_PlazaGate |
| `GateRescueReach` | 400 cm (how far outside the gate line a player is still pulled in, C1d) | BP_PlazaGate |
| `GateRescueHalfWidth` | 600 cm (how far sideways from the gate's centre, C1d) | BP_PlazaGate |
| `MarkerGrantsFreezeFrame` | false (true on the placed `Marker_FreezeFrameGiven` and `Marker_FreezeFrameDoor`) | BP_SceneMarker |
| `TriggerSphere` radius | 300 / 250 / 250 cm | BP_PlazaGate / BP_Checkpoint / BP_SceneMarker (class defaults) |
| `TriggerSphere` radius, placed copies | `Checkpoint_StreetEnd` 550 cm; `Marker_FreezeFrameDoor` 200 cm; `Marker_FreezeFrameGiven` 250 cm | instances in `Lvl_JumpCut` (set by `tools/d1_editor.py`, `tools/e1_editor.py`) |
| `ShowTitleOnStart` | true | BP_JumpCutGameMode |
| `CharLevel` | 0.95 (the cafe script sets 0.55) | `MI_AnimeLook_JumpCut` (post-process on `PP_AnimeLook`) |
| `LineWidth` | 2.0 (the cafe script sets 1.5) | `MI_AnimeLook_JumpCut` |
| `KeyDir` | (-0.579, 0.406, 0.957), towards this level's sun (`Sun_Main`, pitch -45, yaw -35) | `MI_AnimeLook_JumpCut` |

`MI_AnimeLook_JumpCut`'s other parameters were copied from `MI_AnimeLook_Cafe` by `tools/a3_editor.py` (see asset;
the numbers the cafe was built with are in `tools/unreal_make_anime_cafe.py`, the cafe script above).
