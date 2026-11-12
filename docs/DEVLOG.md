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

### 2026-11-12 — A hand-drawn anime look, a coffee shop and a hero (demo branch, not yet agreed)
- **What we asked for:** A look that feels like watching a hand-drawn anime while you control the character, tried out
  on the game's opening scene (the coffee shop), so the team can decide whether to use it.
- **Prompt(s) we gave the agent:** "Can you make a level where we can walk around in 3D as a person in a coffee shop.
  Our main focus is that no matter from what angle it looks like we are watching a hand drawn anime." /
  "This needs to look better or it'll be scrapped" / "Are there any partner companies that can help us make assets?" /
  "looks better but movement is really rough for the player model right now and the arms look weird when he moves" /
  "his jacket is stuck to his arms and the legs look like the bow inwards" /
  "can we move what we did here for this starting scene into the new repo so Justin can see the demo"
- **What happened:**
  - Where it was made: in our practice project on GameStation, in the first hours of the jam (after the 9 PM start on
    Nov 11), then moved here with Unreal's Migrate. Every script that builds it is in this repo.
  - First version: one post-process material that cel-shaded everything. It read as a flat cartoon, and the owner said
    so. The fix was to do what anime does: paint the background, cel-shade only the characters. Characters draw into
    Unreal's custom depth, and the same material uses that as a mask: two flat tones and a rim light for them, real
    light with a brush filter and thin lines for the room. Low golden sun and drawn sunbeams did the rest.
  - Unreal's fog gave no visible light shafts indoors, so the beams are see-through slabs drawn after the look.
  - The whole coffee shop is built by a script from cubes, cylinders and flattened balls (the plant leaves).
  - The hero: Gemini drew him, our local TRELLIS model was lumpy from the side, so we tried the jam partners. Tripo and
    Meshy both made him from the drawing in two minutes; Tripo's face and hair were clearly better.
  - Movement took four rounds. Our script-keyed walk looked rough, so Claude copied Unreal's motion-captured mannequin
    animations onto him with the IK Retargeter (Unreal recognised the skeleton our Blender script builds). Then the
    jacket stuck to his arms: he was modelled arms-down, so sleeves and body were one surface. Tripo's image tool redrew
    him in an A-pose and we made the model again.
  - Claude's own bug cost three failed attempts: on an arms-out model its Blender script measured the "chest" through
    both arms and put the shoulder joint halfway down the upper arm. It only found this by measuring joint positions
    in the animation instead of guessing from pictures.
  - Claude cannot press keys, so it checked the walk by pushing the character along from a script in Simulate mode and
    freezing time for pictures. The owner did the real play tests and caught every one of the problems above.
- **What we learned:** Paint the backgrounds and cel-shade only the characters. Model characters in an A-pose. When an
  animation looks wrong, print the numbers (joint positions) before trying another fix.
- **Media:** `docs/media/anime-cafe-film-look.jpg` (before and after of the room), `docs/media/anime-cafe-jumpcut.jpg`
  (the scene running in this project).
