# Latte art: you pour a cup before the car comes through the wall

*Sun 15 Nov 2026, about 10:50 AM Pacific — GameStation · UE 5.8 · by Fable 5.2 (`claude-fable-5-2`) · branch `Gamestation/latte-art`, NOT in the build*

- **What we asked for:** a latte-art mini game in the cafe, before the opening cutscene. The player has to finish
  one cup for the story to start.

- **Prompt we gave the agent:**

  > Can we open a branch to try to get the latte art? Mini game in? We probably want to use Niagara for the coffee
  > and cream. Let's make the process of making the latte art realistic since we are in unreal engine. [...] This
  > will come before the cut scene. We need the player to do at least one latte art to trigger the cut scene and
  > they must finish it.

  The agent pushed back first: it was 10:21 AM on bug-fix day, 98 minutes before the final build, and a new
  feature in front of the whole game is the riskiest place for one. The answer:

  > We are making it in a branch and if we finish it then it goes in. [...] A pour that looks right and responds
  > to your hand. The pattern should be random each time the user plays, we can include those three at least. We
  > could use the mouse to move the pitcher and use the mouse buttons to pour and adjust how much they are
  > pouring. We need to disable attacks while they are pouring.

- **What happened:**

  **Research first.** The owner asked the agent to watch a video. It cannot watch video, and said so; a research
  agent read written barista guides instead (Prima Coffee's complete guide, Seelaz's foundations, Oddkin's
  rosetta guide; the Barista Hustle pages were behind a paywall). Every guide reduces to two rules:
  - Poured from **high** (7-15 cm), milk plunges under the crema and the cup just fills, brown.
  - Poured **close** (1-2 cm), the foam floats and draws white. A heart is one growing dot; a rosetta is a
    wiggle while you pull back; a tulip is stacked dots, each pushing the last. All three end with a lift and a
    cut straight through.

  **So the game is those two rules.** The cup's surface is a 512 px picture that redraws itself every frame from
  the frame before (`M_LatteSim`, two render targets swapped). A close pour is a *source*: everything already
  drawn is pushed away from the spout, with a mirror source outside the cup wall so the pattern bends round the
  wall instead of leaving. A high pour lays no white, punches a thin brown dot and drags the surface the way the
  pitcher moves. Nobody drew a heart, a rosetta or a tulip. They come out of the two rules:

  ![A rosetta from a wiggle](../media/2026-11-15-latte-rosetta.png)
  ![A tulip from three pours and a cut](../media/2026-11-15-latte-tulip.png)

  Two details made it work. A moving spout drags a thin brown rim, which is what turns a wiggle into separate
  leaves instead of one white band. And the first quarter second of each new pour carries a full brown rim,
  which is the line between a tulip's layers. Without it the three pours merged into one blob.

  **Controls.** Mouse moves the pitcher. LEFT button pours from high; RIGHT pours close. The cup must be filled
  to finish. The pattern is picked at random each cup and the steps are written under the cup. Finish the wrong
  thing and you get a fresh cup.

  **No Niagara.** The owner suggested it; the pattern on the surface is the part that has to respond to the hand,
  and a render target does that exactly and costs nothing. The milk stream is a plain cylinder. A particle
  stream would be the next thing to add.

  **Where it hooks in, without touching the director.** `BP_OpeningDirector` starts the opening the moment the
  player's input unlocks after the title. So `BP_JumpCutGameMode.JumpCutStartPlay` now hands the player to
  `BP_LatteGame.LatteTryBegin` instead of unlocking him, and the mini game unlocks him when the cup is done.
  Input locked also means no attacks while pouring.

  **A bug found on the way.** The first test showed the opening cutscene already 2 seconds in *behind the title
  screen*: on the first frame the director can tick before the game mode has locked the player. The mini game
  now locks the player in its own BeginPlay, before any tick, and is not spatially loaded so it exists on frame
  one. Whether `main` has the same race in a packaged build is not checked.

  **Testing a mouse game without a mouse.** A script cannot hold a button. `tools/latte_pie.py` moves the
  pitcher with `LatteDebugMove` and pours through `LattePour`, the same function the mouse drives, from the
  editor's own tick. The first version of the tulip looked broken in this harness and was not: the game's own
  tick cleared a "was pouring" flag between the script's calls, so every frame counted as a new pour (534 pours
  instead of 3). Counting a new pour by a time gap (0.15 s) fixed the harness and is the better rule anyway.

- **Known flaws:**
  - **Nobody has played it with a mouse.** Every picture here was poured by the script. Mouse speed
    (0.012 cm per count) is a guess.
  - The cup, saucer and pitcher are basic shapes (the pitcher is a cone). The text is world text, not a widget.
  - The judge is loose: a heart is 1.5 s of close pour plus a cut, a rosetta is 6 wiggles plus a cut, a tulip is
    3 pours plus a cut. It does not look at the picture.
  - Whether the health HUD shows over the mini game is not checked.
  - Justin's test scripts that skip the title will now stop at the cup.

- **What we learned:**
  - Ask what has to respond to the hand before picking the technology. Here it was a picture, not particles.
  - Two real rules gave three patterns for free. Drawing three patterns would have given three animations.
  - A test harness that shares state with the thing it tests can fail on its own. Check the counters, not just
    the picture: `Blobs=534` was the clue.
