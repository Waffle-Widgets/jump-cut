# Latte: measuring the pour against the goal, and tuning until it lands

*Sun 15 Nov 2026, about 12:15 PM Pacific — GameStation · UE 5.8 · by Fable 5.2 (`claude-fable-5-2`) · branch `Gamestation/latte-art`, NOT in the build*

- **What we asked for:** proof that the goal can actually be poured.

- **Prompt we gave the agent:**

  > make sure the physics of this mini game make the goal achievable

- **What happened:**

  **A number instead of an eye.** Until now "it looks close" was the agent squinting at a screenshot taken past
  a pitcher. `tools/latte_pie.py` now reads the cup's surface back out of the game after a pour (the render
  target, sampled to 64 x 64), and `tools/latte_match.py` lays it over the goal shape and prints how much they
  share. For a striped pattern both are thickened by two cells first, so a rosetta is judged on its outline,
  not on whether each leaf lands on the same pixel. It also prints the two as text, `#` shared, `g` goal only,
  `p` pour only, which is how every fix below was found.

  | | Heart | Rosetta | Tulip |
  |---|---|---|---|
  | Start | 0.52 | 0.44 | 0.52 |
  | Less foam per second (0.012 to 0.0075) | 0.77 | 0.71 | 0.77 |
  | Test script stops teleporting the pitcher | 0.84 | 0.67 | 0.72 |
  | The cut drags less coffee (0.9 to 0.55) | **0.88** | **0.69** | **0.73** |

  **What was actually wrong.**
  1. **Too much foam.** Every pour covered its goal and then kept going: the heart put foam on 93 % of the goal
     and 53 % of its foam was outside it. One number, the foam laid per second, was 60 % too high.
  2. **The goals were playing-card hearts.** Poured foam is rounder, with a shallower cleft. The goal heart
     curve has a roundness term now (`ROUND = 0.6`), used by all three goals.
  3. **The test was lying.** Each pattern had a white nub on top. The script jumped the pitcher to the start of
     the cut in one frame, and the game correctly read a 3 cm jump as a drag and pulled foam with it. A person
     cannot move a pitcher that way. The script now arrives before it pours.
  4. **The cut was a trench.** It carried a plug of coffee through the design and split it in two. Halving how
     much the cut drags left the cleft and the point and thinned the line.

  ![Goal above, poured below, with the measured match](../media/2026-11-15-latte-goal-vs-poured-measured.png)

- **Known flaws:**
  - **The rosetta is not there.** Its outline matches (0.69) but the pour makes one leaf-shaped patch with a
    few lines at the base, not a fern of separate leaves. Two settings fight: enough coffee between strokes to
    separate the leaves also opens a wide gap down the middle.
  - The tulip is three lobes rather than three clear layers.
  - These are the SCRIPT's pours, following the guide exactly. Nobody has tried with a mouse, so "achievable by
    a person" is still not shown. The heart is the one I would bet on.
  - The game's own judge still counts actions; it does not use this measurement.

- **What we learned:**
  - Print the comparison as text. `p` all round the edge said "too much foam" in one glance.
  - Suspect the test rig when all three results share the same flaw.
