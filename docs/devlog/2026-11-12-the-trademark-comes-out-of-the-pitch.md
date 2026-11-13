# 2026-11-12 — The trademark comes out of the pitch (M Station)

- **What we asked for:** the Team Owner answered the open rules form: rename "Final Cut" **now, today**, and the
  confirmation form link has been sent to Justin.

- **Prompt(s) we gave the agent:** the form answers, quoted —
  *"When should I rename 'Final Cut' to 'Director's Cut'?" → "Now — do it today"*; *"Have you sent Justin the form
  link from the Forms tab?" → "Yes"*.

- **What happened:**
  - Power 4 is now **Director's Cut** in every live design doc: `PITCH.md` (the powers table and the theme line),
    `ROADMAP.md` (the power ladder under "Still to decide") and `INITIAL_PROMPT.md` (which had already half-landed
    the new name in its table while telling agents not to finish the job — that contradiction is gone).
  - The decision in `ROADMAP.md` was **rewritten, not appended to**. It had said the rename was *held*; it now says
    the rename is *done* and that it supersedes the hold recorded earlier the same day. The roadmap's own rule is
    that nothing lives in two places, and a file that says both "held" and "done" is worse than one that says
    neither.
  - Checked before changing anything, with `git grep -i` over every tracked file rather than over `docs/` alone:
    the name was in **no asset name, no Blueprint graph text and no widget string** — eight hits across five docs and
    five more in the devlog. So this was a documentation rename only, and nothing had to be opened in Unreal. No LFS
    locks were needed or held.
  - **The devlog keeps the old name on purpose.** Five entries discuss "Final Cut" as the thing being decided, and
    rewriting them would be editing the record of a decision to hide that the decision was ever made. §15d bans
    trademarks in the *entry* — in-game text, the itch.io page, the video — and the devlog is discussion, which is
    also exactly what the Glass Box is for. `FIRST_BUILD_AUDIT.md` had already reasoned this out; its finding now
    carries a "settled" note instead of being deleted.
  - `FIRST_BUILD_AUDIT.md`'s person-only item 14 was two decisions in one line ("the rename *and* which boss gives
    Rewind"). Half of it is now answered, so it was split: Rewind stays open, the rename is marked settled.
  - `TEAM.md` records that Justin's confirmation request went out on Nov 12 and his reply is outstanding. His Epic
    address stays **provisional** — sending the ask is not the same as getting the answer, and §1c/§2/§13 need the
    answer.
  - One stale line left alone deliberately: `FIRST_BUILD_LEDGER.md:126` lists the rename under "Not fixed, because
    they need people" inside a dated "After the audit (Thu Nov 12, evening)" block. That is a record of what was
    true that evening, not a live to-do, so it was not edited.

- **What we learned:** A held decision is a liability with a date on it. For a day, three files disagreed on the name
  of the same power and one of them told agents to keep it that way — which is how a trademark reaches a video by
  accident, not by anyone choosing it. The cheap fix is the one we took: keep the live docs in one voice, and let the
  devlog be the only place the old name survives.

- **Media:** (none)
