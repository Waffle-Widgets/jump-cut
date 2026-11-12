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
