# Jump Cut — Roadmap

> **Agents:** read this file before any feature, scope or priority discussion. What the game is: [`PITCH.md`](PITCH.md).
> What already happened: [`devlog/`](devlog/README.md). Deadlines and daily checkpoints: `CLAUDE.md`, "Goals, and
> keeping us on track".

**How this file is organized** (every Claude on every PC shares it as its only memory of the plan):

- **Where we are:** one paragraph on the state of the build. Rewrite it when a checkpoint is reached or missed.
- **Open:** what is left to build, by day. When an item ships, it **moves** into its devlog entry. Don't tick it and
  don't just delete it.
- **Waiting for a yes:** proposals nobody has agreed to yet. Never build from these as if they were agreed.
- **Fallbacks:** proposals the team turned *down* but wants kept, in case a playtest changes its mind. They are
  settled, so their line is already in Decisions; this is the one section a settled proposal is allowed to stay
  written down in, and it is not "Waiting for a yes".
- **Still to decide:** open questions for the team.
- **Cut list:** what we drop, in order, when we fall behind.
- **Later:** ideas that are not for this jam. New ideas arrive as GitHub issues labelled `idea`.
- **Decisions:** what the team settled, newest first, one dated line each with who decided. When a proposal or an open
  question is settled, it moves here and leaves its old section, so nothing is ever in two places — the single
  exception being a turned-down proposal the team wants kept, which moves to Fallbacks.

Only a person on the team decides. An agent may propose (in "Waiting for a yes") but never writes its own suggestion
into Open or Decisions.

---

## Where we are (Thu Nov 12, evening)

The first build is **merged into `main`** (Thu Nov 12 evening, from M Station) so the two PCs stop drifting apart;
`playtest` was fast-forwarded to match it. It is a grey-box game in
one level, `Lvl_JumpCut`, built packet by packet by subagents and checked by other subagents
([`FIRST_BUILD_LEDGER.md`](FIRST_BUILD_LEDGER.md)): a title screen; the cafe, where the dying driver hands over
Freeze Frame (a second hand-over spot covers the cafe door); a street with a group of goons and the player's fists; a
checkpoint; a walled plaza whose entry gate closes behind you, with a boss (a big bruiser; his own freeze attack is
switched off) and an exit gate; a HUD; win and lose screens with restart at the checkpoint; the cel-shaded anime
shader on the level; and Rewind, built and then parked (kept, switched off). A scripted run goes from title to win in
25 to 27 s. **The Team Owner played it on GameStation on Thu Nov 12, evening** and called it ready for the
characters to go in. That clears the standing warning that `main` carried Unreal work no person had ever run -
merging it before a playtest was a deliberate call by the Team Owner to stop the two PCs drifting, and the
playtest has now happened. **Per-step results were not reported**, so the play list in
[`FIRST_BUILD_LEDGER.md`](FIRST_BUILD_LEDGER.md) is not ticked off and the length and difficulty problems below
still stand as written. M Station made the three rigged characters (main character, crash driver, mob boss) and a cleaver as FBX
under `Art/Blender/export/Characters/` and `Art/Meshy/` — all of which are now **in Unreal**, imported on
GameStation on Thu Nov 12 evening (the main character was already in) — redrew the cast in the chosen anime
style ([`CHARACTERS.md`](CHARACTERS.md)), and that work is merged into the branch. What the final audit found:
[`FIRST_BUILD_AUDIT.md`](FIRST_BUILD_AUDIT.md).

**The fight has animation now** (Thu Nov 12, 11:45 PM Pacific, GameStation, on `playtest`). The playtest found
that nobody swung at anybody: the combat code did damage and never played a clip, and the mob boss's mesh was in
single-node mode, which cannot play a montage at all. The player now throws punch 1, 2 and a finisher by combo
step, goons and the boss swing, react to hits and fall over, and the boss walks from an `ABP_CleaverBoss` anim
blueprint driven by his own speed. The motion is Epic's mannequin capture, retargeted. `EnemyDefeatLinger` went
0.6 s -> 1.2 s so the death animation finishes before the body is removed. **Verified in Play-In-Editor by
reading back which montage was playing, not by eye, and not by a person playing it.** Still Epic's mannequin on
the player and the goons: swapping `CafeWalker` onto `BP_Player` needs this same montage set retargeted onto his
skeleton, and is the next job.

