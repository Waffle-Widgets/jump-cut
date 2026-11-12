# First build ledger (Thursday's slice)

Started Thu Nov 12, 10:45 AM Pacific on GameStation (builder), branch `Gamestation/first-build`, from `main`.
Method from [`INITIAL_PROMPT.md`](INITIAL_PROMPT.md): a lead that plans and keeps this file, one builder subagent per
packet, one checker subagent per packet that never sees the builder's report. Only a checker's pass makes `verified`.

**Scope (Team Owner, Nov 12):** jam-sized, not the large city. This run builds today's checkpoint from
[`ROADMAP.md`](ROADMAP.md): player, fists, goons, Rewind and the Freeze Frame boss, in grey boxes, playable from
start to finish in one small level (a cafe, one street, one plaza). No anime look (undecided, on its own branch),
no art, no sound, no cut scenes (markers only). Splice, Stunt Double and the Director are Friday's, not in this run.

**Everything here is untested by a person.** Nothing reaches `playtest` or `main` until someone has played it.

**Keys (polled in Tick, keyboard and gamepad):** move and look = the template's. Attack = left mouse / gamepad X.
Rewind = Q / left shoulder. Freeze Frame = E / right shoulder. Restart on an end screen = R / gamepad A.

**The level, `Lvl_JumpCut`** (real scale, all grey boxes): the cafe (a 12 x 10 m room with a crashed-car box and a
driver box) opens onto a street about 60 m long with one group of goons and a checkpoint at its end, which leads
into a walled plaza about 30 x 30 m. A gate closes behind the player and the Freeze Frame boss wakes up. Beating
him hands over Freeze Frame, opens the far gate and shows the win screen a few steps beyond it.

