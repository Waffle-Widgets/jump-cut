# 2026-11-14 — Say what is there, not what is absent (M Station)

- **What we asked for:** finish the three pictures the Team Owner sent back — the title card, the "to be
  continued" card and the itch.io cover — and make the main character's apron stop changing between them.

- **Prompt(s) we gave the agent:** the Team Owner's review, quoted in full in yesterday's entry. The line
  that set the whole job was *"We need to have a way of making sure characters don't change details like
  this between generations, else the game be labeled AI slop."*

- **What happened:**

  Yesterday we built the character lock: one canonical description per character, held in
  `docs/character-locks.json`, substituted into prompts by a token so no prompt is ever allowed to describe
  him by hand. It worked, in the sense that it made every prompt say the *same* words. It did not work in the
  sense anyone cares about: the model kept drawing a cross-back apron anyway. Four takes, four cross-backs,
  with "no crossed straps" in the prompt **and** "cross-back apron" in the negative list.

  We also could not get a manufacturer badge off the car's grille. "No badge, no emblem" in the prompt,
  "car badge, car emblem" in the negative, ignored every time.

  The thing that broke both open was noticing they were the same sentence. *"Leaving his back bare with no
  crossed straps"* and *"a grille with no badge"* are both descriptions of an **absence**, and the model
  drops absences. So we rewrote the grille as a thing instead: *"a plain black horizontal mesh grille whose
  centre is smooth and empty."* The next take was clean.

  We then did the same surgery on the lock. Both aprons' strap clauses now describe what the back actually
  looks like — *"one single strap that rises from the two top corners of the bib and meets in a loop high
  behind his neck, so that seen from behind the whole of his back is plain khaki shirt with nothing on it"* —
  instead of listing what should not be there. The negatives stayed; they cost nothing. Seven takes later we
  had two that were exactly the lock - the coworker on the title card and the player on the ending card -
  where four takes before the rewording had produced none. Those two are the ones we picked.

  **This is a rewording, not a change to the garment.** The rule we wrote yesterday still stands: a lock is
  never edited to match a picture that came out differently, because the lock describes the rigged model and
  the model is the truth. The apron is the same single-neck-loop bib apron it always was. Only our words for
  it changed. That reasoning is written into the lock's own notes so the next person does not read the edit
  as permission to redefine a character.

  **The badge did not stay fixed, and we stopped rolling dice.** Positive wording cut the rate — one clean
  take in three, then zero in three. Six takes, one badge-free, and the best picture on every other count was
  one with a blank black disc on the grille. So we added `--patch-out` to the new `tools/promote_ui.py`: it
  copies the grille from 76 px to the left over a 40 × 48 px ellipse, feathered. Deterministic, one second,
  and the picture it produces is reproducible from the exact command, which is now in the `PREJAM.md`
  declaration row. It removes a shape and adds nothing, and the disc it removed was already blank — no name,
  no letters, no mark of any kind.

  **Dead end, worth recording:** `--lock-ref`, which hands the model the character's reference sheet as an
  image, was the other lever we had written down for exactly this problem. On a *scene* it is useless. It
  routes through Qwen's image-edit workflow, and both takes came back with different people in a different
  cafe, the car pasted flat into the wall like a sticker and no frozen time at all. It may still be right for
  a portrait. It is not right for a key visual, and nobody should spend ten minutes finding that out again.

  **A correction to yesterday's record.** The declaration row written at 7:15 PM said the prompt change had
  solved the badge. It had not — that row was written before the takes came back. It has been rewritten to
  say what actually happened and to name what it supersedes.

- **What we learned:**
  - **A negation is not an instruction.** Every rule we gave this model as an absence was dropped; every one
    we gave as a description was followed. That is now the first note in `character-locks.json`.
  - **A lock makes us consistent. It does not make the model obedient.** It removes the drift we cause — three
    hand-written descriptions could never have agreed — and improves, but does not guarantee, the rest. Counting
    honestly: **2 of 7 takes after the rewording drew the back exactly as the lock describes it, against 0 of 4
    before it.** The other five ranged from a single diagonal strap to a full cross-back. That is a better
    coin, not a solved problem. **Draw several takes and look at the back of every one before picking.**
  - **When a picture is one small shape away from right, edit the shape.** Six takes to dodge a 40 px disc is
    worse work than removing it, as long as the edit is a committed command and a declared row.
  - **Stretching is drift too.** Qwen draws 16:9 at 1664 × 928, which is 1.793:1, not 1.778:1. Resizing
    straight to 1920 × 1080 squashes by 0.8%, and a different squash each time is the same class of bug the
    lock exists to stop. `promote_ui.py` centre-crops to the target aspect first and never stretches.

- **Media:**

  ![The apron back: a cross-back take beside the canonical one](../media/2026-11-14-apron-back-before-after.jpg)

  ![The title card: street through the hole, the driver by the open door, the register beside the car](../media/2026-11-14-title-card-fixed.jpg)

  ![The ending card: the tower far beyond the end of the street](../media/2026-11-14-ending-card-fixed.jpg)

**Nothing here has been seen in Unreal.** The three screens are source PNGs in `Art/UI/`. The title and the
ending card are already imported as textures from the *old* pictures, so both `.uasset`s need re-importing on
a builder machine before any of this is in the game — that is on issue #44's follow-up, not done here.