## Open

| Day | Goal |
|---|---|
| Thu Nov 12 | Player + the first power (Freeze Frame) + the first fight, in grey boxes, playable start to finish |
| Fri Nov 13 | A person plays Thursday's build (the play list in [`FIRST_BUILD_LEDGER.md`](FIRST_BUILD_LEDGER.md)). Then **everything under "Before people playtest" below**, for all six beats of the demo; making the run 3 to 5 minutes and tuning it (it is 25 to 27 s today); first packaged build. Win/lose and restart screens are built (not yet played). **Feature freeze** |
| Sat Nov 14 | Playtests by people and iterating on what they find; model swaps; art, sound, juice (the flashy combat effects); footage |
| Sun Nov 15 | Bug fixes and submission only |

### The demo: six story beats (Justin, Nov 12, late evening)

The jam entry is **a demo, not the completed game**. It ends after the last boss below.

1. **Cafe.** A peaceful intro at the cafe, interrupted by the car crash. The first boss was driving and is already
   dead. Our protagonist, trying to help, gets his first power, **Freeze Frame**. Then an explosion sends shrapnel
   at a coworker. The action button teaches the player to use Freeze Frame to save the coworker.
2. **Street.** Wander out to the street. Thugs to fight using the new power.
3. **The Splice boss.** The next boss approaches, with the Splice power. Battle him and gain the new ability.
4. **Destroyed buildings.** Platforming across destroyed buildings to get to the final boss, fighting more goons
   along the way.
5. **The last boss has Stunt Double.** He makes a copy of himself and the player must fight both.
6. **Fade to a "continue"** of some type after that battle.

### Before people playtest (Justin, Nov 12, late evening)

1. **Enemy types and basic battle mechanics completely set up**, ready for model swapping after the playtest:
   basic boxing animations for combat, walk and run animations, controls.
2. **Buildings and basic assets laid out to follow the story beats.** Where we have basic assets, use them; no grey
   boxes unless needed.
3. **The look and the combat.** The story is inspired by anime and we want that artsy style. Combat on its own will
   be boring, so it needs flashy effects as well.

Once all of this is in, we playtest and iterate.

## Stretch (only if the critical path is finished)

**The cafe minigame** (Manny, the Team Owner, Nov 12. Only a person moves it into Open.) Before the car comes
through the wall, the player works a shift in the cafe: taking orders and pouring latte art. It is the game's
opening beat and the reason the cafe is the first room.

- It is a **new feature**, and Friday Nov 13 is feature freeze (Open, above). It either lands on Friday or it
  breaks the freeze.
- It shares no work with anything else: ordering and pouring need input and UI that no fight uses, so building
  it buys nothing for the rest of the game.
- It lengthens a run, which is the thing the build is worst at today (25 to 27 s against 3 to 5 minutes) - but
  so does tuning the fights, and that costs nothing new.

## Waiting for a yes

_(nothing right now)_

## Fallbacks (turned down, kept in case we need them)

**One large city level** (Justin's proposal, Nov 12. Not taken for now — see Decisions — and kept here as the way
to grow the game if there is time left. Only a person moves it into Open.)

- The whole game is one city map, laid out like the practice repo's city (a street grid of blocks, sidewalks and
  alleys), rebuilt here from scratch. Cafe start, streets with goons to each boss plaza, a second half that needs
  Splice for platforming, then a climb to the Director's tower. About 30 minutes of play, cut scenes later.
- `docs/INITIAL_PROMPT.md` was written around it. Its lead-and-subagents method is in use; its city is not.

**How we keep it buildable** (Claude's proposal, Nov 12. Turned down the same day — see Decisions — and kept here
in case playtesting shows we need it. Still not something to build from: only a person moves it into Open.)

- **Small Rewind:** record the player's position and health for 10 seconds. Rewind slides the player back along that
  trail in about a second and restores the health. No replay of the whole world.
