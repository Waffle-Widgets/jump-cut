# 2026-11-13 — The demo gets shorter on purpose (Justin's Mac mini, docs only)

- **What we asked for:** make the plan say the demo is beats 1 to 3 plus the "to be continued", with the
  destroyed-building platforming and the Stunt Double boss as nice-to-haves.

- **Prompt we gave the agent:** *"Because of time, we're going to focus on beats 1-3 and making that first
  half be amazing. We might have to move beat 6 (to be continued..) to beat 4 and drop the current 4 and 5.
  Make the plan reflect that as the goal for now. The two dropped beats will be nice to haves."*

- **What happened:** the rescope is written into [`ROADMAP.md`](../ROADMAP.md) (the beats section, the day
  table, the build queue, the cut list, the open questions and a dated entry in Decisions naming what it
  supersedes), [`PITCH.md`](../PITCH.md), [`PLAYTEST.md`](../PLAYTEST.md) and
  [`FIRST_BUILD_LEDGER.md`](../FIRST_BUILD_LEDGER.md). **Nothing in the game changed** — no `.uasset`, no
  level, no LFS lock. Both dropped beats are still built, still on `main` and still in the level; they moved
  to the top of the cut list as nice-to-haves, at positions 1 and 2, so either can come back.

  Writing it down turned up three things that were not obvious when the instruction was given, and all three
  are consequences of the scope change rather than bugs in it:

  1. **The ending went from last in the queue to the only unbuilt beat in the goal.** As beat 6 it was the
     thing after everything else; as beat 4 it is the finish line. It also cannot be started: nobody has
     decided *what* the "to be continued" is (issue #17), which blocks building it (issue #10). Those two
     issues were the least urgent on the board this morning and are now the most.

  2. **Splice is handed over in the demo's last fight and the demo has nowhere to press it.** The Splice
     boss still grants `HasSplice` and the 600 cm blink still works, but the three gaps it exists to cross
     are in the dropped beat. That is either the right cliffhanger (you get a new power, then "to be
     continued") or a reward the player never uses. Recorded as an open question, not answered.

  3. **`Marker_Win` is now in the wrong place for a different reason.** It sits at (14400, 0, 0) on the
     Stunt Double's landing pad, where beat 4's placer parked it. Under the six-beat plan that was "the
     player wins early". Under the four-beat plan it means the win screen is two dropped beats east of where
     the demo now ends, so beating the Splice boss leaves you walking through optional content to finish.
     Three ways out are written into "Still to decide" — end at the plaza, keep the sections as an optional
     coda, or block the route east — and all three are level edits, which this Mac is only `builder (beat 4)`
     for, so none were made.

  On the GitHub board: the three issues that belong to the dropped beats (#9, #29, #36) moved to the
  out-of-scope milestone, #10 and #17 moved up as the ending's blockers, and #21 ("does the player get Stunt
  Double in the demo?") was closed — the rescope answers it, because the boss who would hand it over is out
  of the goal.

- **What we learned:** a scope cut is a set of consequences, not a line through two rows. The instruction
  took one sentence; what it actually did was promote the least urgent decision on the board to the critical
  path, orphan a power the player is still given, and change what a misplaced win marker means. Writing the
  plan out row by row is what surfaced all three — and the second and third would both have been found by a
  player instead, at the end of a demo we had just called finished.

  The other half of it: **dropping a beat is cheap precisely because the beat was built.** The platforming
  and the Stunt Double fight cost nothing to keep on disk and nothing to drop from the goal, and the only
  thing that would have made this expensive is if they had been half-built and unverified. The cut list is
  more useful full of finished things than full of plans.
