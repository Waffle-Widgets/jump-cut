# First build: final audit (unedited)

_Written by a fresh Fable subagent that saw none of the run, Thu Nov 12 evening, against commit `5b6fd55`. The lead has not edited it. What was done about each finding is in `FIRST_BUILD_LEDGER.md`, row F._

# Final audit: `Gamestation/first-build` at `5b6fd55` (Thu Nov 12, evening)

Read-only audit: nothing was edited, no Unreal MCP calls, no state-changing git. I cannot open `.uasset` files, so everything about what is inside a Blueprint, widget or map rests on the graph-text files in `tools/` and commit stats. Those items are marked "editor only".

**Numbers:** 17 ledger rows: 14 `verified`, 1 `smaller` (A3), 2 `todo` (A3b, F). 22 commits in `main..HEAD` (3 are merges, 1 is the anime branch's, 1 is M Station's). 9 Blueprints, 4 widgets, 11 new materials, 1 map. **No person has played any of it.**

---

## A. Ledger against scope

1. **The anime look is not "ready", and the newest entry says it is.** The owner asked: "make sure we have that ready for when we need it".
   - A3 is `smaller`, with done-means (1) failed (`FIRST_BUILD_LEDGER.md:41`).
   - Its fix, A3b, is `todo` with empty Notes (`:42`).
   - `Lvl_Cafe`'s hero blend space `BS_Idle_Walk_Run_CW` points at 17 `*_CW1` animations that do not exist (editor only; taken from the ledger and `FIRST_BUILD_MCP_TIPS.md`, last bullet).
   - A3 checked the shader on template mannequins only. It was never checked on a character using the anime materials (`M_AnimeChar`), which is what M Station's models will arrive with (inferred).
   - `docs/devlog/2026-11-12-freeze-frame-first-rewind-parked-first-full-run.md` says "**The anime look is ready.**" and "A3, not started". The first is contradicted by A3's check; the second is stale.
   - Fix: build and check A3b, test the look on one imported character, and correct this in a new devlog entry.

2. **The branch is not on the latest `main`.** `git log HEAD..origin/main` shows 3 commits the branch lacks: `75b98e7` (three rigged characters and a cleaver, FBX and textures under `Art/Blender/export/Characters/` and `Art/Meshy/`), `bbc02d9` (art style decided), `31d400a`.
   - They touch `CLAUDE.md`, `ROADMAP.md`, `CHARACTERS.md` and `PREJAM.md`.
   - The 3D assets the anime look is meant to be ready for are therefore not on this branch.
   - Local `main` is 4 behind `origin/main` (`git status -sb` / `git branch -vv`), and this is as of the last fetch; I did not fetch.
   - Fix: fetch, merge `origin/main`, and resolve `ROADMAP.md` by hand (both sides edited "Still to decide" and Decisions).

3. **E2 is `verified` with no independent checker.** `:43`: "Done by E1's Fable checker". The same agent did the run-through and passed it. Only a different checker's pass makes `verified`. Fix: say so in the row, or have a second agent re-run it.

4. **Three `verified` packets have a done-means line that was reinterpreted or not met as written.**
   - B4 (5), "the HUD's Rewind icon shows the cooldown": Notes say "(5) is variables only: no HUD yet" (`:32`).
   - D2 (5), "the HUD shows its icon and cooldown": the same (`:38`). B2's later check did see both icons, but neither row was updated.
   - E1 (2), "health 0 with Rewind on cooldown shows the lose screen": impossible as written once G1 set `HasRewind` false. The row still says "all five pass" and the packet title still reads "you lose at 0 health with Rewind on cooldown" (`:40`).
   - Fix: reword each line to what was actually checked and say it changed.

5. **A3's status is `smaller`, but nothing was made smaller.** A check failed and the fix was split into A3b. The Notes do say why. The honest state is "(1) failed, A3b todo". Fix: a status word is a team call; do not let `smaller` read as "done".

