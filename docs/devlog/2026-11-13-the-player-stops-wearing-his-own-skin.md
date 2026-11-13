# 2026-11-13 — The player stops wearing his own skin (M Station)

- **What we asked for:** part of the city brief — *"If any characters need to be remade for consistency then
  do so."*

- **What happened:**

  **We measured instead of guessing, and the answer was not the one we expected.** The brief could have been
  answered with an opinion, so it was answered with `tools/color_audit.py` over all ten models at once — the
  first time the whole cast has been ranked side by side. Two flagged. Only one was real.

  **`CafeCoworker` flagged and must not be remade.** Her red is only the band of bare forearm between the
  disc the audit allows around each hand and the hem of her short sleeve. Her shirt is white, her apron teal,
  her trousers charcoal — nothing skin-coloured is clothing anywhere on her. The repo had *already* worked
  this out and written it down; running the check again just confirmed it. Remaking her would have cost 35
  credits and a drift risk to fix nothing.

  **`CafeWalker` — the player — was the real one, and he was the worst model in the game.** 6.13% front and
  3.94% back of his body sat within dE76 14 of his own face tone. The leak map put all of it on the
  shoulders, the upper arms and the sleeve down to the elbow: the cream shirt. Measured straight off that
  map, it was **`#F3E3CF`, dE 8.8 from `#FDD9BF`**, with dominant texels as close as **6.0**, against a
  threshold of 14. At distance his torso and his arms were one shape.

  **The repo already knew.** `COWORKER-APOSE` names it in as many words — *"the one failure this cast already
  has (`CafeWalker`'s cream shirt, dE76 14.4 from his face)"* — and her whole design was written to avoid
  repeating it. It was recorded in November and never fixed, and the baked model turned out worse than the
  14.4 that was written down.

  **The timing was the best it will ever be.** `BP_Player` still wears Epic's mannequin, so nothing
  downstream pointed at the old model — no retarget, no material instance, no placed actor. After the import
  it would have cost the same 35 credits *plus* the rework.

  **The replacement colour was chosen by arithmetic before anything was drawn.** Khaki-brown `#9C8457`
  measured against every cast and power colour at once: 34.8 from his skin, 38.6 from his own apron, 33.9
  from his trousers, 47.5 from goon graphite, 50.9 from Freeze Frame's pale cyan, 80.2 from Splice's magenta
  and 57.0 from the Stunt Double's orange. Rust and terracotta were ruled out on the same numbers — they sit
  in the Stunt Double's hue band at 20°, and a shirt that dilutes a power colour is a different bug.

  **One thing had to be learned twice.** The first three takes looked like a failure — cream again — and the
  prompt was rewritten on that basis. They were **stale files**: the wait condition only checked that three
  takes existed, not that they were new, so what came back was the original November sheet. The claim "the
  model drew cream three times" went into `prompts.md` and had to be taken out again before it was committed.
  The second lesson was cheaper: `gen_images.py` defaults to `1664x928`, which puts a standing figure in a
  small part of a wide frame; the rest of the cast was drawn at `1024x1536` and this had to match.

  **It worked.** Nothing about him changed except the colour — same hair, same face, same apron, same
  trousers, same shoes, same pushed-up sleeves.

  | | old (cream) | new (khaki) |
  |---|---|---|
  | shirt on the baked model | `#F3E3CF` | **`#847755`** |
  | dE76 from his own face | **8.8** (threshold 14) | **40.3** |
  | skin leak, front | **6.13%** | **1.03%** |
  | skin leak, back | **3.94%** | **0.44%** |
  | what the red covers | shoulders, upper arms, sleeves | two small bands at the wrists |

  **He still reads FLAG and that residue is the coworker's false positive**, arriving on schedule: the bare
  forearm between the hand allowance and his pushed-up cuff. The sleeves stayed pushed up deliberately — the
  leak map showed they were never the fault, and changing two things at once would have made it impossible to
  say which one fixed it.

  **Verified by re-importing the exported FBX**, not by reading the generator's log: 69 bones (the same count
  as before), 175.01 cm, 30,000 triangles, 0 unweighted vertices, Walk and Idle both present, bake fit
  0.077 cm. The walk was checked by eye: legs alternate, knees bend, feet plant, and the apron does not drag
  with `Bone_010`, which top-owns 18% of the mesh and was the thing most likely to ruin it.

  35 credits (8,287 → 8,252). The remesh and the rig were free. Meshy named him *The Reluctant Barista*.

- **What we learned:**
  - A flag is a reason to open the leak map, not a verdict. Two of this cast's three flags are the tool
    failing to tell a bare arm from a skin-coloured sleeve, and acting on either without looking would have
    burned credits to fix nothing.
  - "Wait until N files exist" is not a wait when the files already exist. It cost a wrong conclusion and a
    sentence that nearly reached a commit as fact.
  - A defect that is written down is not a defect that is fixed. This one sat in `prompts.md`, correctly
    measured, used as a cautionary tale in another character's design, for a full day.
  - Pick a colour by measuring it against everything it has to live beside, *before* it is drawn. It took one
    run, and the alternative — "rust looks nice" — would have quietly diluted boss 3.

- **Media:**

  ![The player's colour audit after the fix: the shirt is clean, only the bare forearms read](../media/2026-11-13-walker-colour-fixed.jpg)
