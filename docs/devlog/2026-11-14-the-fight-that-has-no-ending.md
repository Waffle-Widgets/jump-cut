# 2026-11-14 — Beat 5: the fight that has no ending (Justin's Mac mini)

- **What we asked for:** the Team Owner had just looked at the newly imported city and moved on to the next
  beat, then added a second instruction a few minutes later.

- **Prompt(s) we gave the agent:** the actual words, quoted:

  > Alright city assets are looking good so far. Will need some cleanup, but for now let's get beat 5 started

  and, mid-turn:

  > Also, some github issues were made from the roadmap. Lets check them off if we are covering them.

- **What happened.**

  **The editor was running and could not be reached.** Unreal was open on this Mac with `Lvl_JumpCut`
  loaded — the Team Owner had been in Play mode two minutes earlier, which is where "city assets are looking
  good" came from — but every Unreal tool was dead. The reason was one line in the editor log at startup:

  ```
  LogModelContextProtocol: Starting MCP server on port 8000 (override with -ModelContextProtocolPort=N).
  LogHttpListener: Error: HttpListener unable to bind to 127.0.0.1:8000
  ```

  The previous editor process was still holding port 8000 as this one came up, so the MCP server never
  bound. Nothing holds the port now — it is free — but the server is started **once, at launch**, and the
  plugin exposes no console command to retry it, so only a restart brings it back. A restart does not help
  this chat either: MCP servers are read when a session starts, so a server that failed at startup cannot be
  attached to a running chat. `CmdLinkServer`, which would have let us push console commands in without MCP,
  is `"PlatformAllowList": ["Win64"]` and does not exist on Mac. **So no part of beat 5 reached Unreal.**

  **That turned the turn into maker work, and the maker work found the real problem.** `BP_StuntDouble`'s
  variables were never written into `docs/FIRST_BUILD_DESIGN.md` — the fight was built straight into the
  editor on GameStation — so instead of guessing, we read the name tables out of the committed assets with
  `strings`. A `.uasset` carries every variable and function name it defines, and all 469 LFS objects are
  materialised on this clone, so this is a real structural check and not an inference:

  | asset | has `BossExitGate` | has `PlazaGateOpenForGood` |
  |---|---|---|
  | `BP_BossFreeze.uasset` | yes | yes |
  | `BP_EnemyBase.uasset` | no | no |
  | `BP_StuntDouble.uasset` | no | no, and no `BP_PlazaGate` reference at all |

  **Beat 5 cannot be finished.** The cleaver boss opens the plaza's exit gate when he dies, through
  `EnemyDefeatedHook -> BossExitGate.PlazaGateOpenForGood`, and that wiring is on `BP_BossFreeze`.
  `BP_StuntDouble` is a `BP_EnemyBase` child, so it inherits none of it. Kill the Stunt Double and nothing
  opens, nothing is handed over, and the level stands there.

  **Why nobody saw it.** His fight was signed off on 2026-11-13 with real numbers — boss 300 → 300 with the
  crew up, 300 → 290 with Freeze Frame on, a stand-in 45 → 35 and moved onto the attack line. Every one of
  those came from calling the real functions and reading the result, and that is the kind of check that
  passes perfectly while the beat it belongs to has no way to end. It is the same shape as the bug a day
  earlier where every platform rendered exactly where it was put and sat 74 cm too low.

  **A third thing, smaller and already live:** `tools/beat4_platforming.py` parked `Marker_Win` at
  (14400, 0, 0) — the middle of beat 5's landing pad — and said in its own header that it would have to move
  again once beat 5 was placed. It has not moved. So **today the demo is won by walking onto beat 5's arena**,
  before the boss is awake.

  **What we built instead of Blueprints: two recipe scripts.** This is the pattern that saved Splice when an
  editor quit with it dirty, so it is not a consolation prize.

  `tools/beat5_arena.py` places the arena, in the same shape as `beat4_platforming.py` — only ever touching
  actors tagged `JC_Beat5`, idempotent, with `clear` and `report` modes, and it never saves. `Gate_Beat5Entry`
  at x 13800, open and closing behind the player, with `GateEnemyToWake` pointed at the boss exactly as
  `Gate_PlazaEntry` is for the cleaver boss; `Boss_StuntDouble` at x 14300 facing west; `Gate_Beat5Exit` at
  x 14650, closed; `Marker_Win` moved east of it to x 14720.

  One measurement worth keeping: the entry gate goes on the pad's **west lip**, not further in.
  `BP_PlazaGate`'s opening is 5 m wide and the pad is 15 m, so a gate anywhere on the pad can be walked
  around — but at the lip the only way in is gap 3's single 500 cm slab along y = 0, so 5 m seals it.

  And one number the script deliberately refuses to guess: `BP_SceneMarker` has no `MarkerRadius` variable,
  because the trigger is a component — `c1_layout.py`'s own header records that `Marker_FreezeFrameDoor`'s
  radius 200 was set per-instance by `d1_editor.py`. If `Marker_Win`'s sphere is 200 cm, a marker at 14720
  reaches back to 14520, **west** of the closed exit gate at 14650, and the player wins through it. `report`
  prints the radius it finds and says so.

  `tools/beat5_graphs.py` is the Blueprint recipe: `FighterIdleTimeout` / `FighterIdleLeft` plus a
  `BossTickFighter` function, and the `BossExitGate` variable with the `EnemyDefeatedHook` line that opens it.

