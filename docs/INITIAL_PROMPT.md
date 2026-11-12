# Initial build prompt: one big sweep

**Status: draft, not agreed (Nov 12).** Written from Justin's answers that morning. It has not been run, and it
must not be run yet: the scope it builds — one large city, about 30 minutes — is still under **Waiting for a yes**
in [`docs/ROADMAP.md`](ROADMAP.md), which says in its own header *"Never build from these as if they were agreed"*.
When the team settles the scope, that decision goes in ROADMAP's Decisions and this line changes to point at it.

**How to use it:** open a Claude chat on the repo on the **builder** computer (Computers table in `docs/TEAM.md`),
on the Fable model, with Unreal open and the MCP answering, and paste everything below the line. It can't run on a
maker or tester computer: they may not save Unreal files.

**Why it exists:** `CLAUDE.md` says "one small change at a time, then stop". That stays the rule for every other
chat. This prompt is a one-time exception the team gives on purpose, like the practice repo's overnight run: one
long run that builds the whole grey-box game, with the piece-by-piece work handed to subagents so nothing gets
dropped or quietly made smaller.

---

Build the whole of Jump Cut in grey boxes in one sweep. You are the **lead**. You plan, hand out work, check it and
keep the books. You do not build the pieces yourself.

## 1. Before you start
1. Run `hostname` and check this computer is the builder. If it isn't, stop and say so.
2. Read `CLAUDE.md`, `docs/ROADMAP.md`, `docs/PITCH.md`, `docs/RULES.md` and the `unreal-blueprint` skill. Open with
   the usual line: time left to the deadline and where we stand against today's checkpoint.
3. Write the ledger (section 5), show us the plan in fifteen lines or fewer, then start. Don't wait for an answer.

## 2. What this prompt changes, and what it doesn't
- **Once the team has agreed the scope, this prompt is the "go"** for everything in section 6: for this run only,
  don't stop after each change, and keep going until the ledger is finished or section 8 tells you to stop. Until
  then it is a draft. If you are reading this and `docs/ROADMAP.md` still lists "One large city level" under
  *Waiting for a yes*, stop and ask the team — the agreement is recorded in ROADMAP's Decisions, never here.
- **Everything else in `CLAUDE.md` still applies**, to you and to every subagent: stop Play mode before every edit,
  save after every batch, pull and lock before touching a committed asset, compile and read each graph back,
  Blueprints only (no C++), unique function names, and the "wait for go" list for anything that can't be undone
  or costs credits.
- **Branch:** `<this computer>/first-build`, started from **`main`** — then merge `mendezm87/anime-look` into it for
  the cafe scene and the cel shader. **Don't branch from `anime-look` directly.** It was last pushed before these
  rules existed, so it has none of `docs/ROADMAP.md`, `docs/PREJAM.md`, `docs/devlog/` or the `CLAUDE.md` sections
  that section 1 sends you to read — you would be told to read files that aren't there. Check both directions
  first (`git log --oneline main..mendezm87/anime-look` and `...anime-look..main`) and say what you found. If the
  merge brings a `docs/DEVLOG.md` entry that isn't in `docs/devlog/` yet, move it into its own file before you build.
  This is untested work: it does not reach `playtest` or `main` until a person has played it. Every commit message
  starts `Untested:`.
- **Nothing comes from the practice repo except scripts** (jam rule §7h). Its city, cars and maps are pre-jam work.
  Build the level again here. Keep `docs/PREJAM.md` true: anything written during this run is jam work.
- **Not in this run:** final art, sound, cut scenes (leave markers, section 6), factions that behave differently or
  fight each other, dialogue systems, more than one level.

## 3. The game you are building
The team's own scope from `docs/PITCH.md`, not the smaller proposal. About **30 minutes** start to finish.

**Powers and bosses** (each boss is beaten with the power from the one before):

| # | Power | What the player does with it | Its boss |
|---|---|---|---|
| 1 | Rewind | Slide back along the last 10 seconds to where you were, health restored | None. The driver in the cafe hands it over |
| 2 | Freeze Frame | Everything else stops for 10 seconds | Freezes the arena and gets free hits. Counter: Rewind |
| 3 | Splice | A short teleport. The out-of-combat power: the second half of the city needs it | Blinks around and attacks through portals. Counter: Freeze Frame |
| 4 | Stunt Double | A copy fights beside you and takes one hit | Makes a double of you plus decoys. Counter: Splice |
| 5 | Director's Cut | Only at the ending | The Director calls 10-second scenes with one rule each: "No abilities", "The floor is gone", "You can't move left". Counter: Stunt Double |

**On the fifth power's name:** `docs/PITCH.md` still calls it "Final Cut", which is an Apple trademark, and §15d
allows no trademarks but the Unreal logo. "Director's Cut" is the proposed replacement and the table above uses it,
so the two files disagree on purpose: **the Team Owner is holding the rename**, so don't rename it in `PITCH.md` or
anywhere else yourself, and don't put "Final Cut" into anything a judge sees. Hold the name in one named variable
so the swap is a single edit when the call comes.

