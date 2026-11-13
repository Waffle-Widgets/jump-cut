# 2026-11-12 — The third boss gets written before anyone draws him (GameStation)

- **What we asked for:** boss 3 had just been given a power by the Team Owner's boss-ladder decision and nothing
  else — no design, no colour, no reference art, no prompt. This lane was asked to close that gap in documentation
  only, with the Unreal editor off limits (another lane was in it) and no image generation of any kind, so that
  whichever machine has image generation could draw him later without anyone having to think first.

- **Prompt(s) we gave the agent:** the actual words were

  > YOUR GOAL: write the design for the Stunt Double boss, and write the text-to-image prompt that will produce
  > his reference sheet, so that whichever machine has image generation can render him immediately with no further
  > thinking required.

  with the brief for the character itself:

  > a 'Stunt Double' is the person who takes the hit for the star — doubles, body-doubles, falls, fire gags, wire
  > work, crash pads. Think about what that means for a boss who can presumably create or BE duplicates of
  > himself, or who cannot be hurt because someone else takes the damage. [...] Make him silhouette-distinct from
  > the other three (a lean apron-wearing worker, a burly leather-jacketed biker, a broad-shouldered suited mob
  > boss) — at 64 pixels tall a player must be able to tell them apart.

  and a list of hard constraints that were all things this project has already been burned by: the cel-shaded
  anime style must not drift, pale cyan belongs to Freeze Frame and magenta to Splice, no skin-coloured clothing
  and no clothing-coloured skin, nothing may protrude past the character's outline, a wide A-pose with gaps, and
  any prop must be a separate model on a hand socket.

