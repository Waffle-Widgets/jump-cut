# 2026-11-13 — The driver you have to touch (GameStation)

- **What we asked for:** the Team Owner wrote beat 1 out as he sees it, start to finish — the day job, the latte
  art, the crash, the dead driver, the explosion, the quick time event, and both ways it can end. In his words:

  > The player is working his day job taking orders from customers and making latte art. After a latte art
  > minigame and the drink is delivered a car crashes through the wall. The player runs over to see if the driver
  > is ok but the driver is already dead and when the player touches the driver he acquires the first power,
  > Freeze Frame. All of the sudden an explosion goes off, we can play with what sets off the explosion, and
  > that's when the player is taken into a quick time event as a way to show them how to use the new power. Time
  > freezes and the player sees that shrapnel is heading towards their coworker so they rush over to save them. If
  > the player succeeds then they save the coworker and continue with the level. If the player fails the coworker
  > dies and they can still continue the level.

  Beat 1 had been built an hour earlier. Read against this, three parts of it were wrong — not missing, *wrong* —
  and one part of the scene does not exist at all.

- **The power was free, and it should be earned by touching a body.** Freeze Frame was handed over by two
  `BP_SceneMarker` trigger volumes: walk near `Marker_FreezeFrameGiven` beside the crash, or near
  `Marker_FreezeFrameDoor` on the way out, and you had it. Nobody touched anything. Both markers now have
  `MarkerGrantsFreezeFrame` off.

  **`BP_CrashDriver`** replaces them. He is our own `SK_CrashDriver` — the model we generated, rigged and
  imported yesterday — lying beside the car at (-380, 220), pitched −78° so he reads as a body and not a man
  standing in a wreck. No AnimBlueprint, no death clip: `CHARACTERS.md` already said the cheap version of this
  character is "a static mesh with one flicker effect", and a posed skeletal mesh is that, for free.
  `DriverCanTouch` gates on three things — not already touched, player does not already have the power, player
  inside 220 cm — and lights a blue sphere exactly when a touch would land. `DriverTryTouch` grants the power.
  The grey box `C1_Cafe_Driver` that used to stand in for him is deleted.

  **F** reaches him through `BP_Player.PlayerInteract`, which now walks every `BP_CrashDriver` **and** every
  `BP_Coworker` behind one `PlayerCanAct` check. One button, meaning "the thing in front of me".

- **The quick time event did not start itself.** The scene said *"time freezes and the player sees"* — the freeze
  is something that happens **to** the player, not something they are expected to guess. `BP_Coworker` gained
  `CoworkerExplosionStep`: 1.2 s after the power lands the explosion fires, the shrapnel spawns at the car, the
  rescue arms, and `AutoFreezeOnExplosion` calls `FreezeFrameStart` on the player. The player wakes up already
  inside stopped time with 10 s on the clock and a piece of metal hanging in the air.

- **Failing was a do-over, and it should be a death.** The old beat stood her back up 2.5 s after a hit and sent
  a fresh piece of shrapnel. The Team Owner's scene is one attempt: *"the coworker dies and they can still
  continue the level."* `CoworkerDead` now latches, the prompt stays dark, the scene disarms, and nothing in the
  level waits on her.

- **The bug that made all of it look broken, and the reason to write it down.** With everything above built and
  compiling, the auto-freeze did nothing. The graph was right. The class defaults were right. The *placed actor*
  was wrong: `Coworker_Cafe` was carrying `AutoFreezeOnExplosion = false` and `ExplosionDelay = 0`, because the
  instance was placed into the level before those two variables existed, and Unreal had zero-initialised them as
  instance overrides. **A new variable on a Blueprint does not reach an actor that was already placed.** Check the
  instance before you re-read the graph.

  A second trap cost as long: three of the actor packages would not save, silently. Committed `.uasset` files are
  read-only under this repo's LFS `lockable` rule, including the ones under `__ExternalActors__`, and the editor
  reports success either way. `git lfs lock` on each of them first, as `CLAUDE.md` says.

- **What we checked, and how.** Everything through the real `PlayerInteract` path, reading live actor state in
  Play-In-Editor rather than looking at it:

  | Check | Result |
  |---|---|
  | Out of range (439 cm) | prompt dark, nothing granted |
  | In range (117 cm) | prompt lit |
  | Touch | `HasFreezeFrame` true, `DriverTouched` latched |
  | 1.2 s later | `ExplosionDone`, shrapnel at (-470, 0, 185), `RescueArmed` |
  | Auto-freeze | `FreezeFrameActive` true on its own, 7.65 s of 10 s left |
  | Rescue | `RescueDone`, she moves (300, -250) → (300, 70), `RescueTriesUsed` 0 |
  | Freeze allowed to lapse | `CoworkerDead`, `RescueTriesUsed` 1, nothing restarts |

  Two temporary test changes were made and both are reverted and verified reverted: a `DebugAutoTouch` flag on
  `BP_CrashDriver` (removed), and `ShowTitleOnStart` on `BP_JumpCutGameMode` (back to `true`). Both Blueprints
  recompiled with warnings as errors.

- **Something nobody had written down: the game opens on a title screen.** `BP_JumpCutGameMode` starts in flow
  state 0 with `ShowTitleOnStart` true, which calls `PlayerSetInputLocked(true)`. Until the player presses the
  start key, `PlayerCanAct` is false and **F, punch, rewind and freeze all do nothing**. That is correct
  behaviour, but it is not in `FIRST_BUILD_LEDGER.md`, and the first four Play-In-Editor runs here were spent on
  a build that looked dead. Whoever playtests needs to know to press start first.

- **What we did not build.** The **latte art minigame**, taking orders, and delivering the drink. The beat opens
  on the crash. This is the only part of the Team Owner's scene that is not a few hours of work, and it arrives on
  the day of feature freeze — so it is written into `ROADMAP.md` under "Still to decide" as a keep-or-cut call,
  not quietly dropped. Also left open, by his own words: **what sets off the explosion**. It is a 1.2 s timer that
  nothing in the fiction explains.

- **Still true:** nobody has pressed F. Every claim above is the editor reporting its own state, not a person
  playing the game. And she is still a green box — the coworker's model has not been made.