**Fighting:** fists. One melee button with a short combo. Three hits, the third knocks back. 100 health.
**Goons:** one ordinary enemy type that walks up and punches, in groups on the streets between bosses, there to be
pushed around. One Blueprint, recoloured per district at most.
**You lose** when health runs out while Rewind is on cooldown. You restart at the last checkpoint you reached.

**The level: one large city**, `Content/Game/Maps/Lvl_City`, One File Per Actor on, real scale (1.0) for the
third-person character. Laid out the way the practice city was: a street grid of solid blocks, sidewalks, alleys,
all placed by a script from a table of numbers so the layout can be changed without hand-placing. The player crosses
it in five stretches:

1. **Cafe district.** Start in the cafe (a corner block; the crashed car and the driver are grey boxes, or the
   anime-look branch's `Lvl_Cafe` pieces if you started from it). Streets with goons lead to the first plaza.
2. **First plaza:** the Freeze Frame boss. Then more streets and goons to the second plaza.
3. **Second plaza:** the Splice boss. Beating him opens the second half of the city.
4. **The broken half.** Streets here are cut by gaps, raised walkways and rooftops that can only be crossed with
   Splice. Platforming with some goons, then the third plaza: the Stunt Double boss.
5. **The climb.** More travel and Splice platforming up to the tower at the far corner. The Director is at the top.

Each plaza closes behind the player and opens when its boss is beaten. Size the city so that walking and fighting
through it takes about 30 minutes: roughly 6 by 6 blocks. Say what you chose and why.

**The look:** apply the team's cel shader (post-process `M_AnimeLook`, characters marked with Render CustomDepth;
`tools/unreal_make_anime_look.py` on the anime-look branch builds it) to the city level, so grey boxes already read
in the game's style.

**Cut scenes come later.** Put an empty, named `BP_SceneMarker` where each one will go: the crash in the cafe,
each power handed over, the Director's reveal, the ending.

**Tuning:** every number a designer might change (speeds, cooldowns, health, damage, durations, goon counts) is a
named variable with a sensible default. The final report lists them and where they live.

## 4. How the work is split: you lead, subagents build
A single chat that builds all of this starts skipping steps and shrinking pieces as it fills up. So:

**The lead (you, Fable):**
- Owns the plan, the ledger, the hand-out order and the final report. Reads results, decides what is next.
- Never writes a Blueprint graph, places actors or edits a material itself. If you catch yourself doing a packet's
  work "because it's quick", stop and hand it out.
- Never marks a packet done. Only a checker's verdict does that (below).

**Builders (one subagent per packet):** each builds exactly one packet from the ledger, start to finish, in a fresh
context, and returns a short report. Then it ends. A new packet gets a new subagent.

**Checkers (one subagent per packet, never the one that built it):** given the packet's brief and "done means" list
but **not** the builder's report. It reads the graphs back, runs the checks, takes a capture, and answers each
"done means" line with pass or fail and what it saw. A fail goes back to a new builder with the checker's notes. Two
fails on the same packet: the lead writes down what's wrong, marks it `failed` and moves on.

**The editor rule: one pair of hands in Unreal at a time.** There is one editor, one Play mode and one save state.
Two subagents editing at once will freeze it or lose work.
- Packets marked **Unreal** run strictly one after another: builder, then checker, then the next packet.
- Packets marked **outside** never touch the editor and may run in parallel with each other and beside one Unreal
  packet: writing graph text to `Saved/*.json` for a later Unreal packet to load, writing the Python that lays out
  the city, working out the city's table of numbers, devlog entries, and reviewing a finished packet's graph text.
- A good rhythm: while one subagent builds in Unreal, two or three others prepare the text and scripts for the
  packets that come next.

**Which model does what** (set it on each subagent you start):

| Work | Model | Why |
|---|---|---|
| High-level planning and review: the lead; designing a system before it is built (the Rewind trail, the boss parent, the Director's rule scenes, the city's route and pacing); every checker; the final audit | Fable | Judgement and catching what's missing |
| The workhorse for complex code: building a Blueprint system through the MCP; debugging one that failed a check | Opus | Long, careful tool work |
| Simpler coding tasks: layout and placement scripts, graph text from a finished design, the HUD and menus, devlog entries, captures, the tuning-variable list | Sonnet | Clear spec, lots of typing |

If a cheaper model fails a packet's check once, give the retry to the next model up.

**What every brief contains.** A subagent knows nothing you don't tell it. Each brief has:
1. The packet's ID and one-sentence goal, and how it fits the game (two lines).
2. Files to read first: `CLAUDE.md` ("Lessons from practice" and "How to work with us"), the `unreal-blueprint`
   skill, and any earlier packet's assets it builds on, by full path.
3. Exactly what to build: asset names and folders (`Content/Game/<Type>/`, `BP_`, `M_`, `WBP_` prefixes), variables
   and their defaults, functions and what each does.
