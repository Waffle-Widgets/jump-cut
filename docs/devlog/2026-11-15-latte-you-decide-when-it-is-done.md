# Latte: you decide when it is done, and you choose the pattern

*Sun 15 Nov 2026, about 12:40 PM Pacific — GameStation · UE 5.8 · by Fable 5.2 (`claude-fable-5-2`) · branch `Gamestation/latte-art`, NOT in the build*

- **What we asked for:** the owner played the tuned pours and the game kept taking the cup away from them.

- **Prompt we gave the agent:**

  > it shouldn't pause once you got close enough to the goal, it should allow the user to see their art, decide
  > if they want to add anything, and or be done or start over. We should also have the option to select the
  > art we want to do.

- **What happened:**

  An hour ago the agent made the pour end by itself the moment the design and the cut were counted, and wrote
  that up as an improvement ("the cup is done when the art is done"). Played, it is the game deciding for you:
  the pitcher stops while you are still looking at what you made.

  - **Nothing ends the pour now except you.** E is "I am happy with it", R is a fresh cup with the same
    pattern. A full cup stops taking milk and says so, and still waits.
  - **1, 2, 3 choose heart, rosetta or tulip**, at any time, on a fresh cup. The first cup is still random.
  - The line that shows where to cut goes away once you have made the cut, so it is not drawn across your
    finished art.
  - The keys are always on screen above the cup.

  ![Finished, and still yours](../media/2026-11-15-latte-you-decide-when-it-is-done.png)

  The counting that used to end the pour (seconds of close pour, wiggles, layers, the cut) now only drives the
  guide: which ring or line to show next.

- **Known flaws:**
  - E, R and 1/2/3 have never been pressed by anyone: a script cannot press a key. The check was that a finished
    heart leaves the game still pouring (`Ending=False`) with the keys on screen.
  - Because E always finishes, a bad cup is served like a good one. There is no reaction to quality.
  - Still no customer character.

- **What we learned:**
  - A rule that feels tidy on paper ("it ends when it is complete") can be the game taking a decision away from
    the player. Ask who should be making it.
