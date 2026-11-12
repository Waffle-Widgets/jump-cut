# 2026-11-12 — We audited ourselves against the rules, and found four things wrong (7:38 – 8:10 AM)

- **What we asked for:** A check that the new repo and the anime demo follow the MegaJam rules, and then the fixes.
- **Prompt(s) we gave the agent:** "A new repo has been created for the MegaJam project called jump-cut. A demo for
  the cell shader was implemented for Justin to review. Manny thinks it can use some polishing, but it seems like a
  viable option. Make sure we are following the rules of the MegaJam and let us know if we violate any so we may get
  back on track." / "Don't rename the trademark yet. Write the prejam.md and commit the practice-repo trial. Do what
  needs to be done to declare the pre-jam stuff and whatever we need for the glass box devlog. If we need to be
  public then that is fine."
- **What happened:**
  - **The timing was clean, and we could prove it.** Every file in the anime demo is newer than the 9:00 PM Nov 11
    open — the earliest is 11:57 PM Nov 11, just under three hours in. Rule §7h satisfied, with file stamps to show.
  - **Four real problems.** One: "Final Cut", one of the five power names in `PITCH.md`, is an Apple trademark, and
    §15d allows no trademarks except the Unreal logo. (Left in place for now at the team's call; it has to go before
    it reaches in-game text, the itch page or the video.) Two: nothing in the repo *declared* our pre-jam toolbox,
    which the itch.io page asks for. Three: the demo was authored in the practice repo and arrived here as one
    squashed commit, with the real trail sitting **uncommitted** — one `git checkout` away from not existing. Four:
    the repo was private, which would have made the Glass Box devlog link a dead link to a judge.
  - **The declaration.** Wrote `docs/PREJAM.md`: every pre-jam file by category — the agent configs, 13 Claude
    skills, 42 scripts under `tools/`, 28 Blender scripts, the `.ini` config and the repo setup — plus a
    paste-ready paragraph for the form. It names the commit that proves the split (`e9bfc06` is the pre-jam set,
    everything after it is jam work) and, deliberately, also lists the four helper scripts we wrote *during* the
    jam, so nobody can read `tools/` as if all of it were prepared in advance.
  - **The trail.** Committed the practice-repo working tree as `c86ddd6`: 57 files, the scripts, materials, level,
    hero and five capture passes, with a commit message stating when each was made and that it was migrated here.
    The practice repo had also diverged (M Station had pushed the pre-jam script sweep while GameStation worked), so
    this merged, with one conflict in the devlog where both PCs had appended entries — resolved by date order.
  - **Going public.** With the declaration written and the trail committed, made `jump-cut` public so the devlog
    link in the submission resolves for judges.
  - A thing we got wrong and wrote down: our own `jam-rules-check` skill says "practice work in this repo never goes
    into the jam repo", and on the first night we did exactly that. It was legal — the work was all post-open — but
    it cost us the clean history, and we spent the morning reconstructing what a commit-as-you-go habit would have
    recorded for free.
- **What we learned:** A rule you wrote for yourself still has to be read at 11 PM. And "allowed" and "provable" are
  two different things: §7h says Epic may ask for the Git history, so the history is part of the deliverable, not
  bookkeeping.
- **Media:** (none)
