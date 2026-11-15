# Latte: checked against real latte art, and a guide you can follow

*Sun 15 Nov 2026, about 11:40 AM Pacific — GameStation · UE 5.8 · by Fable 5.2 (`claude-fable-5-2`) · branch `Gamestation/latte-art`, NOT in the build*

- **What we asked for:** the goal pictures should look like real latte art, and the player should be able to make them.

- **Prompt we gave the agent:**

  > We need to make sure the latte art we are shooting for looks how it is supposed to and we also need to make
  > sure the player is able to achieve that art, all while keeping it feeling real/true to latte art. Look at
  > images online of real latte art to see what it is supposed to look like. The movement feels better now.

- **What happened:**

  **Looking at real cups.** The agent opened an image search for heart, rosetta and tulip from above and
  compared them with its own goal pictures. Two things were plainly wrong:
  1. **A real heart and a real tulip have no dark line through them.** Ours were split down the middle. The
     cut-through does not divide the foam, it *pulls* it: the far edge is dragged in (the dimple) and the near
     edge is drawn out (the point). In the simulation the high pour was punching a brown trench. It now drags a
     wider patch of the surface with the pitcher and leaves only a hair-thin stem.
  2. **A latte is caramel, not black coffee.** The crema was two shades too dark.

  ![The heart after the change](../media/2026-11-15-latte-heart-like-a-real-one.png)

  **Making it achievable: the guide is the recipe.** The pours that made the goal pictures are a list of
  positions in `tools/latte_pie.py`. The same numbers now draw a dashed guide on the coffee itself
  (`LatteGuideStep`): a ring to pour into for the heart (it is the size the white should reach), one ring at a
  time for the tulip's three layers, a wavy line to follow for the rosetta, and then a straight line for the
  cut, with dashes that run the way you should move. Follow the guide and you repeat the pour that made the
  goal.

  ![The guide ring for a tulip's next layer](../media/2026-11-15-latte-guide-ring.png)

  **The cup is done when the art is done.** Before, the only way to finish was to fill the cup to the top,
  which meant pouring more milk over a finished heart. Now the pour ends when the design and the cut are done
  and you let go of the mouse. Overflowing first is the way to fail.

  **A goal picture that showed the wrong cup.** Re-capturing a goal texture deletes the old one, and the
  material instance that pointed at it silently fell back to its parent's default: the *live* cup. So the GOAL
  showed whatever was being poured, one frame late, and for one screenshot a rosetta's goal was a tulip.
  Re-pointing the instances after every capture fixes it; `latte_build.py assets` does that.

- **Known flaws:**
  - Not played by a person since these changes. The guide has been seen in one screenshot; nobody has tried to
    follow it with a mouse.
  - Our rosetta's stem is thicker than a real one, and the tulip's layers are rounder.
  - The judge still counts actions (seconds of close pour, wiggles, separate pours, a cut), not the picture.
  - Still no customer character.

- **What we learned:**
  - Compare with the real thing before tuning. Ten minutes of photos found a fault two hours of tuning had not.
  - If you have a script that makes the right answer, show the player the script.
