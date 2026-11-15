# 2026-11-15 — The game stops being silent: 17 sounds wired to their events (Justin's Mac mini)

**Nobody has heard these yet.** Everything below was checked by a script in Play mode, which can prove a sound
node runs on the right event and only once. It cannot tell whether a sound is too loud, too quiet, late,
or just wrong. Justin listens first.

- **What we asked for:** an hour earlier, a read-only check found that 17 of the 24 `SFX_*` sounds in the
  project had **zero referencers**: imported on Nov 14 (#52), wired to nothing. Punches, goon hits, the car
  crash, the explosion, the checkpoint, the gate, and the title, win and lose stings were all silent. Justin
  approved wiring all of them, then said to finish and merge.
- **Prompt(s) we gave the agent:** *"Don't worry about the other stations. Complete the work fully then merge
  to main"* (Justin, 9:56 AM Pacific), after the project assistant's brief listed what each sound is for and
  the rules: one sound per event, never per frame; new switches correct at false; name every pin.

## What happened

**The first attempt was stopped by the Mac itself.** Locking the eight Blueprints (`git lfs lock`) was refused
by the agent's permission check, because the go-ahead had arrived through another chat, not from Justin. The
agent stopped, saved nothing, and asked. Justin answered in his own words, and the locks then went through. That
is the guard working as intended, at the cost of eight minutes.

**Splicing, not rewriting.** Every past sound and effect in this project went in through `write_graph_dsl`,
which replaces a whole function. CLAUDE.md lists five ways that goes wrong silently: orphaned old nodes,
positional arguments landing in `self`, and so on. `PlayerPunch` alone has 79 nodes, of which only 21 are
reachable from its entry, and the reader prints its loop element in a form the writer rejects. So this time
nothing existing was rewritten. Each sound is **one new node spliced into the existing wire**: find the node
it goes after, break that one exec link, connect old -> new -> old target. Where a sound needed a decision
(which punch hit, has the crash already played), the decision went into a **new, tiny function** written from
scratch, and only the call to it was spliced in. Node counts before and after match exactly what was added
(`PlayerPunch` 79 -> 83, four calls), and every touched function has **0** dead `PlaySound2D` nodes.

| Sound | Where | What keeps it to once |
|---|---|---|
| PunchWhoosh | `BP_Player.PlayerPunch` -> new `PlayerPunchSoundStart`, after the punch montage | inside the existing `PlayerCanAct` branch |
| PunchHit1/2/3 | new `PlayerPunchSoundLanded`, before `PlayerSmashProps` | one per punch, picked by combo step; a new `PunchLanded` bool (default false) is set by new `PlayerPunchMarkLanded` after either `EnemyTakeHit`, so a finisher that hits three goons still plays one Hit3 |
| PlayerHit | `BP_Player.PlayerTakeHit`, after the hit flash | inside the existing guard (rewinding, downed, lost, won, safe time) |
| FreezeFrameOn | `BP_Player.FreezeFrameStart`, after `FreezeFrameActive = true` | inside both existing gates; a second call in the same frame is refused (tested) |
| GoonHit | `BP_EnemyBase.EnemyTakeHit`, after the hit-react montage | only in the survives branch, never the stand-in redirect branch |
| GoonDown | `BP_EnemyBase.EnemyDefeatedHook` (was empty) | called once, on the hit that defeats |
| BossDown | `BP_BossFreeze.BossHandOverPower` | his own defeat hook overrides the base one, so he never also plays GoonDown |
| CleaverSwing | `BP_BossFreeze.BossThinkFreeHits` after his punch, and `BossThinkFight` around `EnemyChasePunchStep` | the base chase step is shared with goons, so the boss checks the edge itself: new `BossWasWindingUp` (default false) is stored before the step and new `BossCleaverCheck` plays only when the wind-up ended inside it |
| CarCrash | `BP_OpeningDirector.CineDirectorStep` -> new `CineCrashSoundStep`, after the clock update | new `CineCrashSounded` (default false); starts **0.33 s before** `CineImpactTime` (6.2 s), because the file is a third of a second of engine before the impact |
| Explosion | `BP_OpeningDirector.CineExplBegin`, right after `CineExplFire` | `CineRescueRun` only calls it while the coworker is not yet `Blown`, and the call itself ends the rescue cine |
| Checkpoint | `BP_Checkpoint.CheckpointTickStep`, after `CheckpointTaken = true` | the existing `CheckpointTaken` flag; it is never cleared, so no replay on respawn |
| GateOpen | `BP_PlazaGate.PlazaGateOpen` and `PlazaGateOpenForGood` -> new `GateOpenSoundCheck` | plays only if the gate was closed; a reset that reopens it after a death is silent on purpose |
| WinSting / LoseSting | `BP_JumpCutGameMode.JumpCutShowWin` / `JumpCutShowLose` | both are reached once per win or loss (they change `FlowState`, so the next tick leaves the play step) |
| TitleSting | `BP_JumpCutGameMode.JumpCutFlowSetup` -> new `JumpCutTitleSound` | `FlowSetup` runs once at BeginPlay; plays only when `ShowTitleOnStart` is true |

The real ending was traced, not assumed: `CineOutroWin` -> `PlayerReachWin` -> `HasWon` -> the game mode's
play step -> `JumpCutShowWin`. So the win sting is on the path the demo actually takes.

## The test, by script in Play mode

`ShowTitleOnStart` was switched off on the game mode for the run and put back to **true** afterwards (read
back true). Each step called the real Blueprint function on the live actor and read the state on either side.

- **Opening, in real time:** the clock passed impact (6.2 s), `CineCrashSounded` went true, `CineDone` true,
  objective advanced to 1.
- **Punch at nothing:** `PunchLanded` false, combo 0 -> 1.
- **Three punches into the boss:** health 240 -> 230 -> 210 (finisher) -> 200; `PunchLanded` true each time; the
  combo went 2 -> 0 -> 1 exactly as before.
- **Player takes 5:** 100 -> 95. **Freeze Frame:** active after the first call; a second call in the same frame
  was refused by the existing gate.
- **A goon:** hit for 1 (48.4 -> 47.4, still standing), then killed (defeated true).
- **The boss:** killed; the player got Splice; his exit gate went closed -> open, locked open.
- **Checkpoint:** taken, respawn point moved to (6300, 0, 0); a second call changed nothing.
- **Gate:** close -> open -> open again (the second open does not replay the sound).
- **Lose:** `IsLost` true, and on the next frame the game mode showed the lose screen (`FlowState` 2).
  **Restart from checkpoint**, then **the ending** -> `HasWon`, and on the next frame the win screen
  (`FlowState` 3).
- **Explosion:** `CineExplBegin` ran; the explosion cine started.
- **Title:** with the title on, `FlowState` 0 at start.
- No Blueprint compile errors, and no runtime errors or warnings about these Blueprints or sounds in the log.
  The one audio line was `LogAudioMixerAudioUnit: Warning: Error querying Sample Rate` from the Mac's audio
  device at PIE start, which is not about any asset.

## What is not tested

- **Hearing any of it.** Volume, mix, timing against the animation, and whether the crash lines up with the car
  on screen. All 17 play at volume 1.0, 2D (not positioned in the world).
- **A real key press.** Punches and Freeze Frame were driven by calling the functions the keys call.
- **A Windows build.**

## Found on the way (not changed)

- **The opening cinematic runs behind the title screen.** With the title on, the director's clock was already
  at 2.35 s while the title was still up. So if a player waits on the title, the car crash (and now its sound)
  happens behind it. That was already true before this change; it is a design question for Justin.
- **Every surviving hit on the boss plays GoonHit**, because he shares the base hit code. There is no separate
  boss-hit sound.
- **`BP_StuntDouble` overrides the defeat hook and is placed nowhere**, so it is silent on defeat. It is unused.

## What we learned

- **Splice a node in rather than rewrite the function.** `create_node` + `break_pins` + `connect_pins` changes
  exactly one wire and leaves every pin we did not touch alone. It avoids every `write_graph_dsl` round-trip
  trap at once, and the node count proves it: +1 per sound, 0 orphans.
- **"Once" has to be found per event.** Half of these were already once (the gates, the checkpoint flag,
  `FlowState`). Two needed a new bool (crash, cleaver), one needed a flag carried across a loop (punch hit),
  and the crash needed one because its branch runs every frame for five seconds.
