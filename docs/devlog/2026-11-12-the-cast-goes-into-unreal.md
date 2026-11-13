# 2026-11-12 — The cast goes into Unreal (GameStation)

- **What we asked for:** Justin's Epic-account email and his 18+ confirmation, the news that the build had been
  play tested on GameStation, and "we are ready to add the models".

- **Prompt(s) we gave the agent:** the words above, with the email address itself left out of this file on
  purpose — the repo is public and `docs/TEAM.md` explains where addresses are kept instead.

- **What happened:**
  - Two separate things in one sentence. The first closed the last MegaJam rules gap: both members are now
    **confirmed** for §1c/§2/§13 in `docs/TEAM.md`, and the address itself stayed out of this public repo, as it
    has all along. One field was deliberately *not* marked confirmed — the spelling of Justin's legal name is
    still only as the Team Owner gave it, and a legal name that is nearly right is worth nothing on an entry form.
  - The second was the build being played. `ROADMAP.md` had carried a standing warning that `main` held Unreal
    work **no person had ever run**. That is now false, so the warning was rewritten rather than left to rot. It
    was not replaced with a claim we cannot support: per-step results from the 12-item play list in
    `FIRST_BUILD_LEDGER.md` were not reported, so that list is still not ticked off and the length and difficulty
    problems still stand as written.
  - Then the models. This chat was running **on GameStation with the editor already open**, which matters: the
    three rigged characters and the cleaver had been sitting as FBX since the afternoon because `CLAUDE.md` line
    53 says a maker computer never saves Unreal files.
  - The first question was whether the repo could be brought up to date **without closing Unreal**. Switching
    branches with the editor open is a trap we have already hit. Rather than guess, we asked git: this clone was
    on `Gamestation/first-build`, which turned out to be an *ancestor* of `main` (nothing unmerged, just behind),
    and `git diff --stat HEAD origin/main -- JumpCut/Content` came back **empty**. Four commits of docs, scripts
    and one JPG, and not a single `.uasset`. So the catch-up was safe with the editor open, and it was done
    without closing anything.
  - The import itself followed the `asset-import` skill exactly: drop the FBX into its **own folder** under
    `Content/Game/Imported/` and let Interchange pick it up. It imported the mesh, the skeleton, **both**
    animations and the texture together, with no import window — which is what `bShowImportDialog=False` in
    `DefaultEngine.ini` is for. `SkeletalMeshTools.import_file` was not used; `CLAUDE.md` records that going
    wrong twice.
  - We deliberately copied **only** the `.fbx` and left the `.png` behind, because the skill warns that an FBX
    arriving next to its texture pops a modal that freezes the MCP. It turned out not to matter: the texture is
    *inside* the FBX, and came in by itself. Worth knowing for next time — the separate `Tex/` folder the main
    character has is not something the import produces.
  - Each character got a new instance of our own `M_AnimeChar` with its one parameter, `Tex`, pointed at its own
    baked texture — the same shape as `MI_CafeWalker`, read off the existing asset rather than assumed.

- **What we learned:**
  - **Ask git whether a pull is dangerous, instead of assuming it is.** "Close Unreal before you pull" is a good
    rule, but it is a rule about `.uasset` files. One `git diff --stat ... -- Content` turned a disruptive step
    into a safe one. The editor never closed and nothing was lost.
  - **An Unreal asset thumbnail is cached from import and does not re-render when you change the material.** We
    captured the crash driver twice, before and after assigning `MI_CrashDriver`, and the two PNGs were
    **byte-identical**. Judging by the thumbnail would have told us nothing about whether the assignment worked.
    `get_material` did: it returns the `MI_`. The picture below is therefore honest about what it shows — the
    geometry and the baked texture, not the cel-shader.
  - **Numbers caught something a picture then cleared.** The cleaver's bounds read 35.0 × 11.3 × **0.85 cm** — a
    cleaver thinner than a pound coin, which looked like a flat cutout. Rendering it showed a real blade with a
    wooden handle and rivets. The depth is still genuinely thin, which is what image-to-3D does with a side-on
    reference drawing: fine in a hand from the game camera, wrong seen edge-on. A measurement raised it; only
    looking settled it.
  - **The honest limit: none of this is in the game yet.** The models are assets. They are not placed, not on a
    Blueprint, and nobody has seen them from the game camera. Which boss is the plaza boss is an open question in
    `ROADMAP.md`, and `ROADMAP.md`'s own rule is that only a person on the team decides — so no Blueprint was
    re-pointed and no level was touched.

- **Media:** ![The crash driver, the mob boss and the cleaver as Unreal assets](../media/MODELS-IN-UNREAL.png)
