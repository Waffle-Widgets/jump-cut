# Looking up how people stand, instead of guessing again

*Sun 15 Nov 2026, about 6:30 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** after five rounds on the idle, a fair question.

- **Prompt we gave the agent:**

  > this looks unnatural, why do you keep getting this wrong? If you need to look up how normal people stand please
  > do.

- **Why it kept going wrong:** every round fixed the one thing named (the elbow, the shoulder, the hand) by eye,
  against the previous version of our own pose. Nothing was ever compared with a person. So the parts nobody had
  named yet stayed wrong, and each fix was judged against a stand that was already unnatural.

- **What happened:**

  **Looked it up.** Three things with numbers:
  - People choose to stand with about **17 cm between the heel centres and 14 degrees between the feet** (McIlroy &
    Maki 1996, 262 adults aged 19 to 97).
  - With the arms hanging relaxed, **the fingertips reach mid-thigh**; a drawing guide warns that hands stopping at
    the hip look stunted.
  - Body heights as a share of stature (Pheasant, *Bodyspace*, from memory, not re-checked today): shoulder 0.82,
    wrist 0.485, fingertip 0.375.

  **Measured ours against it.** `posture_check.py` now prints a table, ours beside a person of his height:

  | | ours before | a person | ours now |
  |---|---|---|---|
  | ankles apart | 27.6 cm | 17 | 16.7 |
  | angle between the feet | 28 deg | 14 | 14 |
  | knee bend, left / right | 16 / 24 deg | 0-5 | 10 / 9 |
  | wrist outside the shoulder | 4.5 cm | hangs straight down | 1.0 |
  | fingertip height | 72 cm | 65 (mid-thigh) | 72 |
  | shoulder to wrist | 48 cm | 58 | 48 |

  - **The feet were 28 cm apart**, wider than his shoulders, because an earlier round wanted a "hero" stand. That
    is the single biggest reason he never looked like a person standing.
  - **The hands hovered** 4 to 5 cm out from his thighs, because an earlier round asked for arms that do not touch
    the torso and I pushed the whole arm out instead of letting it hang. A hanging arm clears the ribs by itself.
  - **One knee was bent 8 degrees more than the other.** His right leg is the longer one. The pelvis now rolls 2.5
    degrees to take that up and the chest rolls 2.5 back, so both knees read the same and the shoulders stay level.
  - **The knees pumped with the breath** (3 to 15 degrees), the same mistake as the elbow two entries ago: a
    distance animated on a limb that is nearly straight. The breath is off the pelvis height.

  ![In the game, front](../media/2026-11-15-idle-human-front.png)
  ![In the game, side](../media/2026-11-15-idle-human-side.png)

- **Not fixed:**
  - **His arms are 10 cm short.** Shoulder to wrist is 48 cm where a person his height has 58, so his fingertips
    stop at hip height, not mid-thigh. That is the model's skeleton. Lengthening it changes the rest pose, which
    means rebuilding all 13 clips and re-importing the skeleton; not started this close to the build.
  - The knees are at 10 degrees, not 0 to 5: any straighter and the feet lift off the floor.
  - The other 12 clips still start and end in the old wide stance, so his feet slide about 5 cm each when an
    attack blends back to standing.
  - Stills, one room. A person has to play it.

- **What we learned:**
  - Compare with the real thing, not with the last attempt. A table of "ours / a person" found three faults nobody
    had named in five rounds of feedback.
  - Two requests ("hero stance", "arms off the torso") were each met by a number that later made him look wrong.
    When a new complaint arrives, re-read what earlier fixes did to the same limb.
  - The same bug twice in one morning: breath on a near-straight limb. It is in the code as a comment now.

Sources: [McIlroy & Maki 1996, preferred foot placement](https://data.zhenzhi.com/details/1/903011102) ·
[PoseMy.Art, drawing standing poses](https://posemy.art/blog/drawing-standing-poses-guide/) ·
[Proko, balanced poses](https://proko.com/how-to-draw-balanced-poses)
