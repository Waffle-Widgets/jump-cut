# Latte: the instructions are on the screen, not in the room

*Sun 15 Nov 2026, about 1:05 PM Pacific — GameStation · UE 5.8 · by Fable 5.2 (`claude-fable-5-2`) · branch `Gamestation/latte-art`, NOT in the build*

- **What we asked for:** readable instructions, and a branch that will still merge.

- **Prompt we gave the agent:**

  > The text to tell the player what to do looks like it blends into other assets, make sure this is static on
  > the screen so it is easy to read. M_Station is working on assets for the branch so let's make sure we merge
  > clean

- **What happened:**

  **The words were objects.** Every instruction was a `TextRender` component: letters standing in the world,
  lit by the room, outlined by the cel pass, sitting in front of a counter the same colour. The agent had moved
  them to follow the camera, which made them hold still but did nothing for reading them.

  The game already had the right thing. Justin's director draws its cutscene captions in a box on screen
  (`CineSay` into `WBP_CineOverlay`). `BP_LatteGame.LatteSay` now sends every instruction there: white on a dark
  panel, bottom centre, the same place every time. It only speaks when the message changes, so the box is not
  re-set every frame. No change to Justin's Blueprint or his widget.

  It also shows **one step at a time** now. The old text listed all three steps and left you to work out which
  you were on; `LatteCaptionStep` picks the step from the same counters the guide uses, and the keys ride along
  on the end of the line.

  ![The order, in the caption box](../media/2026-11-15-latte-instructions-on-screen.png)

  **Merging clean.** M Station had pushed nothing to the branch yet. `main` had nine new commits from Justin
  (music, a fanfare, the title animation, two fixes); 43 files changed there and 106 here, **none in common**,
  so it merged without a conflict and is pushed. Two things worth writing down:
  - Unreal has to be closed for a merge that brings `.uasset` changes.
  - After the merge, Git LFS made every asset this PC had not locked read-only again, and the next Blueprint
    save answered `SAVED False`. The script printed it; nothing else would have said so.

- **Known flaws:**
  - Not played by a person. Two captions were seen in a screenshot (the order, and step 1 of a tulip).
  - The caption box belongs to the director. If the director speaks during the shift, it will replace the
    instruction until the step changes.
  - GOAL and MATCH are still small world labels beside their pictures.

- **What we learned:**
  - Look for the thing the game already has before building beside it.
  - Read the save result. A read-only file fails without a sound.