- **One boss Blueprint** with a "which power" setting, not five different bosses.
- **Freeze Frame** shortened to about 3 seconds so fights stay quick.
- **Splice platforming** is one or two gaps, not half a map.
- **Stunt Double** as a still decoy that takes one hit. It's the first thing to cut.
- **Factions** as one grunt enemy recoloured per area, or cut until the bosses work.

## Still to decide

- The Director's real name and the final names of the powers.
- Camera: third person behind the player (the template's) unless we choose otherwise.
- **Which later boss gives Rewind.** The ladder itself is now settled (Decisions below): Freeze Frame -> Splice ->
  Stunt Double -> Director's Cut. Rewind is the one power with no boss. The small Rewind (only the player slides
  back, health restored) is what is built and parked.
- **Who builds which beat, and on which computer.** `TEAM.md` lists no owners, and GameStation is the only builder.
- **What the "continue" after the last fight is** (beat 6): a screen, a card, a cut to the title?
- **Does the player get Stunt Double in the demo**, or does it end when its boss falls?
- **Where Freeze Frame is handed over:** only at the driver, or also at the cafe door (as built, so nobody leaves
  the cafe without it)?
- **How long and how hard the game is at default numbers.** A scripted run takes 25 to 27 s against the 3 to 5
  minutes we want, and the fights are easy. Only people playing it can say what to change.

## Cut list (in the order we drop things)

The Stunt Double boss and the Splice platforming section were numbers 2 and 3 here until Nov 12, late evening.
They are beats 5 and 4 of the demo now (Decisions), so they are off this list.

1. Factions with different behaviour, and factions fighting each other
2. Dialogue: one line of text per power instead
3. A full rewind of the world (already cut: the parked Rewind only moves the player back)
4. More than one level

## Later

_(nothing yet)_

## Decisions

- **2026-11-12 (late evening): The jam entry is a demo in six story beats** (Justin). Cafe, crash and Freeze
  Frame with the coworker rescue as its lesson; street thugs; the Splice boss; platforming across destroyed
  buildings with goons; the Stunt Double boss, who copies himself; a fade to a "continue". The beats and what must
  be in before people playtest are under Open. This **supersedes** three things from earlier the same day: Stunt
  Double as "boss 3, only if there is time" (it is the demo's final fight); Stunt Double and the Splice
  platforming section on the cut list (both removed); and the Director with two rule scenes on Friday's list (the
  demo ends before him). It also confirms the ladder: the dead crash driver gives Freeze Frame, the Splice boss
  gives Splice. **Recorded from Justin's project chat; the Team Owner had not yet seen it when this was written.**
- **2026-11-12: The boss ladder is settled - Freeze Frame, then Splice, then Stunt Double** (Manny, the Team
  Owner). **Boss 1 is the car crash** through the cafe wall and it gives **Freeze Frame**. **Boss 2 is the mob
  boss with the cleaver** and he gives **Splice**. **Boss 3, only if there is time**, gives **Stunt Double** -
  it stays at number 2 on the cut list, so it is still the second thing dropped if we fall behind. Built the
  same evening on `playtest`: `BP_Player` gained a `HasSplice` flag and a `PlayerGrantSplice` function, and
  `BP_BossFreeze.BossHandOverPower` now calls `PlayerGrantSplice` where it used to call
  `PlayerGrantFreezeFrame`. Freeze Frame is not lost by that change: it is already granted inside the cafe by
  two `BP_SceneMarker`s - the driver at (-300, 330) and the cafe door at (560, 0), both confirmed in
  `Lvl_JumpCut` with `MarkerGrantsFreezeFrame` true - so nobody can reach the plaza without it. **`HasSplice`
  gates nothing yet**: the Splice ability itself is not built, so today the hand-over sets a flag and the HUD
  does not show it. The Blueprint is still named `BP_BossFreeze` and still has `BossUsesFreeze` false.
- **2026-11-12: The cafe minigame is a stretch goal, not a Friday feature** (Manny, the Team Owner). Taking
  orders and pouring latte art in the cafe before the crash, to be built "if there is time left over". It sits
  under Stretch above, below everything in Open, and nobody starts it until the critical path is done.
