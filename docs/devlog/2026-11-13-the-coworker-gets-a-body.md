# 2026-11-13 — The coworker gets a body (M Station)

- **What we asked for:** the Team Owner moved to M Station and told us to carry on with the asset queue, having
  already settled the two calls that were blocking it the night before.

- **Prompt(s) we gave the agent:** the actual words, quoted:

  > continue work from M_Station

  and, from the message before it:

  > 1. Boss 3 will only be in if we can finish everything else. 2. We should use meshy where we can, Trellis can
  > be a backup if we run out of credits.

- **Why this character and not another.** `ROADMAP.md`'s hand-off section sets M Station's queue: the coworker
  first, the Director second, **not** boss 3. She is the only character in the opening beat with no face — beat 1
  asks the player to save her from shrapnel, and she has been a green box in `Lvl_JumpCut` the whole time. Boss 3
  was skipped on purpose; the Team Owner's decision is that no Meshy credits go on him until beats 1-4 play
  through.

- **What happened.** The thing GameStation could not do, this machine can. `CLAUDE.md` records that every Meshy
  model is made "in the user's Chrome", and the GameStation lane had no browser tool at all, so her sheet was
  drawn there and then stopped. M Station has `@playwright/mcp` registered at user scope against a dedicated
  Chrome profile the Team Owner signed into by hand, so the whole Meshy flow ran from the chat: upload, generate,
  remesh, rig, download. The account had 8,357 credits and the run cost **35**.

  The documented recipe was followed exactly — High Detail (Meshy 7.1), Texture on, Ultra 2K, texture 2K, License
  Private, Pose -> A-Pose on — with one setting that was **off** when the page loaded and had to be turned on:
  **Pose**. Everything else was already right.

  The remesh-before-rig rule earned its place again. Image-to-3D returned **384,022 faces**, which is over Meshy's
  300K rig gate, but `CLAUDE.md` is explicit that the gate only stops you when it feels like it, so the remesh was
  driven by hand from the viewer's mesh-ops button: Fixed, **30K, Quad**, 0 credits. Smart Rig on the remeshed
  mesh came back clean — **68 bones**, two leg chains, two arm chains, a four-bone spine, a three-bone head and no
  tail, so the `MESHYCHAR-BAD-RIG` guard never fired.

  `Art/Blender/meshy_character.py` then produced `SK_CafeCoworker.fbx` at **162.0 cm** exactly — her documented
  height — 30,000 triangles from 57,447, with Walk and Idle and a bake fit of **0.072 cm**.

- **The mistake, which was free and is worth writing down.** One Image-to-3D run with Pose on leaves **two**
  generated assets in the panel, and the workspace auto-selected the wrong one. The first remesh ran on an
  **untextured** 191,949-vertex asset rather than the textured 210,280-vertex one, and produced a perfectly good
  28,857-face mesh with no colour on it at all. Nothing in the grid says which is which: both thumbnails are the
  same woman and the untextured one simply renders grey, which is also what the viewer does in shaded mode. What
  tells them apart is the **vertex count** in the info panel. The remesh was redone on the textured asset
  (28,762 faces, Quad) and both remeshes cost 0 credits, so the only loss was a minute. Had it not been caught,
  the rig and the download would both have succeeded and she would have arrived in Unreal as a grey statue.

- **Her colour audit reads FLAG, and it is her own arms.** 4.46% of the front and 5.27% of the back sit within
  dE76 14 of her face tone `#DC8754` while being neither head nor hand. The painted sheet shows every red pixel is
  her **bare forearm**: she wears a short-sleeve shirt, and the audit whitelists the head plus a disc at each
  hand, so the stretch between elbow and wrist counts as a defect by construction. No garment is skin-coloured and
  no hair is skin-coloured — the hard rule holds. This is the same shape of false positive as the TRELLIS crash
  driver's brown-leather highlights, and it is the second time the audit has flagged correct art, so it is worth
  knowing that FLAG means *look*, not *fail*.

- **What we learned.**
  - **A browser is a capability, not a preference.** The same task was blocked on one machine and routine on the
    other purely because of a signed-in Chrome profile. Which machine a job belongs on is decided by that, not by
    which GPU is faster.
  - **Meshy cannot label anything.** The current workspace lists assets by date, with no rename in the grid, the
    Assets sidebar or a context menu. It invented *Welcoming Apron Pose* for her. The Team Owner asked that assets
    be labelled properly "even in Meshy if possible" — it is not possible, so the mapping tables in
    `CHARACTERS.md` are the label, and they are now the only way to find a model from its reference picture.
  - **Judge the asset by its vertex count, not its thumbnail.** See above.

- **What we did not do.** She is **not in Unreal**. `CLAUDE.md` gives M Station the *maker* role — Blender, Meshy,
  sounds, scripts — and says plainly: never save in Unreal, hand the files to the builder. The FBX and its texture
  are committed and ready to be dropped into `Content/Game/Imported/CafeCoworker/`, which is GameStation's job.
  Nobody has seen her from the game camera, and `BP_Coworker` still points at a green box.

- **Media:** ![the colour audit sheet: green is skin where it belongs, red is her bare forearms](../media/2026-11-13-coworker-colour-audit.jpg)
