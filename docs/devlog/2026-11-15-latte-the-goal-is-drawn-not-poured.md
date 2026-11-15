# Latte: the goal picture is drawn, not poured, and everything is the right way up

*Sun 15 Nov 2026, noon Pacific — GameStation · UE 5.8 · by Fable 5.2 (`claude-fable-5-2`) · branch `Gamestation/latte-art`, NOT in the build*

- **What we asked for:** goal pictures that look like the thing they name.

- **Prompt we gave the agent:**

  > the goal images don't really look like what they are supposed to be.

- **What happened:**

  The owner was right, for two reasons the agent had talked itself past.

  **1. The goals were the simulation's own output.** An hour earlier the agent had written, proudly, that "a
  sample image made by the system it is a sample for can never promise something the system cannot do". True,
  and beside the point: a goal has to be recognisable first. A blobby tulip is not a picture of a tulip.
  `tools/latte_goals.py` now draws the three goals from the shapes real latte art has: a heart curve; a rosetta
  as a leaf of chevron bands with a hairline stem and a small heart on top; a tulip as three hearts, each
  pushing a thin line of coffee into the one below. Plain Python, no packages (this PC has no Pillow), written
  as data (red = foam, green = the fine layering) so the game's own surface material colours them like the cup.

  **2. Ours were upside-down.** Every photo of a rosetta or a tulip shows the small heart at the top and the
  stem running down to a point. Ours had the heart at the bottom, because the pour had been set up from the
  barista's side of the cup. The rosetta and tulip pours, and the guides on the cup, are flipped: base low,
  small heart on top, the cut runs down.

  ![Goal above, the script's pour below](../media/2026-11-15-latte-goal-vs-poured.png)

- **Known flaws:**
  - **The goal is now cleaner than anything the pour produces.** The poured patterns have the same structure
    (the heart on top, the leaves, the three layers) but they are organic where the goal is crisp. That is
    true of a real barista's reference chart too, but nobody has played it to say whether it feels fair.
  - The rosetta's wavy guide draws as a ladder of side-to-side strokes, not one continuous line.
  - Not played by a person. The judge counts actions, not the picture. No customer character.

- **What we learned:**
  - "Achievable" is not the first job of a goal picture. Being recognisable is.
  - Check which way up the real thing is shown before building three pours around the other way.
