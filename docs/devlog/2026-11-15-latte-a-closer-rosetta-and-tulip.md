# Latte: a closer rosetta and tulip, and R to start over

*Sun 15 Nov 2026, about 11:50 AM Pacific — GameStation · UE 5.8 · by Fable 5.2 (`claude-fable-5-2`) · branch `Gamestation/latte-art`, NOT in the build*

- **What we asked for:** the owner saw our three patterns beside real ones and an honest list of where ours fell short.

- **Prompt we gave the agent:**

  > yes let's make it look as close to real as we can. the user should also have the option to start over if
  > they mess up.

- **What happened:**

  **The simulation did not change. The pour did.** The two weakest patterns were weak because the test pours
  were not how a barista pours them.

  - **Rosetta.** Real: wide leaves at one end narrowing to the other, a small heart at the narrow end, a thin
    stem. Ours was a constant-width wiggle with no heart and a fat stem. The pour is now a short base, a wiggle
    that narrows from 2.0 cm to 0.7 cm over nine swings while pulling back, a 0.7 s rest to make the small
    heart, and a cut that stops short of the far rim. The cut also drags a narrower strip of surface, which
    thins the stem.
  - **Tulip.** Real layers stack up the cup. Ours wrapped round each other like an onion, because every pour
    was the same size and started inside the last. Each layer is now poured *behind* the previous one and
    pushed up into it, and each is smaller (2.3 s, 1.3 s, 0.8 s), so a layer dents the one before it instead of
    swallowing it.

  ![Heart, rosetta and tulip after the change](../media/2026-11-15-latte-three-patterns-v2.png)

  The guide on the cup uses the same numbers: the wavy line tapers, a small ring marks where to rest for the
  rosetta's heart, and the tulip's three rings shrink.

  **Start over.** R pours the same pattern again on a fresh cup, at any time, including after "Beautiful!".
  Overflowing gives a fresh cup with a new random pattern, as before.

  **Room to work.** The fill mark moved from 60 % to 50 % and a close pour fills the cup a fifth slower, so a
  full rosetta (about 7 seconds of close pour) fits even if you start late.

- **Known flaws:**
  - Not played by a person. R, the tapering wavy guide and the small ring have not been seen in any picture:
    the test cup drew a heart the one time the agent looked.
  - The heart is broad in the shoulders, and the rosetta's leaves are still fewer than a real one's.
  - The judge counts actions, not the picture. Still no customer character.

- **What we learned:**
  - When the output looks wrong, check the input before the machine. The same simulation drew a far better
    tulip once it was poured the way a tulip is poured.