| ID | Packet | Kind | Model | Needs | Done means | Status | Notes |
|---|---|---|---|---|---|---|---|
| A1 | Folders, `Lvl_JumpCut` (lit, floor, One File Per Actor), `BP_JumpCutGameMode` | Unreal | Opus | - | (1) `/Game/Game/Maps/Lvl_JumpCut` exists and loads; (2) World Settings: Use External Actors on, game mode override = `BP_JumpCutGameMode`; (3) a capture shows a lit floor and sky, not black; (4) `git status` shows the new files | verified | Built by an Opus builder, checked by a Fable checker (all four pass; pawn stands on the floor in Play mode). Extra: a `VolumetricCloud_Main` actor. The floor has no material yet. Switching on Use External Actors opened a modal window that froze the MCP for 300 s; closed from PowerShell. |
| B1 | `BP_EnemyBase` (health, takes hits, knockback, dies) and `BP_Player` (health 100, three-hit fist combo, hit reaction, keys polled) | Unreal | Opus | A1 | (1) both compile; (2) in Play mode `PlayerTakeHit 30` on the live player leaves health 70; (3) `PlayerPunch` called three times within the combo window next to a placed `BP_EnemyBase` lowers its health three times and the third moves it at least 150 cm away; (4) an enemy at 0 health is destroyed; (5) every tuning number is a named variable | verified | Opus builder, Fable checker: all five pass (100 -> 70 after a 30 hit; punches 100 -> 90 -> 80 -> 60 and the third threw the enemy 590 cm; beaten enemy gone after the 0.6 s linger). Exactly one live `BP_Player_C`. Also made: `M_WarnPunch`, game mode Default Pawn = None, graphs as text in `tools/b1_graphs.py`. Needs a person: punch feel, movement, being pushed. Checker reads leave Blueprints (and the template character) marked unsaved: never save `BP_ThirdPersonCharacter`. |
| B2 | `WBP_HUD`: health bar, one icon per power with its cooldown | Unreal | Sonnet | B1 | (1) compiles; (2) a game-camera capture in Play mode shows the health bar and the Rewind icon; (3) after `PlayerTakeHit 30` a second capture shows a shorter bar; (4) no sentences on screen | todo | |
| B3 | `BP_Goon` (walks up, punches, can be knocked back and beaten) and `BP_GoonSpawner` (places a group) | Unreal | Opus | B1 | (1) both compile; (2) in Play mode a goon 800 cm from the player is within 200 cm of it a few seconds later; (3) left alone next to the player it lowers the player's health; (4) a spawner set to 3 gives 3 live goons; (5) three `PlayerPunch` hits remove a goon | verified | Opus builder, Fable checker: all five pass (goon closed 800 cm to 122 cm in 2.5 s; 8 damage about every 1.85 s; spawner counts 1, 3 and 4 right; three punches 40 -> 30 -> 20 -> 0). Respawn rebuilds the full group. Goons are orange (`M_Goon`). **Found:** in a line of three, the middle goon ends up waiting behind the other two (1 punch against 6 each in 11 s); raising `EnemyAttackRange` from 130 to about 180 would let it swing. Three goons take a standing player from 100 to 0 in 9.4 s. Needs a person: fight feel, whether that is too hard. |
| B4 | Rewind on `BP_Player`: a 10-second trail of position and health; slide back along it in about a second, health restored; cooldown | Unreal | Opus | B1 | (1) compiles; (2) move the live player 1000 cm, wait, call `RewindStart`: it ends within 50 cm of where it stood 10 s earlier (or at its start point if less time has passed); (3) health lost in those 10 s is back; (4) a second `RewindStart` during the cooldown does nothing; (5) the HUD's Rewind icon shows the cooldown | verified | Opus builder, Fable checker: all pass. Teleport test landed 0 cm from the 10-seconds-ago spot, health 50 -> 100; real walking at 600 cm/s landed 25 cm off (samples are up to 60 cm apart at that speed, so worst case is just over the 50 cm bar). Works from the downed grace window and after a fall. Hits ignored during the slide and 0.5 s after. (5) is variables only: no HUD yet. Needs a person: Q / left shoulder, how the slide looks (nothing on screen says "rewinding" yet), the 1.7 cm drop on landing. `write_graph_dsl` once doubled a graph instead of replacing it. |
| C1 | The level: cafe, street, plaza, `BP_PlazaGate` (closes behind, opens on defeat), `BP_Checkpoint`, `BP_SceneMarker`s, the player start and one goon group | Unreal | Sonnet | A1, B3 | (1) a top-down capture shows cafe, street and plaza joined; (2) the player placed in the cafe can be moved along the route with no wall in the way (traces); (3) calling the gate's close and open functions moves it (two captures); (4) touching the checkpoint stores it on the player; (5) markers `Marker_Crash`, `Marker_RewindGiven`, `Marker_FreezeFrameGiven` exist | verified | Sonnet builder, Fable checker: all five pass. The live player walked cafe to win marker in 17 s with nothing in the way; no gaps in the walls; gates block when shut. Extra: `Marker_BossSpot`, a floor slab under the exit run, six flat materials. **Found, fixed in C1b:** the checkpoint can be walked past (5 m trigger in a 10 m street); the floor's material isn't saved to disk; Rewind can slide the player back out through the shut entry gate. **Found, left for a person:** goons walk in straight lines and get stuck on the cafe's front wall, so the cafe is a safe spot. Don't re-run `tools/c1_layout.py` after D1: it re-creates the gates and breaks the boss's links. |
| C1b | Fixes from C1's check: checkpoint trigger as wide as the street; `Floor_Base` material saved; the entry gate closing clears the Rewind trail so Rewind can't leave the plaza | Unreal | Opus (with D1) | C1 | (1) the live player walking along y=330 past the checkpoint stores it; (2) `Floor_Base`'s actor file on disk changed and the material survives a level reload; (3) after the entry gate closes behind the player, `RewindStart` leaves the player inside the plaza | todo | |
| D1 | `BP_BossFreeze` (child of `BP_EnemyBase`): health, a warning before each attack, punches, freezes the player and takes free hits; Rewind breaks the freeze; defeat hands over Freeze Frame and opens the gate | Unreal | Opus | B4, C1 | (1) compiles; (2) his freeze stops the live player moving and a warning is visible before it (capture); (3) `RewindStart` while frozen ends the freeze; (4) at 0 health the player's `HasFreezeFrame` is true and the gate is open | todo | |
| D2 | The player's Freeze Frame: everything else stops for its duration; cooldown; HUD icon | Unreal | Opus | D1 | (1) compiles; (2) without the power, `FreezeFrameStart` does nothing; (3) with it, a live goon does not move while it lasts and the player still can; (4) goons move again afterwards; (5) the HUD shows its icon and cooldown | todo | |
| E1 | `WBP_Title`, `WBP_Win`, `WBP_Lose`; you lose at 0 health with Rewind on cooldown; restart at the last checkpoint; input mode back to "game only"; the game starts in `Lvl_JumpCut` | Unreal | Sonnet | D2 | (1) all compile; (2) health 0 with Rewind on cooldown shows the lose screen (capture); (3) restart puts the player at the stored checkpoint with full health; (4) beating the boss and reaching the end shows the win screen (capture); (5) `GameDefaultMap` and `EditorStartupMap` point at `Lvl_JumpCut` | todo | |
| E2 | Run-through: cafe to win screen by calling the player's functions and moving it marker to marker | Unreal | Fable | E1 | (1) every step in play order works without a person; (2) both gates behave; (3) the list of what a person must still play is written | todo | |
| F | Final audit by a fresh subagent: this ledger and the scope above, line by line, against what is in the project | outside | Fable | E2 | Every line of the scope has a verified packet behind it, or is listed as missing | todo | |

## Notes for checkers (from the design note, [`FIRST_BUILD_DESIGN.md`](FIRST_BUILD_DESIGN.md))
- `PlayerPunch` only hits what is in front: face the player at the enemy first (`PlayerDebugTeleport` takes a yaw).
- A beaten enemy is destroyed 0.6 s later, not at once, so the knockback can be seen.
- Measure Rewind only after `IsRewinding` is false again. Hits are ignored during the slide and for 0.5 s after.
- Gates report open at once but the mesh takes about half a second to slide: capture after that.
- At 0 health with Rewind ready there is a 1.5 s grace window before the lose screen. That is the design, not a bug.
- "The player can / can't move" can't be proven without keys. Check the variables; a person plays the rest.
- The win marker is only guarded by the exit gate: the run-through (E2) must go through the boss, not teleport past him.
- There must be exactly one live `BP_Player_C`, placed in the level with auto-possess, and the game mode must keep
  the template's player controller.

## Cut order if we fall behind
From the bottom up: the title screen (keep win and lose), the player's own Freeze Frame (D2; keep the boss), the
HUD's cooldown display, goon spawner (place goons by hand).

## Tuning variables
Filled in as packets are verified: name, default, which Blueprint.