- **What happened:**

  He came out as a cheerful man in a safety-orange fire-gag coverall with flat navy pads on every joint, and the
  design turns on one idea: **the doubles he makes wear the player's face.** A stunt double's job is that the
  damage lands on the wrong person on purpose, so the boss does to the player what has been done to him for twenty
  years. Every hit on him transfers to a stand-in and he cannot be touched until they are gone; Splice is the
  counter because teleporting puts you behind the screen of doubles. He is also the only boss who is not angry,
  which is free — it lives in his face and costs no geometry. The full write-up is
  [`CHARACTERS.md`](../CHARACTERS.md#the-third-boss--stuntdouble-proposed) and it is labelled a **proposal**,
  because `ROADMAP.md` says an agent may propose and never writes its own suggestion into Decisions.

  **The colour was chosen with a calculator, not an eye, and that is the reusable part.** The cast's one real
  colour failure is `CafeWalker`'s cream shirt sitting **dE76 14.4** from his face skin — close enough that 6% of
  his front flags as skin in `tools/color_audit.py` and his head, shirt and hands merge at game-camera size. That
  was found *after* the model existed. So this time the palette was checked before a word of it was written down:
  skin `#F0C49A`, hair `#241A15`, coverall `#E8601D`, navy `#232A38`, hi-vis bands `#C9CFD6`. Worst skin
  separation **33.0**, worst pair anywhere on him **17.0**, both clear of the threshold with room.

  The orange was also checked against the rest of the game rather than asserted to be different: dE **98.4** from
  Freeze Frame's pale cyan, **74.0** from the mob boss's measured magenta shirt. The interesting one was the crash
  driver's brown leather, which `CHARACTERS.md` records only as "jacket brown" with no hex — so his committed
  texture was sampled directly. `T_CrashDriver_BaseColor.png`'s two biggest non-background clusters are `#584848`
  and `#483838`: very dark, nearly desaturated browns at value 0.28–0.35, dE **76.1** and **78.4** from the new
  orange. That also quietly confirms what the Gemini pass said in words — he is much the darkest of the three.

  **Sampling that texture needed a detour.** `tools/color_audit.py` cannot run on GameStation: neither Python 3.14
  nor 3.13 on this machine has Pillow or numpy, which is why the audit has only ever been run on M Station. Rather
  than install anything on a jam machine mid-jam, the PNG was decoded in pure standard-library Python — zlib plus
  the five PNG row filters, every fourth row and every fourth pixel into a 4-bit-per-channel histogram. It read a
  2048×2048 texture in 4.7 seconds. Worth writing down: **any machine can read a baked texture's colours without
  the audit tool installed.**

  **Two things in the prompt are deliberately different from the four codes that drew the existing cast**, and
  both are inherited failures rather than taste. His arms are asked for at about **fifty-five degrees** rather
  than forty-five, because the lane running TRELLIS on the 5090 at the same time as this one found that
  `trellis_character.py`'s automatic weighting handed `clavicle_r` 2,234 of 14,140 verts (16%) on
  `SK_CrashDriverTrellis`'s shoulder accessory, against `upperarm_r`'s 348, so a 50° shoulder swing flattens the
  sleeve into a plate — and this character's shoulder pads are exactly that kind of accessory. The finding asked
  for a wider A-pose in the reference sheet, so it is in the prompt before he is drawn once. And the **pads are
  pinned down hard** — flat panels, level with the surface, no gap underneath, no bulging foam — because a pad
  drawn floating above a sleeve comes back from image-to-3D as a loose shell, which is the same class of defect as
  the crash driver's ice spikes crossing his silhouette.

  **He gets no prop, and that was a decision rather than an omission.** The obvious stunt prop is a breakaway
  chair, and the honest reading of our own history is that a chair would fail: four thin spindly legs is precisely
  the geometry image-to-3D fuses into a block or shatters, and the cleaver only survived because it is a single
  flat slab. His weapon is the doubles, so there is nothing to split into a second prompt, no hand socket to solve
  and no second 3D asset to make — which is the right shape for a boss sitting at number 2 on the cut list.

  **Where the prompt went: both files, on purpose.** The self-contained version is `GEM2-BOSS3` in
  [`prompts-gemini.md`](../prompts-gemini.md), and a version for the local ComfyUI script is `BOSS3-APOSE` in
  [`prompts.md`](../prompts.md). Putting it in only the Gemini file would have left the path the canonical cast
  actually came from unable to draw him — the Team Owner's Nov 12 decision is that the ComfyUI/Qwen models are the
  ones we build on — and putting it in only `prompts.md` would have lost the self-contained text the design now
  lives in. The new code was checked against `gen_images.py`'s parser rather than assumed to work: all six codes in
  the file still resolve, including the new one, which has explanatory prose between its heading and its quote.

  **The one thing nobody should read past:** nothing was drawn. There is no picture of this character, no model and
  no asset. This entry is a design and two prompts, and boss 3 is still conditional on Friday going well.

- **What we learned:**

  - **Check a palette before the model exists, not after.** `CafeWalker`'s shirt-to-face 14.4 cost a grid search
    over every pale colour and still has no agreed fix. The same check costs about a minute while the character is
    still only words, and it is the one defect in this pipeline that is cheap to prevent and expensive to repair.
  - **A measured colour beats a described one.** "Jacket brown" cannot be compared to anything. `#584848` can.
  - **You do not need the audit tool to read a texture.** Pure-Python zlib plus the PNG row filters decoded a
    2048² base colour in 4.7 s on a machine with no Pillow and no numpy.
  - **A finding from another lane is worth more if it reaches a prompt the same evening.** The TRELLIS shoulder
    weighting result landed while this was being written, and the fix it asked for is in `GEM2-BOSS3` before a
    single take has been drawn — which is the cheapest a fix is ever going to be.
  - **Design costs nothing to write and everything to not have.** Boss 3 has been "if there is time" for two days,
    and if Friday had gone well we would have spent Saturday evening inventing him from scratch. He is still only
    a proposal, and a person still decides; but the proposal exists now, with its numbers done.

- **Media:** none. Nothing was generated — no image generation ran on either machine for this entry, which is the
  point of it.