4. What it must not touch: other packets' assets, anything outside its folders, anything locked by a teammate.
5. The packet's "done means" list, word for word from the ledger.
6. The editor rules: stop Play mode first, lock, back up a graph before replacing it, compile, read back, save,
   check `git status`. No sleeping inside tool scripts. Keys read by polling in Tick, no Timelines.
7. What to send back: what it built and where, what it checked and how, what it could not check, anything it made
   smaller than asked and why, and the actual text of any error. No "should work".

**Shrinking is never silent.** If a builder can't do a packet as written, it says so and stops; it doesn't deliver
a smaller thing as if it were the packet. The lead then splits the packet, or records it in the ledger as
`smaller` with the reason. A packet is never dropped from the ledger.

## 5. The ledger
`docs/FIRST_BUILD_LEDGER.md`, written before any building and committed with every packet. One row per packet:

| ID | Packet | Kind | Model | Needs | Done means | Status | Notes |
|---|---|---|---|---|---|---|---|

- **Kind:** Unreal or outside. **Needs:** the packets that must be verified first.
- **Done means:** two to five checks a checker can run without playing: "compiles", "`RewindStart` called on the live
  player moves it back to within 50 cm of where it stood 10 seconds earlier", "a capture from the game camera
  shows the plaza gate closed".
- **Status:** `todo`, `building`, `checking`, `verified`, `smaller`, `failed`. Only a checker's pass makes
  `verified`.
- **Notes:** who built it, what the checker saw, what still needs a person in Play mode.

After each verified packet: commit on the branch (`Untested: <packet>`), with its devlog entry file
(`devlog-entry` skill) and the updated ledger. Update "Where we are" in `docs/ROADMAP.md` at the end of each group
below. Don't write into Decisions; only people decide.

## 6. The packets
Break these down further where a packet is more than about an hour of one subagent's work. Keep the order of the
groups; inside a group, follow "Needs".

**A. Ground floor**
- A1 Branch, `Lvl_City` (empty, lit, One File Per Actor), `BP_JumpCutGameMode`, folders. (Unreal)
- A2 Design note: the city's route, block table and where each plaza, gap and marker goes, sized for 30 minutes.
  (outside, Fable)
- A3 The cel shader applied to `Lvl_City`. (Unreal)

**B. The player and a fight**
- B1 `BP_Player`: health, fists combo, hit reactions, input by polling. (Unreal)
- B2 HUD: health, one icon per power with its cooldown. Icons and bars, no sentences. (Unreal)
- B3 `BP_Goon`: walks up, punches, can be knocked back and beaten; a spawner that places a group. (Unreal)
- B4 Rewind: design (outside, Fable), then build (Unreal).

**C. The city**
- C1 `BP_CityBlock` and the layout script from A2's table. (script: outside; placing: Unreal)
- C2 Plazas with gates that close and open. (Unreal)
- C3 The broken half: gaps, walkways and rooftops for Splice. (Unreal)
- C4 The tower and the climb. (Unreal)
- C5 Goon groups along every stretch; checkpoints; `BP_SceneMarker`s. (Unreal)

**D. Bosses and powers** (design each outside on Fable first, then build)
- D1 `BP_BossBase`: health, a warning before each attack, defeat hands over a power, opens its plaza.
- D2 Freeze Frame boss, and the player's Freeze Frame.
- D3 Splice boss, and the player's Splice.
- D4 Stunt Double boss, and the player's Stunt Double.
- D5 The Director: the three rule scenes, each shown on screen in a few words, and the ending.

**E. Start to finish**
- E1 Title, win and lose screens, restart from the last checkpoint. Input mode reset to "game only" on level start.
- E2 A run-through by a checker: every plaza can be reached in order by calling the player's functions and moving
  it marker to marker, and every gate opens. (Unreal, Fable)
- E3 First packaged build with the `package-build` skill, launched once. (Unreal)

**F. Final audit** (Fable, a fresh subagent that has seen none of the run): reads this prompt and the ledger side
by side and lists every line of the prompt that has no verified packet behind it.

## 7. If you fall behind
Don't shrink everything a little. Cut whole things, from the bottom of this list up, and record each cut in the
ledger: D4 Stunt Double (boss and power), C4's platforming (keep a plain climb), C3's platforming (keep the Splice
fight), goon variety. The roadmap's cut list is the team's order; this follows it.

## 8. When to stop
- Unreal freezes, the MCP stops answering, or a save prompt blocks the editor: stop and tell us. Don't start Unreal
  as a child of the chat.
- Something needs the "wait for go" list (deleting assets, a forced unlock or push, credits, C++).
- A teammate holds a lock you need: skip that packet, note it, carry on.
- The ledger is finished and the audit is done.

## 9. The final report
- What was asked, what was built and what was left out, with numbers: packets verified, smaller, failed and cut;
  Blueprints made; commits.
- The audit's list, unedited.
- **What was checked by subagents** and **what a person still has to play**, as an exact list: which key, what
  should happen, in play order from the cafe to the tower. Feel is never yours to call verified.
- Every assumption you made, and the tuning variables with where they live.

