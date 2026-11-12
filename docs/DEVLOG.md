# Devlog

Our Glass Box devlog: how two gamers with almost no dev experience built an Unreal game with AI agents.
Link screenshots and clips from `docs/media/`. Our practice-week devlog lives in the practice repo.

## Template for each entry

### YYYY-MM-DD — short title
- **What we asked for:**
- **Prompt(s) we gave the agent:**
- **What happened:** (including failures, retries and dead ends)
- **What we learned:**
- **Media:**

---

### 2026-11-12 — The jam repo is born
- Created by `tools/bootstrap/new_jam_repo.ps1`: a fresh Unreal 5.8 project from Epic's Third Person Blueprint template,
  with our MCP, import and editor settings, our agent instructions, and the scripts we prepared during practice week.
- No gameplay, levels or art were copied from practice. Everything in the game is made from here on.

### 2026-11-11 to 12 — The theme drops, and the game gets a name
- **What we asked for:** Ideas for the theme "Directors Cut", then a name for the game the team came up with, then the repo.
- **Prompt(s) we gave the agent:** "The theme has dropped "Directors Cut"" / "This theme is vague and can be abstract they said" / "I need some help thinking of a name for the game. We sort of had a story going already where the main character is a normal person working at a coffee shop when a car comes crashing through. The main character gets a mysterious power from the person in the vehicle because they died. The power leads them to four other powers which eventually complete the entity's power. At the end, it turns out that power was being controlled by the bad guy of the story, and he's tricked the MC into restoring him to full power." / "The first power is called Rewind. Hits taken in the last 10 seconds miss on replay." / "Are those the best names you could come up with?" / "Give me a prompt to describe the game so I could hand it to other AIs to also collaborate on the name" / "Jump Cut was suggested, what do you think?" / "Do it and let's get the repo up."
- **What happened:**
  - Claude offered six pitches for the theme. The team already had its own story (the coffee shop, the crash, five powers, a villain pulling the strings) and kept that instead. The story and the powers are the team's; Claude's part was the scope.
  - Naming took several rounds. Claude's first list was flat and we said so ("Are those the best names you could come up with?"). The second list was better (Back in Ten, As Directed, The Missing Reels, Off Script). We then asked Claude for a description of the game to hand to other AIs, and one of them suggested **Jump Cut**.
  - Claude backed Jump Cut once it saw the powers list: the third power, Splice, is a teleport, so the name describes what the player does as well as the film theme. It searched Steam and itch.io and found no game with that exact name.
  - Claude flagged that one power name, "Final Cut", is an Apple trademark (the jam allows none) and suggested "Director's Cut".
  - Scope: the team's list is five powers, five bosses and factions. Claude proposed a smaller Rewind (only the player rewinds), one boss Blueprint with a setting, and a cut list with Stunt Double and the factions at the top. Not agreed yet; it's written in `PITCH.md` as a proposal.
  - Before making the repo, Claude checked every computer and sister project for lessons we hadn't written down, and brought in 12 helper scripts and three lessons from GameStation's first jam hours.
  - First try at the bootstrap went wrong: run from Git Bash, the backslashes in the folder path were swallowed and the project landed in a folder called `Userstheclcodejump-cut` inside the practice repo. Deleted, and run again from PowerShell.
- **What we learned:** Ask more than one AI for names, and settle the name before making the repo: the Unreal project name is hard to change later. Pass Windows paths from PowerShell, not Git Bash.
- **Media:** (none)

### 2026-11-12 — We audited ourselves against the rules, and found four things wrong (7:38 – 8:10 AM)
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
