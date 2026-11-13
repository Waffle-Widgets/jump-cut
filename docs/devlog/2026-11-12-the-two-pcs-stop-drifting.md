# 2026-11-12 — The two PCs stop drifting (M Station)

- **What we asked for:** "Close out any forms that have been answered already. We should merge so we don't drift.
  Then what's next? Should we work from M_station or GameStation?"

- **Prompt(s) we gave the agent:** the words above, exactly.

- **What happened:**
  - Two machines had been working all evening without meeting. `main` was 1 commit ahead (the colour audit from
    M Station) and `Gamestation/first-build` was 26 ahead (the whole grey-box game). The merge base was
    `b59c327`, and the gap was not just big, it was *overlapping*: the same three docs — `ROADMAP.md`,
    `PREJAM.md`, `CHARACTERS.md` — had been edited on both sides the same evening.
  - The merge was tested with `git merge-tree --write-tree` **before** touching the working tree, which named
    the two real conflicts up front without putting the clone in a conflicted state. Worth keeping: you can ask
    git "would this merge?" without starting the merge.
  - Both conflicts were pure additions at the same spot. `PREJAM.md` — both sides appended rows to the jam-work
    table; kept both, in date order. `ROADMAP.md` — both sides appended to **Decisions**; kept all four, and let
    the branch's fuller cel-shaded-anime entry *replace* the shorter one from `main` instead of sitting next to
    it, because the roadmap's own rule is that nothing lives in two places.
  - While in there, one decision that existed only in chat got written down: **the "Final Cut" rename is held**.
    The name stays only in `PITCH.md` as a design note and must change before it reaches in-game text, the
    itch.io page or the video (§15d). It was sitting in *Still to decide* as "the Team Owner is holding it",
    which is not the same thing as a decision — so it moved to Decisions and left the open list.
  - `playtest` was 47 commits behind with nothing of its own, and it is the branch testers pull from. Since it
    was a strict ancestor of `main`, it was fast-forwarded — lossless, and Justin now has something to play.
  - After the merge, three branches hold nothing `main` does not: `mendezm87/anime-look`, `justin/agent-rules`
    and `playtest`. `Gamestation/first-build` is 2 behind and 0 ahead.

- **What we learned:**
  - **The honest cost of this merge, written down rather than buried:** every commit on that branch is labelled
    *Untested* and **no person has played any of it**. `CLAUDE.md:220` says untested `.uasset` work is pushed to
    a branch, *played on another PC*, and only then merged. The Team Owner chose ending the drift over that rule,
    so `main` now carries untested Unreal work. That is a real trade, not a formality: `main` is what a new PC
    bootstraps from. The warning is in `ROADMAP.md`'s "Where we are" so nobody reads `main` as known-good.
  - **A conflict you resolve the same evening is cheap; the same conflict in two days is not.** Both sides were
    appending to the same two tables. Nothing was lost here because both authors were still reachable — one of
    them being this chat.
  - **"The Team Owner is holding it" is not a decision.** A held decision with no recorded trigger reads as an
    open question forever. Writing the trigger down ("before it reaches anything a player or judge sees") closes
    it without forcing the rename today.

- **Media:** none — this episode is git history. The branch picture is in `ROADMAP.md`.