- **The one real design decision: the despawn timer goes on the boss, not on the stand-in.** Issue #9 is
  written about the attack stand-in, so the obvious home is `BP_StuntStandIn`. That would have been wrong,
  and quietly:

  1. The **soak** doubles are `BP_StuntStandIn` too, with `StandInFights` false, and they stand still with
     nothing in range to attack **by design** — which is the exact condition the timer fires on. A timer on
     the stand-in would delete the boss's entire damage shield a few seconds into every fight. That is the
     opposite of the fight the Team Owner described, and it would look like the soak "not working" rather
     than like a despawn.
  2. The boss owns `FighterRef` and allows at most one fighter alive. A stand-in that destroyed itself would
     leave that reference dangling and the boss would never tag another one in — so the despawn would end the
     bodyguard trick for the rest of the fight instead of recycling it.

  Scoped to the boss's `FighterRef` it cannot touch the soak crew, and `FighterRef` stays consistent. It also
  makes the recorded intent true: *"running away from the bodyguard a real option rather than a stall."*

  He hands over **no power** on death, deliberately — whether the player ever gets Stunt Double is still open
  (issue #21), and this change opens the gate and nothing else.

- **We also brought the play list up to date, which was its own small disaster.** Issue #28 asked for the
  title-screen input lock to be written down. Reading the list to add it showed three of its twelve steps
  were describing a build that no longer exists: step 2 still said to walk to a cyan ball to get Freeze
  Frame, and step 3 said you get the power at the cafe door anyway — both of those markers were switched
  off when the crash driver became the only source of the power, and **F**, bullet time, the countdown, the
  coworker rescue, the city and Splice were in the list nowhere at all. A tester following it would have
  reported beat 1 as broken. It is now 18 steps in play order with the five controls stated once at the top,
  and `docs/PLAYTEST.md` has a "press R first, or it looks broken" section with the control table.

- **What we checked ourselves, and what is worth nothing yet.** The three asset findings are structural and
  repeatable (`strings <asset> | grep BossExitGate`). The port-8000 diagnosis is from the editor's own log.
  Everything else here is **text**: not one line of the two recipes has been compiled or run, and
  `beat5_graphs.py` says so at the top rather than reading like `splice_graphs.py`, which was a transcript of
  work that had actually been measured. The ids most likely to be wrong are flagged in the file, including
  the one that matters — calling `EnemyDistToPlayer` on *another* actor, where a positional argument lands in
  the `self` pin and silently measures the boss's own distance instead of the fighter's, compiles cleanly, and
  looks plausible in play.

- **What we learned.**
  - **A beat can be verified mechanic by mechanic and still have no way to end.** Every check on the Stunt
    Double fight was a function call and a health readback, and none of them could have noticed that killing
    him does nothing. Ask "how does this beat finish?" as its own question.
  - **A `.uasset` will tell you its own variable names.** `strings` over the committed asset is a real
    structural check when the editor is unreachable, and it is how all three of today's findings were found.
    It settled in seconds what a design doc had never recorded.
  - **A script that moves a shared actor and says "this will need moving again" is a bug with a timer on it.**
    `beat4_platforming.py` was honest about `Marker_Win` in its header, and the header is not where anyone was
    going to read it. The note belonged in `ROADMAP.md`.
  - **Two Unreal editors on one machine cost the whole turn.** Port 8000 is bound once at launch; if the old
    process still holds it, the new editor comes up looking completely normal and completely unreachable.
    Check the log for `unable to bind` before assuming the plugin or the config is wrong.