6. **Asked for, with no packet at all:**
   - "We want to showcase the most fun abilities first… innovative mechanics would get us huge points." No packet addresses making Freeze Frame fun or visible. The ledger itself says "Nothing on screen shows the world is stopped" (D2) and that Freeze Frame "makes both [fights] trivial" (`:75`).
   - The 3-5 minute length (`CLAUDE.md` scope guardrails; the owner's "1 level 3-5 minutes"). The scripted run takes 25-27 s (`:72`). This is disclosed under "For the team to tune" but has no packet.
   - Thursday's checkpoint, "core loop playable start to finish", is met by script only.

7. **Work with no ledger row.**
   - The design note (INITIAL_PROMPT's A2) was written by "a design subagent" (kickoff devlog) and committed inside A1's commit `72490ba`. It has no row and no checker. IDs jump A1 to A3.
   - The devlog entries have no rows either.
   - Fix: add an A2 row saying it was unchecked.

8. **Stale lines in the ledger's own text.**
   - `:9`: "No anime look (undecided, on its own branch)".
   - `:23-24`: "the Freeze Frame boss wakes up. Beating him hands over Freeze Frame".
   - `:51`: "At 0 health with Rewind ready there is a 1.5 s grace window… That is the design".
   - C1 (5) names `Marker_RewindGiven` and a plaza `Marker_FreezeFrameGiven`; G1 renamed both.
   - `:76` states "Enemies beaten during a Freeze Frame… block the lane" as fact; the tips file says "inferred, not measured".

9. **Fine:** every "Found, fixed in X" points at a verified packet (C1b, C1c, C1d, G1) except A3 to A3b (todo). No packet is `failed`. No row was dropped. F is `todo` and is this audit.

10. **Not asked today and absent:** a packaged build (INITIAL_PROMPT E3; Friday in ROADMAP), Splice, Stunt Double, the Director, sound, art.

---

## B. Ledger against the repository

1. **Parts of verified packets exist only in the level files and in gitignored scripts.**
   - C1b's checkpoint radius of 550, D1's boss placement and gate links, G1's door-marker radius of 200 and GiftMesh fixes, and all of A3's editor steps live in `JumpCut/Saved/d1_editor.py`, `e1_editor.py`, `a3_editor.py`, `a3_pie.py`. `Saved/` is ignored (`git status --ignored`).
   - `tools/c1_layout.py`, re-run, re-creates the checkpoint at the Blueprint's default radius (250) and the gates without links. The ledger warns about the gates only.
   - Fix: move those scripts into `tools/`, or add a "never re-run `c1_layout.py`" line that also names the checkpoint and the door marker.

2. **A3 has no committed script or graph text.** `5b6fd55` changes `BP_Player`, `BP_EnemyBase`, `BP_BossFreeze`, the map, two actor files and `MI_AnimeLook_JumpCut`, with nothing in `tools/`. Fix: commit `a3_editor.py`.

3. **Graph-text files:** `b1`, `b2` (+C1d), `b3`, `b4`, `c1`, `d1` (+C1b), `d2` (+C1c), `e1` (+G1) all exist. There is no `g1_graphs.py` or A3 file; G1 is inside `e1_graphs.py` and its header says so.

4. **Every verified packet has a commit holding the assets its Notes name.** Checked with `git show --stat`:
   - A1 `72490ba`, B1 `6adb3a6`, B4 `279a6d6`, B3 `981bfb3`.
   - C1 `62b53f8` (3 Blueprints, 6 materials, 30 actor files).
   - D1 + C1b `65d1358`, D2 + C1c `70f931a`, B2 + C1d `3581980`.
   - G1 + E1 + E2 `95e6894` (3 widgets, ini), A3 `5b6fd55`.
   - Whether the contents match the Notes is editor only.

5. **Commit hygiene.**
   - All commits are by `mendezm87`.
   - All carry the co-author line except merge `d56531e`, which has the default message "Merge commit '3581980…' into HEAD" and no co-author line.
   - Every commit carrying Unreal work starts `Untested:`, apart from the three merges, which carry `.uasset` files and are not prefixed.
   - `4cd2803` and `d07c440` are docs-only and unprefixed, which is fine.

6. **The token was never committed.** `git log --all -S'AndroidFileServerRuntimeSettings' -- JumpCut/Config/DefaultEngine.ini` returns nothing. `SecurityToken` appears in history only in docs commits (`00daa2e`, `f113c96`) and one devlog line. The block with `SecurityToken=8B85…` sits uncommitted in the working tree (`git diff`). Fix: discard that hunk before any `git add -A`; Unreal will keep re-adding it.

7. **Working tree:** clean apart from that one ini hunk. No tracked files under `Saved/`. No raw sources tracked under `Imported/` (only `.uasset`). `E1`'s "three lines" in `DefaultEngine.ini` matches the diff in `95e6894`.

8. **The kickoff devlog's `.git/info/exclude` claim is no longer true.** It says 11 leftover anime files were hidden there; the file now holds only the default comments. Harmless now that the branch is merged.

---

## C. The owner's latest decisions against the files

**What holds**
- **Rewind kept, switched off.** `tools/e1_graphs.py:6-7`: class default `HasRewind = false`, "no graph changed". `b4_graphs.py` is intact. The HUD still contains `RewindBox`, the "Q" letter and `RewindTint`, collapsed while `HasRewind` is false (`b2_graphs.py:131`). Whether the asset matches is editor only.
- **Freeze Frame first, from the driver, and losing at 0 health:** G1 is verified by its checker.
- **Anime branch merged:** `1591f3a`; `git branch --merged` lists `mendezm87/anime-look`. Its assets, three scripts, devlog entry (own file) and credits rows are on the branch. The branch still exists on origin.

**Stale or contradictory sentences**
1. `PITCH.md:9-11`: "Which trick is the core is open… either Rewind is the power the worker already has at the cafe, or Freeze Frame is the core and Rewind is cut." This contradicts `ROADMAP.md:94` (Rewind moves to a later boss).
2. `PITCH.md:37-39`: "Rewind… the worker's own power from the start, or cut." Same contradiction. The power table has no Rewind row, and `:5` says "three more" powers.
3. `ROADMAP.md:34-35`: "Still to come on that branch today: Freeze Frame handed over in the cafe, win/lose screens and restart, the cel shader on the level, and a start-to-finish run-through". All four are committed. The heading still says "late afternoon".
4. `ROADMAP.md:43`: Friday still lists "win/lose and restart screens" (built today, unplayed).
5. `ROADMAP.md:85`: cut list item 5, "already cut: only the player rewinds", reads oddly now that Rewind is parked.
6. `FIRST_BUILD_DESIGN.md`:
   - `:176`: `HasRewind | bool | true`.
   - Section 5.1 (`:430`, `:479`): "the answer is Rewind", "Rewind is the only thing that works".
   - `:462`: the boss's defeat grants Freeze Frame.
   - Section 6 (`:514-519`): the Rewind-based lose rule and downed window. The As-built paragraph at `:654` corrects it, 140 lines later.
   - `:605-606`: the old marker names.
   - Section 10: E1 (2) checked via `RewindStart`.
   - Section 11, questions 2 to 4: all Rewind questions.
   - Section 7: checkpoint radius 250, while the placed copy is 550.
   - It has no As-built text for C1b or A3 at all (grep for `A3`, `C1b`, `anime`, `550` returns nothing).
7. `INITIAL_PROMPT.md:3`: the status is dated 10:45 AM and does not mention the afternoon decision. `:66-68` still says of Rewind "Do not build it" (kept "as written" on purpose, but nothing says it is superseded).
8. `CHARACTERS.md:13,42`: speaks of the look as living on `mendezm87/anime-look`.
9. `CLAUDE.md`, "The current game", only points at the pitch, so it inherits items 1 and 2. On `origin/main` `CLAUDE.md` has 17 new lines this branch lacks.
10. The art-style Decision exists twice, worded differently: `ROADMAP.md:97` here (Team Owner) and on `origin/main` (Manny). This will conflict on merge.
11. **The plaza boss has no place in the current design.** The pitch's first fighting boss is the Splice mob boss. `BP_BossFreeze` is now a big goon with `BossUsesFreeze` false, in a Blueprint named for a power he does not use. This needs a team decision, not a doc fix.

---

## D. The "done" list and reporting rules

1. **Nothing is pushed, and no teammate can see that.** `Gamestation/first-build` has no upstream (`git branch -vv`). `ROADMAP.md`'s "Where we are" names the branch without saying it is local-only, and that text is itself unpushed. The newest devlog entry's own lesson is "Push a build branch early, even when it is untested". Fix: push the branch (untested branches are allowed) once the owner says so.

2. **A3 has no devlog entry.** `first-build-a3-anime-boss.png` and `first-build-a3-anime-street.png` are linked from nowhere. Fix: one new entry (A3, the `_CW1` failure, the correction to "ready").

3. **Devlog entries are not in the same commit as their change** (done-list rule 3). Each sits in a separate commit minutes later (`0619dcd`, `10dc2d1`, `2a9dc30`, `0d9c94b`). D2's check (39 sessions) is barely narrated.

4. **Devlog content is otherwise sound.** One file per entry, template followed, the owner's four prompts quoted exactly, failures included. Every image link in every entry resolves. Small errors:
   - The Freeze Frame caption says "two orange goons walking"; the picture shows three, and they are stopped.
   - The kickoff entry says "eleven packets"; there are now 17 (true when written).

5. **`ROADMAP.md` "Where we are" is not true as of the last commit** (C3).

6. **LFS locks.** `git lfs locks` shows 2 held: `BP_JumpCutGameMode.uasset` and `BP_PlazaGate.uasset`. No other new asset is locked, and no doc says whether that was deliberate. With the branch unpushed, the two held locks block nobody but protect nothing either. Fix: decide and write one line; release both at hand-off.

7. **`CREDITS.md`.** It covers the template mannequin (used for player, goons and boss), the retargeted animations and the Gemini/Tripo hero. The first build added nothing sourced (inferred from commit stats: Blueprints, flat materials and widgets only; the engine's basic shapes are engine content). The "AI tools used" list omits Unreal Engine 5.8 and Epic's Unreal MCP, which `PREJAM.md`'s own checklist says go in "Tools you used".

8. **`PREJAM.md`.** The new `tools/b1…e1_graphs.py` and `c1_*.py` are correctly not listed as pre-jam. They are also missing from the "Made during the jam" table, which the file's own checklist asks for, along with the ledger, design note and tips file.

9. **Jam rules.**
   - "Final Cut" appears only in docs: `PITCH.md:16,35,43`, `ROADMAP.md:77`, `INITIAL_PROMPT.md:71,74` and three devlog entries. It is in no asset name and no graph text.
   - Player-facing text is "JUMP CUT", "CUT!", "THAT'S A WRAP", "R / (A)", "Q", "E": English, no trademark (widget contents are editor only).
   - The devlog folder is public and is the Glass Box submission, so the trademark name is visible to judges there as discussion, not as game content.
   - No pre-jam gameplay was brought in by this run.
   - Already declared in `PREJAM.md`: the anime look, cafe and hero were authored in the practice project during the jam and migrated in as one commit, `c19e0ad`. That is now part of the build.

---

## E. The method

1. **Builder and checker were separate on every row except E2** (A3). Builders were Opus or Sonnet and checkers Fable, per the Notes. I can only confirm this from the Notes; there is no transcript in the repo.
2. **Combined packets, disclosed only in the Model column:** C1b with D1, C1c with D2, C1d with B2, G1 with E1. One builder built two packets each time, and apparently one checker checked each pair (inferred). The prompt says one builder per packet. G1+E1+E2 share one commit.
3. **Model changes are not explained.** B2 and E1 are listed as Sonnet and were built by Opus. No Note says whether that was a retry after a failed check.
4. **No fail-and-retry history is recorded anywhere.** No packet is shown failing even once, so "did any fail twice" cannot be answered from the books.
5. **The lead did not build:** every commit touching `.uasset` files maps to a packet row. The lead's own commits are docs, the ledger and merges. The design note is the unrowed exception (A7).
6. **Final-report material.**
   - Present: the play list (`:57-69`, 12 steps with keys, in play order), "For the team to tune", the cut order.
   - Still a placeholder: "## Tuning variables" at `:83-84` ("Filled in as packets are verified").
   - The design note's section 12 is the real table, but it omits `GatePastDepth`, `GateSafeDepth`, `GateRescueReach`, `GateRescueHalfWidth`, `BossUsesFreeze`, `MarkerGrantsFreezeFrame`, the per-instance radii (550, 200) and every `MI_AnimeLook_JumpCut` parameter. It lists Rewind and boss-freeze numbers without saying they are switched off.
   - Absent: a list of assumptions, and the asked/built/left-out summary with counts.

---

## F. What is left before `playtest` / `main`, in order

**Wrong**
1. Merge `origin/main` (3 commits, the character assets, the `ROADMAP.md` conflict).
2. A3b: the `_CW1` blend space; then test the look on one real character.
3. Correct "The anime look is ready" and write the A3 devlog entry.
4. Fix `PITCH.md:9-11,37-39` and rewrite ROADMAP's "Where we are".
5. Move the `Saved/*_editor.py` scripts into `tools/`, or guard `c1_layout.py`.

**Unverified**
6. E2 has no independent check.
7. B4 (5), D2 (5) and E1 (2) need rewording.
8. Holding R through the win reload ("read from the graph, not tested").
9. Seen only at 2.25:1, never 16:9 (B2).
10. No packaged build exists.

**Only a person can do**
11. The 12-step play list (`FIRST_BUILD_LEDGER.md:57-69`).
12. The game is 25-27 s against a 3-5 minute target: one combo clears all three goons, the boss falls in 6.3 s, and a 10 s Freeze Frame trivialises both fights. This is the biggest design gap and needs people.
13. Decide what the plaza boss is.
14. Decide the "Final Cut" rename and which later boss gives Rewind.
15. Say whether to push the branch.

**Paperwork**
16. Never stage the `AndroidFileServer` ini hunk.
17. Fill the ledger's Tuning variables section and complete design section 12.
18. Add an A2 row.
19. Add the first-build files to PREJAM's "Made during the jam" table.
20. Add Unreal and the MCP to the tools list.
21. Record the LFS lock decision and release the 2 locks at hand-off.
22. Fix the stale lines in A8 and C6-C8.

---

## Unedited list of every asked-for line with no verified work behind it

- "make sure we have that [the cel-shaded anime look] ready for when we need it": A3 `smaller` with (1) failed, A3b `todo`; never tested on an anime-material character.
- "Make sure we are on the latest main": true at kickoff and at the 15:52 merge; now 3 commits behind `origin/main`.
- "We want to showcase the most fun abilities first… innovative mechanics would get us huge points": no packet; Freeze Frame has no on-screen effect beyond a border and makes both fights trivial.
- "1 level 3-5 minutes" (`CLAUDE.md` guardrail): the run takes 25-27 s; no packet.
- Thursday's checkpoint, "Core loop playable start to finish": by script only; no person.
- E2 "verified": no checker other than the agent that did it.
- B4 (5), D2 (5): the HUD line was passed as "variables only".
- E1 (2): the line as written could not be run after G1.
- A3 (1): failed.
- A3b: all three lines, todo.
- F: this audit; the row is still `todo`.
- INITIAL_PROMPT section 9, "the tuning variables with where they live": the ledger section is a placeholder and the design table is incomplete.
- INITIAL_PROMPT section 9, "Every assumption you made": not written anywhere.
- INITIAL_PROMPT section 5, "commit… with its devlog entry file": entries are in separate commits; A3 has none.
- `CLAUDE.md` done list 1 (a person confirmed it): nothing.
- `CLAUDE.md` done list 2 (pushed): nothing pushed.
- `CLAUDE.md` done list 6 (ROADMAP tells the truth): "Where we are" is stale.
- "We should keep the work that has been done for Rewind": supported by the graph-text headers only; that nothing was deleted inside `BP_Player.uasset` is editor only (inferred from "no graph changed" and G1's checker note).
