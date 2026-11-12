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

## Where we are (Thu Nov 12, morning)

The jam repo exists with the Third Person template, our tools, skills and docs. No gameplay is on `main` yet. Today's
checkpoint: the core loop (player, the first power, the first boss) playable start to finish in grey boxes. Character
work started on M Station this afternoon: the main character, the crash driver and the mob boss ([`CHARACTERS.md`](CHARACTERS.md)).

## Open

| Day | Goal |
|---|---|
| Thu Nov 12 | Player + the first power (Freeze Frame) + the first fight, in grey boxes, playable start to finish |
| Fri Nov 13 | The Splice boss (the mob boss), the Director with two rule scenes, win/lose and restart screens, first packaged build. **Feature freeze** |
| Sat Nov 14 | Art, sound, juice, playtests, footage. Stunt Double only if Friday went well |
| Sun Nov 15 | Bug fixes and submission only |

## Waiting for a yes

**One large city level** (Justin's proposal, Nov 12: the team still has to say yes)

- The whole game is one city map, laid out like the practice repo's city (a street grid of blocks, sidewalks and
  alleys), rebuilt here from scratch. Cafe start, streets with goons to each boss plaza, a second half that needs
  Splice for platforming, then a climb to the Director's tower. About 30 minutes of play, cut scenes later.
- **This is far bigger than `CLAUDE.md`'s scope guardrail** ("one level, one core mechanic, 3-5 minutes of play").
  The guardrail has not been changed. The team needs to pick one.
- `docs/INITIAL_PROMPT.md` is a draft first prompt for the builder that is written around it.

## Fallbacks (turned down, kept in case we need them)

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

- **Art style.** GameStation is testing an anime look (cel-shaded characters over painted backgrounds) and a cafe
  level in the practice project. If the team keeps it, it moves here as jam work.
- The Director's real name and the final names of the powers.
- Camera: third person behind the player (the template's) unless we choose otherwise.
- **What happens to Rewind.** It was the core mechanic in `PITCH.md` *and* the first boss's gift. The first boss now
  gives Freeze Frame, so Rewind is either the power the main character already has at the cafe, or it is cut and
  Freeze Frame becomes the core mechanic. Nobody has said which. Everything else in the chain still works: Splice is
  countered by Freeze Frame, so the ladder reads Freeze Frame -> Splice -> Stunt Double -> Final Cut.
- **Rewind's size**, if it stays at all. The cut list below says a full rewind of the world is "already cut", but the
  smaller Rewind is only a fallback. One of the two needs a line in Decisions.

## Cut list (in the order we drop things)

1. Factions with different behaviour, and factions fighting each other
2. Stunt Double (power and boss)
3. Splice platforming section (keep the teleport for the fight)
4. Dialogue: one line of text per power instead
5. A full rewind of the world (already cut: only the player rewinds)
6. More than one level

## Later

_(nothing yet)_

## Decisions

- **2026-11-12: The first boss gives Freeze Frame**, not Rewind. He is the driver who crashes through the cafe
  wall in the opening; he still does not fight (Manny).
- **2026-11-12: The second boss gives Splice and is a Japanese mob boss with a cleaver** (Manny).
- **2026-11-12: The main character, the crash driver and the mob boss are the first three characters to build**
  (Manny). Designs and reference pictures: [`CHARACTERS.md`](CHARACTERS.md).
- **2026-11-12: Build to the team's own scope in the pitch** (five powers, the bosses as listed), not Claude's smaller
  proposal. Change it later only if playtesting shows the need (Justin).
- **2026-11-12: Losing restarts at the last checkpoint**, not at the cafe (Justin).
- **2026-11-12: The player fights with fists** for now, and there are ordinary goons between bosses (Justin).
- **2026-11-12: The Splice gap comes after the Splice boss** (Justin).
- **2026-11-12: The devlog is one file per entry** in `docs/devlog/`, so teammates never collide on one file (Justin).
- **2026-11-12: The game is called Jump Cut** (the team; the story is in the devlog entry for Nov 11 to 12).
- **2026-11-11: Prize focus is Glass Box first, Render Royalty second, Best Team third**, Best Overall as a stretch
  (the team; `CLAUDE.md`, "Goals, and keeping us on track").
