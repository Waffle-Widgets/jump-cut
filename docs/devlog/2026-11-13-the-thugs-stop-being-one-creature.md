# 2026-11-13 — The thugs stop being one creature (Justin's Mac mini)

- **What we asked for:** items 2 and 3 of the beats 1-3 clean-up list, after playing with the city in:

  > 2 enemies have zero life to them. Need some more animations to give them personality. 3. Thugs all move
  > together and die together like they aren't separate entities.

- **Prompt(s) we gave the agent:** the two lines above, then "continue" twice (the work was cut off mid-test by a
  usage limit and picked up from what was on disk).

- **What happened:**

  **We read the Blueprints before changing anything, and the report was literally true.** Three things made
  three goons one creature:

  1. `BP_Player.PlayerPunch` damaged **every** enemy inside the punch arc on every punch. Goons standing together
     took the same hits on the same frames, so they flinched together and died together.
  2. `BP_Goon` has no graph and no state of its own. Every goon had the same speed, wind-up, cooldown, health and
     aggro range, woke on the same frame, walked the same straight line at the player and swung on the same frame.
  3. The first animation pass made exactly one montage per job: one punch, one hit react, one death.

  **What changed** (`tools/goon_individual_graphs.py` is the whole recipe, graph text included):

  - Light punches (hits 1 and 2 of the combo) land on the **one** nearest enemy in the arc. The finisher still
    sweeps everybody, which is what a finisher is for.
  - `BP_EnemyBase` gains `EnemyVary`. It is **off by default**, so the cleaver boss, the Stunt Double and his
    stand-ins are untouched, and on for `BP_Goon`. With it on, each goon rolls its own speed, wind-up, health,
    aggro range, stand-off distance, size (0.93 to 1.08) and facing when it spawns.
  - Goons keep apart from each other, circle the player at their own stand-off distance while they wait, and only
    **one** may be winding up at a time (`EnemyMaxAttackers`). The others hold and circle, then take their turn.
  - A goon waiting its turn throws a feint every 4 to 9 seconds (`AM_Human_Charged`) and stands for it.
  - Punches, hit reacts and deaths are picked per hit from lists. A heavy blow gets the heavy react; a blow from
    behind or the side gets the matching react or fall.

  **The animations are Epic's, already in the project.** `tools/unreal_goon_variety_anims.py` wraps 13 clips the
  Third Person template ships and we were not using (six more hit reacts, five more deaths, the charged attack)
  as montages. Nothing was downloaded or generated. They are sourced, not scored; the wrappers and the logic that
  picks them are ours.

  **Three traps on the way.** Three of the graphs silently appended a second copy when written; they compiled and
  would have run everything twice. Counting nodes after each write is what found them. The feint clip has root
  motion switched on in its source, so the goon stands still for 80% of its length rather than being carried
  forward by it. And the work stopped mid-test with a play session left running for 17 minutes; the next session
  found it from the editor log and stopped it before touching a Blueprint.

  **Measured in Play mode, twice** (`tools/goon_individual_test.py`: presses start, stands the player in front of
  the street goons for 12 s, then punches; reads all three goons ten times a second):

  | | Run 1 | Run 2 |
  |---|---|---|
  | Health rolled | 42.5 / 42.6 / 48.4 | 36.8 / 46.3 / 49.3 |
  | Walk speed rolled | 339 / 304 / 314 | 358 / 253 / 344 |
  | Wind-up rolled (s) | 0.49 / 0.52 / 0.59 | 0.61 / 0.42 / 0.48 |
  | Size rolled | 0.959 / 0.997 / 1.010 | 1.037 / 0.997 / 0.933 |
  | Samples with two goons winding up at once | **0 of 169** | **0 of 176** |
  | Feints thrown while waiting | 2 | 2 |
  | Died at (s) | 14.69 / 15.56 / 16.19 | 14.11 / 15.74 / 16.69 |
  | Death clips | Death, Death, Death | Front03, Front02, Front02 |

  Before the change the same test had all three swinging on the same frames and dying on the same punch.
  Punches 1 and 2 moved exactly one goon's health every time; the one finisher that had two goons in its arc hit
  both. Hit reacts varied within a single goon (light, medium, heavy on the finisher). No Blueprint runtime
  errors in the log across both runs.

  **Siblings checked.** `BP_BossFreeze`, `BP_StuntDouble` and `BP_StuntStandIn` all read `EnemyVary = false` with
  empty lists and their own death montage, so they play exactly as before.

- **What we learned:**
  - **"They act as one" can be the attacker's fault.** Half of this bug was in the player's punch, not in the
    enemies. An area hit applied every time makes any group look synchronised however clever each member is.
  - **Variety costs nothing if it is rolled at spawn.** Ten random numbers per goon did more for "separate
    entities" than any of the steering.
  - **One attacker at a time reads as a crew.** It also changes how hard the fight is, and that has not been tuned:
    the test player, who stands still on purpose for 12 s, ended the runs on 20 and 12 health out of 100.
    Tuning is issue #12.
  - **Count nodes after every graph write.** A doubled graph compiles.
  - **Not checked:** nobody has played it. The numbers say they are three different goons; whether they have
    *personality* is a person's call. They also still wear Epic's mannequin; the street goon model is issue #6.

- **Media:** none; the result is the table.
