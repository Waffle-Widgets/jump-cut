# 2026-11-12 — The boss that walked on its arms (M Station)

- **What we asked for:** models made from the CleaverBoss reference pictures that had never been through Meshy.

- **Prompt we gave the agent:**

  > create meshy models for the Cleaver boss images that were not used yet.

- **What happened:**

  Six unused CleaverBoss pictures existed. Two were made into models and four were deliberately left alone, which
  is worth saying out loud because "not used yet" could have meant all six and burned 210 credits instead of 70.
  `BOSS2-APOSE-1/2/3` have the cleaver crossing the trouser leg — image-to-3D fuses whatever overlaps, which is the
  exact defect the `BOSS2-NOBLADE` prompt was written to dodge. `BOSS2-NOBLADE-1` is a fine picture in the ComfyUI
  rendering the team has since voted against. That left the two Gemini takes, both in the agreed cel-shaded anime
  look: one drawn with an earlier picture of ours attached, one drawn in the text-only chat with nothing uploaded.

  Both generated cleanly on meshy.ai in our own browser — 35 credits each, A-Pose enforced, texture on, Ultra 2K,
  License Private — and the credit counter moved 8,427 → 8,357, which is exactly 2 × 35 and is how we know both
  were charged rather than one silently failing.

  Then the interesting part. **Meshy's "rigging refuses over 300K" gate is not reliable.** The 477,752-face model
  was stopped and offered the free remesh dialog, as documented. The 300,892-face model — also over 300K — was
  waved straight through to the real *Rig Model* dialog. We let it, reasoning that Meshy knows its own limits and
  our Blender step decimates to 30,000 triangles anyway.

  It came back green. 60 bones, 178 cm, 300,892 → 30,000 triangles, bake fit 0.058 cm, Walk and Idle exported. The
  contact sheet showed a man walking. Every number was fine.

  Except the log also said `"legs": []`. A two-legged man with no legs. Reading the bone positions settled it: the
  chain the script had labelled an *arm* ran from z = 83 cm to z = 47 cm to z = 9 cm, with its last bone sitting on
  the floor at z = 3 cm. That is a leg. Smart Rig on the un-remeshed mesh had produced a degenerate 60-bone
  skeleton with a **one-bone spine**, and our limb-finding heuristic had assigned the legs to the arm slots and
  found no legs at all. The walk was swinging the legs *as arms* and leaving the real arms hanging dead — which,
  from the side, at six frames, looks like walking.

  Remeshing that same model to 28,025 Quad and rigging *that* gave a clean 31-bone rig: two legs, two arms,
  a four-bone spine, no phantom tail. The standalone remesh (viewer bottom bar → mesh-ops → Remesh → 30K + Quad)
  is **also 0 credits**, so there was never a reason to skip it.

- **What we learned:**

  - **Always remesh to 30K Quad before rigging.** Do not let Meshy's gate decide for you; it let a 300,892-face
    model through and the rig it produced was unusable. Written into `CLAUDE.md`.
  - **A green log is not a result.** Every headline number on the broken run was good. The only tell was a single
    empty list in a field nobody reads, and the rendered picture *agreed* with the wrong answer. This is the second
    time in two days the limb-finder has silently mislabelled a bone chain — the first was a human's leg called a
    tail.
  - So `meshy_character.py` now prints `MESHYCHAR-BAD-RIG` and writes to stderr when a `smart` rig comes back with
    no leg chains. A bad rig that shouts costs ten minutes; one that renders a plausible walk costs whatever it
    costs to find it in Unreal on Saturday.
  - **Nothing was overwritten.** `SK_CleaverBoss.fbx` on `main` is untouched; these landed as new names, so the
    boss is now a choice between three rather than a replacement nobody agreed to.

- **Still untested:** none of this has been inside Unreal or seen from the game camera. On a maker computer that is
  the honest limit — `CLAUDE.md` line 53 says a maker hands the files over and GameStation judges them.

- **Media:** ![The three CleaverBoss models — reference, idle and walk for each](../media/2026-11-12-cleaverboss-three-models.jpg)
