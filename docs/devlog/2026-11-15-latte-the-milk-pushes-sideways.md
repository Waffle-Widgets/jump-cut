# Latte: milk pushes coffee sideways, not behind it, and the rosetta grows leaves

*Sun 15 Nov 2026, about 12:30 PM Pacific — GameStation · UE 5.8 · by Fable 5.2 (`claude-fable-5-2`) · branch `Gamestation/latte-art`, NOT in the build*

- **What we asked for:** the two patterns that still fell short.

- **Prompt we gave the agent:**

  > the Rosetta and tulip still need a bit of work, mostly the Rosetta

- **What happened:**

  **Four rounds of tuning had not grown a single leaf, so the agent stopped tuning and read its own rule.** A
  moving stream pushes a ring of coffee out around itself; that ring is what should leave a thin brown line
  between one stroke of the wiggle and the next. But the ring went **all the way round**, including behind the
  stream, so every stroke wiped out the trail it had just laid. Turn the ring up and the leaves vanished into a
  brown gap down the middle; turn it down and they merged into one white patch. There was no setting between,
  because the rule was wrong, not the number.

  Real milk shoulders coffee **aside**. The ring is now weighted by direction: full to the sides of the motion,
  nothing ahead or behind (`side = 1 - |dot(direction to the pixel, direction of travel)|`). A still pour has no
  direction, so it keeps its full ring, which is what starts each new layer of a tulip. One line of shader.

  | Outline match (script) | Heart | Rosetta | Tulip |
  |---|---|---|---|
  | Before this session | 0.88 | 0.69 | 0.73 |
  | Now | **0.89** | **0.73** | **0.83** |

  The rosetta's number barely moved and the picture changed completely: it went from a leaf-shaped patch to a
  fern with separate leaves either side of a hair-thin stem. The outline score cannot see leaves. The tulip's
  gain is from a thicker starting ring for each layer, a higher top layer and a smaller base.

  ![Goal above, poured below](../media/2026-11-15-latte-goal-vs-poured-round-two.png)

  Also: six swings instead of nine in the rosetta (the strokes were closer together than they were wide, so
  they could never separate), and the wavy guide on the cup finally draws as a wave.

- **Known flaws:**
  - The poured rosetta has no small heart at the top; the goal does.
  - The tulip's layers read as steps down the sides more than as three separate hearts.
  - Poured by script, following the guide exactly. Nobody has tried with a mouse.
  - The judge still counts actions.

- **What we learned:**
  - When two settings fight and no value satisfies both, the rule they share is wrong. Stop turning dials.
  - A score that cannot see the thing you are fixing will tell you nothing happened. Look at the picture too.
