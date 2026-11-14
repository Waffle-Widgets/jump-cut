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

**And the boss still was not walking** (Fri Nov 13, 4:20 AM Pacific, GameStation, on `playtest`). The Team Owner
played it again and reported the same fault. The cause was one wire in `ABP_CleaverBoss`: `BS_Idle_Walk_Run_CB`
is a two-axis blend space, **X = Direction, Y = Speed**, and `BossAnimSpeed` was plugged into **X** while **Y**
sat at its literal `0`. His speed was being read as a heading, and his speed was always zero - which samples the
idle row, where every cell is `MM_Idle_CB`. His montages were never affected, because the Slot node is
downstream of the blend space: the cleave, the hit react and the death worked all along. `BossAnimSpeed` now
drives **Y**, with **X** pinned to `0.0` (he faces the player every frame before he moves, so he always walks
forward). **Measured, not read back:** the largest per-frame bone movement across all 83 bones is 0.03-0.06 cm
standing, **2-6 cm walking** and 6-15 cm mid-cleave. The previous fix was signed off by reading back which
montage was playing, which is a check that cannot see a blend space at all - see
[the devlog entry](devlog/2026-11-13-the-boss-was-walking-on-the-wrong-axis.md). Still not played by a person.

**Beat 1 has its lesson now** (Fri Nov 13, 1:15 AM Pacific, GameStation, on `playtest`). The demo's opening beat
asked the player to save a coworker from shrapnel using Freeze Frame, and none of it existed - no coworker
anywhere in the project, no shrapnel, and no action button on the player at all. `BP_Coworker` and `BP_Shrapnel`
are built and `Coworker_Cafe` is placed in `Lvl_JumpCut` at (300, -250), between the counter and the door.
Picking up Freeze Frame is what starts the danger; while time is stopped the shrapnel does not move or age; **F**
(or the gamepad's top face button) pulls her clear, and it only works while time is stopped, so the beat cannot
be passed without using the power it teaches. **Verified in Play-In-Editor by reading live actor positions and
state, not by eye - and the F key itself has not been pressed by a person.** She is still a green box: her design
and prompt are in [`CHARACTERS.md`](CHARACTERS.md), her model is not made.

**Beat 1 now plays the scene the Team Owner described** (Fri Nov 13, 2:35 AM Pacific, GameStation, on
`playtest`). He wrote the beat out in full - day job, latte art, the crash, touching the dead driver, the
explosion, the quick time event, and both endings - and three things in the build did not match it, so they were
changed:

1. **The power comes from touching the driver.** It used to be handed over by walking near a marker.
   `BP_CrashDriver` is a real actor on our own `SK_CrashDriver` model, lying beside the car at (-380, 220), and
   **F** on his body is what grants Freeze Frame. Both markers that used to give the power away for free
   (`Marker_FreezeFrameGiven`, `Marker_FreezeFrameDoor`) are switched off, and the grey placeholder box that
   stood in for his body is deleted.
2. **Time freezes by itself when the explosion goes off**, 1.2 s after the power lands - the player is *put*
   into the quick time event rather than being expected to guess the button. `AutoFreezeOnExplosion` and
   `ExplosionDelay` on `BP_Coworker` are the dials.
3. **Failing kills her.** The old behaviour stood her back up after 2.5 s and let the player try again. It is now
   one attempt: she dies, the scene disarms, and the level carries on - which is what the Team Owner asked for.

What is still **not** built from his description: the day job (taking orders), the **latte art minigame**, and
delivering the drink. The beat currently starts at the crash. See "Still to decide".

**Verified in Play-In-Editor through the real `PlayerInteract` path**, by reading live actor state: touching the
driver sets `HasFreezeFrame`; 1.2 s later the explosion fires, the shrapnel spawns at the car and
`FreezeFrameActive` goes true on its own with 7.65 s of its 10 s left; the rescue moves her (300, -250) ->
(300, 70) with `RescueTriesUsed` still 0; and when the freeze is allowed to run out instead, she ends
`CoworkerDead` with `RescueTriesUsed` 1 and nothing restarts. **The F key itself still has not been pressed by a
person.**

**The game has a city to stand in** (Fri Nov 13, 11:20 AM -> 1:50 PM Pacific, M Station, on `main`). The
level has been a grey corridor since the first build: two 60 m boxes for the street and five more for the
cafe. There are now **44 models and 216 worked-out placements** for it — the coffee shop as a real room,
nine building types, five ruin pieces for beat 4 and twenty pieces of street clutter — in
[`CITY.md`](CITY.md). **It is all procedural geometry from our own Blender script, 0 Meshy credits, and
nothing was uploaded anywhere**; the whole city is 20,615 triangles, fewer than the single goon model. The
cast is untouched and still comes from ComfyUI and Meshy, so the Nov 13 pipeline decision stands.
Tokyo and New York are blended by **zoning**: the 10 m lane the player walks is Tokyo, the 42-62 m towers
above and behind it are New York, and a New York avenue at x = -1900 is what the car came down before it
hit the cafe's west wall. **Verified by measurement, not by eye**: the kit writes its own footprints and
[`tools/jumpcut_city_layout.py`](../tools/jumpcut_city_layout.py) checks all 216 placements against them —
it found 17 real collisions on its first run and now reports none. **Nothing has been seen in Unreal.**
`tools/jumpcut_city_place.py` was written on M Station, which is a maker with no editor, so it has never
been run; expect to fix a line, not a layout. See
[the devlog entry](devlog/2026-11-13-the-city-gets-built.md).

**The player stopped wearing his own skin** (Fri Nov 13, 12:00 -> 1:35 PM Pacific, M Station, on `main`). The
first full-cast colour audit ranked all ten models side by side and put **the player worst**, on the one rule
the Team Owner set: his cream shirt measured **dE76 8.8** from his own face tone against a threshold of 14, so
his torso and arms merged at distance. The repo had already written this down in `prompts.md` and never fixed
it. `SK_CafeWalker.fbx` is now re-made from a redrawn sheet with a **khaki-brown** shirt measured at **dE
40.3**; skin leak went **6.13% -> 1.03%** front and **3.94% -> 0.44%** back, and what is left is only the bare
forearm the audit miscounts on anyone in short or rolled sleeves. **35 credits**, nothing else about him
changed, verified by re-importing the FBX: 69 bones, 175.01 cm, 30,000 tris, 0 unweighted vertices, Walk +
Idle. The old model is superseded and lives in git history, not beside it. **He is still not in Unreal** -
`BP_Player` wears Epic's mannequin until the builder imports him, which is why this was the cheapest possible
moment to redo him. See [the devlog entry](devlog/2026-11-13-the-player-stops-wearing-his-own-skin.md).

**`playtest` is merged into `main`** (Fri Nov 13, 12:57 PM Pacific, from M Station - PR #3, merge commit
`f9f05c0`). The Team Owner called it with one word, "merge", on feature-freeze day, so the two branches stop
drifting: `main` and `playtest` now hold the same thing. Thirteen files crossed - `BP_Player.uasset` and
`WBP_HUD.uasset` carrying the **Splice** blink and its violet SHIFT box, `tools/splice_graphs.py` and the two test
harnesses, the devlog entry, the PREJAM Splice row and the `INITIAL_PROMPT.md` banner. Everything `main` already
had - the 44-model city kit, the coffee shop, the re-made `CafeWalker`, the goon models - is untouched by the
merge; `playtest` had taken them in at `58e3deb`, so every FBX in it is `main`'s own blob and no LFS object was
duplicated.

**What `main` now carries that no person has played**, so nobody reads this branch as tested:

- **Nobody has pressed Left Shift.** Every Splice number (0 cm with no power, 600 open, 455 against a wall whose
  trace reads 500, 600 straight through `BP_StuntStandIn` and the cleaver boss) comes from driving `SpliceStart`
  through a temporary `DebugSplice` hook in PIE, first on GameStation and then on the Mac.
- ~~**None of the city has been seen in Unreal.**~~ **Done Fri Nov 13, 23:55 UTC, Justin's Mac mini** - the 37
  models the layout uses are imported and all 224 city actors are placed and saved in `Lvl_JumpCut`. See "The
  city is in the level" below. Still nobody has *played* it.
- **`BP_Player` and `BP_Goon` still wear Epic's mannequin.** The re-made `CafeWalker` and the street goon are
  committed FBX, not imported assets.
- **There is still no packaged build**, which Friday's checkpoint asks for.

`CLAUDE.md` says the builder merges `playtest` into `main` "when testers confirm". Testers did not confirm this
content. The merge was the Team Owner's deliberate call to stop the branches drifting on freeze day, and the four
lines above are the record of what it brought with it. Every other branch (`Gamestation/first-build`,
`claude/project-thread-8yvb6s`, `justin/agent-rules`, `mendezm87/anime-look`) is now behind `main` and has nothing
`main` lacks: anyone resuming one of them merges `main` in first.

**The demo is four beats now, not six** (Justin, Fri Nov 13, 4:30 PM Pacific). "Because of time, we're going
to focus on beats 1-3 and making that first half be amazing. We might have to move beat 6 (to be continued..)
to beat 4 and drop the current 4 and 5. Make the plan reflect that as the goal for now. The two dropped beats
will be nice to haves." So the goal is **cafe -> street -> Splice boss -> "to be continued"**, and the
destroyed-building platforming and the Stunt Double boss leave the goal for the cut list as nice-to-haves.
**Nothing is deleted and nothing was removed from the level**: both are built, both are on `main`, and both
still play. What changed is which work counts as finishing the demo. Two consequences worth reading before
anyone picks up a task:

- **The ending is now the only unbuilt beat, and it is a decision before it is a build.** It was last in the
  queue when it was beat 6; it is the finish line now. Nobody has said what the "to be continued" is
  (issue #17), so issue #10 cannot start.
- **Splice is granted in beat 3 and the only place it is used is a dropped beat.** The Splice boss still
  hands over `HasSplice` and the blink still works - but the gaps it exists to cross are now a nice-to-have,
  so as the demo stands the player receives a power on the last fight and never presses it. That may be
  exactly the right cliffhanger or exactly the wrong one; it is in "Still to decide", not settled here.

## Open

| Day | Goal |
|---|---|
| Thu Nov 12 | Player + the first power (Freeze Frame) + the first fight, in grey boxes, playable start to finish |
| Fri Nov 13 | A person plays Thursday's build (the play list in [`FIRST_BUILD_LEDGER.md`](FIRST_BUILD_LEDGER.md)). Then **everything under "Before people playtest" below** - now for **beats 1 to 3 and the ending**, not for six beats (the Fri Nov 13 4:30 PM rescope in Decisions); making the run 3 to 5 minutes and tuning it (it is 25 to 27 s today); first packaged build. Win/lose and restart screens are built (not yet played). **Feature freeze** |
| Sat Nov 14 | Playtests by people and iterating on what they find; **the three character models go in** (`CafeWalker`, `SK_StreetGoon`, `SK_CafeCoworker` - all three are in beats 1 to 3); art, sound, juice (the flashy combat effects); footage |
| Sun Nov 15 | Bug fixes and submission only |

### Tonight: the work moves to M Station (Fri Nov 13, 4:20 AM Pacific)

**Pull first, with Unreal closed.** `main` is `e12ab52` and `playtest` matches it exactly. The pull moves
`.uasset` binaries, so close the editor before switching or pulling - that is the trap this project has already
hit. **No LFS locks are held by anyone**, so nothing is blocked.

**What M Station may not do:** save Unreal files. [`CLAUDE.md`](../CLAUDE.md) keeps one builder, and that is
GameStation. M Station's lane is art, prompts and docs.

**What only M Station can do:** reach Meshy and Gemini in a signed-in browser. GameStation now has ComfyUI and
the same Qwen-Image models, but no signed-in browser - and the decision above makes **Meshy the model path**, so
generating characters belongs on M Station.

**The queue, in play order** (the work-order rule in Decisions: the earliest unfinished beat wins):

1. ~~**The coworker, `CafeCoworker`**~~ - **done on M Station, Fri Nov 13 morning**, 35 credits. Drawn, modelled,
   Smart Rigged (68 bones) and exported as `Art/Blender/export/Characters/CafeCoworker/SK_CafeCoworker.fbx` at
   162.0 cm with Walk and Idle: see
   [the devlog entry](devlog/2026-11-13-the-coworker-gets-a-body.md). **She is not in Unreal** - importing her is
   the builder's job, so it has moved to the GameStation list below, and `BP_Coworker` still shows a green box.
2. **The goons, `StreetGoon`** - beats 2, 3, 4 and 5. **Moved above the Director on Fri Nov 13 morning by the
   work-order rule in Decisions** ("the earliest unfinished beat wins"): the player fights goons from beat 2
   onward, and the six-beat decision below ends the demo *before* the Director in as many words. `BP_Goon` has
   been playable since the first build wearing Epic's mannequin, and until this morning **no document in this
   repo said what a goon looks like** - no design, no colour, no prompt. They have more screen time than any
   boss. Designed and drawn Fri Nov 13 morning on M Station:
   [`CHARACTERS.md`](CHARACTERS.md#the-goons--streetgoon-beats-2-to-5), with `GOON-APOSE` in
   [`prompts.md`](prompts.md) and `GEM2-GOON` in [`prompts-gemini.md`](prompts-gemini.md). **Modelled twice the
   same day.** First with TRELLIS for 0 credits while the meshy.ai session was logged out; then, after the Team
   Owner said **"spend them"** and logged back in, with **Meshy for 35 credits**. The Meshy build is canonical:
   `Art/Blender/export/Characters/StreetGoon/SK_StreetGoon.fbx`, Smart Rig **76 bones**, 18,000 tris, 180.0 cm,
   Walk + Idle, colour audit clean with **0.00%** skin leak. The TRELLIS build is kept beside it as the free
   fallback, `StreetGoonTrellis`. **The credits bought a measured thing:** Meshy keeps **89%** of the reference
   sheet's head-to-body lightness contrast (42.3 L points) where TRELLIS kept 47% (22.5), and TRELLIS had
   invented a mauve patch on his back. **The cost:** Smart Rig names bones `Bone_000...`, so his three
   mannequin-authored montages will need chains hand-mapped in Unreal the way `SK_CleaverBoss` needed nine.
   See [the devlog entry](devlog/2026-11-13-the-goons-get-a-body.md). **He is not in Unreal** - importing him is
   the builder's job, below.
3. **The Director** - **no beat in the demo.** No design, no colour, no prompt: the write-up has to come before
   any picture, and he is the one genuinely missing model in the *full game's* cast. But the six-beat decision
   below **supersedes** his two rule scenes and ends the demo at the Stunt Double, so no credits and no
   drawing time go on him until the demo plays through. The queue entry that called him "beat 6" was wrong:
   beat 6 is a fade to a "continue", which is a screen and not a character.
4. **Not boss 3.** The Stunt Double is conditional again (Decisions, above). His fight is built and plays on a
   mannequin; no credits go on his art until beats 1 to 4 play through.

**What stays on GameStation:** ~~importing the city~~ (**done on Justin's Mac mini, Fri Nov 13 23:55 UTC** - see
"The city is in the level" below), importing `SK_CafeCoworker.fbx` and `SK_StreetGoon.fbx` (both committed and
canonical; the goon also needs his retarget chains mapped by hand, since Smart Rig does not use mannequin bone
names) and pointing `BP_Coworker` at it (the asset is
committed and waiting; she is a green box in beat 1 until someone does), putting `CafeWalker` on `BP_Player` with
`ABP_Unarmed` retargeted onto his skeleton (the player and the goons are still Epic's mannequin, and that is the
most visible thing left in a judging video), building Splice for beat 4, and laying out beats 4 to 6.

### The demo: four story beats (Justin, Nov 12, late evening; rescoped by Justin, Fri Nov 13, 4:30 PM Pacific)

The jam entry is **a demo, not the completed game**. **The goal is now beats 1 to 3 made amazing, then a "to
be continued".** That **supersedes the six-beat plan** this section used to hold (and the Nov 12 decision that
set it): the destroyed-building platforming and the Stunt Double boss come out of the goal and become
nice-to-haves. Neither is deleted - both are built, on `main`, and still in the level. "Because of time, we're
going to focus on beats 1-3 and making that first half be amazing."

Beats 1 to 3 are unchanged, word for word, from the plan Justin wrote on Nov 12:

1. **Cafe.** A peaceful intro at the cafe, interrupted by the car crash. The first boss was driving and is already
   dead. Our protagonist, trying to help, gets his first power, **Freeze Frame**. Then an explosion sends shrapnel
   at a coworker. The action button teaches the player to use Freeze Frame to save the coworker.
2. **Street.** Wander out to the street. Thugs to fight using the new power.
3. **The Splice boss.** The next boss approaches, with the Splice power. Battle him and gain the new ability.

And the ending, which was beat 6 and is now beat 4:

4. **Fade to a "to be continued"** of some type after beat 3's fight. It is the only one of the four beats
   with **nothing built** (issue #10), and *what it is* - a screen, a card, a cut to the title - is still
   undecided (issue #17, "Still to decide" below). Under the old plan it was the last thing in the queue;
   it is now the thing that finishes the demo.

**Nice to haves (out of the goal, Fri Nov 13, 4:30 PM Pacific - built, kept, not deleted).** Both play
today and neither is finished as a *beat*. They are also back on the cut list below:

- **Destroyed buildings** (was beat 4, written Nov 12 as: *"platforming across destroyed buildings to get to
  the final boss, fighting more goons along the way"*). The 600 cm Splice blink and the three gaps are
  placed, saved and measured; `Marker_Win` sits east of them. **Nobody has pressed Left Shift.**
- **The last boss has Stunt Double** (was beat 5, written Nov 12 as: *"he spawns stunt doubles of himself
  that throw themselves in front of your attacks, so you have to Freeze Frame to land a hit on him at all,
  and he can tag in a double that fights"* - settled Fri Nov 13, 12:30 AM Pacific and built the same hour;
  conditional again since 4:20 AM, out of the goal since 4:30 PM). The fight, the diving stand-ins and the
  Freeze Frame counter are built and verified; his arena is **not** placed, killing him **opens nothing**
  (issue #36), and he has no art (issue #29).

### Before people playtest (Justin, Nov 12, late evening)

1. **Enemy types and basic battle mechanics completely set up**, ready for model swapping after the playtest:
   basic boxing animations for combat, walk and run animations, controls.
2. **Buildings and basic assets laid out to follow the story beats.** Where we have basic assets, use them; no grey
   boxes unless needed.
3. **The look and the combat.** The story is inspired by anime and we want that artsy style. Combat on its own will
   be boring, so it needs flashy effects as well.

Once all of this is in, we playtest and iterate.

### Still to build, in play order (Manny, the Team Owner, Fri Nov 13, 1:15 AM Pacific)

The queue the work-order decision creates. Take the top unfinished line.

| Beat | What is missing |
|---|---|
| 1. Cafe | Crash, Freeze Frame hand-over (touch the driver), auto-freeze and the coworker rescue all work. **Missing from the Team Owner's scene: the day job, the latte art minigame, delivering the drink.** **Her model is made but not imported** (art, not code): `SK_CafeCoworker.fbx` is committed, but `BP_Coworker` is still a green box until the builder imports her |
| 2. Street | **Done** - goons, fists, animation. Tuning only: one combo clears all three in about 1.0 s. **Their model is made but not imported** (art, not code): `SK_StreetGoon.fbx` is committed, but `BP_Goon` still wears Epic's mannequin until the builder imports him, and they are the enemy in beats 2 to 5. Designed, drawn and modelled Nov 13, see `StreetGoon` in [`CHARACTERS.md`](CHARACTERS.md#the-goons--streetgoon-beats-2-to-5) |
| 3. Splice boss | Fight works. He hands over `HasSplice`, which **now opens the Splice blink** (below). **This is the last fight in the demo** as of the Fri Nov 13 4:30 PM rescope, so the ending hangs off his death - and the wiring for that already exists on him: `EnemyDefeatedHook -> BossExitGate.PlazaGateOpenForGood` |
| 4. "To be continued" | **Nothing built, and the top unfinished line in the demo.** Was beat 6. Needs a decision on what it is (issue #17) before it can be built (issue #10). **Where the demo ends is also now open** (issue #37): `Marker_Win` is at (14400, 0, 0), on the Stunt Double's landing pad, two dropped beats east of beat 3 - see "Still to decide" |
| ~~4~~. Destroyed buildings | **Nice to have, out of the goal (Fri Nov 13, 4:30 PM).** **Built and in the level.** The **Splice power** (600 cm blink, Left Shift / gamepad B) and the **platforming section** are both done: 23 actors placed and saved in `Lvl_JumpCut` - three gaps (250 open, 400 and 400 roofed at 215), a 10x15 m landing pad for beat 5, a checkpoint and two goons. Measured after a reload from disk: walkway flush at `z=0`, jump reaches 288 cm against the 400 cm gaps, blink crosses. **Nobody has played it.** See below |
| ~~5~~. Stunt Double boss | **Nice to have, out of the goal (Fri Nov 13, 4:30 PM).** Fight and doubles built, and **Splice past the attack stand-in is measured, not argued** - 600.0 cm straight through `BP_StuntStandIn`, not shoved, because its capsule and mesh both ignore the Visibility channel the blink traces. **But the beat cannot be finished: `BP_StuntDouble` has no `BossExitGate` and no power hand-over, so killing him opens nothing** (read out of the assets, below). Also unbuilt: the attack stand-in's despawn timer, his arena (not placed), and his art. Recipes for the first three: `tools/beat5_graphs.py` and `tools/beat5_arena.py` |

**The top unfinished line is now beat 4, the ending**, and it is a decision before it is a build: nothing can
be built until somebody says what the "to be continued" is (issue #17). Everything above it in the table is
built; what beats 1 to 3 need is **their art in, their numbers tuned and a person playing them** - which is
what "making that first half be amazing" means in work terms.

**One live defect the rescope makes sharper, not softer.** `Marker_Win` is at (14400, 0, 0), in the middle of
the Stunt Double's landing pad - beat 4's placer parked it there and its own header says it must move once
beat 5 is placed. Under the six-beat plan that meant *the player wins early*. Under the four-beat plan it
means **the demo's ending is sitting two dropped beats east of where the demo now ends**, so a player who
beats the Splice boss walks out of the plaza, across the platforming and onto an empty pad to finish. Moving
it is level work on a `.uasset`, so it is written here rather than done - see "Still to decide".

### Beat 4's platforming is built and in the level (Fri Nov 13, 23:20 UTC, Justin's Mac mini)

The Team Owner put beat 4 on this Mac, so its row in [`TEAM.md`](TEAM.md) is now
`tester, maker, builder (beat 4)` - scoped, so GameStation stays the builder for everything else.

**It is placed and saved.** 23 `JC_Beat4` actors are in `Lvl_JumpCut`: 21 ruin pieces, plus
`Checkpoint_Beat4Entry` and `Spawner_Beat4` (2 goons). The five ruin meshes are imported from their
committed FBXs (Nanite off; 284/166/144/204/312 triangles) with `M_CityBrick` / `M_CityConcrete` /
`M_CityMetal`. `tools/beat4_platforming.py` builds the whole thing and is idempotent - re-running it
removed 23 and placed 23, not 46.

**The section, measured after reloading the level from disk** (not from the script's own report):

| | |
|---|---|
| Walking surface | `z = 0` on all three platforms, flush with the street |
| Ground | street to 11200, `B4_P1` 11450-11950, `B4_P2` 12350-13350, landing pad 13750-14750 (10 x 15 m) |
| Gap 1 | 250 cm, open sky - a free jump that teaches the ledge |
| Gaps 2 and 3 | 400 cm, roofed at `z = 215`, ceiling unbroken across the walkway (`y` -240 to +240) |
| Head room | 39 cm, so a jump reaches **288 cm** against a 400 cm gap; the blink reaches **600** |
| Route | clear at chest height from x 10300 all the way through |

**Why the gaps are 250/400/400 and not CITY.md's "6.5-8.5 m".** The player's movement numbers come from
the assets, not from a running editor: `BP_Player` serializes none of them, and `BP_ThirdPersonCharacter`
serializes only `JumpZVelocity` - exactly one `500.0`, no 420/600/700 - beside `AirControl 0.35` and
`BrakingDecelerationFalling 1500`. `MaxWalkSpeed` and `GravityScale` are in neither asset, so engine
defaults 600 and 1; no capsule override, so 34 x 88 and a 176 cm player. A flat jump therefore carries
612 cm, ~680 with a lip at each end - **further than the 600 cm blink**, so no gap width both defeats the
jump and allows the blink. A **ceiling** does.

**Four defects were found and fixed, and every one of them was invisible.**

1. **The ceiling had a 20 cm slit along `y = 0`.** The slabs sat at `y = +-170` and are 320 deep. The
   capsule could never fit the slit - but the script's own ceiling check traces up `y = 0` *exactly*, so
   it would have reported "open sky" over both roofed gaps. Now `+-150`, overlapping.
2. **The old end wall still blocked the route, invisibly.** `C1_Run_End` was hidden but its collision came
   back after a reload: the component-level `set_collision_enabled` did not serialize. A forward trace
   from x 10300 stopped dead at 10615. `bActorEnableCollision` is an actor property and does stick.
   **Beat 4 was unreachable in play until this was fixed.**
3. **Every platform sat 74 cm too low.** `SM_RuinSlab_A` is a *broken* slab: its bounding box reaches 119
   only because of chunks standing up near the edges, while the surface you stand on down the centre line
   is 45 above the origin. Placing at `-H` therefore put the walkway at `z = -74`, which turned the head
   room from 39 cm into **113 cm** - and a jump then carries ~559 cm and **clears both "must-blink"
   gaps**. The slabs looked completely correct the whole time. Placement is now `-45`.
4. **Interchange's auto convex hull did not match the slabs**, so the collision surface and the visible
   surface disagreed. All five meshes are now `CTF_USE_COMPLEX_AS_SIMPLE`, which is right for static
   level geometry and makes the player stand on what they can see.

**A fifth thing, which cost the most.** Unreal restored 23 actor packages from the previous session's
recovery data at startup. They were not in the loaded level, so they looked like harmless orphans - but
World Partition picks up every actor package in the folder, and reloading the map produced **46** beat-4
actors, the whole section doubled. They are moved out of `Content` to
`JumpCut/Saved/jcpy/dupes-2026-11-13/`. A reload now gives 23 with no duplicate labels.

**The one thing a playtest has to answer.** The blink is a fixed 600 cm forward and does **not** stop at a
gap. Clearing gap 2 means launching from the eastern 200 cm of a 500 cm platform; blink from the western
lip and the player lands at 12050, inside the gap, and falls. `Checkpoint_Beat4Entry` is 3 m back so a
mistake costs about five seconds. If it plays badly, narrow the gaps - do not touch the power, which beat
5 also needs.

**Not done.** Nobody has played it: every number above is a trace or an asset read, not a person jumping.
The platforms float over open sky with nothing beneath them, which reads as slabs rather than ruined
buildings - that is dressing, not blocking. And three placeholder materials Interchange made
(`MS_City*` in `Imported/City`) are still there: the meshes no longer point at them, but the asset
registry still lists stale referencers, so deleting them was not worth the risk today.

![The beat 4 run, seen from the side](media/2026-11-13-beat4_side.png)

### The city is in the level (Fri Nov 13, 23:55 UTC, Justin's Mac mini)

The 44-model city kit had never been opened in Unreal on any machine and `tools/jumpcut_city_place.py` had never
been run. It is in now: **37 models imported** (the five ruin meshes beat 4 already uses were deliberately not
re-imported, because re-importing resets materials) and **224 `JC_City` actors placed and saved** in
`Lvl_JumpCut`, with the 8 grey boxes they supersede hidden. This is "Before people playtest" item 2 - buildings
and basic assets laid out to follow the story beats - and it was the only Friday item with no progress at all.

**Measured after reloading the level from disk**, not from the script's own report:

| | |
|---|---|
| Actors in `Lvl_JumpCut` | 289 total: **224** `JC_City`, **23** `JC_Beat4` (untouched), 42 pre-existing |
| Duplicate `JC_City` labels | **0** - the script clears its own tag first, so re-running gives one city |
| Grey boxes superseded | 8, all `hidden_in_game = True` **after a reload** |
| Ground along the route | present at x = 0, 300, 3000, 8120, 11700, 12850, 14250 |
| Route at chest height (z=90, y = -200 / 0 / +200) | clear apart from the two plaza gates, the crashed car, the cafe's own east wall beside the door, and `City_Barrier_2` (a deliberate 200 cm road barrier in a 10 m lane) |

**Four defects were found and fixed. Three of them were in work that already looked finished.**

1. **The committed `city_layout.json` was eight actors out of date.** Regenerating it from the committed
   generator gave **224** actors, not 216 - the extras are every `City_Avenue*` piece, the New York avenue at
   x = -1900 that the generator's own docstring calls *"the one piece of layout the story actually requires"*,
   because it is the road the car comes down before it hits the cafe. The generator had been edited after the
   JSON was last written. The avenue existed in code and nowhere else.
2. **`City_Landmark` stood in the middle of beat 4.** The 62 m `SM_CurtainTower` at (12600, 0) occupies
   x 11891..13309, y -1309..+30 - gap 2, `B4_P2` and gap 3. Beat 4 was placed **after** this layout was
   authored, so the layout checker had never heard of it. The checker now carries a `beat 4 run` no-go box
   (x 11200..14750, |y| <= 300), proved by putting the tower back at 12600 and watching it fail; the tower is
   at **x = 16200**, same view axis, behind the beat-5 landing pad.
3. **The cafe's door curtain sealed the cafe.** Setting the kit's collision to `CTF_USE_COMPLEX_AS_SIMPLE` -
   right for the rest of it - turned `City_CafeNoren` at (648, 0) into a solid 150 x 100 cm wall across the
   **only exit from the cafe**, which would have ended every playtest at beat 1. It renders perfectly; a
   chest-height trace is what found it. `SM_Noren` and `SM_CableSpan` are now walk-through, set on the **actor**
   (`set_actor_enable_collision(False)`), because the component flag did not serialize for beat 4's end wall.
4. **The grey-box hide never reached disk.** `set_greybox` reported success, but after saving, 224 new actor
   packages were dirty and **not one** of the 8 grey-box packages was: hiding an actor does not dirty it, and
   this map is one-file-per-actor, so the grey walls would have come back on the next load standing inside the
   city. They were also read-only under LFS, so the save would have failed silently a second time.

**One line was wrong in the script, exactly as its author predicted** (*"expect to fix a line, not a layout"*):
`set_editor_property('hidden_in_game', ...)` is not a property `AActor` exposes to Python. It is
`set_actor_hidden_in_game()`. The script also did nothing about **Nanite** (Interchange turns it on; its
simplified fallback drops thin parts, which here is the signage, cables, fire escapes, noren and bicycles) or
**collision**; `prepare_meshes()` now does both and is idempotent.

**Not done.** Nobody has played it. The 9 placeholder `MS_City*` materials Interchange made in
`Imported/City` are committed unused alongside the 3 already there - deleting assets opens a modal dialog that
freezes the MCP, so it was not worth the risk on freeze day. And the three beat-4 materials
(`M_CityBrick` / `M_CityConcrete` / `M_CityMetal`) changed, because applying them set their Nanite usage flag.

![The street the player walks, looking east from the cafe door](media/2026-11-13-city-lane.png)

### Beat 5: the arena recipe, and the fight that has no ending (Sat Nov 14, 00:40 UTC, Justin's Mac mini)

**The editor could not be reached, so this is maker work: two recipe scripts and three findings.** Unreal
was running on this Mac with the level loaded, but its MCP server never bound its port -
`LogHttpListener: Error: HttpListener unable to bind to 127.0.0.1:8000` in the editor log at startup,
because the previous editor process was still holding the port as this one came up. The server is only
started once, at launch, so nothing short of restarting the editor brings it back - and an MCP server
cannot be attached to a chat that has already started either. **Nothing in beat 5 reached Unreal.**

**Three findings, read out of the committed `.uasset` name tables - not inferred:**

| | |
|---|---|
| `BP_BossFreeze.uasset` | contains `BossExitGate` **and** `PlazaGateOpenForGood` |
| `BP_EnemyBase.uasset` | contains neither |
| `BP_StuntDouble.uasset` | contains neither, and no `BP_PlazaGate` reference anywhere |
| `BP_StuntStandIn.uasset` | contains `StandInFights` and no other variable of its own |

1. **Beat 5 has no ending.** The cleaver boss opens the plaza's exit gate when he dies
   (`EnemyDefeatedHook` -> `BossExitGate.PlazaGateOpenForGood`), and that wiring lives on `BP_BossFreeze`.
   `BP_StuntDouble` is a `BP_EnemyBase` child, so it has none of it: kill him and nothing opens and nothing
   is handed over. This was never noticed because the fight was verified by calling functions and reading
   health back, which is exactly the check that passes while a beat is unfinishable.
2. **The despawn timer is genuinely unbuilt** (issue #9) - `BP_StuntStandIn` has one variable of its own.
3. **`Marker_Win` is in the wrong place right now.** `tools/beat4_platforming.py` parked it at
   (14400, 0, 0), the middle of the landing pad, with its own header noting it must move again when beat 5
   is placed. It has not moved, so the demo can be won by arriving at beat 5.

**`tools/beat5_arena.py`** places the arena on the pad beat 4 ends at, in the same shape as
`beat4_platforming.py` (tagged `JC_Beat5`, idempotent, `clear` and `report` modes, never saves):
`Gate_Beat5Entry` at x 13800 open and closing behind the player with `GateEnemyToWake` -> the boss;
`Boss_StuntDouble` at x 14300 facing west; `Gate_Beat5Exit` at x 14650 closed; `Marker_Win` moved east of
the exit gate to x 14720. The entry gate sits on the pad's west lip and not further in because
`BP_PlazaGate`'s opening is 5 m against a 15 m pad - at the lip the only way in is gap 3's single 500 cm
slab, so 5 m seals it. Its `report` prints the one number the script cannot settle: `Marker_Win`'s trigger
radius, which is a component property, not a Blueprint variable - at 200 cm it would reach back west of the
closed exit gate and let the player win through it.

**`tools/beat5_graphs.py`** is the Blueprint recipe: `FighterIdleTimeout` / `FighterIdleLeft` plus
`BossTickFighter`, and the `BossExitGate` variable with the `EnemyDefeatedHook` line that opens it. **The
despawn timer goes on the boss, not on the stand-in**, which is the one real design decision here. The soak
doubles *are* `BP_StuntStandIn` with `StandInFights` false, and they stand still with nothing in range to
attack by design - the exact condition the timer fires on - so a timer living on the stand-in would delete
the boss's whole damage shield seconds into every fight. Scoped to the boss's `FighterRef` it cannot touch
them, and it keeps `FighterRef` consistent so he can tag another double in afterwards. He deliberately hands
over **no power**: whether the player ever gets Stunt Double is still open (issue #21).

**Unlike `tools/splice_graphs.py`, this recipe has not been compiled.** Its design and its findings are
solid; its node ids were written from the assets and are a proposal to read back and correct. The ids most
likely to be wrong are flagged in the file, including the one that matters: calling
`EnemyDistToPlayer` on *another* actor, where a positional argument lands in the `self` pin and silently
measures the boss's own distance instead of the fighter's.

### Splice is on disk (Fri Nov 13, 18:20 UTC, Justin's Mac mini)

The blink that was built and measured on GameStation was lost before saving - the editor quit with
`BP_Player` and `WBP_HUD` dirty. **It has been rebuilt on Justin's Mac mini and committed.**

The route was `tools/splice_graphs.py`, the recipe's own known-good path. It was the only route available
here: the GameStation autosaves in `JumpCut/Saved/jcpy/recovered/` are on that machine and are not in git, so
they do not exist on the Mac. That settles the open question - re-run the recipe - without anyone having to
answer it.

**What was checked rather than assumed.** The DSL printer collapses two things in a way that can hide a wrong
graph, so both were read at the pin level instead:

- The stop-short vector is fed from `BreakHitResult` **output 5, `ImpactPoint`** - not the struct's first pin
  (`bBlockingHit`), which is what the printer's collapsed `(Collision|BreakHitResult _outhit)` form could
  equally have meant.
- The trace is `TraceChannel = TraceTypeQuery1` (Visibility), `bIgnoreSelf = true`, `bTraceComplex = false`.
  Visibility is the whole design: the Pawn collision preset ignores it, so the blink passes through people and
  stops only on world geometry - which is what delivers the Team Owner's beat-5 call ("Splice lets the user get
  past the attack Stunt Double") with no code in the stunt-double fight at all.

All nine defaults read back exact (600 cm, 1.2 s cooldown, 30 cm trace radius, 45 cm wall back-off). `BP_Player`
compiled with warnings as errors. In Play-In-Editor the live pawn carries every Splice value correctly, map
check is clean and there were **no Blueprint runtime errors**.

**The HUD box is new work, not a restore.** The GameStation autosave pre-dated the `HudRefresh` edit, so those
lines had never been saved anywhere. `SpliceBox` / `SpliceIcon` / `SpliceKey` / `SpliceBar` now sit third along
the bottom-left row (violet, `SHIFT`), and all **11** `HudShowIf` `Target` pins were audited after the
whole-function rewrite to confirm none lost its widget.

### Splice re-measured on the Mac (Fri Nov 13, 19:05 UTC, Justin's Mac mini)

The note that used to sit here said the blink could not be re-measured on this machine. That was wrong: a
temporary `DebugSplice` bool plus a one-line hook in `PlayerTickInput` drives the real `SpliceStart` on the live
Play-In-Editor pawn, exactly as on GameStation. **Splice is now measured here, not inherited.**

| Test | Measured | Expected |
|---|---|---|
| No power (`HasSplice` false), input unlocked | **0.0 cm**, cooldown untouched | 0 - the gate holds |
| Open ground, facing +X from x=1000 | **600.0 cm** (1000 -> 1600.0) | 600 |
| Wall: building face 500 cm ahead (line trace = 500) | **455.0 cm**, x drift **0.0** | 455 = 500 - 45 back-off |
| **Through the attack stand-in**, `BP_StuntStandIn` 250 cm dead ahead | **600.0 cm** (1000 -> 1600.0); stand-in **not shoved** (0.0) | 600 = passed through |
| Cooldown is written by a successful blink | **19.44 s of 30** still left afterwards | > 0 |
| Fire again while that cooldown runs | **0.0 cm** with **8.54 s** left | 0 - the gate blocks |

To prove the cooldown is really written rather than inferred from the graph, `SpliceCooldown` was temporarily
raised 1.2 -> 30 s for one run, so the value could still be read after the round trip. It is back at 1.2.

**The through-a-body claim is now proved structurally as well, which is stronger than any single blink.** Every
character's **capsule and skeletal mesh both** set `Visibility -> ECR_Ignore`:

| Body | Capsule profile | Visibility | Capsule r / half-height |
|---|---|---|---|
| `BP_Goon` | `Pawn` | `ECR_Ignore` | 34 / 88 |
| `BP_StuntStandIn` | `Pawn` | `ECR_Ignore` | 34 / 88 |
| `BP_BossFreeze` (cleaver) | `Pawn` | `ECR_Ignore` | 45 / 115 |
| `BP_Player` | `Custom` | `ECR_Ignore` (+ `Camera` ignored) | 35 / 90 |

Their meshes are all profile `CharacterMesh`, `QueryOnly`, with `Pawn` / `Visibility` / `Vehicle` ignored. And
`DefaultEngine.ini` declares **no custom trace channels**, so `TraceTypeQuery1` is the engine default -
Visibility. A character therefore *cannot* block the blink: there is no surface on them that answers the channel
it traces. This is the first time the **stand-in** itself was checked; GameStation tested a goon and the cleaver
boss, which is the case the beat-5 call actually depends on.

**What is still not measured here.** The goon and cleaver-boss pass-throughs are still GameStation's numbers.
Both were attempted and both runs were thrown away rather than reported: the test goon chased the player across
the street and **killed him** (`Health` 0, `IsLost` true), and `PlayerCanAct` is false when lost, so every
later blink read 0 cm for a reason that had nothing to do with Splice. The stand-in is the usable case because
with `StandInFights` false it genuinely stands still. The two bodies are structurally identical to it (table
above), so nothing is left in doubt about the mechanic - only about those two specific numbers.

**And still true: nobody has pressed Left Shift.** Every measurement above drives `SpliceStart` directly. The
*key poll* is unproven, and cannot be driven from here: `PressKey` presses and releases inside one call, while
`PlayerTickInput` reads `IsInputKeyDown` once per tick, so a simulated press never spans a tick.

**Three traps found doing this.**
- `ObjectTools.set_properties` only writes **instance-editable** Blueprint variables. A non-exposed one is
  refused by name (`SpliceCooldownLeft`), which is the loud failure. The quiet one is worse: `InputLocked` was
  exposed, accepted the write **without any error**, and still read back `true` - the write simply did not take.
- The title screen cannot be dismissed by a simulated key either: its "pressed" test is also an
  `IsInputKeyDown` poll (R / `Gamepad_FaceButton_Bottom`) on the game-mode tick. The way in is
  `ShowTitleOnStart` on `BP_JumpCutGameMode`: with it false, `JumpCutFlowTick` calls the real `JumpCutStartPlay`
  itself, which is how these runs reached `FlowState` 1 with `InputLocked`/`MoveLocked` both false. It is back
  at true.
- MCP tool calls run **on the game thread**, so the world does not tick inside one script. Setting the hook and
  reading the result must be two separate calls or the blink has not happened yet.

**Everything temporary was reverted and verified:** the hook removed from `PlayerTickInput` (read back - no
`Debug` references, and exactly **one** `CallFunction|SpliceStart` call site, so nothing was duplicate-appended),
the `DebugSplice` variable deleted, the two instance-editable flags put back, `SpliceCooldown` back to 1.2 and
`ShowTitleOnStart` back to true. The three test bodies were removed from `Lvl_JumpCut`, which ended the session
**not dirty**, so no actor package was written or orphaned. `BP_Player.uasset` and `BP_JumpCutGameMode.uasset`
re-serialized to different bytes on save with identical content, so both were restored to their committed bytes
and the LFS locks released - the working tree is clean.

**Two traps worth keeping.** `HudShowIf` is printed positionally but takes a `Target` parameter, so writing the
function back as printed is rejected outright ("Could not connect pin ... to self") - every call needs the
`:Target` / `:Show` keyword form, not just the new ones. And the reader attributes the player's `GetHealth` /
`GetMaxHealth` to `Class|AbilitySystemTestAttributeSet`, a colliding engine class; they must be written back as
`Class|BPPlayer|`.


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

**A crowd on the street** (M Station, Nov 13). The city is dressed but has no people in it. The cheap route
is `BP_Civilian` walking instances of the two bodies we already own (`SK_StreetGoon`, `SK_CafeCoworker`)
in six recoloured material instances — **0 credits, no new rig** — but it needs Blueprint work on the
builder, and it is unverified whether `M_AnimeChar` exposes a tint parameter to drive. Reasoning in
[`CHARACTERS.md`](CHARACTERS.md#crowds--making-the-street-feel-populated-fri-nov-13-m-station), including
why generating clothing separately from bodies is **not** worth it here.


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
- **May Justin's Mac mini change Unreal files?** It already has, twice, and the rule says it may not. `TEAM.md`
  gives it `tester, maker`, and a maker *"never saves in Unreal"* - only the builder (GameStation) changes
  `.uasset`/`.umap`. The Splice commits `26d437b` and `2c76ffc` were made on the Mac, and the Fri Nov 13 19:05 UTC
  verification saved in Unreal there too (nothing from it reached the repo). **It happened again on Fri Nov 13,
  23:55 UTC**, and wider than before: the Team Owner said *"Continue beat 4 on this mac"*, which `TEAM.md` records
  as `builder (beat 4)`, and the city import saves 37 meshes, 12 materials and 224 actor packages across the whole
  of `Lvl_JumpCut` - that is not beat 4. It was done because it is the only Friday checkpoint item with no
  progress, GameStation was asleep, and art going in is allowed after feature freeze; it is written here rather
  than quietly widening the role. **The scoped row in `TEAM.md` is unchanged and still says beat 4 only.**
  The rule exists for a real reason -
  binary files cannot be merged, and two chats in one editor is how the first Splice build was lost - so this
  wants an answer rather than a habit. Three ways out: make the Mac **`builder (area)`** for a named area with LFS
  locks (the table's own mechanism, and the only option that keeps "exactly one builder" true per area); hand all
  Unreal work back to **GameStation**; or record a deliberate exception here. Until then the Mac should stick to
  docs, scripts and art. **Nobody has decided this; it has only happened.**
- **Whether to fix the author on the two Splice commits.** `26d437b` and `2c76ffc` are authored
  `Claude <noreply@anthropic.com>`, not under Justin's name, although that clone's `user.name` / `user.email` are
  set correctly. `CLAUDE.md` requires every commit to be under the teammate's own name *because Epic may read our
  Git history, and it shows who built what* - so this is a submission-facing detail, not tidiness. Fixing it means
  rewriting commits already pushed to `playtest`, which GameStation and at least one other chat have, so it is
  a force-push and needs saying out loud first. The alternative is to leave them and note it in the submission.
- **What the "to be continued" is** (now **beat 4**, was beat 6): a screen, a card, a cut to the title? This
  was the last question in the queue and is now the **first**: it is the demo's ending and the only beat in
  the goal with nothing built (issue #17 blocks issue #10).
- **Where the demo ends, and what happens to the two nice-to-have beats in the level** (new, Fri Nov 13,
  4:30 PM Pacific, from the rescope - **issue #37**). `Marker_Win` is at (14400, 0, 0) on the Stunt Double's
  landing pad.
  Three ways, and this is a person's call because all three are level edits on a `.uasset`:
  1. **End at the plaza.** Move `Marker_Win` just east of the plaza exit gate, so beating the Splice boss
     walks you into the "to be continued". Tightest demo, and the Splice boss's own
     `BossExitGate -> PlazaGateOpenForGood` already fires on his death, so the trigger exists. The
     platforming and the Stunt Double's pad are then built content nobody reaches.
  2. **Keep them as a coda.** Leave `Marker_Win` east and let the platforming (and, if it gets an arena,
     the Stunt Double) sit between beat 3 and the ending as an optional stretch. Gives Splice something to
     do; makes the demo longer and the "first half" harder to call amazing, because the last thing a judge
     plays is the half we deprioritised.
  3. **Hide them.** Keep the actors, block the route east of the plaza, decide later. Cheap to undo.
- ~~**Does the player get Stunt Double in the demo**, or does it end when its boss falls?~~ **Answered Fri
  Nov 13, 4:30 PM Pacific** by the rescope, not by a separate decision: the boss who would hand it over is
  out of the goal, so **the demo does not hand out Stunt Double**. If he comes back off the cut list, this
  question comes back with him (issue #21).
- **The GitHub beat labels keep the Nov 12 numbering** (not a decision, a note so nobody renumbers them
  mid-jam): `beat-6` is the ending that is now beat 4, and `beat-4` / `beat-5` are the two nice-to-haves.
  The board changes the rescope did make: #9, #29 and #36 moved to the out-of-scope milestone; #10 and #17
  are critical-path as the ending and its blocker; #21 is closed, answered by the rescope; **#37 is new**,
  for where the demo ends.
- **Does Splice stay a reward with nothing to spend it on?** (new, Fri Nov 13, 4:30 PM Pacific.) See the
  second bullet in "Where we are". Either the beat-3 hand-over *is* the cliffhanger ("you just got a new
  power" -> to be continued, which costs nothing), or the demo needs one place inside beats 1 to 3 to press
  Left Shift, or the platforming comes back as the coda above. Nobody has decided.
- ~~**Where Freeze Frame is handed over:** only at the driver, or also at the cafe door?~~ **Settled Fri Nov 13,
  2:35 AM Pacific** by the Team Owner's scene: only at the driver, and only by touching him. Both markers are off.
- **What sets off the explosion.** The Team Owner said "we can play with what sets it off". It is now a **2.0 s**
  timer after the power lands (he asked for "a couple seconds"), which nothing in the fiction still explains. A
  leaking fuel tank, a spark, the driver's body flickering as the power leaves him - any of these is an effect
  plus a trigger, on top of a delay that is already the right length.
- ~~**Is the cafe day job in the demo?**~~ **Settled Fri Nov 13, 2:55 AM Pacific**, as an ordering rather than a
  cut: the day job and the **latte art minigame** get built *after* the beats up to and including the Splice boss
  play through with their art in. Until that bar is met the demo opens on the crash. See Decisions.
  **The Fri Nov 13 4:30 PM rescope makes that bar the whole goal**, so this is no longer a question about a
  stretch goal at the end of a six-beat list: the minigame is the next *new* feature the moment beats 1 to 3
  play through with their models in, and it is in the beat the rescope says to make amazing (issue #24).
- **How long and how hard the game is at default numbers.** A scripted run takes 25 to 27 s against the 3 to 5
  minutes we want, and the fights are easy. Only people playing it can say what to change.

## Cut list (in the order we drop things)

The Stunt Double boss and the Splice platforming section were numbers 2 and 3 here until Nov 12, late
evening, when they became beats 5 and 4 of the demo and came off this list. **They are back on it as of Fri
Nov 13, 4:30 PM Pacific** (Decisions), at the top, because the demo's goal is now beats 1 to 3 plus the
ending. The difference from the first time they were listed: both are **already built**, so dropping them
costs nothing and keeping them costs only the work of finishing them as beats (an arena, a death hand-over,
a despawn timer, art). They are nice-to-haves, and this is the order they come back in if there is time.

1. The destroyed-building platforming (built; nobody has pressed Left Shift)
2. The Stunt Double boss (built; no arena, killing him opens nothing, no art)
3. Factions with different behaviour, and factions fighting each other
4. Dialogue: one line of text per power instead
5. A full rewind of the world (already cut: the parked Rewind only moves the player back)
6. More than one level

## Later

_(nothing yet)_

## Decisions

- **2026-11-13 (4:30 PM Pacific): the demo is four beats - 1 to 3 plus the "to be continued" - and the
  platforming and the Stunt Double boss become nice-to-haves** (Justin). "Because of time, we're going to
  focus on beats 1-3 and making that first half be amazing. We might have to move beat 6 (to be continued..)
  to beat 4 and drop the current 4 and 5. Make the plan reflect that as the goal for now. The two dropped
  beats will be nice to haves." This **supersedes the Nov 12 six-beat demo plan** (below) and **completes the
  Fri Nov 13 4:20 AM narrowing** that had already made boss 3 conditional: he is now out of the goal
  outright, and the platforming leaves with him. It is a **scope decision, not a deletion** - both beats are
  built, on `main`, still in the level, and back on the cut list at positions 1 and 2, so either can return
  if beats 1 to 3 land early. What it changes in practice: the ending moves from last in the queue to the
  only unbuilt beat in the goal; the three committed character models (`CafeWalker`, `SK_StreetGoon`,
  `SK_CafeCoworker`) all live in beats 1 to 3 and so are now the most valuable unfinished work in the repo;
  the run-length problem gets harder, because the two beats that added minutes are the ones that left; and
  Splice becomes a power handed over in the last fight with nowhere in the goal to use it. The last two are
  open questions in "Still to decide", not answered here.
- **2026-11-13 (12:57 PM Pacific): merge `playtest` into `main` on feature-freeze day, before any tester
  confirmed it** (Manny, the Team Owner). "merge". `CLAUDE.md` says the builder merges when testers confirm;
  nobody had played the Splice blink, none of the city had been imported, and there was no packaged build. The
  call was made anyway so the two branches stop drifting with eleven hours of freeze day left, which is the same
  reasoning as the Nov 12 evening merge below. PR #3 went in as `f9f05c0` and `playtest` was fast-forwarded to
  match. What is untested is listed in "Where we are" above rather than left for someone to discover.
- **2026-11-13 (11:00 AM Pacific): spend the credits on the goons, and keep ComfyUI + Meshy as the pair**
  (Manny, the Team Owner). "spend them", and then "Remember to use ComfyUI and Meshy for consistency." This
  **confirms the Nov 13 4:20 AM decision above rather than changing it**, and closes the deviation reported that
  morning: the goon had been built with TRELLIS only because the meshy.ai session had lapsed to logged-out, not
  because credits were short. The Team Owner logged the browser profile back in, 35 credits were spent, and the
  **Meshy build is canonical** (`SK_StreetGoon.fbx`, Smart Rig, 76 bones) with `StreetGoonTrellis` kept beside it
  as the free fallback. The pipeline is now settled in both halves: **reference sheets are drawn locally with
  ComfyUI + Qwen-Image for 0 credits, models are made on Meshy for 35** - so the whole cast is drawn in one hand
  and modelled by one generator. It was measured before being recorded: the Meshy bake keeps **89%** of the
  reference sheet's head-to-body lightness contrast against TRELLIS's 47%. The cost accepted with it is that
  Smart Rig's `Bone_000...` names need retarget chains mapped by hand in Unreal.
- **2026-11-13 (4:20 AM Pacific): Boss 3 is in only if everything else is finished** (Manny, the Team Owner).
  "Boss 3 will only be in if we can finish everything else." This **narrows the six-beat demo plan** approved on
  Nov 12 (below), which had made the Stunt Double boss a required beat 5; he is conditional again. The fight
  itself is already built on `playtest` - `BP_StuntDouble`, his diving stand-ins and the Freeze Frame counter -
  so what is left for him is art and an arena, not mechanics. Nothing else waits on him, and no Meshy credits
  go on him until beats 1 to 4 play through.
- **2026-11-13 (4:20 AM Pacific): Meshy makes the models; TRELLIS is the credit backup** (Manny, the Team
  Owner). "We should use meshy where we can, Trellis can be a backup if we run out of credits." This settles the
  TRELLIS-vs-Meshy question raised on Nov 12: **`SK_CrashDriver` (Meshy) stays the canonical crash driver** and
  `SK_CrashDriverTrellis` stays on disk as the fallback. The local TRELLIS.2 path on GameStation's 5090 costs
  **0 credits** and names bones the way Epic's mannequin does (so Unreal retargets onto it without the nine
  hand-mapped chains a Meshy skeleton needs) - but Meshy's output was measured cleaner, and credits are not
  short (about 8,400 left, 35 per character). Reach for TRELLIS when the credits run low, not before.
- **2026-11-13 (4:20 AM Pacific): `playtest` is merged into `main`** (Manny, the Team Owner). "Go ahead and
  merge to main." `main` was fast-forwarded to `playtest` - 19 commits, no merge commit and no conflict, because
  `main` was a strict ancestor. It carries the Unreal imports, the Splice hand-over, the fight animation, beat 1's
  quick time event and the boss 3 fight shell. **The Team Owner has played the plaza fight**; the rest of that
  list has been checked in the editor only, and the 12-step play list in
  [`FIRST_BUILD_LEDGER.md`](FIRST_BUILD_LEDGER.md) is still not ticked off step by step.

- **2026-11-13 (2:55 AM Pacific): The explosion opens a bullet-time window; the player presses Freeze Frame
  themselves** (Manny, the Team Owner). The explosion goes off **2 seconds** after the power is picked up (was
  1.2) and drops the world into **bullet time at 0.25 speed for 3.5 real seconds**, instead of freezing time
  *for* the player. Inside that window **E** activates Freeze Frame normally and the ten-second freeze takes
  over. "this way they are given a chance to learn how to use the power" - the old auto-freeze taught nothing,
  because the player never pressed the button that beat 1 exists to teach. Miss the window and the shrapnel
  finishes its flight; the coworker dies once and the level continues. Built and verified in Play-In-Editor
  (`BP_Player.PlayerBulletTimeStart/End/TickBulletTime`, `BP_Coworker.BulletTimeOnExplosion`), not yet by a
  person.
- **2026-11-13 (2:55 AM Pacific): Freeze Frame counts down out loud, like a film set** (Manny, the Team
  Owner). At **5 seconds remaining** a large number appears on the HUD and a 1 kHz pop plays on each whole
  second - 5, 4, 3, 2, 1 - with a clapperboard "Action" cue when time resumes. This is the first sound in the
  game: `SFX_CountdownBeep`, `SFX_CountdownAction` and `SFX_BulletTime`, synthesized by `tools/make_sfx.py`
  from the standard library, so nothing needs crediting. **Nobody has heard them yet.**
- **2026-11-13 (2:55 AM Pacific): The latte art minigame waits until the Splice boss is beatable** (Manny, the
  Team Owner). It is no longer an open keep-or-cut question - it is sequenced: "We can start working on the
  latte art minigame after we complete the sequences up until we defeat the Splice boss and add the assets
  into the game." So the queue is beats 1-3 playable with their art in, **then** the minigame. It stays under
  Stretch until that bar is met.
- **2026-11-13 (2:55 AM Pacific): GameStation draws reference art too** (Manny, the Team Owner). "We should
  have GameStation create more assets if we aren't making any here. We should also install ComfyUI here in
  case we need to start generating here so the art stays consistent." ComfyUI + the same **Qwen-Image** models
  M Station uses are now installed on GameStation's RTX 5090 (`tools/install_comfyui.sh`), pinned to the exact
  filenames `tools/gen_images.py` asks for so the two machines draw in the same hand. Verified: ComfyUI 0.45.0
  on torch cu128, all four models present, server answers on :8188.

- **2026-11-13 (1:15 AM Pacific): We build in the order the game is played** (Manny, the Team Owner). When
  there is a choice of what to do next, the earliest unfinished beat wins, not the most interesting one: "if we
  still have work to be done on earlier beats we should do that." The first thing this rule found was that
  **beat 1 had no coworker, no shrapnel and no action button** while beat 5 already had a working boss power -
  built and shipped the same hour (`BP_Coworker`, `BP_Shrapnel`, `BP_Player.PlayerInteract`, see the devlog).
  Read the beats list under Open as a work queue, top down.
- **2026-11-13 (1:15 AM Pacific): Splice gets a job in the beat-5 fight after all** (Manny, the Team Owner).
  Splice lets the player **get past the attack stand-in** - the double the boss tags in to fight for him - and
  reach the boss directly. This softens, but does not cancel, the deliberate rule break recorded in
  [`PITCH.md`](PITCH.md): **Freeze Frame is still the counter** to the diving doubles, because stopping time is
  the only thing that stops a dive. Splice is the answer to the *bodyguard*, not to the soak. **Not built**:
  Splice itself does not exist yet (`HasSplice` still gates nothing), and under the work-order rule above it is
  beat 4's job to build it.
- **2026-11-13 (1:15 AM Pacific): The attack stand-in leaves when it has nothing to fight** (Manny, the Team
  Owner). The double that fights for the boss only stays on the field while it is in combat; once nothing is in
  its range to attack, a timer starts and it disappears. This stops the arena silting up with tagged-in doubles
  during a long fight, and it makes running away from the bodyguard a real option rather than a stall. **Not
  built** - it is a change to `BP_StuntStandIn`, and it is beat 5 work.
- **2026-11-13 (12:30 AM Pacific): How the Stunt Double boss fights** (Manny, the Team Owner). His doubles are
  copies of **himself**, not of the player. They soak damage the way a stunt double does - they jump into the
  path of the blow - so while any of them is standing, every hit meant for the boss lands on one of them
  instead. **The counter is Freeze Frame**: with time stopped nobody can dive, so the hit reaches him. He can
  also **tag in** a double that actually fights, played for the film trick it is. This settles the three-way
  disagreement between this file, `PITCH.md` and the boss 3 proposal in `CHARACTERS.md`, and it drops the
  "doubles wear the player's face" idea, which was the expensive half. Built on `playtest` the same hour:
  `BP_StuntStandIn`, a stand-in redirect in `BP_EnemyBase.EnemyTakeHit`, and the spawn logic on
  `BP_StuntDouble`. Verified in Play-In-Editor, not yet by a person.
- **2026-11-13 (12:30 AM Pacific): "Boss 1" means the head of his organisation, not the first fight** (Manny,
  the Team Owner). The crash driver is boss 1 because he is the boss of his faction; he is never fought. The
  **first boss the player actually fights is the cleaver boss**, who gives Splice. Wording only - no change to
  the ladder.
- **2026-11-12 (late evening): The jam entry is a demo in six story beats** (Justin). Cafe, crash and Freeze
  Frame with the coworker rescue as its lesson; street thugs; the Splice boss; platforming across destroyed
  buildings with goons; the Stunt Double boss, who copies himself; a fade to a "continue". The beats and what must
  be in before people playtest are under Open. This **supersedes** three things from earlier the same day: Stunt
  Double as "boss 3, only if there is time" (it is the demo's final fight); Stunt Double and the Splice
  platforming section on the cut list (both removed); and the Director with two rule scenes on Friday's list (the
  demo ends before him). It also confirms the ladder: the dead crash driver gives Freeze Frame, the Splice boss
  gives Splice. Recorded from Justin's project chat, and **approved by Manny, the Team Owner, on Thu Nov 12,
  11:45 PM Pacific** (in his chat: "Plan is approved").
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