- **2026-11-12: The plaza boss is the Splice mob boss** (Manny, the Team Owner, answering "Mob boss"). The
  built plaza boss is kept and turned into him rather than dropped, so every number the playtest settled -
  240 health, 15 damage, 380 move speed, his capsule and his warning sign - survives. `BP_BossFreeze` now
  wears `SK_CleaverBoss` with `MI_CleaverBoss`, plays Unreal's mannequin idle and walk retargeted onto his own
  skeleton, and carries `SM_Cleaver` in a `cleaver_r` socket on his right hand. Which power he hands over was
  settled the same evening - Splice, see the entry above.
- **2026-11-12: The ComfyUI models are the ones we build on** (Manny). Of everything generated, `SK_CafeWalker`,
  `SK_CrashDriver`, `SK_CleaverBoss` and `SM_Cleaver` - all made from the local ComfyUI/Qwen reference sheets -
  came out best, so `SK_CleaverBoss` is the canonical second boss and the two Gemini-sourced bosses
  (`CleaverBossGemRef`, `CleaverBossGemText`) stay in the repo as alternates. This supersedes the earlier
  preference for drawing the cast in Gemini; the cel-shaded anime look is unchanged and still the style.
- **2026-11-12: GameStation's RTX 5090 is the machine for image generation when speed matters** (Manny).
  M Station's 3090 runs Qwen-Image at about 2 minutes a picture; the 5090 is there when a batch needs to be
  faster. `tools/gen_images.py` is machine-independent, so this is a choice of where to run it, not a code change.
- **2026-11-12: Power 4 is "Director's Cut", renamed from "Final Cut"** (Manny, the Team Owner, by form answer:
  "Now - do it today"). "Final Cut" is an Apple trademark and the jam allows none (§15d). This **supersedes the
  hold** recorded earlier the same day: the rename is done, in `PITCH.md`, `ROADMAP.md` and `INITIAL_PROMPT.md`.
  "Final Cut" now survives only in `docs/devlog/`, where it is discussion of the decision and not game content.
  Nothing player-facing may carry the old name.
- **2026-11-12: Rewind moves to a later boss.** The jam game is one level of 3 to 5 minutes, so the most fun powers
  come first: Freeze Frame is the first power the player gets. The Rewind work already built stays in the project,
  switched off, for that later boss (Team Owner).
- **2026-11-12: The art style is cel-shaded anime** (Manny, the Team Owner; recorded from both PCs). It was the
  leading candidate all along (the `mendezm87/anime-look` demo, the `CafeWalker` model); it is now the chosen look
  and everything we draw or model matches it. Its work on `mendezm87/anime-look` comes into the build so it is ready
  when the 3D assets from M Station arrive. The cast was redrawn in it through Gemini the same evening:
  [`CHARACTERS.md`](CHARACTERS.md#gemini-pass-2026-11-12).
- **2026-11-12: The first boss gives Freeze Frame**, not Rewind. He is the driver who crashes through the cafe
  wall in the opening; he still does not fight (Manny).
- **2026-11-12: The second boss gives Splice and is a Japanese mob boss with a cleaver** (Manny).
- **2026-11-12: The main character, the crash driver and the mob boss are the first three characters to build**
  (Manny). Designs and reference pictures: [`CHARACTERS.md`](CHARACTERS.md).
- **2026-11-12: Scope stays jam-sized.** We build to the jam's rules and `CLAUDE.md`'s guardrail (one small level,
  a few minutes of play), not the one large 30-minute city. If there is time left we look at growing it (Team Owner).
- **2026-11-12: Build to the team's own scope in the pitch** (five powers, the bosses as listed), not Claude's smaller
  proposal. Change it later only if playtesting shows the need (Justin).
- **2026-11-12: Losing restarts at the last checkpoint**, not at the cafe (Justin).
- **2026-11-12: The player fights with fists** for now, and there are ordinary goons between bosses (Justin).
- **2026-11-12: The Splice gap comes after the Splice boss** (Justin).
- **2026-11-12: The devlog is one file per entry** in `docs/devlog/`, so teammates never collide on one file (Justin).
- **2026-11-12: The game is called Jump Cut** (the team; the story is in the devlog entry for Nov 11 to 12).
- **2026-11-11: Prize focus is Glass Box first, Render Royalty second, Best Team third**, Best Overall as a stretch
  (the team; `CLAUDE.md`, "Goals, and keeping us on track").
